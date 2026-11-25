import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from app import app

if __name__ == '__main__':
    print("Starting Flask server on http://127.0.0.1:5000...", flush=True)
    app.run(host='0.0.0.0', port=5000, debug=False)
