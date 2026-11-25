import pandas as pd
import numpy as np
from services.data_service import load_raw_dataset
from services.currency_config import (
    USD_TO_INR, 
    CURRENCY_SYMBOL, 
    CURRENCY_CODE, 
    format_inr, 
    format_compact_inr, 
    convert_usd_to_inr
)

def get_visualization_payloads():
    """Prepares structured visualization datasets for interactive frontend charts in INR & USD."""
    df = load_raw_dataset().drop_duplicates().copy()

    # 1. Claim Distribution (Histogram with 20 bins)
    charges = df['charges'].values
    counts, bin_edges = np.histogram(charges, bins=20)
    hist_data = []
    for i in range(len(counts)):
        bin_start_inr = convert_usd_to_inr(bin_edges[i])
        bin_end_inr = convert_usd_to_inr(bin_edges[i+1])
        hist_data.append({
            "bin_start": round(float(bin_edges[i]), 2),
            "bin_end": round(float(bin_edges[i+1]), 2),
            "bin_start_inr": round(bin_start_inr, 2),
            "bin_end_inr": round(bin_end_inr, 2),
            "label": f"{format_compact_inr(bin_start_inr)} - {format_compact_inr(bin_end_inr)}",
            "label_usd": f"${int(bin_edges[i]):,}-${int(bin_edges[i+1]):,}",
            "count": int(counts[i])
        })

    # 2. Smoker Box Plot & Stats in INR and USD
    smoker_box = {}
    for smk in ['no', 'yes']:
        sub = df[df['smoker'] == smk]['charges']
        q1 = float(sub.quantile(0.25))
        q3 = float(sub.quantile(0.75))
        iqr = q3 - q1
        mean_val = float(sub.mean())
        median_val = float(sub.median())
        min_val = float(sub.min())
        max_val = float(sub.max())

        smoker_box[smk] = {
            "min": round(min_val, 2),
            "q1": round(q1, 2),
            "median": round(median_val, 2),
            "q3": round(q3, 2),
            "max": round(max_val, 2),
            "mean": round(mean_val, 2),
            "min_inr": round(convert_usd_to_inr(min_val), 2),
            "q1_inr": round(convert_usd_to_inr(q1), 2),
            "median_inr": round(convert_usd_to_inr(median_val), 2),
            "q3_inr": round(convert_usd_to_inr(q3), 2),
            "max_inr": round(convert_usd_to_inr(max_val), 2),
            "mean_inr": round(convert_usd_to_inr(mean_val), 2),
            "formatted_mean_inr": format_compact_inr(convert_usd_to_inr(mean_val)),
            "formatted_median_inr": format_compact_inr(convert_usd_to_inr(median_val)),
            "formatted_mean_inr_full": format_inr(convert_usd_to_inr(mean_val)),
            "formatted_median_inr_full": format_inr(convert_usd_to_inr(median_val)),
            "outlier_count": int(len(sub[(sub < (q1 - 1.5 * iqr)) | (sub > (q3 + 1.5 * iqr))]))
        }

    # 3. Age vs Charges Scatter (sample/full)
    age_scatter = []
    for _, row in df.iterrows():
        raw_c = float(row['charges'])
        c_inr = convert_usd_to_inr(raw_c)
        age_scatter.append({
            "age": int(row['age']),
            "charges": round(raw_c, 2),
            "charges_inr": round(c_inr, 2),
            "formatted_charges": format_inr(c_inr),
            "smoker": "Smoker" if row['smoker'] == 'yes' else "Non-Smoker",
            "bmi": round(float(row['bmi']), 1),
            "sex": row['sex'].capitalize()
        })

    # 4. BMI vs Charges Scatter
    bmi_scatter = []
    for _, row in df.iterrows():
        raw_c = float(row['charges'])
        c_inr = convert_usd_to_inr(raw_c)
        bmi_scatter.append({
            "bmi": round(float(row['bmi']), 2),
            "charges": round(raw_c, 2),
            "charges_inr": round(c_inr, 2),
            "formatted_charges": format_inr(c_inr),
            "smoker": "Smoker" if row['smoker'] == 'yes' else "Non-Smoker",
            "age": int(row['age']),
            "is_obese": bool(row['bmi'] >= 30.0)
        })

    # 5. Regional Comparison
    reg_summary = df.groupby('region').agg(
        mean_charge=('charges', 'mean'),
        median_charge=('charges', 'median'),
        count=('charges', 'count'),
        total_charges=('charges', 'sum')
    ).reset_index()
    regional_chart = []
    for _, r in reg_summary.iterrows():
        mean_inr = convert_usd_to_inr(r['mean_charge'])
        median_inr = convert_usd_to_inr(r['median_charge'])
        total_inr = convert_usd_to_inr(r['total_charges'])
        regional_chart.append({
            "region": r['region'].capitalize(),
            "mean_charge": round(float(r['mean_charge']), 2),
            "median_charge": round(float(r['median_charge']), 2),
            "mean_charge_inr": round(mean_inr, 2),
            "median_charge_inr": round(median_inr, 2),
            "formatted_mean_inr": format_compact_inr(mean_inr),
            "formatted_median_inr": format_compact_inr(median_inr),
            "claim_count": int(r['count']),
            "total_charges": round(float(r['total_charges']), 2),
            "total_charges_inr": round(total_inr, 2),
            "formatted_total_inr": format_compact_inr(total_inr)
        })

    # 6. Children vs Charges
    child_summary = df.groupby('children').agg(
        mean_charge=('charges', 'mean'),
        median_charge=('charges', 'median'),
        count=('charges', 'count')
    ).reset_index()
    children_chart = []
    for _, r in child_summary.iterrows():
        mean_inr = convert_usd_to_inr(r['mean_charge'])
        median_inr = convert_usd_to_inr(r['median_charge'])
        children_chart.append({
            "children": int(r['children']),
            "label": f"{r['children']} Children" if r['children'] > 0 else "No Dependents",
            "mean_charge": round(float(r['mean_charge']), 2),
            "median_charge": round(float(r['median_charge']), 2),
            "mean_charge_inr": round(mean_inr, 2),
            "median_charge_inr": round(median_inr, 2),
            "formatted_mean_inr": format_compact_inr(mean_inr),
            "count": int(r['count'])
        })

    # 7. Correlation Heatmap Matrix
    corr_df = df.copy()
    corr_df['smoker_num'] = corr_df['smoker'].map({'yes': 1, 'no': 0})
    corr_df['sex_num'] = corr_df['sex'].map({'male': 1, 'female': 0})
    for reg in ['northeast', 'northwest', 'southeast', 'southwest']:
        corr_df[f'region_{reg}'] = (corr_df['region'] == reg).astype(int)

    matrix_cols = ['age', 'bmi', 'children', 'smoker_num', 'sex_num', 
                   'region_northeast', 'region_northwest', 'region_southeast', 'region_southwest', 'charges']
    col_labels = ['Age', 'BMI', 'Children', 'Smoker', 'Sex (Male)', 
                  'Reg: NE', 'Reg: NW', 'Reg: SE', 'Reg: SW', 'Claim Charges (₹)']
    
    corr_matrix = corr_df[matrix_cols].corr().round(3)
    
    heatmap_data = {
        "columns": col_labels,
        "matrix": [[float(val) for val in row] for row in corr_matrix.values]
    }

    return {
        "currency": CURRENCY_CODE,
        "currency_symbol": CURRENCY_SYMBOL,
        "exchange_rate": USD_TO_INR,
        "claim_distribution": hist_data,
        "smoker_box_plot": smoker_box,
        "age_scatter": age_scatter,
        "bmi_scatter": bmi_scatter,
        "regional_chart": regional_chart,
        "children_chart": children_chart,
        "correlation_heatmap": heatmap_data
    }
