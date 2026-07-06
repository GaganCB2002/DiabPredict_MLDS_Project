from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import numpy as np
import os
import sqlite3
import datetime

app = Flask(__name__,
            template_folder='frontend/templates',
            static_folder='frontend/static')
app.secret_key = "super_secret_key_for_diabpredict_ai"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role


@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return User(id=row[0], username=row[1], role=row[2])
    return None

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model_parameters.csv")

import os
# Use /tmp for writable SQLite database in Vercel Serverless environments
if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/hms.db"
else:
    DB_PATH = "hms.db"

COLUMNS_V1 = [
    "pregnancies",
    "glucose",
    "bloodPressure",
    "skinThickness",
    "insulin",
    "bmi",
    "diabetesPedigreeFunction",
    "age",
]


def load_model():
    if not os.path.exists(MODEL_PATH):
        print("Warning: model_parameters.csv not found. Please run model.py")
        return None
    df = pd.read_csv(MODEL_PATH)
    intercept = df[df["Feature"] == "Intercept"]["Weight"].values[0]
    feature_rows = df[df["Feature"] != "Intercept"]
    features = list(feature_rows["Feature"])
    weights = feature_rows["Weight"].values
    means = feature_rows["Mean"].values
    scales = feature_rows["Scale"].values
    return {
        "intercept": intercept,
        "features": features,
        "weights": weights,
        "means": means,
        "scales": scales,
    }


try:
    model_data = load_model()
except Exception as e:
    print(f"Warning: Failed to load model: {e}")
    model_data = None


def log_audit(user_id, action):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO audit_logs (user_id, action, timestamp) VALUES (?, ?, ?)",
            (user_id, action, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                email TEXT,
                phone TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles_doctor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                specialization TEXT,
                department TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles_patient (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                dob TEXT,
                gender TEXT,
                blood_group TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                doctor_id INTEGER,
                appointment_date TEXT,
                status TEXT DEFAULT 'Scheduled',
                FOREIGN KEY (patient_id) REFERENCES users (id),
                FOREIGN KEY (doctor_id) REFERENCES users (id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                timestamp TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consultations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                doctor_id INTEGER,
                date TEXT,
                symptoms TEXT,
                diagnosis TEXT,
                notes TEXT,
                FOREIGN KEY (patient_id) REFERENCES users (id),
                FOREIGN KEY (doctor_id) REFERENCES users (id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prescriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                consultation_id INTEGER,
                medicine_name TEXT,
                dosage TEXT,
                duration TEXT,
                FOREIGN KEY (consultation_id) REFERENCES consultations (id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                prediction INTEGER NOT NULL,
                probability REAL NOT NULL,
                timestamp TEXT NOT NULL,
                message TEXT NOT NULL,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        existing = [row[1] for row in cursor.execute("PRAGMA table_info(predictions)")]
        for col in COLUMNS_V1:
            if col not in existing:
                cursor.execute(
                    f"ALTER TABLE predictions ADD COLUMN {col} REAL DEFAULT 0"
                )

        cursor.execute("SELECT COUNT(*) FROM users")
        needs_seed = cursor.fetchone()[0] == 0
        if needs_seed:
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                ("admin", generate_password_hash("admin123"), "Admin"),
            )

            cursor.execute(
                "INSERT INTO users (username, password_hash, role, email, phone) VALUES (?, ?, ?, ?, ?)",
                (
                    "doctor",
                    generate_password_hash("doctor123"),
                    "Doctor",
                    "doctor@hospital.com",
                    "123-456-7890",
                ),
            )
            doc_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO profiles_doctor (user_id, specialization, department) VALUES (?, ?, ?)",
                (doc_id, "Endocrinologist", "Diabetology"),
            )

            cursor.execute(
                "INSERT INTO users (username, password_hash, role, email, phone) VALUES (?, ?, ?, ?, ?)",
                (
                    "patient",
                    generate_password_hash("patient123"),
                    "Patient",
                    "patient@email.com",
                    "098-765-4321",
                ),
            )
            pat_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO profiles_patient (user_id, dob, gender, blood_group) VALUES (?, ?, ?, ?)",
                (pat_id, "1990-05-15", "Male", "O+"),
            )
        conn.commit()
    if needs_seed:
        log_audit(1, "System Initialized & Seeded")


init_db()


@app.route("/")
def home():
    return render_template("index.html", current_user=current_user)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        data = request.get_json(silent=True) or request.form
        username = data.get("username")
        password = data.get("password")
        email = data.get("email")
        phone = data.get("phone")
        role = data.get("role")

        if not username or not password or role not in ["Patient", "Doctor"]:
            return jsonify({"error": "Missing required fields or invalid role"}), 400

        try:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute("SELECT id FROM users WHERE username = ?", (username,))
                if c.fetchone():
                    return jsonify({"error": "Username already exists"}), 400

                hashed_pw = generate_password_hash(password)
                c.execute(
                    "INSERT INTO users (username, password_hash, role, email, phone) VALUES (?, ?, ?, ?, ?)",
                    (username, hashed_pw, role, email, phone),
                )
                user_id = c.lastrowid

                if role == "Patient":
                    dob = data.get("dob") or "1990-01-01"
                    gender = data.get("gender") or "Other"
                    blood_group = data.get("blood_group") or "O+"
                    c.execute(
                        "INSERT INTO profiles_patient (user_id, dob, gender, blood_group) VALUES (?, ?, ?, ?)",
                        (user_id, dob, gender, blood_group),
                    )
                elif role == "Doctor":
                    specialization = data.get("specialization") or "General"
                    department = data.get("department") or "General Medicine"
                    c.execute(
                        "INSERT INTO profiles_doctor (user_id, specialization, department) VALUES (?, ?, ?)",
                        (user_id, specialization, department),
                    )

            return jsonify({"success": True, "redirect": url_for("login")})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json(silent=True) or request.form
        username = data.get("username")
        password = data.get("password")
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, password_hash, role FROM users WHERE username = ?",
                (username,),
            )
            row = cursor.fetchone()
            if row and check_password_hash(row[2], password):
                user = User(id=row[0], username=row[1], role=row[3])
                login_user(user)
                next_url = request.args.get("next") or url_for("home")
                return jsonify({"success": True, "redirect": next_url})
        return jsonify({"error": "Invalid username or password"}), 401
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/analysis")
@login_required
def analysis():
    return render_template("analysis.html")


@app.route("/admin")
@login_required
def admin_dashboard():
    if current_user.role != "Admin":
        return redirect(url_for("home"))
    return render_template("admin_dashboard.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)
    if not data or not data.get("message"):
        return jsonify({"error": "No message provided"}), 400
    msg = data["message"].lower()
    if "diabetes" in msg or "risk" in msg:
        reply = "Diabetes risk is calculated using 8 key metrics, including Glucose, BMI, and Age..."
    elif "glucose" in msg or "sugar" in msg:
        reply = "Normal fasting blood glucose levels are typically under 100 mg/dL..."
    elif "bmi" in msg or "weight" in msg:
        reply = "A healthy BMI is between 18.5 and 24.9..."
    elif "hello" in msg or "hi" in msg:
        reply = "Hello! I am your DiabPredict AI Assistant..."
    else:
        reply = "That's a great question. While I am an AI, I recommend discussing this with your healthcare provider..."
    return jsonify({"reply": reply})


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.get_json(silent=True) or request.form
        username = data.get("username", "").strip()
        password = data.get("password", "")
        role = data.get("role", "Patient")
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400
        if role not in ("Patient", "Doctor"):
            role = "Patient"
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username=?", (username,))
            if cursor.fetchone():
                return jsonify({"error": "Username already exists"}), 400
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, generate_password_hash(password), role),
            )
            user_id = cursor.lastrowid
            if role == "Patient":
                cursor.execute(
                    "INSERT INTO profiles_patient (user_id) VALUES (?)", (user_id,)
                )
            elif role == "Doctor":
                cursor.execute(
                    "INSERT INTO profiles_doctor (user_id) VALUES (?)", (user_id,)
                )
            conn.commit()
            log_audit(user_id, f"User registered: {username} ({role})")
        return jsonify(
            {"success": True, "message": "Registration successful. Please log in."}
        )
    return render_template("login.html", register_mode=True)


@app.route("/favicon.ico")
def favicon():
    return "", 204


def run_prediction(payload):
    data = {str(k).lower(): v for k, v in payload.items()}
    name = payload.get("name", "Patient")
    input_values = {}
    for col in COLUMNS_V1:
        raw_value = data.get(col.lower())
        if raw_value is None or raw_value == "":
            raw_value = 0
        input_values[col] = float(raw_value)
    feature_map = {f.lower(): f for f in COLUMNS_V1}
    input_data = []
    for feature in model_data["features"]:
        feature_key = feature.lower()
        canonical_key = feature_map.get(feature_key)
        if canonical_key is None:
            raw_value = 0
        else:
            raw_value = input_values[canonical_key]
        input_data.append(float(raw_value))
    input_array = np.array(input_data)
    scaled_input = (input_array - model_data["means"]) / model_data["scales"]
    z = np.dot(scaled_input, model_data["weights"]) + model_data["intercept"]
    probability = float(1 / (1 + np.exp(-z)))
    prediction = 1 if probability >= 0.5 else 0
    if prediction == 1:
        message = f"Based on the data, {name} is predicted to have diabetes."
    else:
        message = f"Based on the data, {name} is predicted to not have diabetes."
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cols = ",".join(COLUMNS_V1)
        placeholders = ",".join(["?"] * len(COLUMNS_V1))
        vals = [input_values[col] for col in COLUMNS_V1]
        user_id = current_user.id if current_user.is_authenticated else None
        cursor.execute(
            f"INSERT INTO predictions (name, prediction, probability, timestamp, message, user_id, {cols}) VALUES (?, ?, ?, ?, ?, ?, {placeholders})",
            (name, prediction, probability, timestamp, message, user_id, *vals),
        )
        conn.commit()
        last_id = cursor.lastrowid
    return {
        "id": last_id,
        "name": name,
        "prediction": prediction,
        "probability": probability,
        "message": message,
        "timestamp": timestamp,
        **input_values,
    }


@app.route("/predict", methods=["POST"])
def predict():
    if model_data is None:
        return jsonify({"error": "Model not loaded on the server."}), 500
    try:
        payload = request.get_json(silent=True)
        if payload is None:
            payload = request.form.to_dict()
        if payload is None:
            payload = {}
        result = run_prediction(payload)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/report", methods=["POST"])
def report():
    if model_data is None:
        return render_template("report.html", error="Model not loaded on the server.")
    try:
        payload = request.form.to_dict()
        result = run_prediction(payload)
        name = result.get("name", "")
        history = []
        if name:
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                cols_str = ",".join(["id","name","prediction","probability","timestamp","message"] + COLUMNS_V1)
                c.execute(f"SELECT {cols_str} FROM predictions WHERE LOWER(name) LIKE ? AND id != ? ORDER BY id DESC LIMIT 10", (f"%{name.lower()}%", result["id"]))
                history = [dict(r) for r in c.fetchall()]
        return render_template("report.html", result=result, history=history)
    except Exception as e:
        return render_template("report.html", error=str(e))


@app.route("/api/predictions/by-name", methods=["GET"])
def predictions_by_name():
    name = request.args.get("name", "").strip()
    if not name:
        return jsonify([])
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        cols_str = ",".join(["id","name","prediction","probability","timestamp","message"] + COLUMNS_V1)
        c.execute(f"SELECT {cols_str} FROM predictions WHERE LOWER(name) LIKE ? ORDER BY id DESC LIMIT 20", (f"%{name.lower()}%",))
        return jsonify([dict(r) for r in c.fetchall()])

@app.route("/api/prediction/<int:pred_id>", methods=["GET"])
def get_prediction(pred_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM predictions WHERE id = ?", (pred_id,))
        row = cursor.fetchone()
        if row is None:
            return jsonify({"error": "Prediction not found"}), 404
        return jsonify(dict(row))


@app.route("/api/prediction/<int:pred_id>", methods=["DELETE"])
def delete_prediction(pred_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM predictions WHERE id = ?", (pred_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Prediction not found"}), 404
        return jsonify({"success": True, "id": pred_id})


@app.route("/api/history", methods=["GET"])
def history():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cols_str = ",".join(
            [
                "id",
                "name",
                "prediction",
                "probability",
                "timestamp",
                "message",
                "user_id",
            ]
            + COLUMNS_V1
        )
        if current_user.is_authenticated:
            if current_user.role in ["Admin", "Doctor"]:
                cursor.execute(
                    f"SELECT {cols_str} FROM predictions ORDER BY id DESC LIMIT 100"
                )
            else:
                cursor.execute(
                    f"SELECT {cols_str} FROM predictions WHERE user_id = ? ORDER BY id DESC LIMIT 100",
                    (current_user.id,),
                )
        else:
            cursor.execute(
                f"SELECT {cols_str} FROM predictions WHERE user_id IS NULL ORDER BY id DESC LIMIT 10"
            )
        rows = cursor.fetchall()
        return jsonify([dict(ix) for ix in rows])


@app.route("/api/dashboard")
def dashboard_stats():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            "SELECT COUNT(*) as total, COALESCE(SUM(prediction),0) as high_risk, COALESCE(SUM(CASE WHEN prediction=0 THEN 1 ELSE 0 END),0) as low_risk FROM predictions"
        )
        row = dict(c.fetchone())
        c.execute(
            "SELECT COALESCE(AVG(bmi),0) as avg_bmi, COALESCE(AVG(glucose),0) as avg_glucose, COALESCE(AVG(age),0) as avg_age FROM predictions"
        )
        stats = dict(c.fetchone())
        c.execute(
            "SELECT name, prediction, probability, timestamp FROM predictions ORDER BY id DESC LIMIT 5"
        )
        recent = [dict(r) for r in c.fetchall()]
        c.execute(
            "SELECT COALESCE(AVG(probability),0) as avg_prob_high FROM predictions WHERE prediction=1"
        )
        avg_high = dict(c.fetchone())
        return jsonify(
            {
                "total": row["total"],
                "high_risk": row["high_risk"],
                "low_risk": row["low_risk"],
                "avg_bmi": round(stats["avg_bmi"], 1),
                "avg_glucose": round(stats["avg_glucose"], 1),
                "avg_age": round(stats["avg_age"], 1),
                "recent": recent,
                "avg_prob_high": round(avg_high["avg_prob_high"] * 100, 1),
            }
        )


@app.route("/api/admin/stats", methods=["GET"])
@login_required
def admin_stats():
    if current_user.role != "Admin":
        return jsonify({"error": "Unauthorized"}), 403
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users WHERE role='Patient'")
        patients = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM users WHERE role='Doctor'")
        doctors = c.fetchone()[0]
        c.execute(
            "SELECT COUNT(*) FROM appointments WHERE date(appointment_date) = date('now')"
        )
        appointments_today = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM predictions")
        predictions = c.fetchone()[0]
        c.execute("SELECT action, timestamp FROM audit_logs ORDER BY id DESC LIMIT 10")
        recent = [{"action": r[0], "timestamp": r[1]} for r in c.fetchall()]
    return jsonify(
        {
            "totalPatients": patients,
            "totalDoctors": doctors,
            "appointmentsToday": appointments_today,
            "predictionsCompleted": predictions,
            "hospitalOccupancy": str(
                min(round((predictions / max(patients + doctors, 1)) * 100), 100)
            )
            + "%",
            "recentActivity": recent,
        }
    )


@app.route("/doctor")
@login_required
def doctor_dashboard():
    if current_user.role != "Doctor":
        return redirect(url_for("home"))
    return render_template("doctor_dashboard.html")


@app.route("/api/doctor/patients", methods=["GET"])
@login_required
def doctor_patients():
    if current_user.role != "Doctor":
        return jsonify({"error": "Unauthorized"}), 403
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
            SELECT u.id, u.username, u.email, u.phone, p.dob, p.gender, p.blood_group,
                (SELECT COUNT(*) FROM predictions WHERE user_id = u.id) as prediction_count,
                (SELECT MAX(timestamp) FROM predictions WHERE user_id = u.id) as last_prediction
            FROM users u
            LEFT JOIN profiles_patient p ON u.id = p.user_id
            WHERE u.role = 'Patient'
            ORDER BY u.username
        """)
        return jsonify([dict(row) for row in c.fetchall()])


@app.route("/api/doctor/consultations", methods=["GET", "POST"])
@login_required
def doctor_consultations():
    if current_user.role != "Doctor":
        return jsonify({"error": "Unauthorized"}), 403
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        if request.method == "GET":
            patient_id = request.args.get("patient_id")
            if patient_id:
                c.execute(
                    """
                    SELECT c.id, c.patient_id, c.date, c.symptoms, c.diagnosis, c.notes,
                           u.username as patient_name
                    FROM consultations c
                    JOIN users u ON c.patient_id = u.id
                    WHERE c.patient_id = ?
                    ORDER BY c.date DESC
                """,
                    (patient_id,),
                )
            else:
                c.execute("""
                    SELECT c.id, c.patient_id, c.date, c.symptoms, c.diagnosis, c.notes,
                           u.username as patient_name
                    FROM consultations c
                    JOIN users u ON c.patient_id = u.id
                    ORDER BY c.date DESC
                """)
            consultations = [dict(row) for row in c.fetchall()]
            for cons in consultations:
                c.execute(
                    "SELECT id, medicine_name, dosage, duration FROM prescriptions WHERE consultation_id = ?",
                    (cons["id"],),
                )
                cons["prescriptions"] = [dict(r) for r in c.fetchall()]
            return jsonify(consultations)
        elif request.method == "POST":
            data = request.get_json()
            c.execute(
                """
                INSERT INTO consultations (patient_id, doctor_id, date, symptoms, diagnosis, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    data["patient_id"],
                    current_user.id,
                    data.get("date", datetime.datetime.now().strftime("%Y-%m-%d")),
                    data.get("symptoms", ""),
                    data.get("diagnosis", ""),
                    data.get("notes", ""),
                ),
            )
            cons_id = c.lastrowid
            for med in data.get("prescriptions", []):
                c.execute(
                    """
                    INSERT INTO prescriptions (consultation_id, medicine_name, dosage, duration)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        cons_id,
                        med.get("medicine_name"),
                        med.get("dosage"),
                        med.get("duration"),
                    ),
                )
            conn.execute(
                "INSERT INTO audit_logs (user_id, action, timestamp) VALUES (?, ?, ?)",
                (
                    current_user.id,
                    f"Added consultation for patient {data['patient_id']}",
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
            conn.commit()
            return jsonify({"success": True, "id": cons_id})


@app.route("/api/doctor/stats", methods=["GET"])
@login_required
def doctor_stats():
    if current_user.role != "Doctor":
        return jsonify({"error": "Unauthorized"}), 403
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users WHERE role='Patient'")
        patients = c.fetchone()[0]
        c.execute(
            "SELECT COUNT(*) FROM consultations WHERE doctor_id=?", (current_user.id,)
        )
        consult_count = c.fetchone()[0]
        c.execute(
            "SELECT COUNT(*) FROM appointments WHERE doctor_id=? AND date(appointment_date)=date('now')",
            (current_user.id,),
        )
        today_appts = c.fetchone()[0]
        c.execute(
            "SELECT COUNT(*) FROM appointments WHERE doctor_id=? AND status='Scheduled'",
            (current_user.id,),
        )
        pending = c.fetchone()[0]
    return jsonify(
        {
            "totalPatients": patients,
            "totalConsultations": consult_count,
            "todayAppointments": today_appts,
            "pendingAppointments": pending,
        }
    )


@app.route("/api/prediction/<int:pred_id>", methods=["PUT"])
def update_prediction(pred_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No data provided"}), 400
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        fields = []
        values = []
        if "name" in data:
            fields.append("name=?")
            values.append(data["name"])
        for col in COLUMNS_V1:
            if col in data:
                fields.append(f"{col}=?")
                values.append(float(data[col]))
        if not fields:
            return jsonify({"error": "No valid fields to update"}), 400
        values.append(pred_id)
        cursor.execute(f'UPDATE predictions SET {",".join(fields)} WHERE id=?', values)
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Prediction not found"}), 404
        return jsonify({"success": True, "id": pred_id})


@app.route("/api/doctor/predictions/<int:patient_id>", methods=["GET"])
@login_required
def doctor_patient_predictions(patient_id):
    if current_user.role != "Doctor":
        return jsonify({"error": "Unauthorized"}), 403
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        cols_str = ",".join(
            ["id", "name", "prediction", "probability", "timestamp", "message"]
            + COLUMNS_V1
        )
        c.execute(
            f"SELECT {cols_str} FROM predictions WHERE user_id = ? ORDER BY id DESC LIMIT 20",
            (patient_id,),
        )
        return jsonify([dict(row) for row in c.fetchall()])


@app.route("/api/admin/patients", methods=["GET", "POST"])
@login_required
def admin_patients():
    if current_user.role != "Admin":
        return jsonify({"error": "Unauthorized"}), 403
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        if request.method == "GET":
            c.execute(
                "SELECT u.id, u.username, u.email, u.phone, p.dob, p.gender, p.blood_group FROM users u LEFT JOIN profiles_patient p ON u.id = p.user_id WHERE u.role = 'Patient'"
            )
            return jsonify([dict(row) for row in c.fetchall()])
        elif request.method == "POST":
            data = request.get_json()
            c.execute(
                "INSERT INTO users (username, password_hash, role, email, phone) VALUES (?, ?, 'Patient', ?, ?)",
                (
                    data["username"],
                    generate_password_hash(data.get("password", "patient123")),
                    data.get("email"),
                    data.get("phone"),
                ),
            )
            pat_id = c.lastrowid
            c.execute(
                "INSERT INTO profiles_patient (user_id, dob, gender, blood_group) VALUES (?, ?, ?, ?)",
                (pat_id, data.get("dob"), data.get("gender"), data.get("blood_group")),
            )
            log_audit(current_user.id, f"Added Patient: {data['username']}")
            conn.commit()
            return jsonify({"success": True})


@app.route("/api/admin/doctors", methods=["GET", "POST"])
@login_required
def admin_doctors():
    if current_user.role != "Admin":
        return jsonify({"error": "Unauthorized"}), 403
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        if request.method == "GET":
            c.execute(
                "SELECT u.id, u.username, u.email, u.phone, d.specialization, d.department FROM users u LEFT JOIN profiles_doctor d ON u.id = d.user_id WHERE u.role = 'Doctor'"
            )
            return jsonify([dict(row) for row in c.fetchall()])
        elif request.method == "POST":
            data = request.get_json()
            c.execute(
                "INSERT INTO users (username, password_hash, role, email, phone) VALUES (?, ?, 'Doctor', ?, ?)",
                (
                    data["username"],
                    generate_password_hash(data.get("password", "doctor123")),
                    data.get("email"),
                    data.get("phone"),
                ),
            )
            doc_id = c.lastrowid
            c.execute(
                "INSERT INTO profiles_doctor (user_id, specialization, department) VALUES (?, ?, ?)",
                (doc_id, data.get("specialization"), data.get("department")),
            )
            log_audit(current_user.id, f"Added Doctor: {data['username']}")
            conn.commit()
            return jsonify({"success": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
