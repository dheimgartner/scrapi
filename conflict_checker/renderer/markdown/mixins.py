class MarkdownRenderable:
    def render_as_markdown(self) -> str:
        raise NotImplementedError


class SearchResultMarkdownMixin(MarkdownRenderable):
    def render_as_markdown(self) -> str:
        return self.ai_content


class WebSearchResultMarkdownMixin(SearchResultMarkdownMixin):
    def render_as_markdown(self) -> str:
        url = self.source.get("url", "")
        return f"**Source:** {url}\n\n{self.ai_content}"


class InferenceResultMarkdownMixin(MarkdownRenderable):
    def render_as_markdown(self) -> str:
        return self.result


class SearchInferenceResultMarkdownMixin(InferenceResultMarkdownMixin):
    def render_as_markdown(self) -> str:
        return f"**Summary:** {self.structured_output.summary}\n\n**Result:** {self.structured_output.result}"


class SummaryInferenceResultMarkdownMixin(InferenceResultMarkdownMixin):
    def render_as_markdown(self) -> str:
        return (
            f"{self.structured_output.result}\n\n"
            f"**Key passages:**\n\n{self.structured_output.paragraphs}"
        )
