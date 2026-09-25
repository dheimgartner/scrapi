from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True)
class SearchStatus(ABC):
    status: int
    message: str | None = None

@dataclass(frozen=True)
class SuccessfulSearch(SearchStatus): ...

@dataclass(frozen=True)
class FailedSearch(SearchStatus):
    error: Exception | None = None
