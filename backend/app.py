import os
import sys
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.data_service import (
    get_dataset_summary, 
    get_paginated_records, 
    get_dashboard_kpis,
    upload_and_set_dataset,
    reset_to_default_dataset,
    load_raw_dataset
)
from services.preprocessing_service import run_preprocessing_audit
from services.analysis_service import get_comprehensive_analysis
from services.visualization_service import get_visualization_payloads
from services.feature_selection_service import calculate_feature_selection
from services.ml_service import train_and_evaluate_all_models, predict_claim_status
from services.prediction_service import predict_insurance_claim
from services.report_service import generate_project_report
from services.claim_analysis_service import analyze_individual_claim, get_curated_sample_claims
from services.risk_intelligence_service import (
    get_risk_intelligence_summary,
    get_filtered_risk_claims,
    get_claim_investigation_details
)

DIST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'dist')

app = Flask(__name__, static_folder=DIST_DIR, static_url_path='')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Centralized error handler for API routes
@app.errorhandler(Exception)
def handle_exception(e):
    if request.path.startswith('/api/'):
        return jsonify({
            "success": False,
            "error": str(e),
            "type": type(e).__name__
        }), 500
    raise e

# ----------------- API ROUTES ----------------- #

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "project": "Medical Insurance Claim Analysis",
        "version": "2.0.0",
        "chatbot_enabled": False
    })

# 1. Authentication (Fig 1)
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    role = data.get('role', 'Claims Officer')

    # Demo credentials or any non-empty password
    if username and password:
        return jsonify({
            "success": True,
            "token": "demo-jwt-token-mediclaim-2026",
            "user": {
                "username": username,
                "name": username.replace('.', ' ').title() if username != 'admin' else 'Administrator',
                "role": role,
                "email": f"{username.lower().replace(' ', '')}@mediclaim.ai"
            }
        })
    else:
        return jsonify({
            "success": False,
            "message": "Please enter username and password"
        }), 400

# 2. Dashboard KPIs & Charts (Fig 2)
@app.route('/api/dashboard/kpis', methods=['GET'])
def dashboard_kpis():
    kpis = get_dashboard_kpis()
    return jsonify({"success": True, "data": kpis})

# 3. Dataset Upload (Fig 3)
@app.route('/api/dataset/upload', methods=['POST'])
def upload_dataset():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected."}), 400
        content = file.read()
        res = upload_and_set_dataset(content, filename=file.filename)
        return jsonify({"success": True, "data": res, "message": "Dataset uploaded and analyzed successfully."})
    
    data = request.get_json(silent=True) or {}
    if 'csv_content' in data:
        filename = data.get('filename', 'uploaded_claims.csv')
        res = upload_and_set_dataset(data['csv_content'], filename=filename)
        return jsonify({"success": True, "data": res, "message": "Dataset uploaded and analyzed successfully."})
    
    return jsonify({"success": False, "error": "No CSV file or content provided."}), 400

# 4. Reset Dataset
@app.route('/api/dataset/reset', methods=['POST'])
def reset_dataset():
    res = reset_to_default_dataset()
    return jsonify({"success": True, "data": res, "message": "Dataset reset to default canonical dataset."})

# 5. Dataset Summary & Metadata
@app.route('/api/dataset/summary', methods=['GET'])
def dataset_summary():
    summary = get_dataset_summary()
    return jsonify({"success": True, "data": summary})

# 6. Paginated Dataset Records (Fig 4)
@app.route('/api/dataset/records', methods=['GET'])
def dataset_records():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'id')
    sort_dir = request.args.get('sort_dir', 'asc')
    
    filters = {
        'claim_status': request.args.get('claim_status', 'all'),
        'disease_category': request.args.get('disease_category', 'all'),
        'gender': request.args.get('gender', 'all')
    }

    result = get_paginated_records(page, per_page, search, sort_by, sort_dir, filters)
    return jsonify({"success": True, "data": result})

# 7. Comprehensive Analysis (Fig 5 & Fig 6)
@app.route('/api/analysis', methods=['GET'])
def exploratory_analysis():
    kpis = get_dashboard_kpis()
    try:
        deep_analysis = get_comprehensive_analysis()
    except Exception as err:
        print(f"Deep analysis error: {err}")
        deep_analysis = {}
    return jsonify({
        "success": True, 
        "data": {
            "disease_category_analysis": kpis.get('disease_category_analysis', []),
            "monthly_trend": kpis.get('monthly_trend', []),
            "status_distribution": kpis.get('status_distribution', []),
            "gender_analysis": kpis.get('gender_analysis', []),
            "hospital_type_analysis": kpis.get('hospital_type_analysis', []),
            "deep_analysis": deep_analysis
        }
    })

# 8. Claim Status Prediction (Fig 7)
@app.route('/api/predict/claim-status', methods=['POST'])
def predict_claim_approval():
    data = request.get_json(silent=True) or {}
    age = data.get('age', 45)
    gender = data.get('gender', 'Male')
    policy_type = data.get('policy_type', 'Individual')
    disease_category = data.get('disease_category', 'Heart Disease')
    claim_amount = data.get('claim_amount', 100000)
    hospital_type = data.get('hospital_type', 'Private')
    length_of_stay = data.get('length_of_stay', 3)

    result = predict_claim_status(
        age=age,
        gender=gender,
        policy_type=policy_type,
        disease_category=disease_category,
        claim_amount=claim_amount,
        hospital_type=hospital_type,
        length_of_stay=length_of_stay
    )
    return jsonify({"success": True, "data": result})

# 9. Regression Claim Amount Prediction (What-If)
@app.route('/api/predict', methods=['POST'])
def predict_claim():
    data = request.get_json(silent=True) or {}
    age = data.get('age', 35)
    sex = data.get('sex', 'female')
    bmi = data.get('bmi', 28.5)
    children = data.get('children', 1)
    smoker = data.get('smoker', 'no')
    region = data.get('region', 'southeast')

    result = predict_insurance_claim(age, sex, bmi, children, smoker, region)
    return jsonify({"success": True, "data": result})

# 10. ML Models Training & Evaluation
@app.route('/api/models/train', methods=['GET', 'POST'])
def train_models():
    result = train_and_evaluate_all_models()
    return jsonify({"success": True, "data": result})

# 11. Project Summary Report (Fig 8)
@app.route('/api/report', methods=['GET'])
@app.route('/api/report/summary', methods=['GET'])
def get_report():
    kpis = get_dashboard_kpis()
    rep = generate_project_report()
    rep['kpis'] = kpis
    return jsonify({"success": True, "data": rep})

# 12. Claim Analysis & Risk Scoring
@app.route('/api/claims/sample-list', methods=['GET'])
def get_sample_claims():
    samples = get_curated_sample_claims()
    return jsonify({"success": True, "data": samples})

@app.route('/api/claims/analyze', methods=['POST'])
def analyze_claim():
    data = request.get_json(silent=True) or {}
    result = analyze_individual_claim(data)
    return jsonify({"success": True, "data": result})

# 13. Risk Intelligence
@app.route('/api/risk-intelligence/summary', methods=['GET'])
def get_risk_summary():
    summary = get_risk_intelligence_summary()
    return jsonify({"success": True, "data": summary})

@app.route('/api/risk-intelligence/claims', methods=['GET'])
def get_risk_claims():
    search = request.args.get('search', '').strip()
    risk_level = request.args.get('risk_level', 'all').strip()
    anomaly_status = request.args.get('anomaly_status', 'all').strip()
    recommended_action = request.args.get('recommended_action', 'all').strip()
    amount_range = request.args.get('amount_range', 'all').strip()
    sort_by = request.args.get('sort_by', 'priority_rank').strip()
    sort_dir = request.args.get('sort_dir', 'asc').strip()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 15))

    data = get_filtered_risk_claims(
        search=search,
        risk_level=risk_level,
        anomaly_status=anomaly_status,
        recommended_action=recommended_action,
        amount_range=amount_range,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        per_page=per_page
    )
    return jsonify({"success": True, "data": data})

@app.route('/api/risk-intelligence/investigate/<int:claim_id>', methods=['GET'])
def investigate_claim(claim_id):
    try:
        data = get_claim_investigation_details(claim_id)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 404

# Serve Frontend SPA
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join(DIST_DIR, path)):
        return send_from_directory(DIST_DIR, path)
    elif os.path.exists(os.path.join(DIST_DIR, 'index.html')):
        return send_from_directory(DIST_DIR, 'index.html')
    else:
        return jsonify({
            "message": "Medical Insurance Claim Analysis Backend API is running.",
            "api_health": "/api/health",
            "dashboard_kpis": "/api/dashboard/kpis"
        })

if __name__ == '__main__':
    print("Starting Medical Insurance Claim Analysis API on port 5000...", flush=True)
    app.run(host='0.0.0.0', port=5000, debug=False)
