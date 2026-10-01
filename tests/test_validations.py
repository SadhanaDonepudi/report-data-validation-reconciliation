"""Pytest: harness detects exactly the injected defects (SYNTHETIC DATA)."""
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "src"))

import run_validations  # noqa: E402

@pytest.fixture(scope="module")
def results():
    return run_validations.main()

@pytest.fixture(scope="module")
def manifest():
    return json.loads((BASE / "data" / "manifest.json").read_text())

def by_name(results):
    return {r["name"]: r for r in results}

def test_exactly_25_tests(results):
    assert len(results) == 25
    assert [r["id"] for r in results] == list(range(1, 26))

def test_source_layer_clean(results):
    src = [r for r in results if r["layer"] == "Source"]
    assert len(src) == 10
    for r in src:
        assert r["status"] == "PASS", r
        assert r["failures"] == 0, r

def test_report_defects_match_manifest(results, manifest):
    m = manifest["defects"]
    r = by_name(results)
    assert r["unique_rpt_customers_customer_id"]["failures"] == m["report_customers_duplicate_customer_id_extra_rows"]
    assert r["not_null_rpt_customers_customer_name"]["failures"] == m["report_customers_null_customer_name"]
    assert r["unique_rpt_products_product_id"]["failures"] == m["report_products_duplicate_product_id_extra_rows"]
    assert r["not_null_rpt_products_category"]["failures"] == m["report_products_null_category"]
    assert r["unique_rpt_orders_order_id"]["failures"] == m["report_orders_duplicate_order_id_extra_rows"]
    assert r["not_null_rpt_orders_customer_id"]["failures"] == m["report_orders_null_customer_id"]
    assert r["relationships_rpt_orders_customer_id"]["failures"] == m["report_orders_orphan_customer_id"]
    assert r["relationships_rpt_orders_product_id"]["failures"] == m["report_orders_orphan_product_id"]
    assert r["unique_rpt_payments_payment_id"]["failures"] == m["report_payments_duplicate_payment_id_extra_rows"]
    assert r["not_null_rpt_payments_payment_amount"]["failures"] == m["report_payments_null_payment_amount"]
    assert r["assert_report_orders_quantity_positive"]["failures"] == m["report_orders_out_of_range_quantity_le_zero"]
    assert r["assert_report_orders_amount_nonnegative"]["failures"] == m["report_orders_negative_order_amount"]
    assert r["assert_report_payments_amount_positive"]["failures"] == m["report_payments_negative_payment_amount"]

def test_reconciliation_orders_fails_threshold(results, manifest):
    gt = manifest["reconciliation_ground_truth"]
    r = by_name(results)["assert_reconciliation_orders_total_within_threshold"]
    assert abs(r["diff_pct"] - gt["orders_diff_pct"]) < 0.01
    assert gt["orders_diff_pct"] > 0.01
    assert r["status"] == "FAIL"

def test_reconciliation_payments_threshold_logic(results, manifest):
    gt = manifest["reconciliation_ground_truth"]
    r = by_name(results)["assert_reconciliation_payments_total_within_threshold"]
    assert abs(r["diff_pct"] - gt["payments_diff_pct"]) < 0.01
    expected = "PASS" if gt["payments_diff_pct"] <= 0.01 else "FAIL"
    assert r["status"] == expected

def test_reconciliation_direct_recompute():
    so = pd.read_csv(BASE / "data" / "source_orders.csv")
    ro = pd.read_csv(BASE / "data" / "report_orders.csv")
    pct = abs(ro["order_amount"].sum() - so["order_amount"].sum()) / so["order_amount"].sum() * 100
    assert pct > 0.01  # injected drift must exceed threshold

def test_counts_programmatic():
    # 20 generic in schema.yml + 5 singular sql = 25
    schema = (BASE / "models" / "schema.yml").read_text()
    # count generic test entries: lines with "- unique" / "- not_null" etc at test level
    generic = schema.count("- unique") + schema.count("- not_null") + schema.count("- relationships:") + schema.count("- accepted_values:")
    singular = len(list((BASE / "tests").glob("*.sql")))
    assert generic == 20, generic
    assert singular == 5, singular
    assert generic + singular == 25
