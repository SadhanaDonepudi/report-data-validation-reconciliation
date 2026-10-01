# User Training Guide — Report Data Validation & Reconciliation Framework

> **SYNTHETIC DATA NOTICE**: Every example, number, and screenshot description in this guide uses synthetic data. In production you would point the same framework at your real Snowflake and Power BI datasets.

---

## Table of Contents
1. Welcome & Who This Guide Is For
2. Why Report Validation Matters (Business Story)
3. Key Concepts in Plain Language
4. The Two Layers: Snowflake Source vs Power BI Report
5. What the 25 Tests Actually Check
6. How to Read the Validation Report (Step by Step)
7. Daily / Weekly Workflows
8. Investigating a FAIL: Triage Playbook
9. Reconciliation Explained: The 0.01% Rule
10. Grain, Duplicates, and Why They Break Totals
11. Nulls, Orphans, and Out-of-Range Values
12. Working With Excel Exports
13. Roles & Responsibilities
14. FAQ
15. Hands-On Exercises
16. Glossary
17. Getting Help & Escalation
18. Appendix: Test Catalog Summary

---

## 1. Welcome & Who This Guide Is For
This guide is for business users, report consumers, analysts, and managers who rely on Power BI dashboards that are fed from Snowflake. You do **not** need to write SQL to use this guide. By the end you will be able to open the validation report, tell in under two minutes whether a dashboard is safe to trust today, and know exactly who to call and what to say when something fails.

If you are a data engineer, you will also find the mapping from business language ("the total looks wrong") to technical checks (grain, relationships, reconciliation) useful when you triage with stakeholders.

## 2. Why Report Validation Matters (Business Story)
Imagine the Monday sales review. The Power BI total says $656,082 but Finance's Snowflake extract says $655,327. The difference is only $755 — 0.12% — small enough to wave away, large enough to hide eight inflated orders, three negative amounts, and four duplicated orders that will double-count revenue if someone exports to Excel and sums again. Without automated checks, that meeting spends forty minutes arguing about whose number is right. With this framework, the validation report already answered it before the meeting started: Test 24 failed, the drift is 0.1152%, and the injected-defect log tells you precisely which categories to inspect.

Validation is not about distrusting people; it is about distrusting silent transformations. Every refresh, join, and filter is a place where a row can duplicate, a key can orphan, or a total can drift. The 25 tests are seatbelts: most days they pass quietly, and on the day they matter, they save the decision.

## 3. Key Concepts in Plain Language
- **Grain**: what one row means. "One row per order" is a grain. If grain breaks (duplicates), every sum double-counts.
- **Primary key**: the column that should be unique at that grain (`order_id` for orders).
- **Null**: a missing value. A null customer on an order means you cannot attribute revenue.
- **Orphan / relationship failure**: a child row points to a parent that does not exist (an order for CUST-999 when there is no such customer).
- **Out-of-range**: a value outside business reality (quantity 0 or −5, negative amounts).
- **Reconciliation**: comparing an independent total in the report layer to the source total and flagging drift beyond tolerance (0.01%).
- **Threshold**: the allowed wiggle room. 0.01% means on a $655k total, about $65 of rounding/ timing difference is tolerated; anything more is investigated.

## 4. The Two Layers: Snowflake Source vs Power BI Report
Think of Snowflake as the warehouse ledger and Power BI as the published newspaper. The ledger (source) should be clean: 100 customers, 20 products, 500 orders, 500 payments in our synthetic example. The newspaper (report) re-publishes the same facts for fast dashboards. If the newspaper reprints a page twice (duplicates), leaves names blank (nulls), cites people who do not exist (orphans), or misprints totals (drift), readers make bad decisions. Our tests check the ledger itself (Tests 1–10, expected PASS) and then check the newspaper against the ledger (Tests 11–25).

## 5. What the 25 Tests Actually Check
Tests are grouped so you can scan by question:
- *"Is the source trustworthy today?"* → Tests 1–10.
- *"Did the report layer duplicate or drop keys?"* → Unique/grain tests 11, 13, 15, 19.
- *"Are required fields missing?"* → Not-null tests 12, 14, 16, 20.
- *"Do report rows point at real parents?"* → Relationship tests 17–18 (and source 7–8).
- *"Are values in the allowed domain?"* → Accepted-values 3, 10 and singular range tests 21–23.
- *"Do the money totals tie out?"* → Reconciliation 24–25.

The full catalog with purpose, layer, and expected behavior lives in `docs/test_catalog.md`. You never need to memorize numbers; the report prints them.

## 6. How to Read the Validation Report (Step by Step)
Open `outputs/validation_report.md` (or the HTML your team publishes from it).

**Step 1 — Look at the header.** It states total tests (25), PASS count, FAIL count. In the synthetic run: *PASS 11, FAIL 14*. That sounds alarming until you remember the report layer was deliberately broken for training; in production, report FAILs are your work queue.

**Step 2 — Check the source block first (Tests 1–10).** If any source test fails, stop: do not debug the dashboard, debug ingestion. In our run all 10 pass, so the ledger is sound.

**Step 3 — Scan the FAIL rows and their Failures count.** The count is literal: Test 12 shows 3 failures = 3 null customer names, matching the defect manifest. You can quote that number in a ticket without opening a database.

**Step 4 — Read reconciliation (Tests 24–25) last.** These summarize money impact. Test 24: source $655,327.30 vs report $656,082.32, diff 0.1152% → FAIL because it exceeds 0.01%. Test 25: diff 0.0069% → PASS, correctly under threshold, teaching you that a PASS does not mean "no defects" (payments still have duplicates caught by Test 19); it means "totals tie within tolerance."

**Step 5 — Decide**: All PASS = publish. Any FAIL = hold publication, file a ticket with test number, name, and failures count, and link the report.

## 7. Daily / Weekly Workflows
**Daily (5 minutes, report publisher)**: run/refresh validations after the morning load, confirm source PASS, count report FAILs vs yesterday, publish only if FAIL count is zero or waived in writing by the data owner.

**Weekly (30 minutes, analyst + business owner)**: review trend of failures, clear orphan queues, confirm reconciliation diff % is trending to zero, close tickets whose fixes are verified by a re-run showing PASS.

**Monthly**: review thresholds (is 0.01% still right?), review accepted-values lists (new segment? new payment method?), archive reports.

## 8. Investigating a FAIL: Triage Playbook
1. Note test number/name/failures from the report.
2. Look up the test in `docs/test_catalog.md` for purpose and expected behavior.
3. Check `docs/injected_defects.md` in training, or your incident log in production, for whether this failure was expected (a known load issue).
4. Ask: is it grain (unique), completeness (not_null), integrity (relationships), domain (accepted/range), or money (reconciliation)? Each has a different owner: ingestion, modeling, or source-system team.
5. Quantify business impact using the report's detail (e.g., reconciliation diff $ and %).
6. File the ticket with those exact numbers; attach the report; assign; re-run after fix and confirm PASS before closing. Never close on "should be fixed" — close on a PASS.

## 9. Reconciliation Explained: The 0.01% Rule
Reconciliation answers "does the report's money equal the source's money?" We sum `order_amount` in both layers, compute `|report − source| / source × 100`, and compare to 0.01%. Why not zero? Real pipelines have rounding and late-arriving rows; 0.01% gives a small, explicit tolerance instead of informal shrugging. Why so tight? Because 0.1% of a large revenue base is material. In training, orders drift 0.1152% (FAIL — investigate) while payments drift 0.0069% (PASS — monitor, but other tests still catch payment duplicates). That contrast is the lesson: reconciliation is necessary, not sufficient.

## 10. Grain, Duplicates, and Why They Break Totals
If `order_id` ORD-0010 appears twice in the report, a dashboard SUM will count it twice even though the bar chart looks normal. Unique tests count *extra rows* (total − distinct). Test 15 reports 4 extra rows = 4 duplicated orders. Fix pattern: find the join or append that duplicated, add a distinct/grain guard, reload, re-run until extra = 0.

## 11. Nulls, Orphans, and Out-of-Range Values
- **Nulls** (Tests 12, 14, 16, 20): filter the report to the failing column IS NULL, count, and trace to source — was it null upstream or introduced by a left join?
- **Orphans** (Tests 17–18): list child FKs not in the parent; CUST-999/998/997 and PROD-99/98 in training are textbook orphans from a bad lookup.
- **Out-of-range** (Tests 21–23): quantity ≤ 0 and negative amounts are never valid sales; quarantine those rows and check the entry system, not just the report.

## 12. Working With Excel Exports
Many users export Power BI tables to Excel. Validation still helps: before you share a workbook, check the validation report date matches your export date, confirm grain tests PASS (otherwise your Excel SUM will double-count duplicates the same way Power BI would), and include the source total and diff % from Tests 24–25 as a cover-note. Never "fix" a workbook by deleting duplicate rows manually without filing a ticket — the next refresh will reintroduce them.

## 13. Roles & Responsibilities
- **Business user**: reads report, holds publication on FAIL, files ticket with test numbers.
- **Report publisher / analyst**: runs validations, triages first line, owns re-run proof.
- **Data engineering**: fixes ingestion/modeling defects, maintains tests and thresholds.
- **Data owner**: approves waivers and threshold changes in writing.

## 14. FAQ
**Q: All source tests PASS but report tests FAIL — what broke?** The transformation/publish step, not the ledger. Start with the earliest report FAIL.
**Q: Reconciliation PASSes but a unique test FAILs — is the dashboard safe?** No. Totals can net out (duplicates + negatives cancel). Grain failures still corrupt row-level exports.
**Q: Can we raise the threshold to 0.5% to make it PASS?** Only with data-owner approval and a written rationale; raising a threshold to silence a failure hides drift.
**Q: What if a test fails intermittently?** Treat as FAIL; intermittent usually means late data or a race in refresh order. Log timestamps.
**Q: Do I need dbt to read results?** No. The Python harness writes a plain Markdown report; dbt files document the same tests for engineering.

## 15. Hands-On Exercises
**Exercise 1 (5 min)**: Open the validation report, find Test 15, state in one sentence how many extra order rows exist and why that matters. *Answer: 4 extra duplicates; sums double-count them.*
**Exercise 2 (10 min)**: Using Tests 24–25, write the two reconciliation sentences you would paste into a Monday meeting note, including $ and %.
**Exercise 3 (15 min)**: Pick any report FAIL, look it up in the test catalog, and draft a ticket title in the form `[Test 17] 3 orphan customer_ids in report_orders — hold publication`.
**Exercise 4 (discussion)**: Payments reconciliation PASSes (0.0069%) yet Test 19 FAILs. Explain to a partner why you still hold the payments visual.

## 16. Glossary
See Section 3; plus **dbt** (data build tool — the SQL test framework these tests are declared in), **Snowflake** (source warehouse), **Power BI** (report layer), **manifest** (ground-truth defect log), **harness** (the Python runner that executes all 25 checks on CSVs).

## 17. Getting Help & Escalation
Start with the report and catalog. If source tests fail, escalate to data engineering with the report attached. If only report tests fail, escalate to the report publisher. If reconciliation fails beyond 0.1% or source fails at all, hold external publication and notify the data owner the same day.

## 18. Appendix: Test Catalog Summary
25 tests = 20 dbt generic (unique/not_null/relationships/accepted_values in `models/schema.yml`) + 5 singular SQL (`tests/*.sql`): quantity positive, order amount nonnegative, payment amount positive, orders reconciliation, payments reconciliation. Full table: `docs/test_catalog.md`. Ground truth defects: `docs/injected_defects.md`. Column definitions: `docs/data_dictionary.md`.

---
*End of guide. You are now able to read the validation report, triage a FAIL, and explain the 0.01% reconciliation rule to any stakeholder. When in doubt: source first, grain second, money last — and never publish on a FAIL without a written waiver.*
