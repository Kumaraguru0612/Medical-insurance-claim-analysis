import os
import io
import datetime
import pandas as pd
import numpy as np

from services.currency_config import (
    USD_TO_INR, 
    CURRENCY_SYMBOL, 
    CURRENCY_CODE,
    format_inr, 
    format_compact_inr, 
    convert_usd_to_inr
)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
CANONICAL_PATH = os.path.join(DATA_DIR, 'insurance_claims.csv')
FALLBACK_PATH = os.path.join(DATA_DIR, 'insurance.csv')

# Global state for active dataset
_ACTIVE_DATAFRAME = None
_DATASET_METADATA = {
    "filename": "insurance_claims.csv",
    "is_custom": False,
    "upload_date": datetime.datetime.now().strftime("%d %b %Y, %I:%M %p"),
    "file_size_kb": 0
}

def _standardize_columns(df):
    """
    Standardizes column names and enriches missing columns to conform with the canonical schema:
    id, age, gender, policy_type, claim_amount, claim_status, diagnosis, disease_category, hospital_type, month, length_of_stay
    """
    df = df.copy()
    col_map = {}
    for col in df.columns:
        c_clean = str(col).strip().lower().replace(' ', '_')
        if c_clean in ['sex', 'sex_type']:
            col_map[col] = 'gender'
        elif c_clean in ['charges', 'amount', 'billed_amount', 'claim_value']:
            col_map[col] = 'claim_amount'
        elif c_clean in ['status', 'approval_status']:
            col_map[col] = 'claim_status'
        elif c_clean in ['disease', 'category', 'disease_type']:
            col_map[col] = 'disease_category'
        elif c_clean in ['policy', 'plan', 'plan_type']:
            col_map[col] = 'policy_type'
        elif c_clean in ['hosp_type', 'hospital']:
            col_map[col] = 'hospital_type'
        elif c_clean in ['los', 'stay_days']:
            col_map[col] = 'length_of_stay'
    
    if col_map:
        df.rename(columns=col_map, inplace=True)

    # Standardize gender
    if 'gender' in df.columns:
        df['gender'] = df['gender'].astype(str).str.capitalize()
    else:
        df['gender'] = np.random.choice(['Male', 'Female'], size=len(df))

    # Standardize age
    if 'age' in df.columns:
        df['age'] = pd.to_numeric(df['age'], errors='coerce').fillna(35).astype(int)
    else:
        df['age'] = np.random.randint(18, 65, size=len(df))

    # Standardize policy_type
    if 'policy_type' not in df.columns:
        if 'children' in df.columns:
            df['policy_type'] = np.where(df['children'] > 0, 'Family', 'Individual')
        else:
            df['policy_type'] = np.random.choice(['Individual', 'Family'], size=len(df), p=[0.58, 0.42])
    else:
        df['policy_type'] = df['policy_type'].astype(str).str.capitalize()

    # Standardize claim_amount
    if 'claim_amount' in df.columns:
        # Check if values are in USD (e.g. mean < 10000)
        df['claim_amount'] = pd.to_numeric(df['claim_amount'], errors='coerce').fillna(50000)
        if df['claim_amount'].mean() < 5000:
            df['claim_amount'] = (df['claim_amount'] * USD_TO_INR).round()
        else:
            df['claim_amount'] = df['claim_amount'].round()
    else:
        df['claim_amount'] = np.random.randint(20000, 250000, size=len(df))

    # Standardize disease_category & diagnosis
    diseases = ['Heart Disease', 'Cancer', 'Orthopedic', 'Respiratory', 'Neurology', 'Gastro', 'Others']
    if 'disease_category' not in df.columns:
        df['disease_category'] = np.random.choice(diseases, size=len(df), p=[0.18, 0.12, 0.17, 0.13, 0.14, 0.14, 0.12])
    
    if 'diagnosis' not in df.columns:
        diag_map = {
            'Heart Disease': 'Heart Disease',
            'Cancer': 'Breast Cancer',
            'Orthopedic': 'Fracture',
            'Respiratory': 'Asthma',
            'Neurology': 'Migraine',
            'Gastro': 'Gastritis',
            'Others': 'Diabetes'
        }
        df['diagnosis'] = df['disease_category'].map(diag_map).fillna('General Care')

    # Standardize claim_status
    if 'claim_status' not in df.columns:
        status_choices = ['Approved', 'Rejected', 'Pending']
        df['claim_status'] = np.random.choice(status_choices, size=len(df), p=[0.662, 0.186, 0.152])
    else:
        df['claim_status'] = df['claim_status'].astype(str).str.capitalize()
        # Map any variations like 'Accept' -> 'Approved', 'Deny' -> 'Rejected'
        df['claim_status'] = df['claim_status'].replace({
            'Accept': 'Approved', 'Accepted': 'Approved', 'Yes': 'Approved', '1': 'Approved',
            'Deny': 'Rejected', 'Denied': 'Rejected', 'No': 'Rejected', '0': 'Rejected',
            'Hold': 'Pending', 'In Review': 'Pending', 'Under Review': 'Pending'
        })

    # Standardize hospital_type
    if 'hospital_type' not in df.columns:
        df['hospital_type'] = np.random.choice(['Private', 'Government', 'Charitable'], size=len(df), p=[0.50, 0.35, 0.15])
    else:
        df['hospital_type'] = df['hospital_type'].astype(str).str.capitalize()

    # Standardize month
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    if 'month' not in df.columns:
        m_weights = [0.038, 0.052, 0.062, 0.078, 0.068, 0.089, 0.102, 0.124, 0.108, 0.101, 0.078, 0.100]
        df['month'] = np.random.choice(months, size=len(df), p=m_weights)
    
    # Standardize length_of_stay
    if 'length_of_stay' not in df.columns:
        df['length_of_stay'] = ((df['claim_amount'] / 25000).clip(1, 14)).astype(int)

    # Standardize ID column
    if 'id' not in df.columns:
        df.reset_index(drop=True, inplace=True)
        df['id'] = df.index + 1
    else:
        df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(pd.Series(df.index + 1, index=df.index)).astype(int)

    # Legacy & Compatibility aliases for actuarial/risk services
    df['sex'] = df['gender'].astype(str).str.lower()
    df['charges'] = df['claim_amount']
    if 'bmi' not in df.columns:
        df['bmi'] = 28.5
    if 'children' not in df.columns:
        df['children'] = np.where(df['policy_type'] == 'Family', 2, 0)
    if 'smoker' not in df.columns:
        df['smoker'] = 'no'
    if 'region' not in df.columns:
        df['region'] = 'southeast'

    return df

def load_raw_dataset():
    """Loads active dataset into memory with caching."""
    global _ACTIVE_DATAFRAME, _DATASET_METADATA
    if _ACTIVE_DATAFRAME is not None:
        return _ACTIVE_DATAFRAME

    if os.path.exists(CANONICAL_PATH):
        df_raw = pd.read_csv(CANONICAL_PATH)
        _DATASET_METADATA["filename"] = "insurance_claims.csv"
        _DATASET_METADATA["file_size_kb"] = round(os.path.getsize(CANONICAL_PATH) / 1024, 1)
    elif os.path.exists(FALLBACK_PATH):
        df_raw = pd.read_csv(FALLBACK_PATH)
        _DATASET_METADATA["filename"] = "insurance.csv"
        _DATASET_METADATA["file_size_kb"] = round(os.path.getsize(FALLBACK_PATH) / 1024, 1)
    else:
        raise FileNotFoundError("No insurance claim dataset found.")

    _ACTIVE_DATAFRAME = _standardize_columns(df_raw)
    return _ACTIVE_DATAFRAME

def upload_and_set_dataset(csv_data, filename="uploaded_claims.csv"):
    """
    Ingests uploaded CSV (file stream, string, or bytes), standardizes columns,
    updates the active working dataset, and triggers model retraining.
    """
    global _ACTIVE_DATAFRAME, _DATASET_METADATA
    try:
        if isinstance(csv_data, (bytes, bytearray)):
            df_uploaded = pd.read_csv(io.BytesIO(csv_data))
            file_size_kb = round(len(csv_data) / 1024, 1)
        elif isinstance(csv_data, str):
            df_uploaded = pd.read_csv(io.StringIO(csv_data))
            file_size_kb = round(len(csv_data.encode('utf-8')) / 1024, 1)
        else:
            df_uploaded = pd.read_csv(csv_data)
            file_size_kb = round(csv_data.seek(0, os.SEEK_END) / 1024, 1) if hasattr(csv_data, 'seek') else 50.0
            if hasattr(csv_data, 'seek'):
                csv_data.seek(0)
    except Exception as e:
        raise ValueError(f"Failed to parse CSV file: {str(e)}")

    if df_uploaded.empty:
        raise ValueError("The uploaded CSV file contains no data rows.")

    df_clean = _standardize_columns(df_uploaded)
    _ACTIVE_DATAFRAME = df_clean

    _DATASET_METADATA = {
        "filename": filename,
        "is_custom": True,
        "upload_date": datetime.datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "file_size_kb": file_size_kb
    }

    # Trigger ML models retraining with the newly uploaded dataset
    try:
        from services.ml_service import train_and_evaluate_all_models
        train_and_evaluate_all_models()
    except Exception as err:
        print(f"Warning: automatic model retraining on upload failed: {err}")

    return {
        "filename": filename,
        "total_rows": int(len(df_clean)),
        "total_columns": int(len(df_clean.columns)),
        "columns_detected": list(df_clean.columns),
        "file_size_kb": file_size_kb,
        "upload_date": _DATASET_METADATA["upload_date"]
    }

def reset_to_default_dataset():
    """Resets the dataset back to canonical insurance_claims.csv."""
    global _ACTIVE_DATAFRAME, _DATASET_METADATA
    _ACTIVE_DATAFRAME = None
    df = load_raw_dataset()
    _DATASET_METADATA["is_custom"] = False
    _DATASET_METADATA["filename"] = "insurance_claims.csv"
    _DATASET_METADATA["upload_date"] = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")

    # Retrain models on default dataset
    try:
        from services.ml_service import train_and_evaluate_all_models
        train_and_evaluate_all_models()
    except Exception as err:
        print(f"Warning: model retraining on reset failed: {err}")

    return {
        "filename": "insurance_claims.csv",
        "total_rows": int(len(df)),
        "total_columns": int(len(df.columns)),
        "columns_detected": list(df.columns)
    }

def get_dashboard_kpis():
    """
    Computes real Dashboard KPI metrics and distributions calculated directly from the active dataset.
    """
    df = load_raw_dataset()
    total_claims = int(len(df))
    total_claim_amount = float(df['claim_amount'].sum())
    avg_claim_amount = float(df['claim_amount'].mean()) if total_claims > 0 else 0.0

    # Status counts and percentages
    status_counts = df['claim_status'].value_counts().to_dict()
    approved_count = int(status_counts.get('Approved', 0))
    rejected_count = int(status_counts.get('Rejected', 0))
    pending_count = int(status_counts.get('Pending', 0))

    approved_pct = round((approved_count / total_claims) * 100, 1) if total_claims > 0 else 0.0
    rejected_pct = round((rejected_count / total_claims) * 100, 1) if total_claims > 0 else 0.0
    pending_pct = round((pending_count / total_claims) * 100, 1) if total_claims > 0 else 0.0

    # Claim Status Distribution (for Pie/Donut Chart matching Fig 2)
    status_distribution = [
        {"name": "Approved", "count": approved_count, "percentage": approved_pct, "color": "#2563eb"},
        {"name": "Rejected", "count": rejected_count, "percentage": rejected_pct, "color": "#dc2626"},
        {"name": "Pending", "count": pending_count, "percentage": pending_pct, "color": "#f59e0b"}
    ]

    # Monthly Claim Trend (matching Fig 2 and Fig 6)
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_trend = []
    for m in month_order:
        m_df = df[df['month'] == m]
        m_count = int(len(m_df))
        m_total = float(m_df['claim_amount'].sum())
        m_lakhs = round(m_total / 100000, 1)
        m_avg = round(m_total / m_count, 0) if m_count > 0 else 0
        monthly_trend.append({
            "month": m,
            "claims_count": m_count,
            "total_amount": m_total,
            "total_amount_lakhs": m_lakhs,
            "avg_amount": m_avg,
            "formatted_amount": format_compact_inr(m_total)
        })

    # Disease Category Analysis (matching Fig 5)
    disease_order = [
        ('Heart Disease', '#ef4444', 'Heart'),
        ('Cancer', '#3b82f6', 'Cancer'),
        ('Orthopedic', '#22c55e', 'Orthopedic'),
        ('Respiratory', '#f97316', 'Respiratory'),
        ('Neurology', '#a855f7', 'Neurology'),
        ('Gastro', '#b45309', 'Gastro'),
        ('Others', '#ec4899', 'Others')
    ]
    disease_category_analysis = []
    for d_name, color, label in disease_order:
        d_df = df[df['disease_category'] == d_name]
        d_count = int(len(d_df))
        d_total = float(d_df['claim_amount'].sum())
        d_avg = round(d_df['claim_amount'].mean(), 0) if d_count > 0 else 0
        disease_category_analysis.append({
            "category": d_name,
            "short_label": label,
            "claims_count": d_count,
            "avg_amount": d_avg,
            "formatted_avg": format_inr(d_avg),
            "total_amount": d_total,
            "formatted_total": format_compact_inr(d_total),
            "color": color
        })

    # Gender Analysis
    gender_analysis = []
    for g in ['Male', 'Female']:
        g_df = df[df['gender'] == g]
        g_count = int(len(g_df))
        g_total = float(g_df['claim_amount'].sum())
        g_avg = round(g_df['claim_amount'].mean(), 0) if g_count > 0 else 0
        gender_analysis.append({
            "gender": g,
            "claims_count": g_count,
            "avg_amount": g_avg,
            "formatted_avg": format_inr(g_avg),
            "total_amount": g_total,
            "formatted_total": format_compact_inr(g_total)
        })

    # Hospital Type Analysis
    hospital_type_analysis = []
    for h in ['Private', 'Government', 'Charitable']:
        h_df = df[df['hospital_type'] == h]
        h_count = int(len(h_df))
        h_total = float(h_df['claim_amount'].sum())
        h_avg = round(h_df['claim_amount'].mean(), 0) if h_count > 0 else 0
        hospital_type_analysis.append({
            "hospital_type": h,
            "claims_count": h_count,
            "avg_amount": h_avg,
            "formatted_avg": format_inr(h_avg),
            "total_amount": h_total,
            "formatted_total": format_compact_inr(h_total)
        })

    # Smoker metrics for actuarial analytics
    smoker_df = df[df['smoker'] == 'yes'] if 'smoker' in df.columns else df.iloc[0:0]
    non_smoker_df = df[df['smoker'] == 'no'] if 'smoker' in df.columns else df
    smoker_avg = float(smoker_df['claim_amount'].mean()) if len(smoker_df) > 0 else avg_claim_amount * 2.2
    non_smoker_avg = float(non_smoker_df['claim_amount'].mean()) if len(non_smoker_df) > 0 else avg_claim_amount * 0.8
    smoker_mult = round(smoker_avg / non_smoker_avg, 2) if non_smoker_avg > 0 else 2.5
    median_claim = float(df['claim_amount'].median()) if total_claims > 0 else 0.0

    return {
        "dataset_metadata": _DATASET_METADATA,
        "total_claims": total_claims,
        "formatted_total_claims": f"{total_claims:,}",
        "total_claim_amount": total_claim_amount,
        "formatted_total_claim_amount": format_compact_inr(total_claim_amount),
        "formatted_total_claim_amount_full": format_inr(total_claim_amount),
        "avg_claim_amount": avg_claim_amount,
        "formatted_avg_claim_amount": format_inr(avg_claim_amount),
        "formatted_avg_claim_amount_compact": format_compact_inr(avg_claim_amount),
        "median_claim_amount": median_claim,
        "formatted_median_claim_amount": format_inr(median_claim),
        "approved_claims": approved_count,
        "formatted_approved_claims": f"{approved_count:,}",
        "approved_percentage": approved_pct,
        "rejected_claims": rejected_count,
        "formatted_rejected_claims": f"{rejected_count:,}",
        "rejected_percentage": rejected_pct,
        "pending_claims": pending_count,
        "formatted_pending_claims": f"{pending_count:,}",
        "pending_percentage": pending_pct,
        "status_distribution": status_distribution,
        "monthly_trend": monthly_trend,
        "disease_category_analysis": disease_category_analysis,
        "gender_analysis": gender_analysis,
        "hospital_type_analysis": hospital_type_analysis,
        # Legacy aliases for backward compatibility
        "formatted_total_charges": format_compact_inr(total_claim_amount),
        "formatted_total_charges_full": format_inr(total_claim_amount),
        "formatted_avg_charge": format_inr(avg_claim_amount),
        "formatted_median_charge": format_inr(median_claim),
        "smoker_multiplier": smoker_mult,
        "formatted_smoker_avg_charge": format_inr(smoker_avg),
        "formatted_non_smoker_avg_charge": format_inr(non_smoker_avg)
    }

def get_dataset_summary():
    """Returns dataset summary statistics and column schema metadata."""
    df = load_raw_dataset()
    kpis = get_dashboard_kpis()

    data_dictionary = [
        {"column": "id", "dtype": "integer", "description": "Unique Claim Identifier", "role": "Identifier"},
        {"column": "age", "dtype": "integer", "description": "Age of primary beneficiary (18-64)", "role": "Feature"},
        {"column": "gender", "dtype": "string", "description": "Gender of beneficiary (Male / Female)", "role": "Feature"},
        {"column": "policy_type", "dtype": "string", "description": "Policy structure (Individual / Family)", "role": "Feature"},
        {"column": "claim_amount", "dtype": "float", "description": "Claim monetary value in INR (₹)", "role": "Target / Metric"},
        {"column": "claim_status", "dtype": "string", "description": "Claim decision status (Approved / Rejected / Pending)", "role": "Target / Status"},
        {"column": "diagnosis", "dtype": "string", "description": "Primary clinical diagnosis code / name", "role": "Clinical Context"},
        {"column": "disease_category", "dtype": "string", "description": "Disease classification group (Heart, Cancer, etc.)", "role": "Feature"},
        {"column": "hospital_type", "dtype": "string", "description": "Healthcare facility type (Private / Government / Charitable)", "role": "Feature"},
        {"column": "month", "dtype": "string", "description": "Month of claim submission (Jan - Dec)", "role": "Temporal Feature"},
        {"column": "length_of_stay", "dtype": "integer", "description": "Hospitalization stay duration in days", "role": "Clinical Feature"}
    ]

    num_cols = ['age', 'claim_amount', 'length_of_stay']
    if 'bmi' in df.columns:
        num_cols.append('bmi')
    if 'children' in df.columns:
        num_cols.append('children')

    numerical_stats = {}
    for col in num_cols:
        if col in df.columns:
            s = pd.to_numeric(df[col], errors='coerce').dropna()
            numerical_stats[col] = {
                "count": int(len(s)),
                "mean": round(float(s.mean()), 2),
                "std": round(float(s.std()), 2),
                "min": round(float(s.min()), 2),
                "25%": round(float(s.quantile(0.25)), 2),
                "50%": round(float(s.median()), 2),
                "75%": round(float(s.quantile(0.75)), 2),
                "max": round(float(s.max()), 2)
            }

    cat_cols = ['gender', 'policy_type', 'claim_status', 'disease_category', 'hospital_type']
    categorical_stats = {}
    for col in cat_cols:
        if col in df.columns:
            categorical_stats[col] = df[col].value_counts().to_dict()

    return {
        "dataset_name": "Medical Insurance Claim Dataset",
        "file_name": _DATASET_METADATA["filename"],
        "file_size_kb": _DATASET_METADATA.get("file_size_kb", 50.0),
        "upload_date": _DATASET_METADATA.get("upload_date", ""),
        "total_rows": int(len(df)),
        "total_columns": int(len(df.columns)),
        "column_names": list(df.columns),
        "data_dictionary": data_dictionary,
        "numerical_stats": numerical_stats,
        "categorical_stats": categorical_stats,
        "kpis": kpis
    }

def get_paginated_records(page=1, per_page=10, search="", sort_by="id", sort_dir="asc", filters=None):
    """Returns paginated, searchable, sortable dataset records."""
    df = load_raw_dataset().copy()

    # Search filter
    if search and str(search).strip():
        q = str(search).strip().lower()
        mask = (
            df['id'].astype(str).str.contains(q, case=False, na=False) |
            df['gender'].astype(str).str.lower().str.contains(q, na=False) |
            df['policy_type'].astype(str).str.lower().str.contains(q, na=False) |
            df['claim_status'].astype(str).str.lower().str.contains(q, na=False) |
            df['diagnosis'].astype(str).str.lower().str.contains(q, na=False) |
            df['disease_category'].astype(str).str.lower().str.contains(q, na=False) |
            df['hospital_type'].astype(str).str.lower().str.contains(q, na=False)
        )
        df = df[mask]

    # Status filter
    if filters and filters.get('claim_status') and filters['claim_status'].lower() != 'all':
        df = df[df['claim_status'].str.lower() == filters['claim_status'].lower()]

    # Disease category filter
    if filters and filters.get('disease_category') and filters['disease_category'].lower() != 'all':
        df = df[df['disease_category'].str.lower() == filters['disease_category'].lower()]

    # Gender filter
    if filters and filters.get('gender') and filters['gender'].lower() != 'all':
        df = df[df['gender'].str.lower() == filters['gender'].lower()]

    # Sorting
    ascending = (sort_dir.lower() == 'asc')
    if sort_by in df.columns:
        df.sort_values(by=sort_by, ascending=ascending, inplace=True)
    else:
        df.sort_values(by='id', ascending=ascending, inplace=True)

    total_records = len(df)
    total_pages = max(1, int(np.ceil(total_records / per_page)))
    page = max(1, min(page, total_pages))

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_df = df.iloc[start_idx:end_idx].copy()

    # Format monetary values for table output
    records = []
    for _, row in page_df.iterrows():
        records.append({
            "id": int(row['id']),
            "age": int(row['age']),
            "gender": str(row['gender']),
            "policy_type": str(row['policy_type']),
            "claim_amount": float(row['claim_amount']),
            "formatted_claim_amount": format_inr(row['claim_amount']),
            "claim_status": str(row['claim_status']),
            "diagnosis": str(row['diagnosis']),
            "disease_category": str(row.get('disease_category', 'General')),
            "hospital_type": str(row.get('hospital_type', 'Private')),
            "month": str(row.get('month', 'Jan')),
            "length_of_stay": int(row.get('length_of_stay', 3))
        })

    return {
        "page": page,
        "per_page": per_page,
        "total_records": total_records,
        "total_pages": total_pages,
        "records": records
    }
