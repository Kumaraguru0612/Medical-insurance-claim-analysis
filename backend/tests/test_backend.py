import os
import sys
import unittest

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.data_service import get_dataset_summary, get_paginated_records, get_dashboard_kpis
from services.ml_service import train_and_evaluate_all_models, predict_claim_status
from services.prediction_service import predict_insurance_claim
from services.report_service import generate_project_report
from services.claim_analysis_service import analyze_individual_claim, get_curated_sample_claims

class TestMedicalInsuranceBackend(unittest.TestCase):
    
    def test_dataset_loading_and_summary(self):
        summary = get_dataset_summary()
        self.assertGreaterEqual(summary['total_rows'], 1338)
        self.assertGreaterEqual(summary['total_columns'], 7)
        print("[PASS] Dataset summary test passed:", summary['total_rows'], "rows.")

    def test_dashboard_kpis(self):
        kpis = get_dashboard_kpis()
        self.assertGreaterEqual(kpis['total_claims'], 1338)
        self.assertGreater(kpis['total_claim_amount'], 10000000)
        self.assertGreater(kpis['avg_claim_amount'], 10000)
        self.assertEqual(len(kpis['status_distribution']), 3)
        self.assertEqual(len(kpis['monthly_trend']), 12)
        print("[PASS] Dashboard KPIs test passed: Total Claims =", kpis['total_claims'], "Avg Amount =", kpis['formatted_avg_claim_amount'])

    def test_paginated_records(self):
        records = get_paginated_records(page=1, per_page=10)
        self.assertEqual(len(records['records']), 10)
        self.assertGreaterEqual(records['total_records'], 1338)
        print("[PASS] Paginated records test passed: 10 records retrieved.")

    def test_claim_status_classification_prediction(self):
        pred = predict_claim_status(
            age=45,
            gender='Male',
            policy_type='Individual',
            disease_category='Heart Disease',
            claim_amount=100000,
            hospital_type='Private',
            length_of_stay=3
        )
        self.assertIn(pred['predicted_status'], ['Approved', 'Rejected', 'Pending'])
        self.assertGreater(pred['probability'], 50.0)
        print(f"[PASS] Claim Status Prediction passed: {pred['predicted_status']} ({pred['probability_str']})")

    def test_regression_prediction_service(self):
        pred_non_smoker = predict_insurance_claim(age=30, sex='female', bmi=22.5, children=0, smoker='no', region='southwest')
        self.assertGreater(pred_non_smoker['predicted_charges'], 50000)
        print(f"[PASS] Regression Prediction test passed: INR {pred_non_smoker['predicted_charges']:,.2f}")

    def test_report_service(self):
        rep = generate_project_report()
        self.assertIn('title', rep)
        self.assertIn('executive_summary', rep)
        print("[PASS] Report generation test passed.")

    def test_sample_claims(self):
        samples = get_curated_sample_claims()
        self.assertEqual(len(samples), 5)
        print("[PASS] Curated sample claims list verified: 5 presets available.")

if __name__ == '__main__':
    unittest.main()
