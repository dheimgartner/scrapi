from abc import ABC, abstractmethod

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


class BaseLLM(ABC):
    """Base class for conversational (stateful) LLM interactions.

    A new LLM endpoint inherits from this class; its single responsibility
    is to initialize the llm field via `create_llm`.

    Attributes:
        llm: Chat model instance created by `_create_llm()`, used to
            generate responses.
        history: Running list of messages exchanged so far, in order.
            Grows with each call to `prompt()`.
    """

    def __init__(self) -> None:
        self.llm = self._create_llm()
        self.history: list[BaseMessage] = []

    @abstractmethod
    def _create_llm(self) -> BaseChatModel:
        pass

    def prompt(self, message: BaseMessage | str) -> AIMessage:
        """Send a message to the LLM and append the exchange to history.

        Args:
            message: The message to send. If a plain string is given,
                it is wrapped in a `HumanMessage`.

        Returns:
            The LLM's response as an `AIMessage`.
        """
        if isinstance(message, str):
            message = HumanMessage(message)
        self.history.append(message)
        result = self.llm.invoke(self.history)
        self.history.append(result)
        return result
