# Running the repaired master notebook

Use a fresh Colab session with Python 3.10–3.12 (tested here: Linux Python 3.12.14). Download/update the entire project, not just the notebook. The previous missing `src/data` files are now tracked; old ZIP exports do not contain this fix.

Open `notebooks/00_Run_All_Colab.ipynb`. The first code cell mounts Drive and searches bounded project locations, including the user's folder with spaces. To explicitly select this installation, run the following before Run all:

```python
import os
os.environ['BRFSS_REPO'] = '/content/drive/MyDrive/PPTK-main (1)/PPTK-main/BRFSS2015-Statistical-Methods'
os.environ['BRFSS_DATA'] = '/content/drive/MyDrive/Diabetes_Statistics_2015/01_Raw_Data/LLCP2015XPT.zip'
os.environ['BRFSS_PROTOCOL'] = 'NEW_PROTOCOL'
os.environ['BRFSS_PROFILE'] = 'quick'
# Optional: local audited CDC codebook. Without it, only the recorded CDC PDF
# is downloaded and its exact SHA256 verified before use.
# os.environ['BRFSS_CODEBOOK'] = '/path/to/codebook15_llcp.pdf'
```

Run all. Dependencies are installed with the current kernel's Python; NumPy 2.0.2 is accepted. If already-imported binary package versions changed during installation, restart the session and Run all again. Changing Python outside the supported range requires revalidation, not removal of the guard. Set `BRFSS_INSTALL_OPTIONAL=0` to omit booster/extension installation; unavailable model dependencies are explicitly marked skipped. Core dependencies remain required.

The ZIP is read through the shared validated loader. Only a unique LLCP2015.XPT member is extracted into `/content/brfss_xpt/<archive_sha256>/`; trailing spaces in the original member name are normalized. Traversal, symlinks, bad CRC, invalid XPORT headers and oversized members fail. A cached extraction is reused only after its digest matches the archive manifest. Data are never replaced with a different dataset. Real-data audit still requires 441,456 records, 330 source columns, valid respondent IDs, outcome and survey design variables, weights and codebook evidence.

## Protocols

`NEW_PROTOCOL` is the default. It uses the existing full core pipeline: data audit, cohort, descriptive survey statistics, design-based inference and sensitivity analyses, deterministic split, training/CV candidate selection, frozen models/thresholds, one prespecified test batch and a report. Output defaults to `REPO/runs/new_protocol_2015` on persistent Drive. `protocol.json` declares seed, selection criterion and scientific scope; `run_manifest.json` records source/code hashes and versions; `split.json` records train/test IDs, cohort/test checksums and seed. Test fraction is prespecified in config. All learned prediction preprocessing, feature selection and SMOTENC are fitted in training folds. Candidate and threshold choice use training OOF predictions only. CV scores used to select candidates/thresholds are optimistic development scores, not unbiased final performance. No split is selected using final-test results.

Historical test overlap is UNKNOWN unless independently audited against the old bundle. A new internal holdout is not external validation of models already developed on BRFSS 2015. Do not claim it is a reconstruction, proof of improvement over Chang, or pristine validation of previously published results. The advanced post-audit experiment grid remains the legacy development workflow; NEW_PROTOCOL runs the core predefined experiments and does not pretend to reproduce all 21 historical gap experiments.

`LEGACY_RESUME` requires the complete preserved bundle and its original code/config hashes, frozen model hashes and one-time evaluation ledger to pass the existing independent audit. A missing split or any other protected artifact fails with a list; nothing is generated to impersonate a historical checkpoint. The original split was recoverable locally from the pre-extension archive, but no Git commit ever contained it, and publishing that split alone would not restore the full legacy state. Use the original complete bundle in a separate installation for historical work. Updating source can correctly cause its original-code hash audit to fail; do not bypass this check.

Resume the same protocol with identical configuration and output path. Changed signatures require a separate output directory. An interrupted test access ledger fails closed. Do not delete or overwrite it. New runs cannot write into named historical output directories. Outputs and checkpoints use atomic writes and hash validation; Drive remote synchronization still merits backups.

## Verification limits

See `reports/COLAB_REPAIR_AUDIT.md` and `reports/colab_repair_validation/`. The complete master was executed twice in clean kernels on a source-only checkout without legacy runs. Actual hosted Colab execution remains **COLAB_RUNTIME_NOT_VERIFIED**. The real CDC ZIP passed audit, descriptive statistics, inference and development in Linux; its final holdout was not accessed for this repair. No claim of a complete real-data Run all PASS is made.

The verifier validates the complete active project dependency closure. Global pip conflicts from unrelated Colab applications are displayed separately; missing or incompatible study dependencies still stop execution. This does not relax data, survey-design, split or test-access validation.
