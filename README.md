# Report Data Validation & Reconciliation Framework

> ## ⚠️ SYNTHETIC DATA
> **All data in this repository is SYNTHETIC** (generated, seed 42). No real Snowflake, Power BI, customer, or financial data is used anywhere. Numbers below are real outputs from running the harness on that synthetic data.

**Snowflake · dbt · SQL · Excel** — a masters-level portfolio project by Sadhana Donepudi (M.S. Data Analytics, UIS, 4.0 GPA) reproducing the resume claim: *25 data tests — grain checks, null/duplicate detection, and Power BI totals vs Snowflake source reconciliation within 0.01%* — plus a data dictionary and a comprehensive user training guide.

## Overview
Two-layer validation: a clean Snowflake-style **source** layer and a Power BI **report** layer with deliberately injected defects (nulls, duplicate keys, orphan FKs, out-of-range values, total drift). The framework declares 25 dbt-style tests, executes all 25 in a Python harness against CSVs, and asserts in pytest that detected defect counts exactly match the ground-truth manifest.

## Architecture
```
data/ (SYNTHETIC CSVs, seed 42)
  source_customers/products/orders/payments.csv   <- clean ledger (expected PASS)
  report_customers/products/orders/payments.csv   <- report layer + injected defects
  manifest.json                                   <- machine-readable ground truth
models/ (dbt-style)
  staging/stg_source_*.sql, marts/rpt_*.sql, schema.yml (20 generic tests)
tests/
  assert_*.sql (5 singular tests) + test_validations.py (pytest)
src/
  generate_data.py  -> writes CSVs + docs/injected_defects.md from ground truth
  run_validations.py-> executes all 25 checks -> outputs/validation_report.md
docs/
  test_catalog.md (exactly 25) · data_dictionary.md · user_training_guide.md · injected_defects.md
outputs/validation_report.md (real harness output)
```

## How to run
```bash
# Python: use the project venv (system pandas may be broken)
/home/hatch/.venv-baird/bin/python src/generate_data.py      # regenerate synthetic data + manifest
/home/hatch/.venv-baird/bin/python src/run_validations.py    # execute 25 tests -> outputs/validation_report.md
/home/hatch/.venv-baird/bin/python -m pytest tests/test_validations.py -v
```
dbt declarations are provided for Snowflake/dbt adoption (`dbt_project.yml`, `models/schema.yml`, `tests/*.sql`); the Python harness is the executable reference implementation for the CSV seeds.

## The 25 tests (programmatic count: 20 generic + 5 singular = 25)
Generic (schema.yml): source grain/null/relationships/accepted-values (Tests 1–10, expected PASS) and report grain/null/relationships (Tests 11–20, expected FAIL where defects injected). Singular (tests/*.sql): quantity > 0 (21), order_amount ≥ 0 (22), payment_amount > 0 (23), orders reconciliation within 0.01% (24), payments reconciliation within 0.01% (25). Full catalog: `docs/test_catalog.md`. Count verified in code (`run_validations.py` asserts `len(results) == 25`; pytest `test_counts_programmatic` recounts schema + SQL files).

## RESULTS — actual harness output (seed 42, real numbers)
Executed by `src/run_validations.py`:

- **Total tests: 25 — PASS: 11, FAIL: 14**
- Source layer (Tests 1–10): **all PASS** (source is clean by construction)
- Report grain/null/orphan/range tests (11–23): **all FAIL with exactly the injected counts** — duplicate extra rows: customers 2, products 1, orders 4, payments 2; nulls: customer_name 3, category 2, order customer_id 5, payment_amount 3; orphans: customer 3, product 2; out-of-range: quantity ≤0 = 4, negative order_amount = 3, negative payment_amount = 2
- Reconciliation (0.01% threshold):
  - Orders: source $655,327.30 vs report $656,082.32 — diff $755.02 (**0.1152%**) → **FAIL** (exceeds 0.01%)
  - Payments: source $655,327.30 vs report $655,282.36 — diff -$44.94 (**0.0069%**) → **PASS** (correctly under threshold; duplicates still caught by grain Test 19)
- Pytest: **7 passed** — asserts exactly-25, source clean, every defect count equals `data/manifest.json` / `docs/injected_defects.md`, and reconciliation drift/threshold flagging.

Full per-test table: `outputs/validation_report.md`. Ground truth: `docs/injected_defects.md`.

## Docs
- `docs/data_dictionary.md` — every table/column, type, grain, source
- `docs/user_training_guide.md` — comprehensive business-user guide (TOC, concepts, reading the report, workflows, triage playbook, FAQ, exercises)
- `docs/test_catalog.md` — the exact 25
- `docs/injected_defects.md` — every injected defect with exact counts (generated, never hand-edited)

## Reproducibility note
Resume claim reproduced by construction: exactly 25 tests and 0.01% reconciliation are asserted in code. One nuance reported honestly: on seed-42 synthetic data the *payments* reconciliation PASSes (0.0069% < 0.01%) because injected duplicates/negatives partially net out — the framework still catches those defects via grain/null tests, and the threshold logic is proven on both sides (orders FAIL at 0.1152%). No metrics are invented; every number above is harness/manifest output.
