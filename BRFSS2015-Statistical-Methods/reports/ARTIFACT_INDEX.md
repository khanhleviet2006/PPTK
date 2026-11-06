# Artifact index

- final_report.md: canonical original-data binary empirical report draft.
- tables/: canonical inference, sensitivity, development and evaluation tables.
- figures/: canonical original-data figures.
- evidence/: machine-readable empirical results, audit/cohort metadata, frozen selection, run manifest and test-access ledger.
- notebook_execution_verified/: all 13 notebooks executed twice, each repetition using a fresh kernel and the same checkpoint directory.
- VERIFICATION.md and execution_status.md: actual validation scope and commands.
- logs/: retained validation and real-data execution logs.

Detailed split IDs/checksums, CV indices, OOF caches, model binaries and source signatures remain in runs/real_final_quick in the working repository and are not included in the source archive. Re-running with the same original source and seed reconstructs the split; the canonical split checksum is retained in evidence/split_summary.json. Raw CDC data are external, not committed or packaged. Download provenance/fingerprints are in docs/source_manifest.json.

Other runs/ directories record pre-final development or synthetic validation. Their own manifests identify the executed version. The earlier runs/real_quick contains no final-test evaluation. Canonical empirical test access is recorded only in runs/real_final_quick/test_access.json. Do not present synthetic or superseded artifacts as new epidemiological results.

Research-gap audit update: reports/RESEARCH_GAP_AUDIT.md and reports/research_gap_evidence.csv are the authoritative claim-level audit; project-root research_gap_evidence.csv is an identical convenience copy. docs/chang_gap_catalog.json records 21 claim/direction definitions, and reports/evidence/literature/Chang_2022_100118.pdf preserves the unchanged author-posted original article. Source provenance and protected before/after hashes are in reports/evidence/research_gap_audit_provenance.json. Canonical-run reports and checkpoints remain untouched; the published report and literature documents received an editorial audit correction.

Current post-audit release: FINAL_RESEARCH_REPORT.md, RESEARCH_GAP_EXECUTION_MATRIX.md, research_gap_execution_matrix.csv, and detailed comparison/feasibility reports. Canonical binary run: runs/gap_real_quick_v4. Core-three run: runs/gap_real_three_v3, with matching archived engine. Temporal source/freeze: runs/temporal_2017 and recovery_versions/temporal_v1.py. Use the COMPLETE research ZIP for the protected legacy bundle; earlier source-only exports do not contain it.
