import os
import datetime
import pandas as pd
import numpy as np
import joblib

from services.data_service import load_raw_dataset
from services.prediction_service import predict_insurance_claim
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

def get_curated_sample_claims():
    """Returns curated representative claims from the dataset with distinct risk profiles."""
    df = load_raw_dataset().copy()
    
    samples = [
        {
            "id": 2,
            "label": "Claim #2 — Routine Low-Risk Beneficiary",
            "tag": "Standard Low Risk",
            "age": int(df.iloc[1]['age']),
            "sex": str(df.iloc[1]['sex']),
            "bmi": round(float(df.iloc[1]['bmi']), 2),
            "children": int(df.iloc[1]['children']),
            "smoker": str(df.iloc[1]['smoker']),
            "region": str(df.iloc[1]['region']),
            "charges_usd": round(float(df.iloc[1]['charges']), 2),
            "charges_inr": round(convert_usd_to_inr(df.iloc[1]['charges']), 2),
            "formatted_charges": format_inr(convert_usd_to_inr(df.iloc[1]['charges'])),
            "formatted_charges_compact": format_compact_inr(convert_usd_to_inr(df.iloc[1]['charges'])),
            "profile_summary": "18y male, normal dependent profile, non-smoker."
        },
        {
            "id": 15,
            "label": "Claim #15 — Obese Smoker Claim",
            "tag": "Expected High Severity",
            "age": int(df.iloc[14]['age']),
            "sex": str(df.iloc[14]['sex']),
            "bmi": round(float(df.iloc[14]['bmi']), 2),
            "children": int(df.iloc[14]['children']),
            "smoker": str(df.iloc[14]['smoker']),
            "region": str(df.iloc[14]['region']),
            "charges_usd": round(float(df.iloc[14]['charges']), 2),
            "charges_inr": round(convert_usd_to_inr(df.iloc[14]['charges']), 2),
            "formatted_charges": format_inr(convert_usd_to_inr(df.iloc[14]['charges'])),
            "formatted_charges_compact": format_compact_inr(convert_usd_to_inr(df.iloc[14]['charges'])),
            "profile_summary": "27y male, BMI 42.1 (severe obesity), active smoker."
        },
        {
            "id": 578,
            "label": "Claim #578 — Obese Smoker Claim",
            "tag": "Severe Liability Outlier",
            "age": int(df.iloc[577]['age']),
            "sex": str(df.iloc[577]['sex']),
            "bmi": round(float(df.iloc[577]['bmi']), 2),
            "children": int(df.iloc[577]['children']),
            "smoker": str(df.iloc[577]['smoker']),
            "region": str(df.iloc[577]['region']),
            "charges_usd": round(float(df.iloc[577]['charges']), 2),
            "charges_inr": round(convert_usd_to_inr(df.iloc[577]['charges']), 2),
            "formatted_charges": format_inr(convert_usd_to_inr(df.iloc[577]['charges'])),
            "formatted_charges_compact": format_compact_inr(convert_usd_to_inr(df.iloc[577]['charges'])),
            "profile_summary": f"{int(df.iloc[577]['age'])}y {str(df.iloc[577]['sex'])}, BMI {round(float(df.iloc[577]['bmi']), 1)}, active smoker ({str(df.iloc[577]['region']).capitalize()})."
        },
        {
            "id": 1301,
            "label": "Claim #1301 — Catastrophic Upper Outlier",
            "tag": "Top 0.5% Outlier",
            "age": int(df.iloc[1300]['age']),
            "sex": str(df.iloc[1300]['sex']),
            "bmi": round(float(df.iloc[1300]['bmi']), 2),
            "children": int(df.iloc[1300]['children']),
            "smoker": str(df.iloc[1300]['smoker']),
            "region": str(df.iloc[1300]['region']),
            "charges_usd": round(float(df.iloc[1300]['charges']), 2),
            "charges_inr": round(convert_usd_to_inr(df.iloc[1300]['charges']), 2),
            "formatted_charges": format_inr(convert_usd_to_inr(df.iloc[1300]['charges'])),
            "formatted_charges_compact": format_compact_inr(convert_usd_to_inr(df.iloc[1300]['charges'])),
            "profile_summary": "45y male smoker, claim exceeding ₹59 Lakh."
        },
        {
            "id": 582,
            "label": "Claim #582 — Duplicate Policy Audit Example",
            "tag": "Duplicate Portfolio Record",
            "age": int(df.iloc[581]['age']),
            "sex": str(df.iloc[581]['sex']),
            "bmi": round(float(df.iloc[581]['bmi']), 2),
            "children": int(df.iloc[581]['children']),
            "smoker": str(df.iloc[581]['smoker']),
            "region": str(df.iloc[581]['region']),
            "charges_usd": round(float(df.iloc[581]['charges']), 2),
            "charges_inr": round(convert_usd_to_inr(df.iloc[581]['charges']), 2),
            "formatted_charges": format_inr(convert_usd_to_inr(df.iloc[581]['charges'])),
            "formatted_charges_compact": format_compact_inr(convert_usd_to_inr(df.iloc[581]['charges'])),
            "profile_summary": "19y female, exact demographic match with Claim #581."
        }
    ]
    return samples

def analyze_individual_claim(claim_input):
    """
    Comprehensive claim analysis and risk intelligence calculation.
    
    Parameters:
    claim_input (dict): {
        'claim_id': int (optional),
        'age': int,
        'sex': 'female' | 'male',
        'bmi': float,
        'children': int,
        'smoker': 'yes' | 'no',
        'region': 'northeast' | 'northwest' | 'southeast' | 'southwest',
        'submitted_charges': float (in INR)
    }
    """
    df_raw = load_raw_dataset().copy()
    
    # 1. Parse and validate inputs
    claim_id = claim_input.get('claim_id')
    
    if claim_id and (isinstance(claim_id, int) or (isinstance(claim_id, str) and str(claim_id).isdigit())):
        c_idx = int(claim_id) - 1
        if 0 <= c_idx < len(df_raw):
            row = df_raw.iloc[c_idx]
            age = int(row['age'])
            sex = str(row['sex']).lower()
            bmi = float(row['bmi'])
            children = int(row['children'])
            smoker = str(row['smoker']).lower()
            region = str(row['region']).lower()
            # If user didn't provide custom charges, use record's actual charges
            if 'submitted_charges' in claim_input and claim_input['submitted_charges'] is not None and str(claim_input['submitted_charges']).strip() != '':
                submitted_charges_inr = float(claim_input['submitted_charges'])
            else:
                submitted_charges_inr = convert_usd_to_inr(row['charges'])
        else:
            claim_id = None
    
    if not claim_id or not (0 <= (int(claim_id) - 1) < len(df_raw)):
        age = int(claim_input.get('age', 35))
        sex = str(claim_input.get('sex', 'female')).lower().strip()
        bmi = float(claim_input.get('bmi', 28.0))
        children = int(claim_input.get('children', 0))
        smoker = str(claim_input.get('smoker', 'no')).lower().strip()
        region = str(claim_input.get('region', 'southeast')).lower().strip()
        submitted_charges_inr = float(claim_input.get('submitted_charges', 100000.0))

    # Basic boundary constraints
    age = max(18, min(64, age))
    bmi = max(15.0, min(55.0, round(bmi, 2)))
    children = max(0, min(5, children))
    sex = 'male' if sex == 'male' else 'female'
    smoker = 'yes' if smoker == 'yes' else 'no'
    if region not in ['northeast', 'northwest', 'southeast', 'southwest']:
        region = 'southeast'
    submitted_charges_inr = max(1000.0, round(submitted_charges_inr, 2))

    # 2. Execute existing ML Model Prediction
    ml_pred = predict_insurance_claim(age, sex, bmi, children, smoker, region)
    predicted_charges_inr = ml_pred['predicted_charges']
    predicted_charges_usd = ml_pred['predicted_charges_usd']
    submitted_charges_usd = round(submitted_charges_inr / USD_TO_INR, 2)
    
    # 3. Variance & Deviation Calculation
    diff_inr = round(submitted_charges_inr - predicted_charges_inr, 2)
    pct_deviation = round(((submitted_charges_inr - predicted_charges_inr) / predicted_charges_inr) * 100, 1)

    # 4. Statistical Distribution & Outlier Checks (Tukey's IQR Fences)
    charges_all_inr = df_raw['charges'] * USD_TO_INR
    q1_inr = float(charges_all_inr.quantile(0.25))
    q3_inr = float(charges_all_inr.quantile(0.75))
    iqr_inr = q3_inr - q1_inr
    upper_fence_inr = float(q3_inr + 1.5 * iqr_inr) # ~32.95 Lakh
    p95_inr = float(charges_all_inr.quantile(0.95)) # ~38.2 Lakh
    p99_inr = float(charges_all_inr.quantile(0.99)) # ~46.3 Lakh

    rmse_inr = convert_usd_to_inr(4249.33) # Champion Gradient Boosting RMSE in INR (~4.05 Lakh)
    residual_inr = submitted_charges_inr - predicted_charges_inr
    z_residual = round(residual_inr / rmse_inr, 2)

    is_outlier = bool(submitted_charges_inr > upper_fence_inr)
    is_extreme_outlier = bool(submitted_charges_inr > p99_inr)

    if is_extreme_outlier or z_residual > 3.0:
        anomaly_status = "Anomalous (Extreme Statistical Outlier)"
        anomaly_flag = "Critical"
    elif is_outlier or z_residual > 1.8:
        anomaly_status = "Anomalous (Above IQR Upper Fence)"
        anomaly_flag = "Elevated"
    elif z_residual < -2.0:
        anomaly_status = "Unusually Low (Underbilling Warning)"
        anomaly_flag = "Low"
    else:
        anomaly_status = "Normal (Within Expected Statistical Range)"
        anomaly_flag = "Normal"

    # 5. Duplicate & Similar Claims Search across Portfolio
    # Exact demographic match
    exact_matches = df_raw[
        (df_raw['age'] == age) &
        (df_raw['sex'] == sex) &
        (np.abs(df_raw['bmi'] - bmi) <= 0.05) &
        (df_raw['children'] == children) &
        (df_raw['smoker'] == smoker) &
        (df_raw['region'] == region)
    ]
    
    exact_duplicate_found = False
    matching_duplicate_ids = []
    
    if len(exact_matches) > 0:
        for m_idx, m_row in exact_matches.iterrows():
            m_id = m_idx + 1
            if claim_id is not None and m_id == int(claim_id):
                continue
            matching_duplicate_ids.append(m_id)
            # If charges are identical within 2%
            if abs(convert_usd_to_inr(m_row['charges']) - submitted_charges_inr) < (0.02 * submitted_charges_inr):
                exact_duplicate_found = True

    # Find Top 5 Similar Claims using Euclidean Distance in Normalized Feature Space
    df_sim = df_raw.copy()
    df_sim['id'] = df_sim.index + 1
    if claim_id is not None:
        df_sim = df_sim[df_sim['id'] != int(claim_id)]

    df_sim['age_dist'] = np.abs(df_sim['age'] - age) / 46.0
    df_sim['bmi_dist'] = np.abs(df_sim['bmi'] - bmi) / 38.0
    df_sim['smoker_dist'] = (df_sim['smoker'] != smoker).astype(float) * 2.0 # High penalty for smoker mismatch
    df_sim['child_dist'] = np.abs(df_sim['children'] - children) / 5.0
    df_sim['region_dist'] = (df_sim['region'] != region).astype(float) * 0.3
    
    df_sim['total_dist'] = np.sqrt(
        df_sim['age_dist']**2 + 
        df_sim['bmi_dist']**2 + 
        df_sim['smoker_dist']**2 + 
        df_sim['child_dist']**2 + 
        df_sim['region_dist']**2
    )

    top_similar = df_sim.sort_values('total_dist').head(5)
    similar_claims = []
    for _, sim_row in top_similar.iterrows():
        sim_id = int(sim_row['id'])
        sim_charge_inr = convert_usd_to_inr(sim_row['charges'])
        sim_pct = max(60, min(99, int(round((1.0 - (sim_row['total_dist'] / 2.5)) * 100))))
        
        # Determine status
        if sim_charge_inr > upper_fence_inr:
            sim_risk = "High Risk"
            sim_badge = "rose"
        elif sim_charge_inr > (15.0 * 100000):
            sim_risk = "Moderate Risk"
            sim_badge = "amber"
        else:
            sim_risk = "Standard Risk"
            sim_badge = "emerald"

        reason = f"Age {int(sim_row['age'])}, {str(sim_row['smoker']).capitalize()} smoker, BMI {round(float(sim_row['bmi']), 1)}, {sim_row['region'].capitalize()}"

        similar_claims.append({
            "claim_id": sim_id,
            "age": int(sim_row['age']),
            "sex": str(sim_row['sex']).capitalize(),
            "bmi": round(float(sim_row['bmi']), 1),
            "smoker": str(sim_row['smoker']).capitalize(),
            "region": str(sim_row['region']).capitalize(),
            "claim_amount": sim_charge_inr,
            "formatted_amount": format_compact_inr(sim_charge_inr),
            "formatted_amount_full": format_inr(sim_charge_inr),
            "similarity_pct": sim_pct,
            "similarity_reason": reason,
            "risk_profile": sim_risk,
            "risk_badge": sim_badge
        })

    # 6. Component Risk Scoring (0–100)
    # Component A: Prediction Deviation Score
    if pct_deviation <= 0:
        score_pred_dev = 0
    elif pct_deviation <= 15:
        score_pred_dev = int(pct_deviation * 1.5) # 0 to 22
    elif pct_deviation <= 50:
        score_pred_dev = 25 + int((pct_deviation - 15) * 1.0) # 25 to 60
    elif pct_deviation <= 100:
        score_pred_dev = 60 + int((pct_deviation - 50) * 0.5) # 60 to 85
    else:
        score_pred_dev = min(100, 85 + int((pct_deviation - 100) * 0.2))

    # Component B: Outlier & Anomaly Score
    if submitted_charges_inr < q3_inr:
        score_anomaly = 10
    elif submitted_charges_inr < upper_fence_inr:
        score_anomaly = 30 + int(((submitted_charges_inr - q3_inr) / (upper_fence_inr - q3_inr)) * 30) # 30 to 60
    elif submitted_charges_inr < p95_inr:
        score_anomaly = 65 + int(((submitted_charges_inr - upper_fence_inr) / (p95_inr - upper_fence_inr)) * 20) # 65 to 85
    else:
        score_anomaly = min(100, 85 + int(((submitted_charges_inr - p95_inr) / (p99_inr - p95_inr)) * 15))

    # Component C: Clinical Cohort Pattern Consistency
    score_pattern = 10
    pattern_notes = []
    
    # Non-smoker claiming high catastrophic amounts
    if smoker == 'no' and submitted_charges_inr > (25.0 * 100000): # > 25 Lakh for non-smoker
        score_pattern += 55
        pattern_notes.append("Claim exceeds 3.5x non-smoker actuarial expectation without smoker multiplier.")
    elif smoker == 'no' and submitted_charges_inr > (15.0 * 100000):
        score_pattern += 30
        pattern_notes.append("Elevated claim for non-smoker policyholder cohort.")

    # Youth (<25 yrs) claiming > 15 Lakh
    if age < 25 and submitted_charges_inr > (15.0 * 100000):
        score_pattern += 25
        pattern_notes.append(f"Disproportionate claim amount for age {age} baseline liability.")

    # Normal BMI without chronic indicator
    if bmi < 25.0 and submitted_charges_inr > (20.0 * 100000):
        score_pattern += 20
        pattern_notes.append("Optimal physiological BMI with unexplained high-tier claim exposure.")
    
    score_pattern = min(100, score_pattern)

    # Component D: Duplicate Similarity Risk
    if exact_duplicate_found:
        score_duplicate = 90
    elif len(matching_duplicate_ids) > 0:
        score_duplicate = 45
    else:
        score_duplicate = 0

    # Component E: Data Integrity / Consistency
    score_consistency = 5 # Normal valid record

    # Overall Composite Weighted Risk Score
    composite_score = (
        0.35 * score_pred_dev + 
        0.25 * score_anomaly + 
        0.25 * score_pattern + 
        0.10 * score_duplicate + 
        0.05 * score_consistency
    )
    risk_score = int(round(max(0, min(100, composite_score))))

    # 7. Risk Level Classification & Decision Support
    if risk_score < 30:
        risk_level = "LOW RISK"
        risk_color = "emerald"
        action = "Proceed with standard processing"
        priority = "Normal Automated Processing"
        recommendation_summary = "Claim amounts align with supervised machine learning benchmarks and empirical population distribution. No significant anomalous deviation detected."
    elif risk_score < 60:
        risk_level = "MEDIUM RISK"
        risk_color = "amber"
        action = "Perform additional verification"
        priority = "Secondary Documentation Check"
        recommendation_summary = "Moderate variance detected between submitted claim and baseline risk factors. Recommend validating diagnostic codes and hospital itemized billings."
    elif risk_score < 80:
        risk_level = "HIGH RISK"
        risk_color = "orange"
        action = "Send for manual review"
        priority = "Claims Officer Review Required"
        recommendation_summary = "Significant actuarial deviation and outlier indicators identified. Mandatory manual underwriting audit recommended prior to claim settlement."
    else:
        risk_level = "CRITICAL RISK"
        risk_color = "rose"
        action = "Escalate for detailed investigation"
        priority = "Special Investigation Unit (SIU) Referral"
        recommendation_summary = "Severe statistical anomalies, extreme model variance, or potential duplicate profile detected. Escalate to fraud investigation and forensic medical audit."

    # 8. Explainable Risk Indicators (Pass / Warning / Alert)
    indicators = []

    # Indicator 1: Model Prediction Deviation
    if pct_deviation > 50:
        indicators.append({
            "status": "alert",
            "title": f"Claim Amount {pct_deviation}% Above ML Expected Benchmark",
            "detail": f"Submitted charge ({format_compact_inr(submitted_charges_inr)}) exceeds Gradient Boosting model expectation ({format_compact_inr(predicted_charges_inr)}) by {format_compact_inr(diff_inr)}.",
            "impact": "High"
        })
    elif pct_deviation > 20:
        indicators.append({
            "status": "warning",
            "title": f"Elevated Variance (+{pct_deviation}%) from Actuarial Benchmark",
            "detail": f"Submitted claim is moderately higher than expected model mean of {format_compact_inr(predicted_charges_inr)}.",
            "impact": "Medium"
        })
    elif pct_deviation < -30:
        indicators.append({
            "status": "warning",
            "title": f"Submitted Amount Significantly Below Expected Benchmark ({pct_deviation}%)",
            "detail": f"Claim amount ({format_compact_inr(submitted_charges_inr)}) is unusually low relative to predicted cost ({format_compact_inr(predicted_charges_inr)}). Potential partial claim.",
            "impact": "Low"
        })
    else:
        indicators.append({
            "status": "pass",
            "title": "Claim Amount Within Actuarial Expected Range",
            "detail": f"Submitted amount ({format_compact_inr(submitted_charges_inr)}) closely matches the trained Gradient Boosting model estimate ({format_compact_inr(predicted_charges_inr)}).",
            "impact": "Neutral"
        })

    # Indicator 2: Statistical Outlier Test
    if is_extreme_outlier:
        indicators.append({
            "status": "alert",
            "title": "Top 1% Catastrophic Claim Distribution Outlier",
            "detail": f"Claim of {format_compact_inr(submitted_charges_inr)} sits in the 99th percentile of all portfolio claims, exceeding the ₹46.3 Lakh upper threshold.",
            "impact": "Critical"
        })
    elif is_outlier:
        indicators.append({
            "status": "warning",
            "title": "Tukey's IQR Outlier Fence Exceeded",
            "detail": f"Claim exceeds the upper fence (Q3 + 1.5×IQR = {format_compact_inr(upper_fence_inr)}), indicating a high-cost outlier.",
            "impact": "Medium-High"
        })
    else:
        indicators.append({
            "status": "pass",
            "title": "Statistical Distribution Range Verified",
            "detail": f"Claim amount falls within standard IQR interquartile boundaries (< {format_compact_inr(upper_fence_inr)}).",
            "impact": "Neutral"
        })

    # Indicator 3: Duplicate / Similar Record Check
    if exact_duplicate_found:
        indicators.append({
            "status": "alert",
            "title": "Potential Exact Duplicate Claim Record Detected",
            "detail": f"Matches existing historical records in portfolio with identical demographic and billing parameters (Claim #{', #'.join(map(str, matching_duplicate_ids))}).",
            "impact": "Critical"
        })
    elif len(matching_duplicate_ids) > 0:
        indicators.append({
            "status": "warning",
            "title": "Matching Policyholder Demographic Pattern Found",
            "detail": f"Identical demographic characteristics match Claim #{', #'.join(map(str, matching_duplicate_ids[:3]))} in portfolio database.",
            "impact": "Medium"
        })
    else:
        indicators.append({
            "status": "pass",
            "title": "No Duplicate Claim Records Detected",
            "detail": "Portfolio scan verified zero identical duplicate submissions.",
            "impact": "Neutral"
        })

    # Indicator 4: Clinical Cohort Alignment
    if smoker == 'yes' and bmi >= 30.0:
        indicators.append({
            "status": "warning" if pct_deviation > 30 else "pass",
            "title": "Compounding Risk Factor Profile (Smoking + Obesity)",
            "detail": f"Beneficiary exhibits dual high-risk chronic factors (BMI {bmi} + Smoker) which empirically escalates claim exposure ~3.8x.",
            "impact": "High"
        })
    elif smoker == 'no' and submitted_charges_inr > (20.0 * 100000):
        indicators.append({
            "status": "alert",
            "title": "Clinical Severity Discrepancy (High Cost Non-Smoker)",
            "detail": "Non-smoker cohort has empirical mean of ₹8.05 Lakh; submitted claim of ₹" + f"{submitted_charges_inr/100000:.2f} Lakh requires procedural justification.",
            "impact": "High"
        })
    else:
        indicators.append({
            "status": "pass",
            "title": "Clinical Cohort Parameters Consistent",
            "detail": f"Demographic parameters (Age {age}, BMI {bmi}, Smoker: {smoker}) show standard risk-cost progression.",
            "impact": "Neutral"
        })

    # 9. Structured Reasons for Recommendation
    reasons = []
    if pct_deviation > 40:
        reasons.append(f"Submitted claim exceeds model expectation by {pct_deviation}% ({format_compact_inr(diff_inr)} excess liability).")
    elif pct_deviation <= 15:
        reasons.append(f"Submitted claim aligns with predictive gradient boosting benchmark ({format_compact_inr(predicted_charges_inr)}).")
    
    if is_outlier:
        reasons.append(f"Claim amount ({format_compact_inr(submitted_charges_inr)}) surpasses the statistical IQR upper fence ({format_compact_inr(upper_fence_inr)}).")
    else:
        reasons.append("Claim amount falls within standard distribution fences.")

    if exact_duplicate_found:
        reasons.append(f"Potential duplicate submission matches Claim #{matching_duplicate_ids[0]}.")
    
    if pattern_notes:
        reasons.extend(pattern_notes[:2])

    return {
        "analysis_timestamp": datetime.datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "model_used": "Gradient Boosting Regressor (R² = 90.17%)",
        "risk_method": "Actuarial Deviation & Multi-Signal Statistical Anomaly Scoring",
        "currency": CURRENCY_CODE,
        "currency_symbol": CURRENCY_SYMBOL,
        "exchange_rate": USD_TO_INR,
        "claim_details": {
            "claim_id": claim_id or "HYPO-" + str(np.random.randint(1000, 9999)),
            "is_dataset_record": bool(claim_id is not None and (0 <= (int(claim_id) - 1) < len(df_raw))),
            "age": age,
            "sex": sex.capitalize(),
            "bmi": bmi,
            "bmi_category": ml_pred['bmi_assessment']['category'],
            "children": children,
            "smoker": smoker.capitalize(),
            "region": region.capitalize(),
            "submitted_charges": submitted_charges_inr,
            "submitted_charges_usd": submitted_charges_usd,
            "formatted_submitted_charges": format_inr(submitted_charges_inr),
            "formatted_submitted_charges_compact": format_compact_inr(submitted_charges_inr)
        },
        "prediction_comparison": {
            "predicted_charges": predicted_charges_inr,
            "predicted_charges_usd": predicted_charges_usd,
            "formatted_predicted_charges": format_inr(predicted_charges_inr),
            "formatted_predicted_charges_compact": format_compact_inr(predicted_charges_inr),
            "difference_inr": diff_inr,
            "formatted_difference": format_compact_inr(abs(diff_inr)),
            "formatted_difference_full": format_inr(abs(diff_inr)),
            "percentage_deviation": pct_deviation,
            "confidence_interval": ml_pred['confidence_interval']
        },
        "risk_assessment": {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_color": risk_color,
            "priority": priority,
            "recommended_action": action,
            "recommendation_summary": recommendation_summary,
            "reasons": reasons
        },
        "risk_breakdown": [
            {"component": "Prediction Deviation", "score": score_pred_dev, "weight": "35%", "description": f"{pct_deviation}% variance from ML benchmark"},
            {"component": "Claim Amount Anomaly", "score": score_anomaly, "weight": "25%", "description": f"Z-score: {z_residual} | Outlier: {is_outlier}"},
            {"component": "Cohort Pattern Consistency", "score": score_pattern, "weight": "25%", "description": "Clinical lifestyle & demographic alignment"},
            {"component": "Duplicate / Similarity Risk", "score": score_duplicate, "weight": "10%", "description": "Historical portfolio matching audit"},
            {"component": "Data Consistency", "score": score_consistency, "weight": "5%", "description": "Validated parameter boundaries"}
        ],
        "anomaly_analysis": {
            "anomaly_status": anomaly_status,
            "anomaly_flag": anomaly_flag,
            "z_residual": z_residual,
            "is_outlier": is_outlier,
            "upper_fence_inr": round(upper_fence_inr, 2),
            "formatted_upper_fence": format_compact_inr(upper_fence_inr),
            "explanation": f"Claim of {format_compact_inr(submitted_charges_inr)} sits {z_residual} standard errors relative to model prediction."
        },
        "indicators": indicators,
        "similar_claims": similar_claims
    }
