from pathlib import Path
import io
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.utils.io import atomic_bytes, read_json, write_json, write_csv


def generate(out, synthetic=False):
    out = Path(out)
    fig = out / "figures"
    fig.mkdir(exist_ok=True)

    def save_figure(path):
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=140)
        atomic_bytes(path, buffer.getvalue())

    audit = read_json(out / "audit.json") if (out / "audit.json").exists() else {}
    res = read_json(out / "final_metrics.json") if (out / "final_metrics.json").exists() else None
    prev = read_json(out / "prevalence.json") if (out / "prevalence.json").exists() else {}
    if (out / "missingness.csv").exists():
        missing = pd.read_csv(out / "missingness.csv")
        m = missing[missing.outcome.astype(str).eq("all")]
        ax = m.set_index("variable").fraction.sort_values().plot.barh(figsize=(7, 6))
        ax.set_xlabel("Fraction missing")
        ax.set_title("Synthetic data" if synthetic else "BRFSS 2015 cohort")
        plt.tight_layout()
        save_figure(fig / "missingness.png")
        plt.close()
        heat = missing.pivot(index="variable", columns="outcome", values="fraction")
        _, ax = plt.subplots(figsize=(7, 6))
        im = ax.imshow(heat.to_numpy(), aspect="auto", vmin=0, vmax=1, cmap="Reds")
        ax.set_xticks(range(len(heat.columns)), heat.columns)
        ax.set_yticks(range(len(heat.index)), heat.index)
        ax.set_xlabel("Outcome group")
        plt.colorbar(im, ax=ax, label="Missing fraction")
        plt.tight_layout()
        save_figure(fig / "missingness_by_outcome.png")
        plt.close()
    if res:
        cm = res["selected"]["confusion_matrix"]
        _, ax = plt.subplots()
        im = ax.imshow(cm, cmap="Blues")
        plt.colorbar(im, ax=ax)
        for i, row in enumerate(cm):
            for j, value in enumerate(row):
                ax.text(j, i, str(int(value)), ha="center", va="center")
        ax.set(
            xlabel="Predicted class",
            ylabel="Observed class",
            title="Frozen model test confusion matrix",
        )
        save_figure(fig / "confusion_matrix.png")
        plt.close()
        cal = pd.read_csv(out / "calibration.csv")
        _, ax = plt.subplots()
        for c, g in cal.groupby("class"):
            ax.plot(g.predicted, g.observed, "o-", label=f"Class {c}")
        ax.plot([0, 1], [0, 1], "k--")
        ax.set(xlabel="Mean predicted probability", ylabel="Observed frequency")
        ax.legend()
        save_figure(fig / "calibration.png")
        plt.close()
    status = {
        "data": "SYNTHETIC_ONLY" if synthetic else "REAL_DATA_EXECUTED",
        "colab": "COLAB_RUNTIME_NOT_VERIFIED",
        "empirical_results_available": res is not None,
    }
    write_json(out / "execution_status.json", status)
    title = (
        "Synthetic validation report — not epidemiological evidence"
        if synthetic
        else "BRFSS 2015 Statistical Methods: empirical report draft"
    )
    cohort = read_json(out / "cohort.json") if (out / "cohort.json").exists() else {}
    manifest = read_json(out / "run_manifest.json") if (out / "run_manifest.json").exists() else {}

    def markdown(frame):
        head = "| " + " | ".join(map(str, frame.columns)) + " |"
        rule = "| " + " | ".join(["---"] * len(frame.columns)) + " |"
        rows = [
            "| " + " | ".join(str(v).replace("|", "/") for v in row) + " |"
            for row in frame.itertuples(index=False, name=None)
        ]
        return "\n".join([head, rule] + rows)

    prevalence_text = "[UNAVAILABLE: prevalence stage has not executed.]"
    if prev:
        pr = pd.DataFrame([{"class": k, **v} for k, v in prev.items()])
        prevalence_text = markdown(pr[["class", "estimate", "lower", "upper", "n"]].round(5))
        disease_class = "2.0" if manifest.get("mode") == "core_three" else "1.0"
        if disease_class in prev:
            r = prev[disease_class]
            prevalence_text += (
                f"\n\nWeighted diabetes prevalence within this defined analysis domain was {100 * r['estimate']:.2f}% "
                f"(95% design CI {100 * r['lower']:.2f}% to {100 * r['upper']:.2f}%). This domain excludes unknown outcomes and may exclude borderline/pregnancy-only responses; it is not an unconditional whole-population estimate."
            )
    association_text = "[UNAVAILABLE: adjusted inference has not executed.]"
    assoc_path = out / (
        "multinomial_rrr.csv" if manifest.get("mode") == "core_three" else "adjusted_or.csv"
    )
    if assoc_path.exists():
        assoc = pd.read_csv(assoc_path)
        effect = "RRR" if "RRR" in assoc else "OR"
        terms = [
            "_BMI5_per_10",
            "SEX_2",
            "BPHIGH4_3",
            "TOLDHI2_2",
            "_AGEG5YR_13",
            "INCOME2_8",
            "GENHLTH_5",
        ]
        subset = assoc[assoc.term.map(lambda t: t.split(":")[-1] in terms)]
        association_text = (
            "Prespecified illustrative contrasts are below; the complete coefficient table accompanies this report. "
            "OR/RRR compare coded levels with the first codebook category, holding included covariates fixed. "
            "BMI is per 10 kg/m²; no coefficient is a causal effect.\n\n"
            + markdown(subset[["term", effect, "lower", "upper", "p"]].round(5))
        )
    development_text = "[UNAVAILABLE: model development has not executed.]"
    if (out / "development.json").exists():
        history = read_json(out / "development.json")
        comparison = pd.DataFrame(
            [
                {k: v for k, v in r.items() if k not in ["cv_fold_scores", "oof_metrics"]}
                for r in history
            ]
        )
        write_csv(out / "model_comparison.csv", comparison)
        good = comparison[comparison.status.eq("SUCCESS")]
        development_text = (
            "Development scores guided selection and threshold tuning; they are optimistic for the selected strategy. "
            "They are not final test performance. All candidates and skipped dependencies are in model_comparison.csv.\n\n"
            + markdown(
                good[["model", "selector", "k", "imbalance", "cv_mean", "threshold"]]
                .sort_values("cv_mean", ascending=False)
                .head(15)
                .round(5)
            )
        )
    result_text = "[UNAVAILABLE: final evaluation has not executed; no result inferred.]"
    conclusion = "Empirical prediction conclusions remain unavailable until frozen final evaluation executes."
    if res:
        selected = res["selected"]
        ci = res["conditional_respondent_bootstrap_ci"]
        rows = [
            {
                "metric": k,
                "selected": selected[k],
                "baseline": res["baseline"][k],
                "CI_lower": ci.get(k, {}).get("lower"),
                "CI_upper": ci.get(k, {}).get("upper"),
            }
            for k in [
                "accuracy",
                "balanced_accuracy",
                "sensitivity",
                "specificity",
                "precision",
                "f1",
                "roc_auc",
                "pr_auc",
                "brier",
                "log_loss",
            ]
        ]
        result_text = markdown(pd.DataFrame(rows).round(5))
        delta = res["paired_difference_ci"]["balanced_accuracy"]
        difference = selected["balanced_accuracy"] - res["baseline"]["balanced_accuracy"]
        result_text += (
            f"\n\nThe frozen model was evaluated on {res['test_n']:,} test respondents once. "
            f"Balanced-accuracy difference versus the fixed same-cohort logistic comparator was {difference:.4f} "
            f"(paired conditional bootstrap 95% interval {delta['lower']:.4f} to {delta['upper']:.4f}). "
            "Intervals describe test respondents conditional on fixed fitted models; they do not include survey population or model-selection uncertainty. See final_metrics.json for all per-class errors, comparisons and weighted point estimates."
        )
        direction = "excludes zero" if delta["lower"] > 0 or delta["upper"] < 0 else "includes zero"
        conclusion = (
            f"The paired balanced-accuracy interval {direction}. The executed {manifest.get('profile', 'unknown')} profile "
            "supports the reported same-cohort comparison under this protocol; it does not establish superiority to a different published cohort or clinical diagnostic utility. "
            "Associations remain cross-sectional and require interpretation alongside outcome coding, missingness and sensitivity tables."
        )
    if synthetic:
        conclusion = "All numerical results in this report are synthetic software validation. They provide no evidence about diabetes prevalence, real-world associations, or predictive benefit."
    sections = [
        f"# {title}",
        "## Abstract",
        "This cross-sectional analysis investigates self-reported diabetes associations and fixed-protocol predictive classification. Estimates describe associations, not causal effects or future incident disease.",
        "## Research questions and prespecified analysis",
        "RQ1: adjusted associations using complex survey design. RQ2: training-only feature, imbalance and model comparisons. RQ3: balanced accuracy, sensitivity, calibration and discrimination versus a same-cohort logistic baseline. RQ4: subgroup and outcome/missingness sensitivity. Full estimands and hypotheses are in docs/RESEARCH_PROTOCOL.md.",
        "## Data and cohort",
        f"Source records: {audit.get('records', 'unavailable'):,}. Eligible: {cohort.get('eligible', 0):,}. Complete cases: {cohort.get('complete_case', 0):,}. Design strata: {audit.get('strata', 0):,}. Profile: {manifest.get('profile', 'unavailable')}. Source fingerprints and exact schema are in audit.json.",
        "## Methods",
        "CDC core DIABETE3=1 versus 3 is the primary contrast; pregnancy-only and borderline responses are excluded. Optional prediabetes ascertainment is not assumed complete. Survey point estimates use _LLCPWT and variance uses stratified _PSU score totals within _STSTR, without a finite population correction. Complete-case inference and median/mode sensitivity target different missing-data assumptions. Preprocessing and feature selection are fitted inside training folds. The final test set is accessed in one frozen-model batch.",
        "## Weighted prevalence",
        prevalence_text,
        "## Statistical associations",
        "Adjusted OR, confidence limits, design-based p-values, and exploratory BH corrections: adjusted_or.csv. Multinomial RRR: multinomial_rrr.csv when completed. Univariate results: univariate.csv. Clinical interpretation must consider coding references, precision, multiplicity, selection, and reverse causation.",
        association_text,
        "## Model development",
        development_text,
        "## Predictive results",
        result_text,
        "## Research gaps and interpretation",
        "The gap matrix distinguishes inspected evidence from hypotheses. Chang et al. (2022), DOI 10.1016/j.health.2022.100118, reported 82.26% accuracy; our cohort/outcome and evaluation may differ. A higher point estimate here does not establish improvement over that publication. The implemented comparison estimates improvement over a prespecified logistic model on identical test respondents. Feature importance measures predictive utility, not causal contribution. Prediction, methodological validity, interpretability, and epidemiological evidence are separate contributions.",
        "## Sensitivity and generalizability",
        "See sensitivity_or.csv, borderline_sensitivity_or.csv, multinomial_rrr.csv, and subgroups.csv. Missing outputs are unavailable rather than negative findings. Core-question borderline status is an imperfect three-category self-report; module analyses require geographic/version eligibility and appropriate weights. External or temporal validation has not been performed.",
        "## Limitations",
        "Self-reported cross-sectional data cannot distinguish all diabetes types, verify biological disease, or determine temporal direction. Complete-case inference may be selected. Deterministic imputation sensitivity is not multiple imputation. Calibrated weights are treated as fixed in the with-replacement linearization. Predictive bootstrap intervals are conditional respondent intervals, not full survey population intervals or uncertainty over model selection. Small demographic groups may be unstable. Quick mode caps training size and is a computational validation rather than a full experimental study.",
        "## Reproducibility",
        "Source hashes, code/config signature, package versions, split IDs/checksum, CV indices, experiment history, frozen model checksum, test-access ledger and atomic checkpoints accompany this report. See execution_status.json; actual Google Colab execution remains unverified.",
        "## Conclusion",
        conclusion,
        "## References",
        """CDC BRFSS 2015 data and codebook: https://www.cdc.gov/brfss/annual_data/annual_2015.html

Chang V, Ganatra MA, Hall K, Golightly L, Xu Q (2022). An assessment of machine learning models and algorithms for early prediction and diagnosis of diabetes using health indicators. Healthcare Analytics 2:100118. https://doi.org/10.1016/j.health.2022.100118""",
    ]
    atomic_bytes(out / "final_report.md", ("\n\n".join(sections) + "\n").encode())
    atomic_bytes(
        out / "execution_status.md", ("\n".join(f"{k}: {v}" for k, v in status.items())).encode()
    )
    return status
