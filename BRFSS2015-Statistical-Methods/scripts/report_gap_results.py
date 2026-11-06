"""Render executed extension results; never runs a model or a final evaluation."""

from pathlib import Path
import json
import shutil
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, precision_recall_curve
from src.utils.io import read_json, write_json, write_csv


def table(df):
    cols = list(df)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    lines += [
        "| " + " | ".join(str(v).replace("|", "/") for v in row) + " |"
        for row in df.itertuples(index=False, name=None)
    ]
    return "\n".join(lines)


def report(run_path="runs/gap_real_quick_v4"):
    root = Path("reports")
    dest = root / "tables/gap_extension"
    dest.mkdir(parents=True, exist_ok=True)
    fig = root / "figures/gap_extension"
    fig.mkdir(parents=True, exist_ok=True)
    run = Path(run_path)
    rows = read_json(run / "registry.json")
    manifest = read_json(run / "manifest.json")
    good = [r for r in rows if r["status"] == "SUCCESS"]
    df = pd.DataFrame(
        [
            {
                "experiment_id": r["experiment_id"],
                **r["config"],
                **{k: v for k, v in r["metrics"].items() if np.isscalar(v)},
                "seconds": r["seconds"],
                "feature_jaccard": r.get("feature_jaccard"),
            }
            for r in good
        ]
    )
    write_csv(dest / "experiment_registry.csv", df)
    write_json(root / "evidence/gap_extension/registry.json", rows)
    write_json(root / "evidence/gap_extension/development_manifest.json", manifest)
    for name in [
        "development_selection.json",
        "integrity.json",
        "calibration_intercept_slope.json",
        "federated_simulation.json",
    ]:
        if (run / name).exists():
            shutil.copy2(run / name, root / "evidence/gap_extension" / name)
    for name in [
        "shap_importance.csv",
        "shap_stability.csv",
        "development_subgroups.csv",
        "optuna_trials.csv",
    ]:
        if (run / name).exists():
            shutil.copy2(run / name, dest / name)
    shutil.copy2(run / "shap_summary.png", fig / "shap_summary.png")
    intro = (
        "These are executed post-audit exploratory development results, not new 2015 final-test results. "
        "CDC2015 binary DIABETE3=1 vs3; 2,000 eligible legacy-development respondents; zero old test-ID overlap. "
        "Two identical outer folds across candidate comparisons; binary thresholds selected in 2-fold inner training OOF. "
        "RandomizedSearch uses inner2 CV; calibration fits complete pipelines inside training. "
        "OOF scores are optimistic after candidate selection; no IID fold t-tests or confirmatory CV p-values. "
        "k is encoded-column/component count. Continuous-only ADASYN/SMOTE results must be compared with continuous-only controls, not full-feature baselines. "
        "Hard voting produces hard-label pseudo-probabilities, unsuitable for interpreting probability calibration.\n\n"
    )
    docs = {
        "FEATURE_SELECTION_COMPARISON.md": (
            "Feature-selection comparison",
            df[df.stage.eq("features")],
        ),
        "ADVANCED_ML_COMPARISON.md": (
            "Advanced-model and nested-search comparison",
            df[df.stage.isin(["screen", "search"])],
        ),
        "ENSEMBLE_COMPARISON.md": ("Ensemble comparison", df[df.stage.eq("ensemble")]),
        "IMBALANCE_EXPERIMENTS.md": ("Imbalance comparison", df[df.stage.eq("imbalance")]),
        "CALIBRATION_ANALYSIS.md": (
            "Calibration and missing-data comparison",
            df[
                df.stage.isin(["calibration", "missing"])
                | ((df.stage == "screen") & (df.model == "logistic"))
            ],
        ),
    }
    for filename, (title, sub) in docs.items():
        display = [
            c
            for c in [
                "model",
                "selector",
                "k",
                "sampling",
                "representation",
                "calibration",
                "missing",
                "search",
                "balanced_accuracy",
                "sensitivity",
                "specificity",
                "roc_auc",
                "pr_auc",
                "brier",
                "log_loss",
                "macro_f1",
            ]
            if c in sub
        ]
        (root / filename).write_text(
            "# "
            + title
            + "\n\n"
            + intro
            + table(sub[display].fillna("").round(5))
            + "\n\nFull settings, fold metrics, inner thresholds and selected-feature lists: runs/gap_real_quick_v4/experiments/*.json. "
            "RFECV/permutation use deterministic codebook encoding and fit imputation/scaling inside internal training folds; outer validation stays excluded. "
            "No claim of full-standard execution, stable feature discovery, a new algorithm or superiority to Chang.\n"
        )
    # Figures only from saved predictions.
    base = next(r for r in good if r["config"] == {"model": "logistic", "stage": "screen"})
    oof = pd.read_csv(run / base["oof_file"])
    y = oof.y.to_numpy()
    p = oof.p1.to_numpy()
    fpr, tpr, _ = roc_curve(y, p)
    plt.plot(fpr, tpr)
    plt.plot([0, 1], [0, 1], "k--")
    plt.xlabel("False-positive rate")
    plt.ylabel("Sensitivity")
    plt.title("2015 development OOF ROC")
    plt.savefig(fig / "roc.png", dpi=180)
    plt.close()
    precision, recall, _ = precision_recall_curve(y, p)
    plt.plot(recall, precision)
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("2015 development OOF precision–recall")
    plt.savefig(fig / "precision_recall.png", dpi=180)
    plt.close()
    from src.evaluation.metrics import calibration, metrics

    cal = pd.DataFrame(calibration(y, oof[["p0", "p1"]].to_numpy()))
    c = cal[cal["class"] == 1]
    plt.plot(c.predicted, c.observed, "o-")
    plt.plot([0, 1], [0, 1], "k--")
    plt.xlabel("Predicted")
    plt.ylabel("Observed")
    plt.title("2015 development OOF calibration")
    plt.savefig(fig / "calibration.png", dpi=180)
    plt.close()
    trade = []
    for t in np.arange(0.05, 0.96, 0.05):
        trade.append(
            {
                "threshold": t,
                **{
                    k: v
                    for k, v in metrics(y, oof[["p0", "p1"]].to_numpy(), t).items()
                    if np.isscalar(v)
                },
            }
        )
    trade = pd.DataFrame(trade)
    write_csv(dest / "threshold_tradeoff.csv", trade)
    for k in ["sensitivity", "specificity", "precision"]:
        plt.plot(trade.threshold, trade[k], label=k)
    plt.legend()
    plt.xlabel("Threshold")
    plt.ylabel("Metric")
    plt.title("Descriptive development tradeoff; not a new test-selected threshold")
    plt.savefig(fig / "threshold_tradeoff.png", dpi=180)
    plt.close()
    top = df.sort_values("balanced_accuracy").tail(18)
    plt.figure(figsize=(8, 8))
    plt.barh(np.arange(len(top)), top.balanced_accuracy)
    plt.yticks(
        np.arange(len(top)),
        [
            str(a) + " " + str(b)
            for a, b in zip(top.model, top.get("selector", pd.Series("all", index=top.index)))
        ],
    )
    plt.xlabel("Outer development BA")
    plt.tight_layout()
    plt.savefig(fig / "model_comparison.png", dpi=180)
    plt.close()
    features = df[df.stage.eq("features")]
    plt.figure(figsize=(8, 5))
    for name, g in features.groupby("selector"):
        plt.plot(g.k, g.balanced_accuracy, "o-", label=name)
    plt.legend(fontsize=7, ncol=3)
    plt.xlabel("Encoded k / PCA components")
    plt.ylabel("Outer development BA")
    plt.tight_layout()
    plt.savefig(fig / "feature_selection.png", dpi=180)
    plt.close()
    processed = read_json("reports/evidence/gap_extension/processed_source_audit.json")
    (root / "CHANG_2022_REPRODUCTION.md").write_text(
        "# Chang 2022 reproduction track\n\nOriginal DOI 10.1016/j.health.2022.100118; audited PDF pages4–6,12–13.\n\n"
        + f"UCI public processed source downloaded and audited: {processed['records']} rows, ID plus21 predictors and Diabetes_binary. Source SHA256 {processed['sha256']}. Metadata itself is inconsistent (35 vs21 features, creation year2017). It is not established as the exact paper input.\n\n"
        + "Exact replication: NOT_POSSIBLE_FROM_AVAILABLE_EVIDENCE. Approximate processed predictive reproduction: NOT_EXECUTED because sequential UCI IDs cannot establish exclusion of the already-accessed 2015 final-test respondents. Repartitioning that potentially overlapping cohort would not create an independent test.\n\n"
        + "The prior approximate reproduction script remains tested synthetically; it is not executed on these real processed rows. No claim of82.26% reproduction. Known Table2 params: RF state42/entropy (tree/depth ambiguity), LR state0, KNN3, DT depth50/entropy. New development experiments on original-source training IDs are a separate track, not a faithful paper baseline.\n"
    )
    temporal = read_json("runs/temporal_2017/external_metrics.json")
    shutil.copy2(
        "runs/temporal_2017/external_metrics.json",
        root / "evidence/gap_extension/temporal_metrics.json",
    )
    shutil.copy2(
        "runs/temporal_2017/frozen_before_external.json",
        root / "evidence/gap_extension/temporal_frozen.json",
    )
    shutil.copy2(
        "runs/temporal_2017/compatibility.json",
        root / "evidence/gap_extension/temporal_compatibility.json",
    )
    (root / "EXTERNAL_VALIDATION_FEASIBILITY.md").write_text(
        "# Temporal validation: executed with scope limits\n\n2015→2017 CDC BRFSS. A separate14-variable LR candidate track was frozen using only2015 development CV before reading2017 row outcomes. Nutrition/alcohol and changed cholesterol screening omitted. Same DIABETE3 yes/no coding; SEX refused9 maps missing. Codebook variable pages and excerpts: runs/temporal_2017/compatibility.json.\n\n"
        + f"2017 original source450016 records, eligible {temporal['eligible_n']}; prespecified simple random eligible sample n={temporal['sample_n']}, seed20261106. External ledger evaluation_count=1. Source hash {temporal['source_sha256']}.\n\n"
        + table(pd.DataFrame([temporal["metrics"]]).drop(columns=["confusion_matrix"]).round(5))
        + "\n\nConditional respondent bootstrap200 repeats (not survey prediction CI):\n\n"
        + json.dumps(temporal["ci_conditional"], indent=2)
        + "\n\nThis is temporal transportability in the same survey system, not clinical validation, proof of person-level independence across years, or a comparison with Chang. Unlinked repeat respondents cannot be excluded. Full-year population prediction uncertainty was not estimated. No post-external tuning occurred.\n"
    )
    (root / "SURVEY_STATISTICAL_INFERENCE.md").write_text(
        "# Survey statistical inference\n\nPreserved original results and code: _LLCPWT/_STSTR/nested_PSU Taylor linearization, full-domain zero influences, design CIs, adjusted OR/RRR. Independent R survey/nnet covariance tests were rerun in the baseline and final test suite.\n\nOriginal binary cohort422558; complete cases243529; weighted conditional-domain diabetes prevalence10.7052% (CI10.5303–10.8826%); BMI OR1.8754 (1.7936–1.9610). Core-three complete cases248053. Median/mode sensitivity is deterministic, not proper multiple imputation. These associations are not causal.\n\nNew development class weighting is not survey weighting. Temporal unweighted CI is not design-based population prediction uncertainty. Full multiple imputation, MNAR and confirmatory subgroup inference remain incomplete.\n"
    )
    repeats = read_json(run / "repeat_seed_results.json")
    (root / "ROBUSTNESS_ANALYSIS.md").write_text(
        "# Development robustness\n\n"
        + intro
        + table(
            pd.DataFrame(
                [
                    {"seed_run": i, **{k: v for k, v in r["metrics"].items() if np.isscalar(v)}}
                    for i, r in enumerate(repeats)
                ]
            ).round(5)
        )
        + "\n\nAdditional RepeatedStratifiedKFold and held-out-state results: runs/gap_real_quick_v4/repeated_cv_* and group_cv. Sex/age/race/BMI/education/income descriptive development groups: tables/gap_extension/development_subgroups.csv. Cohorts differ for complete-case analysis. Overlapping folds are dependent; variability is descriptive, with no IID significance claim. Subgroup sample thresholds30 and presence of all classes are required. No model-selection uncertainty correction or confirmatory fairness claims.\n"
    )
    catalog = read_json("docs/chang_gap_catalog.json")
    statuses = {g["gap_id"]: "PARTIALLY_ADDRESSED" for g in catalog["gaps"]}
    statuses.update(
        C06="REFUTED_AS_GAP",
        C07="REFUTED_AS_GAP",
        C12="RESOLVED",
        C17="RESOLVED",
        C19="INFEASIBLE_WITH_AVAILABLE_DATA",
    )
    matrix = []
    for g in catalog["gaps"]:
        matrix.append(
            {
                "gap_id": g["gap_id"],
                "question": g["gap"],
                "evidence": g["paper_sections"] + " pp." + str(g["paper_pages"]),
                "evidence_status": g["gap_classification"],
                "scientific_status": statuses[g["gap_id"]],
                "test": "Controlled development CV / original inference / source feasibility; see dedicated reports",
                "data_requirements": "CDC2015 original development IDs; C17 CDC2017; C19 external biomarkers; processed linkage unresolved",
                "module": "src_extensions/experiments.py; runner.py; ancillary.py; temporal.py; scripts/gap_feasibility.py",
                "configuration": "runs/gap_real_quick_v4/manifest.json and planned_experiments.json",
                "execution": "78 binary +4 three-class development configs; separate frozen temporal14-variable model",
                "result_artifact": "reports/tables/gap_extension/experiment_registry.csv; reports/evidence/gap_extension/",
                "outcome": g["observed_result"]
                if g["gap_id"] in ["C01", "C02", "C06", "C07", "C12", "C19", "C21"]
                else "New executed evidence described in extension reports; no blanket improvement claim",
                "remaining_limitations": "RESOLVED is scope-limited (design inference / single2017 temporal evaluation). Other gaps require broader evidence; no faithful reproduction, full training run or real federated/privacy validation.",
            }
        )
    md = table(pd.DataFrame(matrix)[["gap_id", "question", "evidence_status", "scientific_status"]])
    write_csv(root / "research_gap_execution_matrix.csv", pd.DataFrame(matrix))
    (root / "RESEARCH_GAP_EXECUTION_MATRIX.md").write_text(
        "# Research-gap execution matrix\n\n"
        + md
        + "\n\nDetailed test/data/module/configuration/artifact/limitations fields: research_gap_execution_matrix.csv. C12 RESOLVED refers to the stated inference scope; C17 RESOLVED refers only to executing a frozen2015→2017 evaluation, not eliminating distribution shift or proving clinical utility. Evidence status remains separate from implementation and scientific status.\n"
    )
    (root / "RESEARCH_GAP_RESULTS.md").write_text(
        "# Research-gap results: PARTIAL COMPLETION\n\n"
        + intro
        + md
        + "\n\n"
        + f"{len(good)} of {len(rows)} binary experiments completed on real development data. Four three-class models executed separately. Best selected development score is not an unbiased final estimate. Temporal BA={temporal['metrics']['balanced_accuracy']:.4f}, sensitivity={temporal['metrics']['sensitivity']:.4f}, specificity={temporal['metrics']['specificity']:.4f}. No comparison of these scores directly to82.26% is valid.\n"
    )
    (root / "REPRODUCIBILITY.md").write_text(
        "# Extension reproducibility\n\nRecoverable pre-modification checkpoint: /workspace/research_checkpoints/brfss_before_gap_extension.tar.gz (local evidence; not a required execution path). Baseline39 tests passed before modification. Legacy src/config/model/split/evaluation evidence remained unchanged; audit snapshot checks in runner and temporal workflow.\n\nEach experiment stores config, source-run signature, OOF rows checksum, fold metrics, feature lists and inner thresholds. Fixed outer splits/development IDs in run folder; seed20261106. Source/dependency versions in manifest. Model serialization uses trusted joblib artifacts. Completed experiment records resume by checksum; modified scientific engine requires new run directory, not deletion of evidence.\n\nFirst attempt had a SMOTENC feature-name export error (77/78); v2 corrected it. V3 additionally isolates inner preprocessing for RFECV/permutation. Temporal evaluation used the earlier unchanged LR factory branch, was not repeated, and is not evidence for the new selector variants. Exact earlier engine sources were recovered with verified original hashes. Earlier attempt preserved. This was development debugging, not repeated final-test evaluation. 2017 evaluation ledger has one batch and no post-result optimization. Original2015 final ledger remains1.\n"
    )
    unfinished = """# Unfinished work — PARTIAL COMPLETION

- Exact/faithful Chang reproduction: unresolved cohort, label, RF tree/depth and preprocessing order; processed UCI linkage to old test unknown. Real processed predictive reproduction deliberately not executed.
- STANDARD/EXTENDED full eligible development execution not run; QUICK budget2000 and shallow nested searches only. Full optimization/long repeated nested CV not claimed.
- Strict inner-preprocessing isolation for RFECV/permutation was corrected in v3; older v2 results remain archived and are superseded for those comparisons.
- Full mixed-feature ADASYN not used; continuous-only experiments cannot establish benefit for nominal-rich full representation. Matched continuous soft-voting/stacking controls remain incomplete.
- Calibration interventions tested on unweighted LR; no claim of repairing the legacy weighted model calibration. Clinical operating constraints/utilities not established.
- Full multiple-imputation survey inference, MNAR, functional-form sensitivity and confirmatory adjusted subgroup effects incomplete.
- SHAP is training-only/descriptive with64-row selector samples and128-row summary; bootstrap3 for stability is limited. No causal explanations or validated interpretability gains.
- Temporal validation limited to a separate14-variable model and5000 eligible2017 respondents; not a clinical external cohort, no survey-valid predictive CIs, possible unlinked repeat respondents across years.
- Genetics/lab biomarkers unavailable. Federation is public-data simulated clients with centralized preprocessing; no real institutions, secure aggregation, differential privacy or privacy guarantee.
- Actual Google Colab runtime not available: COLAB_RUNTIME_NOT_VERIFIED.
- Historical notebook tests retained; only modified notebooks must be reported with current execution counts. No guaranteed zero-error environment claim.
"""
    (root / "UNFINISHED_WORK.md").write_text(unfinished)
    # Course manuscript includes all requested sections; separates old evidence and new tracks.
    sections = [
        "Title",
        "Abstract",
        "Introduction",
        "Literature review",
        "Research Gap",
        "Research objectives",
        "Research questions",
        "Hypotheses",
        "Dataset",
        "Cohort construction",
        "Variables",
        "Statistical methods",
        "Machine-learning methods",
        "Experimental protocol",
        "Results",
        "Baseline comparison",
        "Research-gap evaluation",
        "Statistical inference",
        "Model interpretation",
        "Robustness",
        "Discussion",
        "Limitations",
        "Conclusions",
        "References",
        "Reproducibility appendix",
    ]
    content = {
        "Title": "BRFSS2015 Statistical Methods: design-based inference and post-audit exploratory prediction with temporal validation",
        "Abstract": f"Original inference and protected2015 quick findings were preserved. An extension executed{len(good)} binary configurations and four three-class models on development-only data, plus a separately frozen14-variable temporal model evaluated on5000 BRFSS2017 respondents. Findings show operating-point and calibration tradeoffs; no faithful paper superiority claim.",
        "Introduction": "Self-reported diabetes surveillance supports cross-sectional association and classification, not causal or incidence claims.",
        "Literature review": Path("docs/LITERATURE_REVIEW.md").read_text(),
        "Research Gap": md,
        "Research objectives": "A: source-grounded reproduction feasibility. B: investigate C01–C21 with evidence. C: predictive comparisons under controlled development. D: preserve survey inference. These outcomes are distinct.",
        "Research questions": "RQ1 adjusted associations; RQ2 feature/model/resampling effects; RQ3 threshold/calibration tradeoffs; RQ4 subgroup/seed/year stability.",
        "Hypotheses": "Coefficient/group nulls: adjusted association=0. Predictive contrasts require matched cohorts/conditions; development rankings are exploratory, not confirmatory significance tests.",
        "Dataset": "Original CDC2015 XPT441456×330; UCI processed source audited separately; original CDC2017 XPT450016 for temporal evaluation. See source hashes and codebook evidence.",
        "Cohort construction": "Original binary422558, complete cases243529; all84512 legacy final-test IDs excluded from new development. QUICK draws2000 training-pool respondents. Core-three outcomes and cohorts remain separate.",
        "Variables": "19 original predictors for development; encoded-column k differs from raw-variable count. Temporal model uses14 compatible variables, excludes rotated/changed nutrition/alcohol/cholesterol screening. No genes/lab disease confirmation.",
        "Statistical methods": (root / "SURVEY_STATISTICAL_INFERENCE.md").read_text(),
        "Machine-learning methods": intro
        + "See feature/model/imbalance/ensemble reports and registry for executable settings; no new algorithm claimed.",
        "Experimental protocol": intro
        + "Model and threshold for temporal evaluation frozen before2017 label loading; no new2015 final evaluations.",
        "Results": table(
            df[
                [
                    "model",
                    "stage",
                    "balanced_accuracy",
                    "sensitivity",
                    "specificity",
                    "roc_auc",
                    "pr_auc",
                    "brier",
                ]
            ].round(5)
        )
        + "\n\nTemporal:\n\n"
        + table(pd.DataFrame([temporal["metrics"]]).drop(columns=["confusion_matrix"]).round(5)),
        "Baseline comparison": (root / "CHANG_2022_REPRODUCTION.md").read_text(),
        "Research-gap evaluation": (root / "RESEARCH_GAP_RESULTS.md").read_text(),
        "Statistical inference": (root / "SURVEY_STATISTICAL_INFERENCE.md").read_text(),
        "Model interpretation": "SHAP and bootstrap stability executed on training data; predictive importance is not causal. Adjusted ORs answer a different conditional associational question.",
        "Robustness": (root / "ROBUSTNESS_ANALYSIS.md").read_text(),
        "Discussion": "Soft voting led exploratory development BA, but the separate temporal clinical-feature track selected weighted LR. This is not an apples-to-apples architecture comparison across years. Broad benefits and clinical utility remain unproved.",
        "Limitations": unfinished,
        "Conclusions": "PARTIAL COMPLETION. Feasible selected experiments executed and independent temporal evaluation added; unresolved reproduction, full-budget inference/ML and real privacy/clinical-data requirements remain explicit.",
        "References": "Chang et al.2022, DOI10.1016/j.health.2022.100118; CDC2015 https://www.cdc.gov/brfss/annual_data/annual_2015.html ; CDC2017 https://www.cdc.gov/brfss/annual_data/annual_2017.html ; UCI DOI10.24432/C53919. No unverified methodological deficiency attributed to a paper.",
        "Reproducibility appendix": (root / "REPRODUCIBILITY.md").read_text(),
    }
    (root / "FINAL_RESEARCH_REPORT.md").write_text(
        "\n\n".join("## " + s + "\n\n" + content[s] for s in sections) + "\n"
    )
    for source in ["gap_real_quick_v4", "gap_real_three_v3"]:
        integrity = read_json(Path("runs") / source / "integrity.json")
        assert integrity["unchanged"] and integrity["legacy_test_overlap"] == 0
    write_json(
        root / "evidence/gap_extension/status.json",
        {
            "overall": "PARTIAL_COMPLETION",
            "binary_experiments": len(good),
            "planned": len(rows),
            "three_class_experiments": 4,
            "legacy_test_evaluations": 1,
            "temporal_evaluations": 1,
            "colab": "COLAB_RUNTIME_NOT_VERIFIED",
        },
    )
    print(
        "Reports generated from executed artifacts:",
        len(good),
        "binary configurations; original test unchanged.",
    )


if __name__ == "__main__":
    report()
