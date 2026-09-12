from dataclasses import dataclass
from typing import Any

from app.core.config import Settings


URL_TABLE_NAME = "urls_by_id"


class CassandraUrlStoreError(RuntimeError):
    pass


@dataclass(frozen=True)
class CassandraResources:
    cluster: Any
    session: Any

    def close(self) -> None:
        self.session.shutdown()
        self.cluster.shutdown()


class CassandraUrlStore:
    def __init__(
        self,
        session: Any,
        table_name: str = URL_TABLE_NAME,
    ) -> None:
        self._session = session
        self._table_name = table_name

    @property
    def table_name(self) -> str:
        return self._table_name

    def initialize_schema(self) -> None:
        query = f"""
        CREATE TABLE IF NOT EXISTS {self._table_name} (
            id bigint PRIMARY KEY,
            original_url text
        )
        """
        self._execute(query)

    def store_url(self, url_id: int, original_url: str) -> None:
        self._execute(
            f"""
            INSERT INTO {self._table_name} (id, original_url)
            VALUES (%s, %s)
            """,
            (url_id, original_url),
        )

    def get_url(self, url_id: int) -> str | None:
        result = self._execute(
            f"""
            SELECT original_url
            FROM {self._table_name}
            WHERE id = %s
            LIMIT 1
            """,
            (url_id,),
        )
        row = result.one()

        if row is None:
            return None

        return str(row.original_url)

    def _execute(
        self,
        query: str,
        parameters: tuple[Any, ...] | None = None,
    ) -> Any:
        try:
            if parameters is None:
                return self._session.execute(query)
            return self._session.execute(query, parameters)
        except _driver_exceptions() as exc:
            raise CassandraUrlStoreError(
                "Cassandra URL persistence failed."
            ) from exc


def create_cassandra_resources(settings: Settings) -> CassandraResources:
    from cassandra.auth import PlainTextAuthProvider
    from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
    from cassandra.policies import DCAwareRoundRobinPolicy

    auth_provider = None
    if settings.cassandra_auth_configured:
        auth_provider = PlainTextAuthProvider(
            username=settings.cassandra_username,
            password=settings.cassandra_password,
        )

    profile = ExecutionProfile(
        load_balancing_policy=DCAwareRoundRobinPolicy(
            local_dc=settings.cassandra_datacenter,
        ),
    )
    cluster = Cluster(
        contact_points=list(settings.cassandra_contact_points),
        port=settings.cassandra_port,
        auth_provider=auth_provider,
        execution_profiles={EXEC_PROFILE_DEFAULT: profile},
    )

    try:
        session = cluster.connect(settings.cassandra_keyspace)
    except _driver_exceptions():
        cluster.shutdown()
        raise

    return CassandraResources(cluster=cluster, session=session)


def _driver_exceptions() -> tuple[type[Exception], ...]:
    try:
        from cassandra import DriverException, OperationTimedOut
        from cassandra.cluster import NoHostAvailable
    except ImportError:
        return ()

    return (DriverException, NoHostAvailable, OperationTimedOut)
