from typing import Optional

from aiochclient import ChClient
from aiohttp import ClientSession

from app.config import settings

_session: Optional[ClientSession] = None
_client: Optional[ChClient] = None


async def get_clickhouse_client() -> ChClient:
    global _session, _client

    if _client is None:
        _session = ClientSession()
        _client = ChClient(
            _session,
            url=f"http://{settings.CLICKHOUSE_HOST}:{settings.CLICKHOUSE_PORT}",
        )
    return _client


async def close_clickhouse_client() -> None:
    global _session, _client
    if _client is not None:
        await _client.close()
        _client = None
    if _session is not None:
        await _session.close()
        _session = None