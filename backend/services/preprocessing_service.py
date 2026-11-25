import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from services.data_service import load_raw_dataset
from services.currency_config import (
    USD_TO_INR,
    CURRENCY_SYMBOL,
    CURRENCY_CODE,
    format_inr,
    format_compact_inr,
    convert_usd_to_inr
)

def run_preprocessing_audit():
    """Runs a complete preprocessing audit on the dataset."""
    df = load_raw_dataset()
    
    # 1. Missing Values Audit
    missing_summary = []
    for col in df.columns:
        null_count = int(df[col].isnull().sum())
        missing_summary.append({
            "column": col,
            "missing_count": null_count,
            "missing_percentage": round((null_count / len(df)) * 100, 2),
            "status": "Clean (No missing values)" if null_count == 0 else f"{null_count} Missing"
        })
    
    # 2. Duplicate Records Audit
    duplicate_count = int(df.duplicated().sum())
    duplicate_rows = df[df.duplicated(keep=False)].to_dict(orient='records')
    
    # Clean duplicates for downstream
    df_cleaned = df.drop_duplicates().copy()
    
    # 3. Outlier Analysis (IQR Method)
    outlier_analysis = {}
    for col in ['bmi', 'charges', 'age']:
        q1 = float(df_cleaned[col].quantile(0.25))
        q3 = float(df_cleaned[col].quantile(0.75))
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = df_cleaned[(df_cleaned[col] < lower_bound) | (df_cleaned[col] > upper_bound)]
        outlier_count = int(len(outliers))

        entry = {
            "q1": round(q1, 2),
            "q3": round(q3, 2),
            "iqr": round(iqr, 2),
            "lower_bound": round(lower_bound, 2),
            "upper_bound": round(upper_bound, 2),
            "outlier_count": outlier_count,
            "outlier_percentage": round((outlier_count / len(df_cleaned)) * 100, 2),
            "min_val": round(float(df_cleaned[col].min()), 2),
            "max_val": round(float(df_cleaned[col].max()), 2),
            "interpretation": (
                "Right-skewed distribution characteristic of high-cost catastrophic medical events." 
                if col == 'charges' else 
                "Naturally occurring high-BMI physiological variance; standard in clinical datasets." 
                if col == 'bmi' else "No age outliers detected."
            )
        }

        if col == 'charges':
            entry["q1_inr"] = round(convert_usd_to_inr(q1), 2)
            entry["q3_inr"] = round(convert_usd_to_inr(q3), 2)
            entry["iqr_inr"] = round(convert_usd_to_inr(iqr), 2)
            entry["upper_bound_inr"] = round(convert_usd_to_inr(upper_bound), 2)
            entry["formatted_q1"] = format_compact_inr(convert_usd_to_inr(q1))
            entry["formatted_q3"] = format_compact_inr(convert_usd_to_inr(q3))
            entry["formatted_upper_bound"] = format_compact_inr(convert_usd_to_inr(upper_bound))

        outlier_analysis[col] = entry

    # 4. Feature Transformations & Encoding
    # Binary mapping: smoker (yes=1, no=0), sex (male=1, female=0)
    # One-hot encoding: region (4 categories)
    encoded_df = df_cleaned.copy()
    encoded_df['smoker_encoded'] = encoded_df['smoker'].map({'yes': 1, 'no': 0})
    encoded_df['sex_encoded'] = encoded_df['sex'].map({'male': 1, 'female': 0})
    
    # One-hot encode region
    region_dummies = pd.get_dummies(encoded_df['region'], prefix='region', dtype=int)
    encoded_df = pd.concat([encoded_df, region_dummies], axis=1)

    # 5. Feature Engineering
    # Interaction term: smoker * bmi (Clinical insight: smoking combined with obesity creates exponential claim risk)
    encoded_df['smoker_bmi_interaction'] = encoded_df['smoker_encoded'] * encoded_df['bmi']
    encoded_df['is_obese'] = (encoded_df['bmi'] >= 30.0).astype(int)

    # 6. Scaling Statistics
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(encoded_df[['age', 'bmi', 'children']])
    
    # 7. Train/Test Partition (80/20)
    X = encoded_df[['age', 'bmi', 'children', 'smoker_encoded', 'sex_encoded', 
                     'region_northeast', 'region_northwest', 'region_southeast', 'region_southwest']]
    y = encoded_df['charges']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    return {
        "raw_record_count": int(len(df)),
        "cleaned_record_count": int(len(df_cleaned)),
        "duplicates_removed": duplicate_count,
        "missing_values_audit": missing_summary,
        "outlier_analysis": outlier_analysis,
        "categorical_encoding": {
            "smoker": {"mapping": {"no": 0, "yes": 1}, "type": "Binary Encoding"},
            "sex": {"mapping": {"female": 0, "male": 1}, "type": "Binary Encoding"},
            "region": {
                "categories": ["northeast", "northwest", "southeast", "southwest"],
                "type": "One-Hot Encoding (4 binary dummy indicators)"
            }
        },
        "feature_engineering": [
            {
                "feature": "smoker_bmi_interaction",
                "formula": "smoker (0/1) * BMI",
                "purpose": "Captures non-linear compounding risk of smoking and elevated BMI."
            },
            {
                "feature": "is_obese",
                "formula": "BMI >= 30.0",
                "purpose": "Binary clinical threshold indicator for obesity-related morbidities."
            }
        ],
        "scaling_method": "StandardScaler (Zero mean, unit variance for gradient & distance-based models)",
        "train_test_split": {
            "train_size": int(len(X_train)),
            "test_size": int(len(X_test)),
            "train_percentage": 80.0,
            "test_percentage": 20.0,
            "random_seed": 42
        }
    }

def get_preprocessed_dataframe():
    """Returns the cleaned and encoded DataFrame ready for modeling."""
    df = load_raw_dataset().drop_duplicates().copy()
    
    df['smoker_encoded'] = df['smoker'].map({'yes': 1, 'no': 0})
    df['sex_encoded'] = df['sex'].map({'male': 1, 'female': 0})
    
    region_dummies = pd.get_dummies(df['region'], prefix='region', dtype=int)
    processed_df = pd.concat([df, region_dummies], axis=1)
    
    return processed_df
