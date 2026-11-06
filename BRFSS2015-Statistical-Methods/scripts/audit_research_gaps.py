"""Read-only scientific evidence audit; never fits, predicts, tunes or re-evaluates test data."""

import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {"VERIFIED", "PARTIALLY_VERIFIED", "UNVERIFIED", "HYPOTHESIS"}
RUN = ROOT / "runs/real_final_quick"
PROTECTED = [
    "development.json",
    "frozen.json",
    "baseline_frozen.json",
    "final_metrics.json",
    "test_access.json",
    "split.json",
    "cv_splits.json",
    "training_subset.json",
    "frozen_model.joblib",
    "baseline_model.joblib",
    "run_manifest.json",
]


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def normalized(text):
    return re.sub(r"\s+", " ", re.sub(r"(?<=\w)-\n(?=\w)", "", text)).strip()


def snapshot():
    files = [RUN / n for n in PROTECTED]
    files += list((RUN / "checkpoints").glob("*.json"))
    files += list((ROOT / "src").rglob("*.py"))
    files += list((ROOT / "configs").glob("*.yaml"))
    return {str(p.relative_to(ROOT)): sha(p) for p in files}


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def audit(verify_only=False):
    before = snapshot()
    catalog = read(ROOT / "docs/chang_gap_catalog.json")
    pdf = ROOT / catalog["pdf_path"]
    assert sha(pdf) == catalog["pdf_sha256"], "PDF source changed"
    reader = PdfReader(pdf)
    assert len(reader.pages) == 14
    pages = [normalized(p.extract_text() or "") for p in reader.pages]
    assert catalog["doi"] in pages[0], "Paper identity does not match DOI"
    evidence = {e["evidence_id"]: e for e in catalog["evidence"]}
    for e in evidence.values():
        assert e["quote"] in pages[e["pdf_page"] - 1], (e["evidence_id"], e["quote"])
    rows = catalog["gaps"]
    assert len({g["gap_id"] for g in rows}) == len(rows) == 21
    for g in rows:
        assert g["gap_classification"] in ALLOWED
        for eid in g["evidence_ids"]:
            assert evidence[eid]["pdf_page"] in g["paper_pages"], (g["gap_id"], eid)
        for path in g["artifact_paths"]:
            assert (ROOT / path).is_file(), path

    development = read(RUN / "development.json")
    success = [d for d in development if d["status"] == "SUCCESS"]
    # Winner is independently reconstructed from saved TRAINING CV only.
    # No test metric is read before this assertion and no model is executed.
    cv_winner = sorted(success, key=lambda d: (-d["cv_mean"], d["experiment_id"]))[0]
    frozen = read(RUN / "frozen.json")
    assert frozen["experiment_id"] == cv_winner["experiment_id"]
    assert frozen["threshold"] == cv_winner["threshold"]
    assert frozen["model_sha256"] == sha(RUN / "frozen_model.joblib")
    baseline_frozen = read(RUN / "baseline_frozen.json")
    assert baseline_frozen["model_sha256"] == sha(RUN / "baseline_model.joblib")
    ledger = read(RUN / "test_access.json")
    assert ledger["state"] == "COMPLETE" and ledger["evaluation_count"] == 1
    assert ledger["result_sha256"] == sha(RUN / "final_metrics.json")
    manifest = read(RUN / "run_manifest.json")
    assert all(sha(ROOT / p) == h for p, h in manifest["code"].items())
    assert manifest["synthetic"] is False and manifest["profile"] == "quick"
    for run_name, count in [("synthetic_standard_verified", 39), ("synthetic_three_verified", 17)]:
        rr = ROOT / "runs" / run_name
        assert read(rr / "run_manifest.json")["synthetic"] is True
        assert len(read(rr / "development.json")) == count
    # Read previously frozen metrics solely to describe existing results.
    result = read(RUN / "final_metrics.json")
    assert result["evaluation_count"] == 1 and result["test_n"] == 84512
    selected, baseline = result["selected"], result["baseline"]
    counts = Counter(g["gap_classification"] for g in rows)
    impl_counts = Counter(g["implementation_status"] for g in rows)
    metadata = {
        "audited_at": datetime.now(ZoneInfo("Asia/Bangkok")).isoformat(),
        "timezone": "Asia/Bangkok",
        "catalog_sha256": sha(ROOT / "docs/chang_gap_catalog.json"),
        "paper_doi": catalog["doi"],
        "paper_source_url": catalog["source_url"],
        "paper_pdf_sha256": sha(pdf),
        "paper_pages": 14,
        "quote_checks_passed": len(evidence),
        "gap_count": len(rows),
        "classification_counts": dict(counts),
        "implementation_counts": dict(impl_counts),
        "cv_selection_matches_frozen": True,
        "audit_retrained_models": False,
        "audit_reran_predictions": False,
        "audit_reoptimized_thresholds": False,
        "audit_reran_test_evaluation": False,
        "test_evaluation_count": 1,
        "protected_files_before": before,
    }
    expanded = []
    for g in rows:
        expanded.append(
            {
                **g,
                "paper": catalog["paper"],
                "doi": catalog["doi"],
                "doi_url": "https://doi.org/" + catalog["doi"],
                "paper_source_url": catalog["source_url"],
                "paper_pdf_sha256": sha(pdf),
                "printed_pages": g["paper_pages"],
                "evidence_classification": "VERIFIED_PDF_CONTENT",
                "supporting_quotes": " || ".join(
                    f"{eid} (p.{evidence[eid]['pdf_page']}): {evidence[eid]['quote']}"
                    for eid in g["evidence_ids"]
                ),
                "project_claim_locations": "docs/LITERATURE_REVIEW.md; docs/RESEARCH_GAP_MATRIX.md; docs/literature_evidence.csv; reports/final_report.md; docs/EXPERIMENT_PLAN.md; docs/SCIENTIFIC_AUDIT.md; original master prompt",
                "test_used_for_selection": False,
            }
        )
    if verify_only:
        for location in [
            ROOT / "reports/research_gap_evidence.csv",
            ROOT / "research_gap_evidence.csv",
        ]:
            with location.open(newline="") as f:
                loaded = list(csv.DictReader(f))
            assert len(loaded) == 21 and {x["gap_id"] for x in loaded} == {
                x["gap_id"] for x in rows
            }
        assert sha(ROOT / "research_gap_evidence.csv") == sha(
            ROOT / "reports/research_gap_evidence.csv"
        )
        assert (ROOT / "reports/RESEARCH_GAP_AUDIT.md").is_file()
    else:
        output = io.StringIO(newline="")
        writer = csv.DictWriter(output, fieldnames=list(expanded[0]))
        writer.writeheader()
        for g in expanded:
            writer.writerow(
                {k: "; ".join(map(str, v)) if isinstance(v, list) else v for k, v in g.items()}
            )
        for location in [
            ROOT / "reports/research_gap_evidence.csv",
            ROOT / "research_gap_evidence.csv",
        ]:
            location.write_text(output.getvalue())
        make_report(
            catalog, expanded, evidence, selected, baseline, result, frozen, counts, impl_counts
        )
        write_json(ROOT / "reports/evidence/research_gap_audit_provenance.json", metadata)
    assert before == snapshot(), "Protected research artifacts changed during evidence audit"
    if not verify_only:
        metadata["protected_files_after"] = snapshot()
        metadata["protected_hashes_unchanged"] = True
        write_json(ROOT / "reports/evidence/research_gap_audit_provenance.json", metadata)
    print(
        json.dumps(
            {
                "quotes_verified": len(evidence),
                "gaps": len(rows),
                "classes": dict(counts),
                "implementation": dict(impl_counts),
                "cv_selection_matches_frozen": True,
                "protected_hashes_unchanged": True,
                "test_evaluation_count": 1,
                "verify_only": verify_only,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def make_report(catalog, rows, evidence, selected, baseline, result, frozen, counts, impl_counts):
    doi = "https://doi.org/" + catalog["doi"]
    lines = [
        "# Kiểm toán Research Gap — BRFSS2015-Statistical-Methods",
        "Ngày kiểm toán: 06/11/2026, múi giờ Asia/Bangkok. Báo cáo này đối chiếu bằng chứng bài gốc, mã đã có và kết quả đã đóng băng; không chạy lại nghiên cứu.",
        "## Kết luận chính",
        "Không có bằng chứng rằng dự án đã giải quyết toàn bộ các gap của Chang hoặc vượt Chang trên một benchmark tương thích. Có ba hạng mục được xử lý **trong phạm vi dự án**: quy trình CV/selection trước test (C08), CI và paired comparison có giới hạn (C09), và original-data survey inference (C12). Chúng không tương đương ba chứng minh ưu thế so với bài báo.",
        "Hai nhận định phải bác bỏ: Chang chỉ dùng accuracy (C06) và Chang không có train/test holdout (C07). Bài đã có SMOTE, PCA, sensitivity và RF; vì vậy cũng không được nói bài không xử lý imbalance, không feature selection, không xét minority detection hoặc hoàn toàn không có ensemble. Leakage thực thi vẫn chỉ là HYPOTHESIS (C04).",
        "Thêm thuật toán là mở rộng thực nghiệm, không tự tạo novelty. Trong quick real-data CV, các ensemble không thắng mô hình LR được chọn. Calibration, macro-F1, precision và accuracy của selected policy kém comparator mặc dù sensitivity/balanced accuracy tăng. Chưa có faithful Chang reproduction, external/temporal validation, full real standard/extended run, SHAP, ADASYN ensemble hay clinical/privacy experiment.",
        "## 1. Phạm vi, nguồn và quy tắc phân loại",
        f"Bài được đối chiếu: {catalog['paper']} DOI: [{catalog['doi']}]({doi}). Đã đọc bản typeset 14 trang, do tác giả đăng qua ResearchGate; DOI, tiêu đề, tác giả và journal khớp trang 1. Đây là bản PDF bài gốc được lưu lại, không phải PDF do dự án tái tạo. Không khẳng định đã so byte-for-byte với publisher download vì truy cập trực tiếp publisher bị chặn.",
        f"Nguồn tải: [author-posted PDF]({catalog['source_url']}). Bản lưu: [Chang_2022_100118.pdf](evidence/literature/Chang_2022_100118.pdf). SHA256: `{catalog['pdf_sha256']}`. Trang PDF 1–14 trùng số trang in. Không dùng số trang suy từ HTML/search snippets.",
        "Nguồn nội bộ rà soát: reports/final_report.md, reports/RESULTS_INTERPRETATION.md, docs/LITERATURE_REVIEW.md, docs/RESEARCH_GAP_MATRIX.md, docs/literature_evidence.csv, RESEARCH_PROTOCOL, EXPERIMENT_PLAN, SCIENTIFIC_AUDIT, configs và src tương ứng. Hướng tương lai chỉ tìm thấy khi đọc đầy đủ bài được gắn origin riêng C18–C20; không coi đó là cam kết cũ của dự án.",
        "**VERIFIED**: phát biểu hẹp được nội dung bài xác nhận, gồm cả bất nhất báo cáo hoặc hướng future work. **PARTIALLY_VERIFIED**: một phần có bằng chứng nhưng chưa đủ kết luận hạn chế toàn bộ quy trình. **UNVERIFIED**: gap chưa có căn cứ; nếu có phản chứng thì ghi rõ CONTRADICTED. **HYPOTHESIS**: cơ chế/giải thích cần kiểm chứng. `evidence_classification=VERIFIED_PDF_CONTENT` chỉ xác nhận đã đọc đúng trích đoạn, không biến nghi vấn gap thành VERIFIED.",
        "Trạng thái triển khai độc lập với độ tin cậy gap: ADDRESSED_WITHIN_SCOPE = có code và empirical outputs cho mục tiêu được giới hạn; PARTIALLY_ADDRESSED = thiếu bước hoặc chưa chứng minh tác dụng; NOT_TESTED = chưa có empirical validation tương ứng; NOT_IMPLEMENTED/OUT_OF_SCOPE = chưa có phương pháp; NOT_A_VALIDATED_GAP = gap bị bác bỏ, không được tính là đã giải quyết. Kiểm thử synthetic chỉ chứng minh vận hành, không chứng minh lợi ích thực tế.",
        "## 2. Toàn bộ danh mục và trạng thái",
        "| ID | Gap/phát biểu được audit | Phân loại gap | Trạng thái dự án |",
        "|---|---|---|---|",
    ]
    for g in rows:
        lines.append(
            f"| [{g['gap_id']}](#{g['gap_id'].lower()}) | {g['gap']} | {g['gap_classification']} | {g['implementation_status']} |"
        )
    lines.extend(
        [
            "Phân bố phân loại: "
            + ", ".join(f"{k}: {v}" for k, v in counts.items())
            + ". Phân bố triển khai: "
            + ", ".join(f"{k}: {v}" for k, v in impl_counts.items())
            + ".",
            "### Các hạng mục đã xử lý với giới hạn",
            "C08: quy trình quick CV/selection/holdout có bằng chứng và trace. C09: paired CI cho selected và comparator đã đóng băng; bootstrap chỉ conditional respondents. C12: inference weighted/design-based trên cohort gốc, với numerical R reference. Không mục nào chứng minh rằng toàn bộ quy trình Chang đã được sửa hoặc paper benchmark bị vượt.",
            "### Các hạng mục chưa hoàn tất hoặc chưa thử nghiệm",
            "C01–C05, C10–C11, C13–C16 và C21 mới xử lý một phần. C17 chưa external/temporal validation. C18 chưa ADASYN ensemble. C19 và C20 chưa có dữ liệu/phương pháp clinical/genetic hoặc federated/privacy và ngoài phạm vi hiện tại. C06–C07 bị phản chứng, không thuộc danh sách thành tích.",
            "## 3. Ngân hàng bằng chứng trực tiếp từ bài gốc",
            "Các trích ngắn dưới đây là bằng chứng dùng chung cho các gap; mỗi chi tiết gap ở mục 4 nêu DOI, section, trang và mã E tương ứng. Với phát biểu về thứ không được báo cáo, phạm vi rà soát được chỉ rõ, không dùng sự vắng một từ khóa làm bằng chứng duy nhất.",
            "| Mã | Mục/bảng | Trang in = PDF | Trích nguyên văn ngắn |",
            "|---|---|---|---|",
        ]
    )
    for e in evidence.values():
        lines.append(f"| {e['evidence_id']} | {e['section']} | {e['pdf_page']} | “{e['quote']}” |")
    lines.extend(
        [
            "**Sửa nguồn dẫn cũ:** §3.2 là EDA, còn §3.3 mới là Data pre-processing (trang 4). Table 2 (trang 6) đã nêu RF random_state=42, LR random_state=0, KNN k=3, DT max_depth=50/entropy. Chưa đủ settings để exact reproduction nhưng không còn hợp lệ khi đánh dấu toàn bộ seeds/hyperparameters UNVERIFIED. Table 3 thiếu split trong pseudocode, song §3.3 nói partition trước model; phải giữ cả hai khi bàn leakage.",
            "**Phạm vi negative evidence:** Table 4 (trang 12) chỉ có point metrics và không có CI/paired tests; §3.4, §4.3, Table 4/Fig.19 không trình bày calibration; §3.1/§3.4/Table A.1 không mô tả survey-design variance. Không suy thành tác giả chắc chắn chưa làm bất kỳ thủ tục đó trong code không công khai. Nhận định “không kiểm soát survey” là mở rộng mục tiêu inference, không tự động là lỗi của một bài prediction.",
            "## 4. Đối chiếu chi tiết từng gap với code và thực nghiệm",
        ]
    )
    for g in rows:
        es = "; ".join(
            f"{eid}: tr. {evidence[eid]['pdf_page']}, §/bảng {evidence[eid]['section']}"
            for eid in g["evidence_ids"]
        )
        artifacts = "; ".join(f"`{p}`" for p in g["artifact_paths"])
        lines.extend(
            [
                f'<a id="{g["gap_id"].lower()}"></a>\n\n### {g["gap_id"]} — {g["gap"]}',
                f"**Nguồn:** DOI [{catalog['doi']}]({doi}); mục {g['paper_sections']}; trang "
                + ", ".join(map(str, g["paper_pages"]))
                + f". Bằng chứng: {es}; nội dung trích ở mục 3.",
                f"**Phân loại:** {g['gap_classification']}. **Kết luận về phát biểu:** {g['claim_verdict']}. {g['evidence_interpretation']}",
                f"**Đã triển khai:** {g['implemented_method']}\n\n**Artifacts:** {artifacts}.",
                f"**Kết quả thực tế:** {g['observed_result']}",
                f"**Trạng thái:** {g['implementation_status']}. **Phần còn thiếu:** {g['remaining_work']}",
            ]
        )
    lines.extend(
        [
            "## 5. Kết quả đã đóng băng và những gì có thể kết luận",
            "Dataset A: 441.456 records/330 columns. Cohort binary 422.558; complete case inference 243.529. Prediction split: 338.046 training-pool, capped 4.000 cho quick; final test 84.512. Dự án dùng 19 raw predictors được định nghĩa riêng, khác processed feature/cohort/label của Chang. Full real core-three inference có output; three-class prediction chỉ được xác minh synthetic.",
            f"Selected policy đã đóng băng: `{frozen['experiment']['model']}`, `{frozen['experiment']['imbalance']}`, threshold {frozen['threshold']:.2f}; CV BA {frozen['cv_mean']:.6f}. Comparator là unweighted same-cohort LR, threshold 0,50, không phải reproduction RF của Chang. Training-CV unweighted LR ở threshold đã chọn 0,20 có BA 0,719743; điều đó khác baseline cố định 0,50 dùng trong final comparison.",
            "| Metric test đã lưu | Selected | Fixed baseline | Hiệu selected − baseline |",
            "|---|---|---|---|",
        ]
    )
    for k in [
        "accuracy",
        "balanced_accuracy",
        "sensitivity",
        "specificity",
        "precision",
        "f1",
        "macro_f1",
        "roc_auc",
        "pr_auc",
        "brier",
        "log_loss",
    ]:
        lines.append(
            f"| {k} | {selected[k]:.6f} | {baseline[k]:.6f} | {selected[k] - baseline[k]:+.6f} |"
        )
    delta = result["paired_difference_ci"]["balanced_accuracy"]
    lines.extend(
        [
            f"Δ BA = {selected['balanced_accuracy'] - baseline['balanced_accuracy']:.6f}, paired conditional bootstrap 95% CI [{delta['lower']:.6f}; {delta['upper']:.6f}], {delta['valid_replicates']} replicates. Đây là hiệu hai **policies** cùng cohort, không cô lập tác động class weighting vì threshold cũng khác. Không có test comparison với unweighted LR được threshold-tune tương đương; audit không tính thêm comparison đó từ test đã mở.",
            "ROC-AUC tăng rất nhỏ (khoảng 0,001115), không phải bước nhảy về discrimination. Precision, accuracy, specificity, macro-F1, PR-AUC, Brier và log loss đi theo hướng kém hơn. Binary-positive F1 tăng nhưng macro-F1 giảm; không được dùng từ improved F1 không chỉ rõ định nghĩa. Brier/log loss càng thấp càng tốt. Không gọi calibration gap đã giải quyết chỉ vì đã tạo calibration plot.",
            "Selected accuracy 67,47% không đạt target 82,26%. Baseline nội bộ accuracy 87,21% cũng không chứng minh vượt Chang vì cohort/outcome/evaluation khác. Chang RF sensitivity 80,45% không thể so trực tiếp với 85,51% của dự án. CI predictive là respondent bootstrap conditional trên fixed models, không bao gồm selection/training uncertainty hay complex-survey prediction uncertainty; chỉ 100 replicates quick nên precision Monte Carlo còn hạn chế.",
            "Lưu ý feature count: trường k=10 trong experiment original là tham số không được dùng để cắt features; RankingSelector(original) giữ toàn bộ cột sau encoding. Chỉ MI/L1/tree k=10 thực sự chọn 10 encoded columns; không gọi original là bộ 10 biến gốc.",
            "## 6. Đóng góp khoa học thực sự và mức độ mới",
            "1. **Bằng chứng thực nghiệm có giới hạn:** so sánh một operating policy đã chọn bằng CV với comparator định trước trên cùng holdout cho thấy minority detection/BA tăng, đồng thời specificity, PPV và calibration giảm. Kết quả tradeoff này có giá trị báo cáo; không phải thuật toán mới hoặc clinical-utility validation.",
            "2. **Phân tích dịch tễ đã thực thi:** weighted prevalence và adjusted prevalence OR/RRR cùng design variance; BMI OR 1,8754 (CI 1,7936–1,9610) và các sensitivity đã có. Đây là ước lượng associational cho một domain xác định. Không có systematic novelty review đủ chứng minh phát hiện BMI/diabetes là mới; không có causal inference.",
            "3. **Giá trị phương pháp và reproducibility:** protocol cố định, fold-local preprocessing, survey score covariance có numerical R reference, frozen artifacts và ledger. Đây là chất lượng nghiên cứu/engineering được chứng minh trong dự án; không phải một estimator mới hay bằng chứng quy trình không công khai của Chang chắc chắn sai.",
            "4. **Forensic literature clarification:** xác minh bất nhất cohort/label, sửa section references và metadata tham số từ PDF, đồng thời bác bỏ các gap bị gán quá mức. Đây là kết quả audit có chứng cứ; chưa tái dựng được pipeline của tác giả.",
            "5. **Chưa phải đóng góp đã chứng minh:** thêm XGBoost/LightGBM/CatBoost/voting/stacking; SHAP chưa có; ADASYN/federated/genetic data chưa có; top-k full real chưa chạy; superiority so với paper, external validity và calibration improvement chưa chứng minh. Negative CV findings của ensemble được giữ nguyên, không chọn lại theo final test.",
            "## 7. Integrity và giới hạn audit",
            "Audit chỉ đọc PDF, source/config, development logs và final artifacts đã lưu. Winner và threshold được kiểm lại bằng **training-CV scores**, rồi so với frozen.json trước khi đọc final_metrics để mô tả. Không fit/refit, predict, resample, tính metrics lại từ test rows, tìm threshold từ test, hoặc chạy final_evaluate. Final test ledger vẫn evaluation_count=1. SHA256 source/config, frozen models, splits, CV indices, result JSON, checkpoints và ledger được so trước/sau; xem evidence/research_gap_audit_provenance.json.",
            "Ledger/hash cho thấy artifacts nhất quán và audit không sửa chúng; không phải bằng chứng tuyệt đối về mọi truy cập thủ công trong quá khứ. Full-cohort inference có trước prediction split, nên các lựa chọn prediction chỉ có thể xem là prespecified theo protocol/metadata; audit không dựng một preregistration công khai có timestamp độc lập.",
            "Permutation importance là exploratory trên training-internal split sau khi model class đã được chọn bằng development; không phải independent confirmatory explanation evaluation. Với permutation selector, preprocessing của outer training được thực hiện trước internal split; outer validation vẫn ở ngoài fold, nhưng không nên tuyên bố mọi inner validation hoàn toàn không dùng thông tin preprocessing của inner holdout.",
            "Không chạy thêm ML để lấp gap sau khi đã xem test. Các bước tương lai phải có kế hoạch training/validation trước, giữ công khai lịch sử test cũ; đổi output folder/split trên cùng respondents không tự tạo external test độc lập.",
            "## 8. Tệp đối chiếu và cách kiểm lại",
            "- [research_gap_evidence.csv](research_gap_evidence.csv): 21 rows, DOI/section/pages/quotes, classification, implementation, result và phần còn thiếu. Bản cùng nội dung ở project-root research_gap_evidence.csv.",
            "- docs/chang_gap_catalog.json: danh mục machine-readable; PDF bản lưu giữ nguyên và source SHA256.",
            "- reports/evidence/research_gap_audit_provenance.json: protected artifacts, source identity và kết quả kiểm không đổi model/test.",
            "- `python scripts/audit_research_gaps.py --verify-only`: xác minh quotes trong đúng trang PDF, paths, CSV, hashes và selection từ training CV; không chạy mô hình hoặc test evaluation.",
        ]
    )
    rendered = "\n\n".join(lines) + "\n"
    rendered = re.sub(r"(\|[^\n]*\|)\n\n(?=\|)", r"\1\n", rendered)
    (ROOT / "reports/RESEARCH_GAP_AUDIT.md").write_text(rendered)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify-only", action="store_true")
    audit(**vars(p.parse_args()))
