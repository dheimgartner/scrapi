# LLM Providers

All LLM providers inherit from `BaseLLM` and expose a `.llm` attribute (a LangChain `BaseChatModel`) used by the inference classes.

## BaseLLM

::: scrapi.llm.base.BaseLLM

## AnthropicLLM

::: scrapi.llm.anthropic.AnthropicLLM

## OpenaiLLM

Azure OpenAI backend.

::: scrapi.llm.openai.OpenaiLLM

## OllamaLLM

::: scrapi.llm.ollama.OllamaLLM
