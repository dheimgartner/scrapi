import uuid

from scrapi.scraping.base import BaseScraper
from scrapi.inference.search import SearchInference
from scrapi.inference.summary import SummaryInference
from scrapi.models.inference_result import SearchInferenceResult, SummaryInferenceResult
from scrapi.models.search_result import BaseSearchResult
from scrapi.models.report import PipelineResult, ResultPair


class Orchestrator:
    """Coordinates scraping and LLM analysis."""

    def __init__(
        self,
        scrapers: list[tuple[BaseScraper, dict]],
        search_inference: SearchInference,
        summary_inference: SummaryInference,
    ) -> None:
        """Initializes the Orchestrator with pre-built dependencies.

        Args:
            scrapers: List of (scraper, fetch_kwargs) pairs. Each scraper's
                ``fetch_content`` is called with its associated kwargs.
            search_inference: Inference object for per-result analysis.
            summary_inference: Inference object for final summarisation.
        """
        self.scrapers = scrapers
        self.search_inference = search_inference
        self.summary_inference = summary_inference

        self.search_results: list[BaseSearchResult] = []
        self.search_inference_results: list[SearchInferenceResult] = []
        self.summary_inference_result: SummaryInferenceResult | None = None

        self._pipeline_id = uuid.uuid4().hex

    def run(self) -> PipelineResult:
        """Fetches search results, analyses each, and aggregates to a final summary.

        Iterates over all scrapers, fetches results via each scraper's fetch kwargs,
        runs per-result inference on each, then runs summary-level inference over all
        collected results.

        Returns:
            A ``PipelineResult`` pairing each search result with its inference result
            and containing the final summary.
        """
        for scraper, fetch_kwargs in self.scrapers:
            search_results = scraper.fetch_content(**fetch_kwargs)
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
        return PipelineResult(results=pairs, summary=self.summary_inference_result)

    @property
    def result(self) -> str | None:
        """The final summary text, or None if ``run()`` hasn't been called yet."""
        if self.summary_inference_result is None:
            return None
        return self.summary_inference_result.result
