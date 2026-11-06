# Verified CDC variable dictionary and coding audit

Primary documents (retrieved 2026-11-06):
- https://www.cdc.gov/brfss/annual_data/annual_2015.html (441,456 records; 330 XPT columns).
- https://www.cdc.gov/brfss/annual_data/2015/pdf/codebook15_llcp.pdf (137 numbered pages, August 23, 2016).
- https://www.cdc.gov/brfss/questionnaires/pdf-ques/2015-brfss-questionnaire-12-29-14.pdf
- https://www.cdc.gov/brfss/questionnaires/modules/state2015.htm
- https://www.cdc.gov/brfss/questionnaires/modules/category2015.htm

The archive member has a trailing space (`LLCP2015.XPT `); normalize this when extracting. The data loader checks the XPORT header. File hashes identify the exact locally inspected release; they are integrity fingerprints rather than an independent CDC cryptographic signature. Codebook name validation is automated; code semantics are reviewed in this document and configs/variables.yaml.

| Variable | Meaning / valid coding | Missing or special handling |
|---|---|---|
| DIABETE3 | 1 yes; 2 pregnancy-only; 3 no; 4 borderline/prediabetes | 7 unknown;9 refused;blank missing; numbered p21 |
| PREDIAB1 | 1 yes;2 pregnancy-only;3 no | Optional module, unknown/refused/not asked excluded; DIABETE3=4 automatically yes, p50 |
| _LLCPWT | Final combined landline/cell weight | Must be finite positive; no imputation |
| _STSTR / _PSU | Stratum / primary sampling unit | Nest PSU inside stratum; retain full design for domains |
| _STATE / SEQNO | State / annual sequence | SEQNO is unique within state, not nationally; composite respondent ID |
| _AGEG5YR | 1–13 ordered age groups, 18–24 through 80+ | 14 unknown; categorical |
| SEX | 1 male;2 female | Survey recorded sex |
| _BMI5 | BMI with two implied decimal places | blank; retain codebook numerical range 1–9999; plausibility requires sensitivity |
| EDUCA | 1–6 education | 9 refused, blank |
| INCOME2 | 1–8 income categories | 77 unknown;99 refused,blank |
| _RACE | 1–8 race/ethnicity grouping | 9 unknown/refused; not continuous |
| BPHIGH4 | 1 hypertension;2 pregnancy-only;3 no;4 borderline | 7/9/blank missing; all four categories retained |
| TOLDHI2 | 1 yes;2 no high cholesterol | 7/9/blank; skipped/unscreened not a confirmed negative |
| _SMOKER3 | 1 daily;2 some days;3 former;4 never | 9 unknown/refused |
| EXERANY2 | 1 yes;2 no past-month exercise | 7/9/blank |
| _FRUTSUM / _VEGESUM | Consumption frequency/day, scale by .01 | blank; codebook pp122–123; nutrition is frequency, not weighed servings |
| _DRNKWEK | Alcohol drinks/week, scale by .01 | 99900 unknown/refused/missing; p119 |
| GENHLTH | 1 excellent through 5 poor | 7/9/blank |
| PHYSHLTH / MENTHLTH | 1–30 unhealthy days | 88 means zero;77/99 missing; retain 7 and 9 as valid days |
| HLTHPLN1 | 1 insured;2 uninsured | 7/9/blank |
| MEDCOST | 1 cost prevented care;2 no | 7/9/blank |
| CHECKUP1 | 1–4 time since checkup;8 never | 7/9/blank |

All derived feature code is deterministic. No universal '7/9 is missing' rule is used. Calculated BMI/alcohol/nutrition scales were cross-checked against observed values and codebook. No record with unavailable PREDIAB1 is called a confirmed prediabetes negative. Optional module analyses across questionnaire versions require additional files and version weights; this repository does not silently substitute the core weight for them.
