"""
Server MCP in SOLA LETTURA per il registro elettronico DidUP (Argo Famiglia).

Usa il wrapper non ufficiale `didupwrapper`. Espone solo tool che leggono dati:
nessun tool scrive, giustifica assenze o modifica qualcosa.

Credenziali da variabili d'ambiente:
  DIDUP_SCUOLA   codice scuola (es. SC12345)
  DIDUP_USER     nome utente
  DIDUP_PASS     password

Avvio:
  python didup_mcp.py                      # stdio (Claude Desktop, Hermes, ecc.)
  python didup_mcp.py --http --port 8765   # streamable HTTP
"""
from __future__ import annotations

import argparse
import asyncio
import os
from typing import Any

from didupwrapper import DiDUPClient, DiDUPError
try:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP
    MCP_V2 = False
except ModuleNotFoundError:  # mcp 2.x
    from mcp.server.mcpserver import MCPServer as FastMCP
    MCP_V2 = True

mcp = FastMCP("didup-readonly")

_client: DiDUPClient | None = None
_lock = asyncio.Lock()


async def _get_client() -> DiDUPClient:
    """Crea il client al primo utilizzo e lo riusa (con login pigro)."""
    global _client
    async with _lock:
        if _client is None:
            try:
                scuola = os.environ["DIDUP_SCUOLA"]
                user = os.environ["DIDUP_USER"]
                pwd = os.environ["DIDUP_PASS"]
            except KeyError as e:
                raise RuntimeError(f"Variabile d'ambiente mancante: {e.args[0]}")
            # auto_versione: aggiorna l'header argo-client-version dallo store
            _client = DiDUPClient(scuola, user, pwd, auto_versione=True)
        return _client


def _plain(obj: Any) -> Any:
    """Converte modelli Pydantic (anche annidati) in dati JSON semplici."""
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json")
    if isinstance(obj, (list, tuple)):
        return [_plain(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _plain(v) for k, v in obj.items()}
    return obj


async def _call(fn_name: str, *args: Any) -> Any:
    """Esegue una sola chiamata di lettura e gestisce gli errori in modo leggibile."""
    client = await _get_client()
    try:
        obj: Any = client
        for part in fn_name.split("."):
            obj = getattr(obj, part)
        return _plain(await obj(*args))
    except DiDUPError as e:
        return {"errore": f"{type(e).__name__}: {e}"}


@mcp.tool()
async def media_generale() -> Any:
    """Media generale dei voti."""
    return await _call("get_media_generale")


@mcp.tool()
async def voti() -> Any:
    """Tutti i voti dell'anno."""
    return await _call("get_voti")


@mcp.tool()
async def voti_per_materia(pk_materia: str) -> Any:
    """Voti di una materia. Usa prima `materie` per ottenere pk_materia."""
    return await _call("voti.per_materia", pk_materia)


@mcp.tool()
async def media_per_materia(pk_materia: str) -> Any:
    """Media dei voti di una singola materia."""
    return await _call("voti.media_per_materia", pk_materia)


@mcp.tool()
async def materie() -> Any:
    """Elenco materie con i loro identificativi."""
    return await _call("get_materie")


@mcp.tool()
async def periodi() -> Any:
    """Periodi scolastici (trimestri/quadrimestri)."""
    return await _call("get_periodi")


@mcp.tool()
async def docenti() -> Any:
    """Elenco docenti."""
    return await _call("get_docenti")


@mcp.tool()
async def assenze() -> Any:
    """Assenze, ritardi e uscite."""
    return await _call("get_assenze")


@mcp.tool()
async def assenze_da_giustificare() -> Any:
    """Eventi ancora da giustificare (sola lettura: non giustifica nulla)."""
    return await _call("assenze.da_giustificare")


@mcp.tool()
async def compiti() -> Any:
    """Compiti assegnati."""
    return await _call("registro.compiti")


@mcp.tool()
async def registro_del_giorno(data: str) -> Any:
    """Lezioni e argomenti di un giorno. Formato data: YYYY-MM-DD."""
    return await _call("registro.del_giorno", data)


@mcp.tool()
async def riepilogo_giornata(data: str) -> Any:
    """Cosa è successo in un giorno (YYYY-MM-DD): lezioni e argomenti con compiti
    assegnati, voti presi, assenze/ritardi/uscite e promemoria dei docenti."""
    client = await _get_client()
    try:
        registro, voti_, assenze_, promemoria_ = await asyncio.gather(
            client.registro.del_giorno(data),
            client.get_voti(),
            client.get_assenze(),
            client.get_promemoria(),
        )
    except DiDUPError as e:
        return {"errore": f"{type(e).__name__}: {e}"}

    def _on_day(item: Any, *fields: str) -> bool:
        return any(str(getattr(item, f, "") or "").startswith(data) for f in fields)

    return {
        "data": data,
        "lezioni": _plain(registro),
        "voti": _plain([v for v in voti_ if _on_day(v, "dat_giorno")]),
        "assenze": _plain([a for a in assenze_ if _on_day(a, "data", "dat_evento")]),
        "promemoria": _plain([p for p in promemoria_ if _on_day(p, "dat_giorno")]),
    }


@mcp.tool()
async def promemoria() -> Any:
    """Promemoria inseriti dai docenti."""
    return await _call("get_promemoria")


@mcp.tool()
async def bacheca() -> Any:
    """Comunicazioni in bacheca."""
    return await _call("get_bacheca")


@mcp.tool()
async def bacheca_da_leggere() -> Any:
    """Comunicazioni in bacheca non ancora lette (non le segna come lette)."""
    return await _call("bacheca.da_leggere")


@mcp.tool()
async def note_disciplinari() -> Any:
    """Note disciplinari."""
    return await _call("get_note_disciplinari")


@mcp.tool()
async def prenotazioni() -> Any:
    """Prenotazioni dei ricevimenti (solo elenco)."""
    return await _call("get_prenotazioni")


@mcp.tool()
async def attivita_fuori_classe() -> Any:
    """Attività fuori classe."""
    return await _call("get_fuori_classe")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--http", action="store_true", help="usa streamable HTTP invece di stdio")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()
    if args.http:
        if MCP_V2:
            mcp.run("streamable-http", host=args.host, port=args.port)
        else:
            mcp.settings.host = args.host
            mcp.settings.port = args.port
            mcp.run(transport="streamable-http")
    else:
        mcp.run()
