from abc import ABC, abstractmethod

import scrapi.storage.table_path as tp


class DatabaseStorable(ABC):

    @abstractmethod
    def get_table_path(self) -> tp.TablePath:
        """Return the database location where this object should be stored.

        The returned TablePath specifies the fully qualified location of the target
        table, including server, database, schema, and table name. This information
        is used by storage components to determine where the serialized row should
        be inserted.

        """

    @abstractmethod
    def to_db_dict(self) -> dict:
        """Return a dictionary representation of the object for database insertion.

        The returned dictionary maps database column names to values that can be
        stored directly in the database. All values must be of types supported by
        the target database (e.g., strings, numbers, booleans, dates). Complex
        Python objects such as dictionaries or custom classes must be serialized
        before inclusion.

        """
