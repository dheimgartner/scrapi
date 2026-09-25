from abc import abstractmethod


class MarkdownRenderable:
    @abstractmethod
    def render_as_markdown(self) -> str: ...
