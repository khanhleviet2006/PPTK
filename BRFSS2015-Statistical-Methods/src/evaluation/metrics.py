import numpy as np
from scipy import stats
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    log_loss,
    brier_score_loss,
)


def metrics(y, p, threshold=0.5, weights=None):
    y = np.asarray(y, int)
    p = np.asarray(p, float)
    if (
        p.ndim != 2
        or len(y) != len(p)
        or not np.isfinite(p).all()
        or (p < 0).any()
        or (p.sum(axis=1) <= 0).any()
    ):
        raise ValueError("Expected finite nonnegative probabilities for each respondent")
    p = p / p.sum(axis=1, keepdims=True)
    k = p.shape[1]
    pred = (p[:, 1] >= threshold).astype(int) if k == 2 else p.argmax(axis=1)
    cm = confusion_matrix(y, pred, labels=np.arange(k), sample_weight=weights)
    avg = "binary" if k == 2 else "macro"
    r = {
        "accuracy": accuracy_score(y, pred, sample_weight=weights),
        "balanced_accuracy": float(
            np.mean(np.diag(cm)[cm.sum(axis=1) > 0] / cm.sum(axis=1)[cm.sum(axis=1) > 0])
        ),
        "precision": precision_score(y, pred, average=avg, zero_division=0, sample_weight=weights),
        "sensitivity": recall_score(y, pred, average=avg, zero_division=0, sample_weight=weights),
        "f1": f1_score(y, pred, average=avg, zero_division=0, sample_weight=weights),
        "macro_f1": f1_score(y, pred, average="macro", zero_division=0, sample_weight=weights),
        "log_loss": log_loss(y, p, labels=np.arange(k), sample_weight=weights),
        "confusion_matrix": cm.tolist(),
    }
    for c in range(k):
        tp = cm[c, c]
        fn = cm[c].sum() - tp
        fp = cm[:, c].sum() - tp
        tn = cm.sum() - tp - fn - fp
        r[f"class_{c}_sensitivity"] = tp / (tp + fn) if tp + fn else np.nan
        r[f"class_{c}_specificity"] = tn / (tn + fp) if tn + fp else np.nan
    if len(np.unique(y)) == k:
        r["roc_auc"] = (
            roc_auc_score(y, p[:, 1], sample_weight=weights)
            if k == 2
            else roc_auc_score(y, p, multi_class="ovr", average="macro", sample_weight=weights)
        )
        onehot = np.eye(k)[y]
        r["pr_auc"] = (
            average_precision_score(y, p[:, 1], sample_weight=weights)
            if k == 2
            else average_precision_score(onehot, p, average="macro", sample_weight=weights)
        )
    else:
        r.update(roc_auc=np.nan, pr_auc=np.nan)
    r["brier"] = (
        brier_score_loss(y, p[:, 1], sample_weight=weights)
        if k == 2
        else np.average(np.sum((np.eye(k)[y] - p) ** 2, axis=1), weights=weights)
    )
    r["specificity"] = (
        r["class_1_specificity"]
        if k == 2
        else np.mean([r[f"class_{c}_specificity"] for c in range(k)])
    )
    return r


def calibration(y, p, bins=10, weights=None):
    rows = []
    for c in range(p.shape[1]):
        score = p[:, c]
        obs = (np.asarray(y) == c).astype(float)
        for b in range(bins):
            keep = (score >= b / bins) & (score < ((b + 1) / bins) if b < bins - 1 else score <= 1)
            if keep.sum():
                w = None if weights is None else np.asarray(weights)[keep]
                rows.append(
                    {
                        "class": c,
                        "bin": b,
                        "n": int(keep.sum()),
                        "predicted": np.average(score[keep], weights=w),
                        "observed": np.average(obs[keep], weights=w),
                    }
                )
    return rows


def bootstrap(y, p, repeats=1000, seed=2015, threshold=0.5, other=None):
    # Paired respondent bootstrap conditional on frozen model; NOT a survey population CI.
    rng = np.random.default_rng(seed)
    y = np.asarray(y)
    keys = [k for k, v in metrics(y, p, threshold).items() if np.isscalar(v)]
    vals = {k: [] for k in keys}
    for _ in range(repeats):
        ix = rng.integers(0, len(y), len(y))
        a = metrics(y[ix], p[ix], threshold)
        b = metrics(y[ix], other[ix], 0.5) if other is not None else None
        for k in keys:
            if np.isfinite(a[k]) and (b is None or np.isfinite(b[k])):
                vals[k].append(a[k] if b is None else a[k] - b[k])
    return {
        k: {
            "lower": np.quantile(v, 0.025),
            "upper": np.quantile(v, 0.975),
            "valid_replicates": len(v),
        }
        for k, v in vals.items()
        if v
    }


def mcnemar(y, pred1, pred2):
    a = np.asarray(pred1) == y
    b = np.asarray(pred2) == y
    n01 = int(np.sum(a & ~b))
    n10 = int(np.sum(~a & b))
    return {
        "discordant_01": n01,
        "discordant_10": n10,
        "p_exact": stats.binomtest(n01, n01 + n10, 0.5).pvalue if n01 + n10 else 1.0,
    }
