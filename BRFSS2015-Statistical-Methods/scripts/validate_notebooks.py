"""Validate and actually execute every notebook in a new kernel on synthetic fixtures."""

import argparse
import os
from pathlib import Path
import tempfile
import nbformat
from nbclient import NotebookClient
from src.utils.io import write_json


def validate(execute=False, output="reports/notebook_execution", repeat=2):
    root = Path.cwd()
    results = []
    for path in sorted(Path("notebooks").glob("*.ipynb")):
        nb = nbformat.read(path, as_version=4)
        nbformat.validate(nb)
        if execute:
            with tempfile.TemporaryDirectory(prefix="brfss-notebook-") as temp:
                env = os.environ.copy()
                env.update(
                    BRFSS_REPO=str(root),
                    BRFSS_SYNTHETIC="1",
                    BRFSS_OUT=temp,
                    MPLCONFIGDIR=str(Path(temp) / "mpl"),
                    JUPYTER_PLATFORM_DIRS="1",
                    BRFSS_PROTOCOL="NEW_PROTOCOL",
                    BRFSS_FINAL_EVALUATION="1" if path.name == "10_Final_Evaluation.ipynb" else "0",
                )
                # Each repetition uses a new kernel with the same output directory.
                # Checkpoints must make rerunning idempotent, including final test access.
                for _ in range(repeat):
                    nb = nbformat.read(path, as_version=4)
                    client = NotebookClient(
                        nb,
                        timeout=900,
                        kernel_name=os.environ.get("BRFSS_NOTEBOOK_KERNEL", "python3"),
                        resources={"metadata": {"path": str(root)}},
                    )
                    client.execute(env=env)
                Path(output).mkdir(parents=True, exist_ok=True)
                nbformat.write(nb, Path(output) / path.name)
        results.append(
            {
                "notebook": str(path),
                "schema": "PASS",
                "execution": "PASS" if execute else "NOT_RUN",
                "fresh_kernel_executions": repeat if execute else 0,
            }
        )
        print(results[-1], flush=True)
    write_json(Path(output) / "results.json", results)
    return results


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--execute", action="store_true")
    p.add_argument("--output", default="reports/notebook_execution")
    p.add_argument("--repeat", type=int, default=2)
    validate(**vars(p.parse_args()))
