from pathlib import Path


def save_result_to_md(result: str, md_path: str | Path) -> None:
    """Saves the inference result to a markdown file."""
    path = Path(md_path)
    path.write_text(result, encoding="utf-8")
