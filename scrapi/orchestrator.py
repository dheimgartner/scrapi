import uuid
from typing import TYPE_CHECKING

from scrapi.scraping.base import BaseScraper
from scrapi.inference.search import SearchInference
from scrapi.inference.summary import SummaryInference
from scrapi.models.inference_result import SearchInferenceResult
from scrapi.models.run_result import RunResult, ResultPair

if TYPE_CHECKING:
    from scrapi.renderer.base import BaseRenderer


class Orchestrator:
    """Coordinates scraping and LLM analysis."""

    def __init__(
        self,
        scrapers: list[tuple[BaseScraper, dict]],
        search_inference: SearchInference,
        summary_inference: SummaryInference,
        renderer: "BaseRenderer | None" = None,
    ) -> None:
        """Initializes the Orchestrator with pre-built dependencies.

        Args:
            scrapers: List of (scraper, scrape_kwargs) pairs. Each scraper's
                ``scrape`` is called with its associated kwargs.
            search_inference: Inference object for per-result analysis.
            summary_inference: Inference object for final summarisation.
            renderer: Optional renderer. If provided, ``run()`` renders the
                result and saves it to ``renderer.output_path`` when set.
        """
        self.scrapers = scrapers
        self.search_inference = search_inference
        self.summary_inference = summary_inference
        self.renderer = renderer

        self.run_result: RunResult | None = None
        self._pipeline_id = uuid.uuid4().hex

    def run(self) -> RunResult:
        """Fetches search results, analyses each, and aggregates to a final summary.

        Iterates over all scrapers, fetches results via each scraper's fetch kwargs,
        runs per-result inference on each, then runs summary-level inference over all
        collected results.

        Returns:
            A ``RunResult`` pairing each search result with its inference result
            and containing the final summary.
        """
        pairs: list[ResultPair] = []
        search_inference_results: list[SearchInferenceResult] = []

        for scraper, scrape_kwargs in self.scrapers:
            for sr in scraper.scrape(**scrape_kwargs):
                sr.pipeline_id = self._pipeline_id
                ir = self.search_inference.run(sr)
                ir.pipeline_id = self._pipeline_id
                pairs.append(ResultPair(search=sr, inference=ir))
                search_inference_results.append(ir)

        summary = self.summary_inference.run(search_inference_results)
        summary.pipeline_id = self._pipeline_id

        self.run_result = RunResult(results=pairs, summary=summary)

        if self.renderer is not None:
            self.renderer.render(self.run_result)
            if self.renderer.output_path is not None:
                self.renderer.save()
            if self.renderer.result_md_path is not None:
                self.renderer.save_result_md(self.run_result)

        return self.run_result

    @property
    def result(self) -> str | None:
        """The final summary text, or None if ``run()`` hasn't been called yet."""
        if self.run_result is None:
            return None
        return self.run_result.summary.result
