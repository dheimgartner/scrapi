from pydantic import BaseModel, Field


class SearchSchema(BaseModel):
    summary: str = Field(description="Short summary of the search result.")
    result: str = Field(
        description="Result/answer based on the search result in light of the prompt instruction."
    )


class SummarySchema(BaseModel):
    summary: str = Field(description="Short summary of the context window.")
    paragraphs: str = Field(
        description="Key context window paragraphs to resolve the question(s) raised."
    )
    result: str = Field(
        description="Summary formatted as markdown across all sources in light of the prompt instruction."
    )
