from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.config import get_settings
from app.infrastructure.cassandra_url_store import (
    CassandraUrlStore,
    create_cassandra_resources,
)
from app.infrastructure.redis_id_generator import (
    RedisIdGenerator,
    create_redis_client,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    redis_client = create_redis_client(settings)
    cassandra_resources = None

    try:
        cassandra_resources = create_cassandra_resources(settings)
        url_store = CassandraUrlStore(cassandra_resources.session)
        url_store.initialize_schema()

        app.state.redis_client = redis_client
        app.state.id_generator = RedisIdGenerator(
            client=redis_client,
            start=settings.url_id_start,
        )
        app.state.cassandra_resources = cassandra_resources
        app.state.url_store = url_store

        yield
    finally:
        if cassandra_resources is not None:
            cassandra_resources.close()
        redis_client.close()


app = FastAPI(
    title="url-shortener",
    version="0.1.0",
    description="URL shortening service backed by Redis and Cassandra.",
    lifespan=lifespan,
)

app.include_router(router)
