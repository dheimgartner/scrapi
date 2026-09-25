from pydantic import BaseModel, Field


class SearchSchema(BaseModel):
    summary: str = Field(description="Short summary of the search result.")
    result: str = Field(
        description="Result/answer based on the search result in light of the prompt instruction."
    )