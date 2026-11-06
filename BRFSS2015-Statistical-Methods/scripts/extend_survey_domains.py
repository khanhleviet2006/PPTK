"""Full-population survey domain descriptions, separate from prediction and model selection."""

import argparse
from pathlib import Path
import pandas as pd
import pyreadstat
from src.features.engineering import specifications, transform_raw
from src.data.outcomes import eligible
from src.statistics.survey import Design
from src.utils.io import write_csv, write_json, digest


def run(data, out="reports/tables/gap_extension/survey_domains.csv"):
    specs = specifications()
    raw, _ = pyreadstat.read_xport(
        data, usecols=list(specs) + ["_STATE", "DIABETE3", "_LLCPWT", "_STSTR", "_PSU"]
    )
    design = Design(raw)
    keep, y = eligible(raw)
    X = transform_raw(raw, specs)
    rows = []
    groups = {c: X[c] for c in ["SEX", "_AGEG5YR", "_RACE", "EDUCA", "INCOME2"]}
    groups["BMI"] = pd.cut(X["_BMI5"], [0, 18.5, 25, 30, 100], right=False)
    for name, values in groups.items():
        for level in values.dropna().unique():
            domain = keep & values.eq(level)
            if domain.sum() < 50:
                continue
            r = design.mean((y == 1).astype(float), domain, proportion=True)
            rows.append({"variable": name, "level": str(level), **r})
    write_csv(out, pd.DataFrame(rows))
    write_json(
        Path(out).with_suffix(".json"),
        {
            "source_sha256": digest(data),
            "analysis": "Full2015 eligible-domain descriptive inference, including legacy-test respondents; independent of predictive selection/evaluation",
            "outcome": "DIABETE3=1 vs3",
            "design": "_LLCPWT/_STSTR/nested_PSU Taylor with zero scores outside domain",
            "minimum_n": 50,
            "rows": len(rows),
        },
    )
    print("Survey domain estimates:", len(rows))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True)
    p.add_argument("--out", default="reports/tables/gap_extension/survey_domains.csv")
    run(**vars(p.parse_args()))
