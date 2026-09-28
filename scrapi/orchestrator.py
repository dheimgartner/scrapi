import uuid

from scrapi.scraping.base import BaseScraper
from scrapi.inference.search import SearchInference
from scrapi.inference.summary import SummaryInference
from scrapi.models.inference_result import SearchInferenceResult
from scrapi.models.pipeline_result import PipelineResult, ResultPair


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

        self.pipeline_result: PipelineResult | None = None
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
        pairs: list[ResultPair] = []
        search_inference_results: list[SearchInferenceResult] = []

        for scraper, fetch_kwargs in self.scrapers:
            for sr in scraper.fetch_content(**fetch_kwargs):
                sr.pipeline_id = self._pipeline_id
                ir = self.search_inference.analyse(sr)
                ir.pipeline_id = self._pipeline_id
                pairs.append(ResultPair(search=sr, inference=ir))
                search_inference_results.append(ir)

        summary = self.summary_inference.analyse(search_inference_results)
        summary.pipeline_id = self._pipeline_id

        self.pipeline_result = PipelineResult(results=pairs, summary=summary)
        return self.pipeline_result

    @property
    def result(self) -> str | None:
        """The final summary text, or None if ``run()`` hasn't been called yet."""
        if self.pipeline_result is None:
            return None
        return self.pipeline_result.summary.result
