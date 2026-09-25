"""Chainlit chat interface"""

import chainlit as cl
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain.agents import create_agent

from scrapi.llm.openai import OpenaiLLM
from scrapi.scraping.yahoo import YahooScraper
from scrapi.frontends.tools import make_conflict_check_tool

SYSTEM_PROMPT = """You are a conflict-of-interest research assistant.

Before calling the conflict_check tool, you MUST have explicit, user-provided
values for: query, n, system_prompt, task_prompt, summary_prompt, save.

Do not infer, guess, or default any of these values. If any are missing,
ask the user directly for them — one question at a time if needed — and do
not call the tool until all six have been explicitly stated by the user."""


@cl.on_chat_start
async def on_chat_start() -> None:
    llm = OpenaiLLM()
    scraper = YahooScraper()

    tools = [make_conflict_check_tool(llm, scraper)]
    agent = create_agent(
        llm.llm,
        tools=tools,
        checkpointer=MemorySaver(),
        system_prompt=SYSTEM_PROMPT,
    )
    cl.user_session.set("agent", agent)


@cl.on_message
async def on_message(message: cl.Message) -> None:
    agent = cl.user_session.get("agent")
    config = {"configurable": {"thread_id": cl.context.session.id}}

    response = agent.invoke(
        {"messages": [HumanMessage(message.content)]},
        config=config,
    )

    content = response["messages"][-1].content
    await cl.Message(content=content).send()
