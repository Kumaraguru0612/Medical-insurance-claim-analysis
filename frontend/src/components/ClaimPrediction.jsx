import React, { useState } from 'react';
import { 
  CheckCircle2, 
  XCircle, 
  Clock, 
  RotateCw, 
  ShieldCheck, 
  AlertTriangle,
  ArrowRight,
  Sliders,
  Sparkles
} from 'lucide-react';
import { predictClaimStatus } from '../services/api';
import { formatINR } from '../config/currency';

export default function ClaimPrediction() {
  const [age, setAge] = useState(45);
  const [gender, setGender] = useState('Male');
  const [policyType, setPolicyType] = useState('Individual');
  const [diseaseCategory, setDiseaseCategory] = useState('Heart Disease');
  const [claimAmount, setClaimAmount] = useState(100000);
  const [hospitalType, setHospitalType] = useState('Private');
  const [lengthOfStay, setLengthOfStay] = useState(3);

  const [prediction, setPrediction] = useState({
    predicted_status: 'Approved',
    probability: 82.4,
    probability_str: '82.4%',
    class_probabilities: { 'Approved': 82.4, 'Rejected': 10.2, 'Pending': 7.4 },
    indicators: [
      'Claim amount is within standard coverage threshold.',
      'Provider is an accredited Private healthcare facility.',
      'Standard critical illness clinical pathway for Heart Disease.'
    ]
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handlePredict = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await predictClaimStatus({
        age: Number(age),
        gender,
        policy_type: policyType,
        disease_category: diseaseCategory,
        claim_amount: Number(claimAmount),
        hospital_type: hospitalType,
        length_of_stay: Number(lengthOfStay)
      });
      setPrediction(res);
    } catch (err) {
      setError(err.message || 'Failed to generate prediction.');
    } finally {
      setLoading(false);
    }
  };

  const isApproved = prediction?.predicted_status === 'Approved';
  const isRejected = prediction?.predicted_status === 'Rejected';

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      
      {/* Alert Error */}
      {error && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-semibold">
          {error}
        </div>
      )}

      {/* Main Container Card Matching Fig 7 */}
      <div className="bg-white rounded-3xl p-6 sm:p-10 shadow-sm border border-slate-100">
        
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Left Form: Patient & Claim Details */}
          <div className="lg:col-span-7 space-y-5">
            <div>
              <h3 className="text-lg font-bold text-slate-900">
                Claim Status Prediction
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Enter patient and claim details to predict claim approval
              </p>
            </div>

            <form onSubmit={handlePredict} className="space-y-4 pt-2">
              
              {/* Age Field */}
              <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-3">
                <label className="text-xs font-semibold text-slate-700">
                  Age
                </label>
                <div className="sm:col-span-2">
                  <input
                    type="number"
                    min="18"
                    max="90"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                    required
                    className="w-full px-3.5 py-2 rounded-xl bg-slate-50 border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Gender Dropdown */}
              <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-3">
                <label className="text-xs font-semibold text-slate-700">
                  Gender
                </label>
                <div className="sm:col-span-2">
                  <select
                    value={gender}
                    onChange={(e) => setGender(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl bg-slate-50 border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 cursor-pointer"
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                  </select>
                </div>
              </div>

              {/* Policy Type Dropdown */}
              <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-3">
                <label className="text-xs font-semibold text-slate-700">
                  Policy Type
                </label>
                <div className="sm:col-span-2">
                  <select
                    value={policyType}
                    onChange={(e) => setPolicyType(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl bg-slate-50 border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 cursor-pointer"
                  >
                    <option value="Individual">Individual</option>
                    <option value="Family">Family</option>
                  </select>
                </div>
              </div>

              {/* Disease Category Dropdown */}
              <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-3">
                <label className="text-xs font-semibold text-slate-700">
                  Disease Category
                </label>
                <div className="sm:col-span-2">
                  <select
                    value={diseaseCategory}
                    onChange={(e) => setDiseaseCategory(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl bg-slate-50 border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 cursor-pointer"
                  >
                    <option value="Heart Disease">Heart Disease</option>
                    <option value="Cancer">Cancer</option>
                    <option value="Orthopedic">Orthopedic</option>
                    <option value="Respiratory">Respiratory</option>
                    <option value="Neurology">Neurology</option>
                    <option value="Gastro">Gastro</option>
                    <option value="Others">Others</option>
                  </select>
                </div>
              </div>

              {/* Claim Amount Field */}
              <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-3">
                <label className="text-xs font-semibold text-slate-700">
                  Claim Amount (₹)
                </label>
                <div className="sm:col-span-2">
                  <input
                    type="number"
                    min="5000"
                    max="10000000"
                    value={claimAmount}
                    onChange={(e) => setClaimAmount(e.target.value)}
                    required
                    className="w-full px-3.5 py-2 rounded-xl bg-slate-50 border border-slate-200 text-sm text-slate-800 font-mono font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Hospital Type Dropdown */}
              <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-3">
                <label className="text-xs font-semibold text-slate-700">
                  Hospital Type
                </label>
                <div className="sm:col-span-2">
                  <select
                    value={hospitalType}
                    onChange={(e) => setHospitalType(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl bg-slate-50 border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 cursor-pointer"
                  >
                    <option value="Private">Private</option>
                    <option value="Government">Government</option>
                    <option value="Charitable">Charitable</option>
                  </select>
                </div>
              </div>

              {/* Predict Button Matching Fig 7 */}
              <div className="pt-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-bold text-sm shadow-md shadow-blue-600/20 transition cursor-pointer flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {loading ? (
                    <>
                      <RotateCw className="w-4 h-4 animate-spin" />
                      <span>Evaluating Machine Learning Model...</span>
                    </>
                  ) : (
                    <span>Predict</span>
                  )}
                </button>
              </div>

            </form>
          </div>

          {/* Right Card: Prediction Result Card Matching Fig 7 */}
          <div className="lg:col-span-5 flex flex-col justify-center h-full">
            <div className={`p-8 rounded-3xl border text-center transition-all shadow-xs ${
              isApproved 
                ? 'bg-emerald-50/60 border-emerald-200 text-emerald-950'
                : isRejected
                ? 'bg-rose-50/60 border-rose-200 text-rose-950'
                : 'bg-amber-50/60 border-amber-200 text-amber-950'
            }`}>
              
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-6">
                Prediction Result
              </span>

              {/* Big Circular Checkmark Icon */}
              <div className="w-20 h-20 mx-auto rounded-full flex items-center justify-center shadow-md mb-4 bg-emerald-600 text-white">
                {isApproved ? (
                  <CheckCircle2 className="w-12 h-12" strokeWidth={2.2} />
                ) : isRejected ? (
                  <XCircle className="w-12 h-12 text-white" strokeWidth={2.2} />
                ) : (
                  <Clock className="w-12 h-12 text-white" strokeWidth={2.2} />
                )}
              </div>

              {/* Predicted Status Text */}
              <h2 className={`text-2xl sm:text-3xl font-black tracking-tight ${
                isApproved ? 'text-emerald-700' : isRejected ? 'text-rose-700' : 'text-amber-700'
              }`}>
                {prediction?.predicted_status || 'Approved'}
              </h2>

              {/* Probability */}
              <div className="text-sm sm:text-base font-bold text-slate-700 mt-2 font-mono">
                Probability: <span className="text-slate-900">{prediction?.probability_str || '82.4%'}</span>
              </div>

              {/* Explainable Indicators */}
              {prediction?.indicators && (
                <div className="mt-6 pt-5 border-t border-slate-200/60 text-left text-xs text-slate-600 space-y-1.5">
                  <span className="font-semibold text-slate-700 block text-[11px] uppercase">
                    Audit Verification Signals:
                  </span>
                  {prediction.indicators.map((ind, idx) => (
                    <div key={idx} className="flex items-start gap-2 text-[11px]">
                      <span className="text-emerald-600 font-bold">✓</span>
                      <span>{ind}</span>
                    </div>
                  ))}
                </div>
              )}

            </div>
          </div>

        </div>

      </div>

    </div>
  );
}
