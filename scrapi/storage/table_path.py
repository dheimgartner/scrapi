from dataclasses import dataclass


@dataclass
class TablePath:
    server: str
    database: str
    schema: str
    table: str
