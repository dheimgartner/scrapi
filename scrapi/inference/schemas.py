from pydantic import BaseModel, Field


class SearchSchema(BaseModel):
    """Structured output schema for per-result search inference."""

    summary: str = Field(description="Short summary of the search result.")
    result: str = Field(
        description="Result/answer based on the search result in light of the prompt instruction."
    )


class SummarySchema(BaseModel):
    """Structured output schema for cross-source summary inference."""

    summary: str = Field(description="Short summary of the context window.")
    paragraphs: str = Field(
        description="Key context window paragraphs to resolve the question(s) raised."
    )
    result: str = Field(
        description="Summary across all sources in light of the prompt instruction."
    )
