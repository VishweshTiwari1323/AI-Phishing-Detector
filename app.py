import base64
import logging
import os
import pickle
import re
from urllib.parse import urlparse

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from forms import BatchScanForm, LoginForm, SignupForm, URLScanForm
from models import ScanHistory, db
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)

# ---------------- VERCEL WSGI PATH ROUTING FIX ----------------
class VercelPathMiddleware:
    """Extracts the actual requested URL from Vercel headers so sub-routes work."""
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        raw_path = (
            environ.get("HTTP_X_MATCHED_PATH")
            or environ.get("HTTP_X_FORWARDED_PATH")
            or environ.get("HTTP_X_ORIGINAL_URI")
            or environ.get("RAW_URI")
            or environ.get("PATH_INFO", "")
        )
        
        raw_path = raw_path.split("?")[0]

        for prefix in ("/api/index.py", "/api/index", "/api", "/app.py", "/app"):
            if raw_path.startswith(prefix):
                raw_path = raw_path[len(prefix):] or "/"
                break

        if not raw_path.startswith("/"):
            raw_path = "/" + raw_path

        environ["PATH_INFO"] = raw_path
        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathMiddleware(app.wsgi_app)

# ---------------- CONFIGURATION & DATABASE SETUP ----------------

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "dev-insecure-key-change-me"
)
app.config["WTF_CSRF_ENABLED"] = False  # Allows standard form submission

# Set writable SQLite path in /tmp for Vercel Serverless
if os.environ.get("VERCEL") or not os.access(".", os.W_OK):
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/phishing.db"
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'phishing.db')}"
    )
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        logger.warning(f"Database init warning: {e}")

app.jinja_env.globals["hasattr"] = hasattr

# ---------------- MODEL LOADING ----------------

VECTORIZER_PATH = os.path.join(BASE_DIR, "vectorizer.pkl")
MODEL_PATH = os.path.join(BASE_DIR, "phishing_mnb.pkl")
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = os.path.join(BASE_DIR, "phishing.pkl")

vector = None
model = None

try:
    if os.path.exists(VECTORIZER_PATH) and os.path.exists(MODEL_PATH):
        with open(VECTORIZER_PATH, "rb") as f:
            vector = pickle.load(f)
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        logger.info("ML models loaded successfully.")
    else:
        logger.warning(f"Model or vectorizer not found at: {MODEL_PATH}")
except Exception as e:
    logger.error(f"Failed to load ML models: {e}")

# ---------------- VIRUSTOTAL CONFIGURATION ----------------

VT_API_KEY = os.environ.get(
    "VT_API_KEY",
    "b91d175a771c3f5820804894c6bc7f6d70a3584e2260e44b1d03abba081192ee",
).strip()

# ---------------- HELPER UTILITIES ----------------

def validate_url(url: str):
    """Validates and formats the input URL."""
    if not url or len(url.strip()) < 4:
        return False, "URL is too short"

    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False, "Invalid URL structure"
        return True, url
    except Exception:
        return False, "Invalid URL format"


def perform_ml_prediction(cleaned_url: str):
    """Performs inference using the loaded Vectorizer and ML Model."""
    if not model or not vector:
        return "Model not loaded", 0.0

    try:
        transformed_url = vector.transform([cleaned_url])
        prediction = model.predict(transformed_url)[0]

        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(transformed_url)[0]
            confidence = float(max(probabilities))
        else:
            confidence = 1.0

        pred_str = str(prediction).strip().lower()
        if pred_str in ("bad", "1", "phishing", "malicious"):
            return "Phishing Website", confidence
        elif pred_str in ("good", "0", "safe", "benign"):
            return "Safe Website", confidence
        return "Unknown", confidence
    except Exception as e:
        logger.error(f"ML Prediction error: {e}")
        return "Error", 0.0


def check_virustotal(url: str):
    """Queries the VirusTotal API v3 for URL telemetry."""
    empty_result = {
        "status": "VirusTotal API Key Missing" if not VT_API_KEY else "Error",
        "malicious": 0,
        "suspicious": 0,
        "harmless": 0,
        "undetected": 0,
        "vendors": {},
    }

    if not VT_API_KEY:
        return empty_result

    headers = {"x-apikey": VT_API_KEY}

    try:
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        response = requests.get(
            f"https://www.virustotal.com/api/v3/urls/{url_id}",
            headers=headers,
            timeout=6,
        )

        if response.status_code == 404:
            requests.post(
                "https://www.virustotal.com/api/v3/urls",
                headers=headers,
                data={"url": url},
                timeout=6,
            )
            empty_result["status"] = "Submitted for scanning"
            return empty_result

        if response.status_code != 200:
            empty_result["status"] = f"VirusTotal Error: {response.status_code}"
            return empty_result

        data = response.json()
        attributes = data.get("data", {}).get("attributes", {})
        stats = attributes.get("last_analysis_stats", {})
        vendors = attributes.get("last_analysis_results", {})

        return {
            "status": "Success",
            "malicious": stats.get("malicious", 0),
            "suspicious": stats.get("suspicious", 0),
            "harmless": stats.get("harmless", 0),
            "undetected": stats.get("undetected", 0),
            "vendors": vendors,
        }
    except requests.exceptions.Timeout:
        empty_result["status"] = "Request timeout"
        return empty_result
    except Exception as e:
        empty_result["status"] = f"Error: {str(e)}"
        return empty_result


def evaluate_vt_result(vt_data: dict):
    """Generates standardized verdict labels from VirusTotal responses."""
    status = vt_data.get("status")
    if status == "Submitted for scanning":
        return "URL submitted to VirusTotal. Try again in a few seconds."
    if status == "VirusTotal API Key Missing":
        return "VirusTotal API key is not configured."
    if status and ("Error" in status or status == "Request timeout"):
        return f"⚠️ {status}"

    malicious = vt_data.get("malicious", 0)
    suspicious = vt_data.get("suspicious", 0)

    if malicious > 0:
        return "⚠️ Malicious"
    if suspicious > 0:
        return "⚠️ Suspicious"
    return "✅ Safe"


# ---------------- ROUTE HANDLERS ----------------

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        return redirect(url_for("scan"))
    return render_template("index.html", form=form)


@app.route("/logout")
def logout():
    return redirect(url_for("login"))


@app.route("/scan", methods=["GET", "POST"])
def scan():
    form = URLScanForm()
    predict_ui = None
    url = ""
    confidence = 0.0
    vt_result = None
    malicious = suspicious = harmless = 0
    vendors = {}

    if request.method == "POST":
        raw_url = request.form.get("url", "").strip() or (form.url.data.strip() if form.url.data else "")
        is_valid, validated_url = validate_url(raw_url)

        if is_valid:
            url = validated_url
            cleaned_url = re.sub(r"^https?://(www\.)?", "", url)

            ml_result, confidence = perform_ml_prediction(cleaned_url)
            if ml_result == "Phishing Website":
                predict_ui = "⚠️ Phishing Website"
            elif ml_result == "Safe Website":
                predict_ui = "✅ Safe Website"
            else:
                predict_ui = "⚠️ Unknown"

            vt = check_virustotal(url)
            malicious = vt.get("malicious", 0)
            suspicious = vt.get("suspicious", 0)
            harmless = vt.get("harmless", 0)
            vendors = vt.get("vendors", {})
            vt_result = evaluate_vt_result(vt)

            try:
                scan_record = ScanHistory(
                    url=url,
                    cleaned_url=cleaned_url,
                    ml_prediction=ml_result,
                    vt_result=vt_result,
                    vt_malicious=malicious,
                    vt_suspicious=suspicious,
                    vt_harmless=harmless,
                    ip_address=request.remote_addr,
                )
                db.session.add(scan_record)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logger.error(f"Database write failed: {e}")
        else:
            flash(validated_url, "danger")

    return render_template(
        "scan.html",
        form=form,
        predict=predict_ui,
        url=url,
        confidence=confidence,
        vt_result=vt_result,
        malicious=malicious,
        suspicious=suspicious,
        harmless=harmless,
        vendors=vendors,
    )


@app.route("/batch-scan", methods=["GET", "POST"])
def batch_scan():
    form = BatchScanForm()
    results = []

    if request.method == "POST":
        raw_text = request.form.get("urls", "") or form.urls.data or ""
        urls = [u.strip() for u in raw_text.splitlines() if u.strip()]

        for u in urls[:25]:
            is_valid, validated_url = validate_url(u)

            if not is_valid:
                results.append(
                    {
                        "url": u,
                        "status": "Invalid URL",
                        "prediction": "Error",
                        "confidence": 0.0,
                        "vt_result": "N/A",
                        "vt_malicious": 0,
                        "vt_suspicious": 0,
                    }
                )
                continue

            cleaned_url = re.sub(r"^https?://(www\.)?", "", validated_url)
            ml_result, confidence = perform_ml_prediction(cleaned_url)
            vt = check_virustotal(validated_url)
            vt_result = evaluate_vt_result(vt)
            malicious_count = vt.get("malicious", 0)
            suspicious_count = vt.get("suspicious", 0)
            harmless_count = vt.get("harmless", 0)

            try:
                scan_record = ScanHistory(
                    url=validated_url,
                    cleaned_url=cleaned_url,
                    ml_prediction=ml_result,
                    vt_result=vt_result,
                    vt_malicious=malicious_count,
                    vt_suspicious=suspicious_count,
                    vt_harmless=harmless_count,
                    ip_address=request.remote_addr,
                )
                db.session.add(scan_record)
            except Exception as e:
                logger.error(f"Error prepping batch record: {e}")

            results.append(
                {
                    "url": validated_url,
                    "status": "Success",
                    "prediction": ml_result,
                    "confidence": confidence,
                    "vt_result": vt_result,
                    "vt_malicious": malicious_count,
                    "vt_suspicious": suspicious_count,
                }
            )

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to commit batch scans: {e}")

    return render_template(
        "batch_scan_refactored.html", form=form, results=results
    )


@app.route("/history", methods=["GET"])
def history():
    page = request.args.get("page", 1, type=int)
    per_page = 20
    scans = ScanHistory.query.order_by(
        ScanHistory.scan_timestamp.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    total_scans = ScanHistory.query.count()
    malicious_count = ScanHistory.query.filter(
        ScanHistory.vt_malicious > 0
    ).count()
    safe_count = ScanHistory.query.filter(
        ScanHistory.vt_malicious == 0, ScanHistory.vt_suspicious == 0
    ).count()
    suspicious_count = ScanHistory.query.filter(
        ScanHistory.vt_suspicious > 0, ScanHistory.vt_malicious == 0
    ).count()

    return render_template(
        "history_refactored.html",
        scans=scans,
        total_scans=total_scans,
        malicious_count=malicious_count,
        safe_count=safe_count,
        suspicious_count=suspicious_count,
    )


@app.route("/dashboard", methods=["GET"])
def dashboard():
    total_scans = ScanHistory.query.count()
    phishing_count = ScanHistory.query.filter(
        ScanHistory.ml_prediction == "Phishing Website"
    ).count()
    safe_count = ScanHistory.query.filter(
        ScanHistory.ml_prediction == "Safe Website"
    ).count()
    recent_scans = (
        ScanHistory.query.order_by(ScanHistory.scan_timestamp.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "dashboard_refactored.html",
        total_scans=total_scans,
        phishing_count=phishing_count,
        safe_count=safe_count,
        recent_scans=recent_scans,
    )


@app.route("/api/scan", methods=["POST"])
def api_scan():
    if not request.is_json:
        return jsonify({"error": "Missing JSON body"}), 400

    data = request.get_json()
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"error": "URL is required"}), 400

    is_valid, validated_url = validate_url(url)

    if not is_valid:
        return jsonify({"error": validated_url}), 400

    cleaned_url = re.sub(r"^https?://(www\.)?", "", validated_url)

    ml_result, confidence = perform_ml_prediction(cleaned_url)
    predict_ui = (
        "Phishing Website"
        if ml_result == "Phishing Website"
        else ("Safe Website" if ml_result == "Safe Website" else "Unknown")
    )

    vt = check_virustotal(validated_url)
    vt_result = evaluate_vt_result(vt)
    malicious = vt.get("malicious", 0)
    suspicious = vt.get("suspicious", 0)
    harmless = vt.get("harmless", 0)
    undetected = vt.get("undetected", 0)

    scan_id = None
    try:
        scan_record = ScanHistory(
            url=validated_url,
            cleaned_url=cleaned_url,
            ml_prediction=ml_result,
            vt_result=vt_result,
            vt_malicious=malicious,
            vt_suspicious=suspicious,
            vt_harmless=harmless,
            vt_undetected=undetected,
            ip_address=request.remote_addr,
        )
        db.session.add(scan_record)
        db.session.commit()
        scan_id = scan_record.id
    except Exception as e:
        db.session.rollback()
        logger.error(f"API scan database write failed: {e}")

    return jsonify(
        {
            "url": validated_url,
            "ml_prediction": predict_ui,
            "confidence": confidence,
            "virustotal": {
                "status": vt.get("status", "Error"),
                "malicious": malicious,
                "suspicious": suspicious,
                "harmless": harmless,
                "undetected": undetected,
            },
            "scan_id": scan_id,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)