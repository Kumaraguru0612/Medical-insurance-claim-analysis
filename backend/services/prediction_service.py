import os
import joblib
import pandas as pd
import numpy as np
from services.ml_service import get_trained_pipeline, KMEANS_MODEL_PATH, BEST_MODEL_PATH, train_and_evaluate_all_models

from services.currency_config import (
    USD_TO_INR,
    CURRENCY_SYMBOL,
    CURRENCY_CODE,
    format_inr,
    format_compact_inr,
    convert_usd_to_inr
)

def predict_insurance_claim(age, sex, bmi, children, smoker, region):
    """Generates an accurate, explainable medical insurance claim cost prediction using the trained ML model in INR."""
    # Ensure models exist
    if not os.path.exists(BEST_MODEL_PATH) or not os.path.exists(KMEANS_MODEL_PATH):
        train_and_evaluate_all_models()

    pipeline = joblib.load(BEST_MODEL_PATH)
    kmeans_bundle = joblib.load(KMEANS_MODEL_PATH)

    # Input validation and formatting
    age = int(age)
    bmi = float(bmi)
    children = int(children)
    sex = str(sex).lower().strip()
    smoker = str(smoker).lower().strip()
    region = str(region).lower().strip()

    if sex not in ['female', 'male']:
        sex = 'female'
    if smoker not in ['yes', 'no']:
        smoker = 'no'
    if region not in ['northeast', 'northwest', 'southeast', 'southwest']:
        region = 'southeast'

    # Build input DataFrame
    input_df = pd.DataFrame([{
        'age': age,
        'sex': sex,
        'bmi': bmi,
        'children': children,
        'smoker': smoker,
        'region': region
    }])

    # Model inference (raw USD internally for ML model compatibility)
    raw_prediction = float(pipeline.predict(input_df)[0])
    predicted_claim_usd = max(500.0, round(raw_prediction, 2))
    predicted_claim_inr = round(convert_usd_to_inr(predicted_claim_usd), 2)

    # BMI Clinical Classification
    if bmi < 18.5:
        bmi_category = "Underweight"
        bmi_risk_label = "Low weight / Potential malnutrition risk"
        bmi_badge_color = "amber"
    elif bmi < 25.0:
        bmi_category = "Normal Weight"
        bmi_risk_label = "Optimal physiological weight range"
        bmi_badge_color = "emerald"
    elif bmi < 30.0:
        bmi_category = "Overweight"
        bmi_risk_label = "Moderate cardiovascular / metabolic risk"
        bmi_badge_color = "amber"
    else:
        bmi_category = "Obese (Class I+)"
        bmi_risk_label = "Elevated risk of diabetes, hypertension, and chronic complications"
        bmi_badge_color = "rose"

    # Risk Clustering Assignment
    smoker_enc = 1 if smoker == 'yes' else 0
    cluster_features = np.array([[age, bmi, smoker_enc, predicted_claim_usd]])
    scaled_cf = kmeans_bundle['scaler'].transform(cluster_features)
    cluster_id = int(kmeans_bundle['kmeans'].predict(scaled_cf)[0])
    
    if predicted_claim_inr < convert_usd_to_inr(10000):
        risk_tier = "Tier 1 — Low Claim Risk (Standard)"
        risk_tier_color = "emerald"
        risk_tier_desc = "Beneficiary exhibits minimal chronic risk factors. Low probability of high-cost hospitalizations."
    elif predicted_claim_inr < convert_usd_to_inr(25000):
        risk_tier = "Tier 2 — Moderate Claim Risk (Elevated)"
        risk_tier_color = "amber"
        risk_tier_desc = "Elevated risk profile driven by advancing age or moderate overweight BMI. Moderate medical expense exposure."
    else:
        risk_tier = "Tier 3 — High Claim Risk (Critical)"
        risk_tier_color = "rose"
        risk_tier_desc = "High-risk profile heavily driven by smoking and/or severe obesity. Significant probability of catastrophic claims."

    # Counterfactual Health & Cost Savings Analysis
    savings_scenarios = []
    if smoker == 'yes':
        df_no_smoke = input_df.copy()
        df_no_smoke['smoker'] = 'no'
        pred_no_smoke_usd = max(500.0, float(pipeline.predict(df_no_smoke)[0]))
        pred_no_smoke_inr = convert_usd_to_inr(pred_no_smoke_usd)
        smoke_savings_inr = max(0.0, predicted_claim_inr - pred_no_smoke_inr)
        savings_scenarios.append({
            "scenario": "Smoking Cessation Program",
            "action": "Transition from active smoker to non-smoker",
            "projected_cost": round(pred_no_smoke_inr, 2),
            "formatted_projected_cost": format_inr(pred_no_smoke_inr),
            "estimated_annual_savings": round(smoke_savings_inr, 2),
            "formatted_annual_savings": format_inr(smoke_savings_inr),
            "formatted_annual_savings_compact": format_compact_inr(smoke_savings_inr),
            "savings_percentage": round((smoke_savings_inr / predicted_claim_inr) * 100, 1),
            "health_benefit": "Drastic reduction in pulmonary and cardiovascular catastrophic risk events."
        })

    if bmi >= 25.0:
        df_opt_bmi = input_df.copy()
        df_opt_bmi['bmi'] = 24.0 # Healthy normal target
        pred_opt_bmi_usd = max(500.0, float(pipeline.predict(df_opt_bmi)[0]))
        pred_opt_bmi_inr = convert_usd_to_inr(pred_opt_bmi_usd)
        bmi_savings_inr = max(0.0, predicted_claim_inr - pred_opt_bmi_inr)
        if bmi_savings_inr > 100:
            savings_scenarios.append({
                "scenario": "Weight Management & Nutrition",
                "action": f"Reduce BMI from {bmi} to 24.0 (Normal Weight)",
                "projected_cost": round(pred_opt_bmi_inr, 2),
                "formatted_projected_cost": format_inr(pred_opt_bmi_inr),
                "estimated_annual_savings": round(bmi_savings_inr, 2),
                "formatted_annual_savings": format_inr(bmi_savings_inr),
                "formatted_annual_savings_compact": format_compact_inr(bmi_savings_inr),
                "savings_percentage": round((bmi_savings_inr / predicted_claim_inr) * 100, 1),
                "health_benefit": "Eliminates obesity-associated metabolic syndrome and joint/circulatory stress."
            })

    # Cost Attribution Breakdown in INR
    base_cost = convert_usd_to_inr(2500.0)
    age_contribution = convert_usd_to_inr(max(0.0, (age - 18) * 260.0))
    bmi_contribution = convert_usd_to_inr(max(0.0, (bmi - 22.0) * 350.0) if bmi > 22 else 0.0)
    smoker_contribution = convert_usd_to_inr(24000.0 if smoker == 'yes' else 0.0)
    children_contribution = convert_usd_to_inr(children * 500.0)
    region_contribution = convert_usd_to_inr(1000.0 if region == 'southeast' else 500.0 if region == 'northeast' else 0.0)

    total_sum_factors = base_cost + age_contribution + bmi_contribution + smoker_contribution + children_contribution + region_contribution
    scale_factor = predicted_claim_inr / (total_sum_factors if total_sum_factors > 0 else 1.0)
    
    breakdown = [
        {"component": "Base Actuarial Reserve", "amount": round(base_cost * scale_factor, 2), "formatted_amount": format_inr(base_cost * scale_factor), "icon": "Shield"},
        {"component": f"Age Factor ({age} yrs)", "amount": round(age_contribution * scale_factor, 2), "formatted_amount": format_inr(age_contribution * scale_factor), "icon": "Calendar"},
        {"component": f"BMI Impact ({bmi} kg/m²)", "amount": round(bmi_contribution * scale_factor, 2), "formatted_amount": format_inr(bmi_contribution * scale_factor), "icon": "Activity"},
        {"component": f"Smoker Surcharge ({smoker.capitalize()})", "amount": round(smoker_contribution * scale_factor, 2), "formatted_amount": format_inr(smoker_contribution * scale_factor), "icon": "Flame"},
        {"component": f"Dependents Coverage ({children})", "amount": round(children_contribution * scale_factor, 2), "formatted_amount": format_inr(children_contribution * scale_factor), "icon": "Users"},
        {"component": f"Regional Variance ({region.capitalize()})", "amount": round(region_contribution * scale_factor, 2), "formatted_amount": format_inr(region_contribution * scale_factor), "icon": "MapPin"}
    ]

    # Prediction confidence interval in INR (RMSE ~ $4,400 -> converted to INR)
    rmse_bound_inr = convert_usd_to_inr(4400.0)
    lower_bound_inr = max(convert_usd_to_inr(500.0), round(predicted_claim_inr - 1.28 * rmse_bound_inr, 2))
    upper_bound_inr = round(predicted_claim_inr + 1.28 * rmse_bound_inr, 2)

    return {
        "currency": CURRENCY_CODE,
        "currency_symbol": CURRENCY_SYMBOL,
        "exchange_rate": USD_TO_INR,
        "inputs": {
            "age": age,
            "sex": sex,
            "bmi": bmi,
            "children": children,
            "smoker": smoker,
            "region": region
        },
        "predicted_charges": predicted_claim_inr,
        "predicted_charges_usd": predicted_claim_usd,
        "formatted_charges": format_inr(predicted_claim_inr),
        "formatted_charges_compact": format_compact_inr(predicted_claim_inr),
        "confidence_interval": {
            "lower_bound": lower_bound_inr,
            "upper_bound": upper_bound_inr,
            "formatted_range": f"{format_inr(lower_bound_inr)} — {format_inr(upper_bound_inr)}"
        },
        "bmi_assessment": {
            "category": bmi_category,
            "badge_color": bmi_badge_color,
            "clinical_notes": bmi_risk_label
        },
        "risk_tier": {
            "tier_name": risk_tier,
            "color": risk_tier_color,
            "description": risk_tier_desc
        },
        "cost_breakdown": breakdown,
        "savings_opportunities": savings_scenarios
    }
