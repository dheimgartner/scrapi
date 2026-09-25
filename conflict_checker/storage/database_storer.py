import logging
import os
from typing import List

import sqlalchemy as sql
from sqlalchemy.engine.base import Engine

import conflict_checker.storage.database_storable as ds


class DatabaseStorer:
    """Store DatabaseStorable objects into a SQL table.

    This class manages writing a batch of objects implementing the
    `DatabaseStorable` interface into a single database table. The table
    location (server, database, schema, table name) and database engine are
    dynamically populated via `_load_table_path()` based on the metadata
    returned by the objects being written.

    Attributes:
        _server: The database server hostname.
        _database: The database name.
        _schema: The schema containing the target table.
        _table: The target table name.
        _engine: A SQLAlchemy Engine instance used for executing inserts.

    Notes:
        - The class expects all `DatabaseStorable` instances in a batch to
          refer to the same table path. This is validated in `_load_table_path()`.
        - The engine is lazily created when the write method is called

    """

    def __init__(self):
        self._server = None
        self._database = None
        self._schema = None
        self._table = None
        self._engine = None

    def write(self, db_serializables: List[ds.DatabaseStorable]) -> None:
        """Insert a batch of DatabaseStorable objects into the target table.

        This method writes all provided `DatabaseStorable` instances into the
        database table defined by the table path previously loaded via
        `_load_table_path()`. Each object is converted into a dictionary of
        column-value pairs using `to_db_dict()` and inserted.

        Args:
            db_serializables: A list of objects implementing the
                `DatabaseStorable` interface. Each must provide a valid database
                path and a serializable dictionary of column values.

        """
        self._load_table_path(db_serializables)
        metadata = sql.MetaData()
        table = sql.Table(
            self._table,
            metadata,
            autoload_with=self._engine,
            schema=self._schema,
        )

        with self._engine.begin() as conn:
            for serializable in db_serializables:
                try:
                    stmt = sql.insert(table).values(**serializable.to_db_dict())
                    conn.execute(stmt)
                except Exception as e:
                    logging.warning(
                        f"Failed to insert article {serializable.to_db_dict()}: "
                        f"{type(e).__name__} - {e}"
                    )

    def _load_table_path(self, db_serializables: List[ds.DatabaseStorable]) -> None:
        """Load and validate a common table path from a list of DatabaseStorable objects."""
        paths = [obj.get_table_path() for obj in db_serializables]
        all_paths_same = all(path == paths[0] for path in paths)

        if not all_paths_same:
            raise ValueError(
                "All DatabaseStorable instances must have an identical TablePath."
            )

        self._server = paths[0].server
        self._database = paths[0].database
        self._schema = paths[0].schema
        self._table = paths[0].table
        self._engine = self._create_sql_engine(paths[0].server, paths[0].database)

    @staticmethod
    def _create_sql_engine(server: str, database: str) -> Engine:
        if "DB_USER" in os.environ and "DB_PASSWORD" in os.environ:
            db_user = os.environ["DB_USER"]
            db_password = os.environ["DB_PASSWORD"]
            connection_string = "mssql+pymssql://{}:{}@{}/{}".format(
                db_user,
                db_password,
                server,
                database,
            )
        else:
            connection_string = (
                "mssql+pyodbc://{}/{}?driver=ODBC+Driver+17+for+SQL+Server".format(
                    server,
                    database,
                )
            )
        return sql.create_engine(connection_string, use_setinputsizes=True)
