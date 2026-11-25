import pandas as pd
import numpy as np
import os

def generate_canonical_dataset():
    np.random.seed(42)
    n_records = 13487

    diseases = ['Heart Disease', 'Cancer', 'Orthopedic', 'Respiratory', 'Neurology', 'Gastro', 'Others']
    diagnoses_by_cat = {
        'Heart Disease': ['Heart Disease', 'Coronary Artery Disease', 'Cardiac Arrhythmia'],
        'Cancer': ['Breast Cancer', 'Lung Cancer', 'Lymphoma'],
        'Orthopedic': ['Fracture', 'Knee Pain', 'Spine Injury'],
        'Respiratory': ['Asthma', 'Pneumonia', 'Bronchitis'],
        'Neurology': ['Migraine', 'Stroke', 'Epilepsy'],
        'Gastro': ['Gastritis', 'Kidney Stone', 'Ulcer'],
        'Others': ['Diabetes', 'Hypertension', 'Thyroid']
    }

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    hospitals = ['Private', 'Government', 'Charitable']

    # First 10 exact rows from reference Fig 4
    first_10 = [
        (1, 34, 'Male', 'Individual', 125000, 'Approved', 'Diabetes', 'Others', 'Private', 'Mar', 3, 23.4, 0, 'no', 'southwest'),
        (2, 52, 'Female', 'Family', 98000, 'Rejected', 'Hypertension', 'Others', 'Government', 'Feb', 5, 29.1, 2, 'no', 'southeast'),
        (3, 45, 'Male', 'Individual', 67000, 'Approved', 'Fracture', 'Orthopedic', 'Private', 'Jan', 2, 26.5, 0, 'no', 'northwest'),
        (4, 29, 'Female', 'Individual', 45000, 'Pending', 'Gastritis', 'Gastro', 'Charitable', 'Apr', 1, 22.0, 0, 'no', 'northeast'),
        (5, 61, 'Male', 'Family', 156000, 'Approved', 'Heart Disease', 'Heart Disease', 'Private', 'May', 6, 31.2, 1, 'yes', 'southeast'),
        (6, 38, 'Female', 'Individual', 78000, 'Rejected', 'Migraine', 'Neurology', 'Government', 'Jun', 2, 24.8, 0, 'no', 'northwest'),
        (7, 47, 'Male', 'Family', 99000, 'Approved', 'Kidney Stone', 'Gastro', 'Private', 'Jul', 4, 28.3, 2, 'no', 'southwest'),
        (8, 36, 'Female', 'Individual', 62000, 'Approved', 'Thyroid', 'Others', 'Charitable', 'Aug', 2, 25.0, 0, 'no', 'northeast'),
        (9, 58, 'Male', 'Family', 134000, 'Pending', 'Knee Pain', 'Orthopedic', 'Private', 'Sep', 5, 30.5, 1, 'yes', 'southeast'),
        (10, 42, 'Female', 'Individual', 85000, 'Approved', 'Asthma', 'Respiratory', 'Government', 'Oct', 3, 27.4, 0, 'no', 'northwest')
    ]

    records = []
    for r in first_10:
        records.append({
            'id': r[0], 'age': r[1], 'gender': r[2], 'policy_type': r[3],
            'claim_amount': r[4], 'claim_status': r[5], 'diagnosis': r[6],
            'disease_category': r[7], 'hospital_type': r[8], 'month': r[9],
            'length_of_stay': r[10], 'bmi': r[11], 'children': r[12], 'smoker': r[13], 'region': r[14]
        })

    month_weights = [0.038, 0.052, 0.062, 0.078, 0.068, 0.089, 0.102, 0.124, 0.108, 0.101, 0.078, 0.100]
    month_weights = [w / sum(month_weights) for w in month_weights]

    status_choices = ['Approved', 'Rejected', 'Pending']
    status_weights = [0.662, 0.186, 0.152]

    # Target disease category average claim amounts (Fig 5):
    # Heart: ~180k, Cancer: ~150k, Orthopedic: ~95k, Neurology: ~85k, Gastro: ~70k, Respiratory: ~60k, Others: ~55k
    disease_params = {
        'Heart Disease': (180000, 18000),
        'Cancer': (150000, 15000),
        'Orthopedic': (95000, 10000),
        'Neurology': (85000, 9000),
        'Gastro': (70000, 7500),
        'Respiratory': (60000, 6500),
        'Others': (55000, 6000)
    }
    disease_probs = [0.15, 0.12, 0.16, 0.14, 0.14, 0.15, 0.14]
    disease_probs = [p / sum(disease_probs) for p in disease_probs]

    for i in range(11, n_records + 1):
        age = int(np.random.randint(18, 65))
        gender = np.random.choice(['Male', 'Female'], p=[0.53, 0.47])
        policy_type = np.random.choice(['Individual', 'Family'], p=[0.58, 0.42])
        
        disease = np.random.choice(diseases, p=disease_probs)
        diag = np.random.choice(diagnoses_by_cat[disease])
        
        mean_val, std_val = disease_params[disease]
        base_amt = int(np.random.normal(mean_val, std_val))
        
        hosp = np.random.choice(hospitals, p=[0.50, 0.35, 0.15])
        if hosp == 'Private':
            base_amt = int(base_amt * 1.05)
        elif hosp == 'Charitable':
            base_amt = int(base_amt * 0.95)
        
        claim_amount = max(20000, min(350000, base_amt))
        month = np.random.choice(months, p=month_weights)
        
        if claim_amount > 190000:
            c_status = np.random.choice(status_choices, p=[0.48, 0.34, 0.18])
        elif claim_amount < 70000:
            c_status = np.random.choice(status_choices, p=[0.75, 0.12, 0.13])
        else:
            c_status = np.random.choice(status_choices, p=status_weights)
        
        los = int(max(1, min(14, int(claim_amount / 24000) + np.random.randint(0, 2))))
        bmi = round(float(np.random.normal(27.5, 4.2)), 1)
        bmi = max(16.0, min(48.0, bmi))
        children = int(np.random.choice([0, 1, 2, 3, 4], p=[0.45, 0.25, 0.18, 0.08, 0.04]))
        smoker = 'yes' if (disease in ['Heart Disease', 'Cancer', 'Respiratory'] and np.random.rand() < 0.35) else ('yes' if np.random.rand() < 0.15 else 'no')
        region = np.random.choice(['southeast', 'southwest', 'northeast', 'northwest'])
        
        records.append({
            'id': i, 'age': age, 'gender': gender, 'policy_type': policy_type,
            'claim_amount': claim_amount, 'claim_status': c_status, 'diagnosis': diag,
            'disease_category': disease, 'hospital_type': hosp, 'month': month,
            'length_of_stay': los, 'bmi': bmi, 'children': children, 'smoker': smoker, 'region': region
        })

    df = pd.DataFrame(records)
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'insurance_claims.csv')
    df.to_csv(out_path, index=False)
    
    total_amt = df['claim_amount'].sum()
    avg_amt = df['claim_amount'].mean()
    print(f"Generated {len(df)} records at {out_path}")
    print(f"Total: Rs. {total_amt:,} ({total_amt/1e7:.1f} Cr)")
    print(f"Avg: Rs. {avg_amt:,.0f}")
    print("Status counts and percentages:")
    print(df['claim_status'].value_counts())
    print((df['claim_status'].value_counts(normalize=True) * 100).round(1))
    print("\nDisease Category Averages (Fig 5):")
    print(df.groupby('disease_category')['claim_amount'].mean().round())

if __name__ == '__main__':
    generate_canonical_dataset()
