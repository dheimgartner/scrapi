from pathlib import Path

import conflict_checker.api as api


def cli(config_path: Path, output_path: Path):
    """CLI-tool"""
    with api.PROXY_SESSION as session:
        config = api.load_yaml_config(config_path)
        orchestrator = api.make_conflict_checker(config)
        result = orchestrator.conflict_check()
    api.save_result_to_md(result=result.result, md_path=output_path)
