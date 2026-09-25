import uuid

from conflict_checker.ai.llm.base_llm import BaseLLM
from conflict_checker.scraping.base_scraper import BaseScraper
from conflict_checker.ai.inference.search_inference import SearchInference
from conflict_checker.ai.inference.summary_inference import SummaryInference
from conflict_checker.interface.inference_result.search_inference_result import SearchInferenceResult
from conflict_checker.interface.inference_result.summary_inference_result import SummaryInferenceResult
from conflict_checker.interface.search_result.base_search_result import BaseSearchResult
from conflict_checker.storage.database_storer import DatabaseStorer
from conflict_checker.renderer.report import Report, ResultPair


class Orchestrator:
    """Coordinates conflict checking and storage.

    Initialization of injected objects (llm, scraper) is not the
    responsibility of this class.
    """
    def __init__(
            self,
            system_prompt: str,
            task_prompt: str,
            summary_prompt: str,
            query: str,
            n: int,
            llm: BaseLLM,
            scraper: BaseScraper,
            save=True,
    ) -> None:
        """Initializes the Orchestrator with the given configuration.

        Args:
            system_prompt: System prompt used to initialize the LLM history.
            task_prompt: Task description passed to the LLM during conflict checking.
            summary_prompt: Prompt used to generate a final summary after
                processing all articles.
            query: Search query used to fetch search results via the scraper.
            n: Number of search results to fetch.
            llm: LLM inference instance used for conflict checking and prompting.
            scraper: Scraper instance used to fetch search results.
            save: Whether to persist search and inference results to the
                database. Defaults to True.
        """
        self.system_prompt = system_prompt
        self.task_prompt = task_prompt
        self.summary_prompt = summary_prompt
        self.query = query
        self.n = n
        self.save = save
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

    def conflict_check(self) -> Report:
        """Fetches search results, analyses each, and aggregates to a final summary.

        Fetches `self.n` search results for `self.query` via the scraper, runs
        search-result-level inference on each, then runs summary-level
        inference over all search inference results. If `self.save` is set,
        persists the articles and results to the database.

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

        if self.save:
            self._save_to_database()

        pairs = [
            ResultPair(search=sr, inference=ir)
            for sr, ir in zip(self.search_results, self.search_inference_results)
        ]
        return Report(results=pairs, summary=self.summary_inference_result)

    @property
    def result(self) -> str | None:
        """The final summary text, or None if `conflict_check()` hasn't run yet."""
        if self.summary_inference_result is None:
            return None
        return self.summary_inference_result.result

    def _save_to_database(self) -> None:
        storer = DatabaseStorer()
        storer.write(self.search_results)
        storer.write(self.search_inference_results)
        storer.write([self.summary_inference_result])

