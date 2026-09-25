import contextlib
from pathlib import Path

import click

from conflict_checker.api.frontends import cli as frontend_cli
from conflict_checker.api.frontends import gui as frontend_gui
from conflict_checker.exceptions import ConflictCheckerError


@click.group()
def main() -> None:
    """Conflict checker"""


@main.command()
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to a YAML config file.",
)
@click.option(
    "--output",
    "output_path",
    type=click.Path(path_type=Path),
    required=True,
    help="Path to write the markdown results to.",
)
def cli(config_path: Path, output_path: Path) -> None:
    """CLI-tool: command line interface"""
    with _frontend_runner():
        frontend_cli.cli(config_path, output_path)


@main.command()
def gui() -> None:
    """GUI-tool: chat interface"""
    with _frontend_runner():
        frontend_gui.gui()


@contextlib.contextmanager
def _frontend_runner():
    """Handles frontends exceptions"""
    try:
        yield
    except ConflictCheckerError as e:
        raise click.ClickException(str(e)) from e
    except Exception as e:
        raise click.ClickException(str(e)) from e
