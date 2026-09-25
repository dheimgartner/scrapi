import uuid

from scrapi.llm.base import BaseLLM
from scrapi.scraping.base import BaseScraper
from scrapi.inference.search import SearchInference
from scrapi.inference.summary import SummaryInference
from scrapi.models.inference_result import SearchInferenceResult, SummaryInferenceResult
from scrapi.models.search_result import BaseSearchResult
from scrapi.models.report import Report, ResultPair


class Orchestrator:
    """Coordinates scraping and LLM analysis."""

    def __init__(
            self,
            system_prompt: str,
            task_prompt: str,
            summary_prompt: str,
            query: str,
            n: int,
            llm: BaseLLM,
            scraper: BaseScraper,
    ) -> None:
        """Initializes the Orchestrator with the given configuration.

        Args:
            system_prompt: System prompt used to initialize the LLM history.
            task_prompt: Task description passed to the LLM for per-result analysis.
            summary_prompt: Prompt used to generate a final summary after
                processing all results.
            query: Search query used to fetch results via the scraper.
            n: Number of search results to fetch.
            llm: LLM inference instance used for analysis and summarisation.
            scraper: Scraper instance used to fetch search results.
        """
        self.system_prompt = system_prompt
        self.task_prompt = task_prompt
        self.summary_prompt = summary_prompt
        self.query = query
        self.n = n
        self.llm = llm
        self.scraper = scraper
        self.search_inference = SearchInference(
            llm=llm.llm,
            system_prompt=system_prompt,
            task_prompt=task_prompt,
        )
        self.summary_inference = SummaryInference(
            llm=llm.llm,
            system_prompt=system_prompt,
            task_prompt=summary_prompt,
        )

        self.search_results: list[BaseSearchResult] = []
        self.search_inference_results: list[SearchInferenceResult] = []
        self.summary_inference_result: SummaryInferenceResult | None = None

        self._pipeline_id = uuid.uuid4().hex

    def run(self) -> Report:
        """Fetches search results, analyses each, and aggregates to a final summary.

        Fetches `self.n` search results for `self.query` via the scraper, runs
        per-result inference on each, then runs summary-level inference over all
        results.

        Returns:
            A `Report` pairing each search result with its inference result
            and containing the final summary.
        """
        search_results = self.scraper.fetch_content(query=self.query, n=self.n)

        for sr in search_results:
            sr.pipeline_id = self._pipeline_id
            self.search_results.append(sr)
            inference_result = self.search_inference.analyse(sr)
            inference_result.pipeline_id = self._pipeline_id
            self.search_inference_results.append(inference_result)

        summary_inference_result = self.summary_inference.analyse(self.search_inference_results)
        summary_inference_result.pipeline_id = self._pipeline_id
        self.summary_inference_result = summary_inference_result

        pairs = [
            ResultPair(search=sr, inference=ir)
            for sr, ir in zip(self.search_results, self.search_inference_results)
        ]
        return Report(results=pairs, summary=self.summary_inference_result)

    @property
    def result(self) -> str | None:
        """The final summary text, or None if `run()` hasn't been called yet."""
        if self.summary_inference_result is None:
            return None
        return self.summary_inference_result.result
