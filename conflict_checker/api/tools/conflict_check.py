from langchain_core.tools import tool

from conflict_checker.ai.llm.base_llm import BaseLLM
from conflict_checker.scraping.base_scraper import BaseScraper
from conflict_checker.orchestrator.orchestrator import Orchestrator


def make_conflict_check_tool(llm: BaseLLM, scraper: BaseScraper):
    """Return a LangChain tool that runs a full conflict-of-interest check.

    llm and scraper are infrastructure dependencies captured at agent setup
    time. All analysis parameters are collected from the user at call time,
    so the LLM should ask clarifying questions before invoking the tool.

    Args:
        llm: LLM used by the orchestrator to perform article/summary
            inference.
        scraper: Scraper used by the orchestrator to fetch source
            articles.

    Returns:
        A LangChain `@tool`-decorated `conflict_check` function, ready
        to be included in an agent's tool list.
    """

    @tool
    def conflict_check(
        query: str,
        n: int,
        system_prompt: str,
        task_prompt: str,
        summary_prompt: str,
        save: bool,
    ) -> str:
        """Run a conflict-of-interest analysis against web sources.

        Collect ALL of the following from the user before calling:
        - query: search query used to find relevant articles
        - n: number of articles to fetch and analyse
        - system_prompt: role/context instructions for the LLM analyser
        - task_prompt: per-article analysis instructions
        - summary_prompt: instructions for aggregating results into a summary
        - save: whether to persist results to the database

        NEVER infer any of the parameters - the user has to explicitly specify!
        """
        orchestrator = Orchestrator(
            system_prompt=system_prompt,
            task_prompt=task_prompt,
            summary_prompt=summary_prompt,
            query=query,
            n=n,
            llm=llm,
            scraper=scraper,
            save=save,
        )
        report = orchestrator.conflict_check()
        return report.summary.result

    return conflict_check
