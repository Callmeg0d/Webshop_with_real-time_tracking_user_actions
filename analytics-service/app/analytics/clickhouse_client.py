from typing import Optional

from aiochclient import ChClient
from aiohttp import ClientSession
from shared import get_logger

from app.config import settings

logger = get_logger(__name__)

_session: Optional[ClientSession] = None
_client: Optional[ChClient] = None


async def get_clickhouse_client() -> ChClient:
    global _session, _client

    if _client is None:
        logger.debug("Creating new ClickHouse client")
        _session = ClientSession()
        _client = ChClient(
            _session,
            url=f"http://{settings.CLICKHOUSE_HOST}:{settings.CLICKHOUSE_INTERNAL_PORT}",
        )
        logger.debug(f"ClickHouse client created, url: http://{settings.CLICKHOUSE_HOST}:{settings.CLICKHOUSE_INTERNAL_PORT}")
    return _client


async def close_clickhouse_client() -> None:
    global _session, _client
    logger.debug("Closing ClickHouse client")
    if _client is not None:
        await _client.close()
        _client = None
        logger.debug("ClickHouse client closed")
    if _session is not None:
        await _session.close()
        _session = None
        logger.debug("ClickHouse session closed")

