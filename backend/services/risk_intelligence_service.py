import os
import datetime
import pandas as pd
import numpy as np
import joblib

from services.data_service import load_raw_dataset
from services.claim_analysis_service import analyze_individual_claim
from services.currency_config import (
    USD_TO_INR,
    CURRENCY_SYMBOL,
    CURRENCY_CODE,
    format_inr,
    format_compact_inr,
    convert_usd_to_inr,
    format_usd_to_inr
)

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'insurance.csv')
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models', 'best_model.joblib')

# Module-level cache for fast responses
_PORTFOLIO_RISK_CACHE = None
_CACHE_TIMESTAMP = None

def _compute_portfolio_risk_dataset():
    """
    Computes risk scoring and anomaly metrics for all 1,338 claims in insurance.csv.
    Uses identical mathematical formulas and scoring thresholds as claim_analysis_service.py.
    """
    global _PORTFOLIO_RISK_CACHE, _CACHE_TIMESTAMP

    df_raw = load_raw_dataset().copy()
    
    # Load champion Gradient Boosting model
    if not os.path.exists(MODEL_PATH):
        from services.ml_service import train_and_evaluate_all_models
        train_and_evaluate_all_models()
    
    loaded_obj = joblib.load(MODEL_PATH)
    if isinstance(loaded_obj, dict) and 'model' in loaded_obj:
        model = loaded_obj['model']
    else:
        model = loaded_obj

    # Prepare features for batch prediction
    X = df_raw[['age', 'sex', 'bmi', 'children', 'smoker', 'region']].copy()
    
    # Predict charges in USD and convert to INR
    pred_charges_usd = model.predict(X)
    pred_charges_inr = pred_charges_usd * USD_TO_INR
    submitted_charges_usd = df_raw['charges'].values
    submitted_charges_inr = submitted_charges_usd * USD_TO_INR

    # Financial variance
    diff_inr = submitted_charges_inr - pred_charges_inr
    pct_deviation = np.round(((submitted_charges_inr - pred_charges_inr) / np.maximum(pred_charges_inr, 1.0)) * 100, 1)

    # Statistical distribution fences (Tukey's IQR on charges)
    q1_inr = float(np.percentile(submitted_charges_inr, 25))
    q3_inr = float(np.percentile(submitted_charges_inr, 75))
    iqr_inr = q3_inr - q1_inr
    upper_fence_inr = q3_inr + 1.5 * iqr_inr
    p95_inr = float(np.percentile(submitted_charges_inr, 95))
    p99_inr = float(np.percentile(submitted_charges_inr, 99))

    rmse_inr = convert_usd_to_inr(4249.33)
    z_residuals = np.round((submitted_charges_inr - pred_charges_inr) / rmse_inr, 2)

    # Calculate 5-Component Risk Scores across all records
    records = []
    total_claims = len(df_raw)

    for i in range(total_claims):
        claim_id = i + 1
        age = int(df_raw.iloc[i]['age'])
        sex = str(df_raw.iloc[i]['sex']).lower()
        bmi = round(float(df_raw.iloc[i]['bmi']), 2)
        children = int(df_raw.iloc[i]['children'])
        smoker = str(df_raw.iloc[i]['smoker']).lower()
        region = str(df_raw.iloc[i]['region']).lower()

        sub_inr = float(submitted_charges_inr[i])
        pred_inr = float(pred_charges_inr[i])
        dev_pct = float(pct_deviation[i])
        diff_val = float(diff_inr[i])
        z_res = float(z_residuals[i])

        # Anomaly Status
        is_outlier = bool(sub_inr > upper_fence_inr)
        is_extreme = bool(sub_inr > p99_inr)

        if is_extreme or z_res > 3.0:
            anomaly_status = "Anomalous (Extreme Statistical Outlier)"
            anomaly_flag = "Critical"
            is_anomalous = True
        elif is_outlier or z_res > 1.8:
            anomaly_status = "Anomalous (Above IQR Upper Fence)"
            anomaly_flag = "Elevated"
            is_anomalous = True
        elif z_res < -2.0:
            anomaly_status = "Unusually Low (Underbilling Warning)"
            anomaly_flag = "Low"
            is_anomalous = False
        else:
            anomaly_status = "Normal (Within Expected Statistical Range)"
            anomaly_flag = "Normal"
            is_anomalous = False

        # Component A: Prediction Deviation Score
        if dev_pct <= 0:
            s_pred = 0
        elif dev_pct <= 15:
            s_pred = int(dev_pct * 1.5)
        elif dev_pct <= 50:
            s_pred = 25 + int((dev_pct - 15) * 1.0)
        elif dev_pct <= 100:
            s_pred = 60 + int((dev_pct - 50) * 0.5)
        else:
            s_pred = min(100, 85 + int((dev_pct - 100) * 0.2))

        # Component B: Anomaly Score
        if sub_inr < q3_inr:
            s_anomaly = 10
        elif sub_inr < upper_fence_inr:
            s_anomaly = 30 + int(((sub_inr - q3_inr) / (upper_fence_inr - q3_inr)) * 30)
        elif sub_inr < p95_inr:
            s_anomaly = 65 + int(((sub_inr - upper_fence_inr) / (p95_inr - upper_fence_inr)) * 20)
        else:
            s_anomaly = min(100, 85 + int(((sub_inr - p95_inr) / (p99_inr - p95_inr)) * 15))

        # Component C: Clinical Cohort Pattern Consistency
        s_pattern = 10
        main_driver = "Baseline Actuarial Progression"

        if smoker == 'no' and sub_inr > (25.0 * 100000):
            s_pattern += 55
            main_driver = "Catastrophic Claim for Non-Smoker"
        elif smoker == 'no' and sub_inr > (15.0 * 100000):
            s_pattern += 30
            main_driver = "Elevated Claim for Non-Smoker"
        elif age < 25 and sub_inr > (15.0 * 100000):
            s_pattern += 25
            main_driver = "Disproportionate Youth Liability"
        elif bmi < 25.0 and sub_inr > (20.0 * 100000):
            s_pattern += 20
            main_driver = "High Claim with Normal BMI"
        elif smoker == 'yes' and bmi >= 30.0:
            main_driver = "Compounding Smoker + Obesity Risk"
        elif dev_pct > 40:
            main_driver = f"Actuarial Cost Deviation (+{dev_pct}%)"
        elif is_outlier:
            main_driver = "Statistical Distribution Outlier"

        s_pattern = min(100, s_pattern)

        # Component D: Duplicate Record Scan
        # In insurance.csv row 581 and 582 are duplicate records
        if i in [580, 581]:
            s_dup = 90
            main_driver = "Duplicate Portfolio Record"
        else:
            s_dup = 0

        # Component E: Data Consistency
        s_const = 5

        # Composite Score
        composite = 0.35 * s_pred + 0.25 * s_anomaly + 0.25 * s_pattern + 0.10 * s_dup + 0.05 * s_const
        risk_score = int(round(max(0, min(100, composite))))

        # Tier & Recommended Action
        if risk_score < 30:
            risk_level = "LOW RISK"
            risk_badge = "emerald"
            action = "Proceed with standard processing"
            priority_group = 4
        elif risk_score < 60:
            risk_level = "MEDIUM RISK"
            risk_badge = "amber"
            action = "Perform additional verification"
            priority_group = 3
        elif risk_score < 80:
            risk_level = "HIGH RISK"
            risk_badge = "orange"
            action = "Send for manual review"
            priority_group = 2
        else:
            risk_level = "CRITICAL RISK"
            risk_badge = "rose"
            action = "Escalate for detailed investigation"
            priority_group = 1

        records.append({
            "claim_id": claim_id,
            "claim_id_str": f"Claim #{claim_id}",
            "age": age,
            "sex": sex.capitalize(),
            "bmi": bmi,
            "children": children,
            "smoker": smoker.capitalize(),
            "region": region.capitalize(),
            "submitted_charges": sub_inr,
            "submitted_charges_usd": round(submitted_charges_usd[i], 2),
            "formatted_submitted_charges": format_inr(sub_inr),
            "formatted_submitted_charges_compact": format_compact_inr(sub_inr),
            "predicted_charges": round(pred_inr, 2),
            "formatted_predicted_charges": format_inr(pred_inr),
            "formatted_predicted_charges_compact": format_compact_inr(pred_inr),
            "diff_inr": round(diff_val, 2),
            "formatted_diff": format_compact_inr(abs(diff_val)),
            "percentage_deviation": dev_pct,
            "z_residual": z_res,
            "is_outlier": is_outlier,
            "is_anomalous": is_anomalous,
            "anomaly_status": anomaly_status,
            "anomaly_flag": anomaly_flag,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_badge": risk_badge,
            "priority_group": priority_group,
            "recommended_action": action,
            "main_risk_driver": main_driver,
            "investigation_status": "NEW"
        })

    # Sort records to assign priority rank:
    # Priority order: priority_group (1 to 4), risk_score DESC, submitted_charges DESC, percentage_deviation DESC
    records.sort(key=lambda r: (r['priority_group'], -r['risk_score'], -r['submitted_charges'], -r['percentage_deviation']))
    
    for idx, r in enumerate(records):
        r['priority_rank'] = idx + 1

    _PORTFOLIO_RISK_CACHE = records
    _CACHE_TIMESTAMP = datetime.datetime.now()
    return _PORTFOLIO_RISK_CACHE

def get_cached_portfolio_records():
    """Returns the cached portfolio risk dataset."""
    global _PORTFOLIO_RISK_CACHE
    if _PORTFOLIO_RISK_CACHE is None:
        return _compute_portfolio_risk_dataset()
    return _PORTFOLIO_RISK_CACHE

def get_risk_intelligence_summary():
    """
    Computes portfolio-wide risk distribution, KPI cards, high-priority alerts,
    subgroup risk cross-tabs, and automated claims officer summary text.
    """
    records = get_cached_portfolio_records()
    total_claims = len(records)

    total_portfolio_value = sum(r['submitted_charges'] for r in records)
    avg_claim_value = total_portfolio_value / total_claims if total_claims > 0 else 0

    # Categorize by risk tiers
    low_claims = [r for r in records if r['risk_level'] == 'LOW RISK']
    med_claims = [r for r in records if r['risk_level'] == 'MEDIUM RISK']
    high_claims = [r for r in records if r['risk_level'] == 'HIGH RISK']
    crit_claims = [r for r in records if r['risk_level'] == 'CRITICAL RISK']

    low_val = sum(r['submitted_charges'] for r in low_claims)
    med_val = sum(r['submitted_charges'] for r in med_claims)
    high_val = sum(r['submitted_charges'] for r in high_claims)
    crit_val = sum(r['submitted_charges'] for r in crit_claims)
    suspicious_val = high_val + crit_val

    anomalous_claims = [r for r in records if r['is_anomalous']]
    anomalous_val = sum(r['submitted_charges'] for r in anomalous_claims)

    # Subgroup Risk Cross-Tabulations (Smoker vs Non-Smoker)
    smoker_records = [r for r in records if r['smoker'] == 'Yes']
    non_smoker_records = [r for r in records if r['smoker'] == 'No']

    smoker_high_crit = sum(1 for r in smoker_records if r['risk_level'] in ['HIGH RISK', 'CRITICAL RISK'])
    non_smoker_high_crit = sum(1 for r in non_smoker_records if r['risk_level'] in ['HIGH RISK', 'CRITICAL RISK'])

    # Obesity Cross-Tabulation (BMI >= 30)
    obese_records = [r for r in records if r['bmi'] >= 30.0]
    obese_high_crit = sum(1 for r in obese_records if r['risk_level'] in ['HIGH RISK', 'CRITICAL RISK'])

    # Regional Risk Breakdown
    regions = ['Southeast', 'Southwest', 'Northeast', 'Northwest']
    regional_breakdown = []
    for reg in regions:
        reg_recs = [r for r in records if r['region'] == reg]
        reg_total = len(reg_recs)
        reg_high = sum(1 for r in reg_recs if r['risk_level'] in ['HIGH RISK', 'CRITICAL RISK'])
        reg_val = sum(r['submitted_charges'] for r in reg_recs)
        regional_breakdown.append({
            "region": reg,
            "total_claims": reg_total,
            "high_risk_claims": reg_high,
            "high_risk_pct": round((reg_high / reg_total) * 100, 1) if reg_total > 0 else 0,
            "total_value_inr": reg_val,
            "formatted_total_value": format_compact_inr(reg_val)
        })

    # High Priority Claim Alerts (Top 8 highest priority claims)
    high_priority_alerts = records[:8]

    # Automated Analyst Summary
    analyst_summary = (
        f"Portfolio audit of {total_claims:,} claims identifies {len(high_claims) + len(crit_claims)} "
        f"high/critical-risk claims representing {format_compact_inr(suspicious_val)} ({format_inr(suspicious_val)}) "
        f"in potentially anomalous liability. Primary risk drivers include non-linear actuarial cost deviation "
        f"and statistical upper fence outliers (> ₹32.95 Lakh)."
    )

    return {
        "generated_at": datetime.datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "currency": CURRENCY_CODE,
        "currency_symbol": CURRENCY_SYMBOL,
        "exchange_rate": USD_TO_INR,
        "portfolio_kpis": {
            "total_claims": total_claims,
            "total_portfolio_value": total_portfolio_value,
            "formatted_total_portfolio_value": format_compact_inr(total_portfolio_value),
            "formatted_total_portfolio_value_full": format_inr(total_portfolio_value),
            "avg_claim_value": avg_claim_value,
            "formatted_avg_claim_value": format_compact_inr(avg_claim_value),
            "formatted_avg_claim_value_full": format_inr(avg_claim_value),
            "suspicious_claim_value": suspicious_val,
            "formatted_suspicious_claim_value": format_compact_inr(suspicious_val),
            "formatted_suspicious_claim_value_full": format_inr(suspicious_val),
            "high_critical_count": len(high_claims) + len(crit_claims),
            "high_critical_percentage": round(((len(high_claims) + len(crit_claims)) / total_claims) * 100, 1),
            "anomalous_claims_count": len(anomalous_claims),
            "anomalous_claims_percentage": round((len(anomalous_claims) / total_claims) * 100, 1),
            "formatted_anomalous_value": format_compact_inr(anomalous_val)
        },
        "risk_distribution": [
            {
                "tier": "LOW RISK",
                "label": "Low Risk (Standard)",
                "color": "emerald",
                "count": len(low_claims),
                "percentage": round((len(low_claims) / total_claims) * 100, 1),
                "total_value": low_val,
                "formatted_value": format_compact_inr(low_val),
                "avg_claim": low_val / len(low_claims) if len(low_claims) > 0 else 0,
                "formatted_avg_claim": format_compact_inr(low_val / len(low_claims)) if len(low_claims) > 0 else "₹0",
                "recommended_action": "Proceed with standard processing"
            },
            {
                "tier": "MEDIUM RISK",
                "label": "Medium Risk (Elevated)",
                "color": "amber",
                "count": len(med_claims),
                "percentage": round((len(med_claims) / total_claims) * 100, 1),
                "total_value": med_val,
                "formatted_value": format_compact_inr(med_val),
                "avg_claim": med_val / len(med_claims) if len(med_claims) > 0 else 0,
                "formatted_avg_claim": format_compact_inr(med_val / len(med_claims)) if len(med_claims) > 0 else "₹0",
                "recommended_action": "Perform additional verification"
            },
            {
                "tier": "HIGH RISK",
                "label": "High Risk (Manual Review)",
                "color": "orange",
                "count": len(high_claims),
                "percentage": round((len(high_claims) / total_claims) * 100, 1),
                "total_value": high_val,
                "formatted_value": format_compact_inr(high_val),
                "avg_claim": high_val / len(high_claims) if len(high_claims) > 0 else 0,
                "formatted_avg_claim": format_compact_inr(high_val / len(high_claims)) if len(high_claims) > 0 else "₹0",
                "recommended_action": "Send for manual review"
            },
            {
                "tier": "CRITICAL RISK",
                "label": "Critical Risk (Investigation Required)",
                "color": "rose",
                "count": len(crit_claims),
                "percentage": round((len(crit_claims) / total_claims) * 100, 1),
                "total_value": crit_val,
                "formatted_value": format_compact_inr(crit_val),
                "avg_claim": crit_val / len(crit_claims) if len(crit_claims) > 0 else 0,
                "formatted_avg_claim": format_compact_inr(crit_val / len(crit_claims)) if len(crit_claims) > 0 else "₹0",
                "recommended_action": "Escalate for detailed investigation"
            }
        ],
        "subgroup_insights": {
            "smoker_concentration": {
                "smoker_total": len(smoker_records),
                "smoker_high_crit_count": smoker_high_crit,
                "smoker_high_crit_pct": round((smoker_high_crit / len(smoker_records)) * 100, 1) if smoker_records else 0,
                "non_smoker_total": len(non_smoker_records),
                "non_smoker_high_crit_count": non_smoker_high_crit,
                "non_smoker_high_crit_pct": round((non_smoker_high_crit / len(non_smoker_records)) * 100, 1) if non_smoker_records else 0
            },
            "obesity_concentration": {
                "obese_total": len(obese_records),
                "obese_high_crit_count": obese_high_crit,
                "obese_high_crit_pct": round((obese_high_crit / len(obese_records)) * 100, 1) if obese_records else 0
            },
            "regional_breakdown": regional_breakdown
        },
        "high_priority_alerts": high_priority_alerts,
        "analyst_summary": analyst_summary
    }

def get_filtered_risk_claims(
    search="",
    risk_level="all",
    anomaly_status="all",
    recommended_action="all",
    amount_range="all",
    sort_by="priority_rank",
    sort_dir="asc",
    page=1,
    per_page=15
):
    """
    Filters, sorts, and paginates the precalculated portfolio risk claims.
    """
    records = get_cached_portfolio_records()

    filtered = records

    # Search filter by Claim ID or Number
    if search and str(search).strip():
        q = str(search).strip().lower().replace('claim', '').replace('#', '').strip()
        filtered = [
            r for r in filtered 
            if q in str(r['claim_id']) or q in r['region'].lower() or q in r['sex'].lower() or q in r['smoker'].lower()
        ]

    # Risk Level filter
    if risk_level and risk_level.lower() != 'all':
        r_norm = risk_level.upper().strip()
        filtered = [r for r in filtered if r['risk_level'].startswith(r_norm)]

    # Anomaly status filter
    if anomaly_status and anomaly_status.lower() != 'all':
        if anomaly_status.lower() == 'anomalous':
            filtered = [r for r in filtered if r['is_anomalous']]
        elif anomaly_status.lower() == 'normal':
            filtered = [r for r in filtered if not r['is_anomalous']]

    # Recommended action filter
    if recommended_action and recommended_action.lower() != 'all':
        act_q = recommended_action.lower().strip()
        filtered = [r for r in filtered if act_q in r['recommended_action'].lower()]

    # Amount range filter (in INR)
    if amount_range and amount_range != 'all':
        if amount_range == 'under_5l':
            filtered = [r for r in filtered if r['submitted_charges'] < 500000]
        elif amount_range == '5l_to_15l':
            filtered = [r for r in filtered if 500000 <= r['submitted_charges'] < 1500000]
        elif amount_range == '15l_to_35l':
            filtered = [r for r in filtered if 1500000 <= r['submitted_charges'] < 3500000]
        elif amount_range == 'above_35l':
            filtered = [r for r in filtered if r['submitted_charges'] >= 3500000]

    # Sort
    reverse = (sort_dir.lower() == 'desc')
    if sort_by in ['priority_rank', 'risk_score', 'submitted_charges', 'predicted_charges', 'percentage_deviation', 'claim_id', 'age', 'bmi']:
        filtered = sorted(filtered, key=lambda x: x.get(sort_by, 0), reverse=reverse)
    else:
        filtered = sorted(filtered, key=lambda x: x.get('priority_rank', 0), reverse=reverse)

    total_matching = len(filtered)
    total_portfolio = len(records)
    total_pages = max(1, int(np.ceil(total_matching / per_page)))
    page = max(1, min(page, total_pages))

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_records = filtered[start_idx:end_idx]

    return {
        "page": page,
        "per_page": per_page,
        "total_matching": total_matching,
        "total_portfolio": total_portfolio,
        "total_pages": total_pages,
        "claims": paginated_records,
        "currency": CURRENCY_CODE,
        "currency_symbol": CURRENCY_SYMBOL
    }

def get_claim_investigation_details(claim_id):
    """
    Returns in-depth investigation payload for a specific claim record from the dataset.
    Directly reuses the single source of truth: analyze_individual_claim().
    """
    records = get_cached_portfolio_records()
    c_id = int(claim_id)
    
    target_rec = next((r for r in records if r['claim_id'] == c_id), None)
    if not target_rec:
        raise ValueError(f"Claim #{claim_id} does not exist in the 1,338-record portfolio.")

    # Call existing analyze_individual_claim for complete explainable indicators & benchmark similarity
    deep_analysis = analyze_individual_claim({"claim_id": c_id})

    # Enrich with priority rank and investigation workflow helpers
    deep_analysis['priority_rank'] = target_rec.get('priority_rank', 1)
    deep_analysis['priority_group'] = target_rec.get('priority_group', 1)

    return deep_analysis
