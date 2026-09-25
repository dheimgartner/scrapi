from pydantic import BaseModel, Field


class SummarySchema(BaseModel):
    summary: str = Field(description="Short summary of the context window.")
    paragraphs: str = Field(
        description="Key context window paragraphs to resolve the question(s) raised."
    )
    result: str = Field(
        description="Summary formatted as markdown across all sources in light of the prompt instruction."
    )