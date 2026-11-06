import numpy as np
from src.evaluation.metrics import metrics, bootstrap, mcnemar


def test_hand_metrics():
    y = np.array([0, 0, 1, 1])
    p = np.array([[0.9, 0.1], [0.2, 0.8], [0.3, 0.7], [0.7, 0.3]])
    m = metrics(y, p)
    assert m["accuracy"] == 0.5 and m["sensitivity"] == 0.5 and m["specificity"] == 0.5
    assert m["confusion_matrix"] == [[1, 1], [1, 1]]
    ci = bootstrap(y, p, 30)
    assert ci["accuracy"]["lower"] <= 0.5 <= ci["accuracy"]["upper"]
    assert mcnemar(y, y, y)["p_exact"] == 1


def test_imbalanced_and_multiclass():
    y = np.r_[np.zeros(99), 1].astype(int)
    p = np.tile([0.99, 0.01], (100, 1))
    m = metrics(y, p)
    assert m["accuracy"] == 0.99 and m["balanced_accuracy"] == 0.5
    y = np.array([0, 1, 2])
    m = metrics(y, np.eye(3) * 0.8 + 0.2 / 3)
    assert m["macro_f1"] == 1 and m["class_2_sensitivity"] == 1


def test_single_class_metrics():
    m = metrics(np.zeros(4, int), np.tile([0.9, 0.1], (4, 1)))
    assert np.isnan(m["roc_auc"])
