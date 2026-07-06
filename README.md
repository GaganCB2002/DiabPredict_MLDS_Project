# DiabPredict AI — Medical Intelligence Platform

A full-stack Hospital Management System with AI-powered diabetes prediction, EMR portal, role-based access, and interactive analytics dashboard.

Built with Flask, Logistic Regression (SGD), SQLite, TailwindCSS, Three.js, and Chart.js.

---

## Project Structure

```
├── app.py                     # Flask application — routing, auth, database, ML inference
├── model.py                   # Logistic Regression model trainer (SGDClassifier)
├── diabetes.csv               # PIMA Indians Diabetes Dataset
├── model_parameters.csv       # Trained weights, means, and scales
├── requirements.txt           # Python dependencies
├── .gitignore
├── README.md
│
└── frontend/
    ├── static/
    │   ├── style.css          # Custom styles, glassmorphism, animations
    │   └── script.js          # Three.js particles, GSAP scroll animations, Chart.js
    └── templates/
        ├── index.html             # Landing page — hero, dashboard counters, prediction form, AI chat
        ├── login.html             # Authentication (also handles registration mode)
        ├── admin_dashboard.html   # HMS admin — patient/doctor CRUD, system stats, audit logs
        ├── doctor_dashboard.html  # EMR Portal — patient queue, consultations, prescriptions
        ├── analysis.html          # Assessment history with donut/bar charts and CRUD
        └── report.html            # Printable diagnostic report with radar chart & CSV export
```

---

## Complete Data Flow & System Architecture

### 1. Machine Learning Model Training Pipeline

```
diabetes.csv
│
│ 768 patient records with columns:
│   Pregnancies, Glucose, BloodPressure, SkinThickness,
│   Insulin, BMI, DiabetesPedigreeFunction, Age, Outcome
│
▼
model.py
│
├── Step 1: Load CSV via pandas.read_csv()
│     → DataFrame with 768 rows × 9 columns
│
├── Step 2: Separate features (X) and target (y)
│     X = all columns except 'Outcome'  (shape: 768×8)
│     y = 'Outcome' column              (shape: 768×1)
│
├── Step 3: Standardize features
│     For each of the 8 feature columns:
│       - Compute mean (μ) across all 768 samples
│       - Compute standard deviation (σ)
│       - Transform: X_scaled = (X - μ) / σ
│     → Each feature now has μ=0, σ=1
│
├── Step 4: Train Logistic Regression
│     Model: SGDClassifier(loss='log_loss', max_iter=1000, random_state=42)
│       - loss='log_loss' → uses sigmoid activation
│       - SGD = Stochastic Gradient Descent optimizer
│       - Iterates 1000 times through the data, adjusting weights
│         to minimize binary cross-entropy loss
│     → Learns 8 weight values (one per feature) + 1 intercept (bias)
│
├── Step 5: Evaluate
│     accuracy_score(y_true, y_pred) → ~78% accuracy on test split
│
└── Step 6: Export trained parameters to CSV
      model_parameters.csv
      ─────────────────────
      Feature, Weight, Mean, Scale
      pregnancies,  0.321, 3.84, 3.37
      glucose,      0.892, 120.9, 31.97
      bloodPressure,0.214, 69.1, 19.36
      skinThickness,0.184, 20.5, 15.95
      insulin,      0.312, 79.8, 115.2
      bmi,          0.541, 31.9, 7.88
      diabetesPedigreeFunction, 0.234, 0.47, 0.33
      age,          0.423, 33.2, 11.76
      Intercept,    -5.124, -, -
```

---

### 2. Application Startup & Database Initialization

```
Command: python app.py
            │
            ▼
    app.py executes from top to bottom
            │
            ├── Imports: Flask, flask_login, werkzeug, pandas, numpy, sqlite3, os
            │
            ├── Flask app created with template_folder='frontend/templates'
            │   and static_folder='frontend/static'
            │
            ├── Flask-Login configured with login_view='login'
            │
            ├── User class defined (extends UserMixin):
            │     - id: int
            │     - username: str
            │     - role: str ('Admin', 'Doctor', 'Patient')
            │
            ├── MODEL_PATH = 'model_parameters.csv'
            ├── DB_PATH = 'hms.db'
            │
            ├── COLUMNS_V1 = [
            │     'pregnancies', 'glucose', 'bloodPressure',
            │     'skinThickness', 'insulin', 'bmi',
            │     'diabetesPedigreeFunction', 'age'
            │   ]
            │
            ├── load_model() is called:
            │   ┌──────────────────────────────────────────────────┐
            │   │ 1. Check if model_parameters.csv exists          │
            │   │ 2. Read CSV via pandas                           │
            │   │ 3. Extract intercept, feature names, weights,    │
            │   │    means, and scales into a dictionary           │
            │   │ 4. Return dict or None if file missing           │
            │   └──────────────────────────────────────────────────┘
            │
            ├── init_db() is called:
            │   ┌──────────────────────────────────────────────────┐
            │   │ 1. Connect to hms.db                             │
            │   │ 2. Create tables if they don't exist:            │
            │   │    • users — id, username, password_hash,        │
            │   │               role, email, phone                 │
            │   │    • profiles_doctor — id, user_id(FK),          │
            │   │                       specialization, department  │
            │   │    • profiles_patient — id, user_id(FK),         │
            │   │                        dob, gender, blood_group  │
            │   │    • appointments — id, patient_id(FK),          │
            │   │                     doctor_id(FK),               │
            │   │                     appointment_date, status     │
            │   │    • consultations — id, patient_id(FK),         │
            │   │                      doctor_id(FK), date,        │
            │   │                      symptoms, diagnosis, notes  │
            │   │    • prescriptions — id, consultation_id(FK),    │
            │   │                      medicine_name, dosage,      │
            │   │                      duration                    │
            │   │    • predictions — id, name, prediction,         │
            │   │                    probability, timestamp,        │
            │   │                    message, user_id(FK),         │
            │   │                    + 8 biometric columns         │
            │   │    • audit_logs — id, user_id(FK), action,       │
            │   │                  timestamp                       │
            │   │                                                  │
            │   │ 3. Add biometric columns to predictions table    │
            │   │    if missing (ALTER TABLE)                      │
            │   │                                                  │
            │   │ 4. Seed default users if table is empty:         │
            │   │    • admin / admin123 (Admin)                    │
            │   │    • doctor / doctor123 (Doctor, Endo.)          │
            │   │    • patient / patient123 (Patient, O+)          │
            │   └──────────────────────────────────────────────────┘
            │
            ▼
      Flask development server starts on port 5000
      Waiting for HTTP requests...
```

---

### 3. Complete Request Lifecycle — User Visits Landing Page

```
Browser → GET http://127.0.0.1:5000/
                │
                ▼
          Flask route: @app.route('/')
                │
                ├── Function: home()
                │     └── render_template('index.html', current_user=current_user)
                │
                ▼
          Jinja2 renders index.html:
          ┌────────────────────────────────────────────────────────────────┐
          │ 1. HTML skeleton with TailwindCSS classes                     │
          │ 2. Three.js CDN loaded → <canvas id="bg-canvas">             │
          │ 3. Lenis (smooth scroll) CDN loaded                          │
          │ 4. GSAP + ScrollTrigger CDNs loaded                          │
          │ 5. Chart.js CDN loaded                                       │
          │ 6. Navbar renders based on current_user.is_authenticated:    │
          │    • Not logged in: "Authenticate" button                    │
          │    • Admin: "HMS Admin" button → /admin                      │
          │    • Doctor: "EMR Portal" button → /doctor                   │
          │    • Any user: "Reports" button → /analysis, "Logout"        │
          │ 7. Hero section with clip-reveal text animation               │
          │ 8. Dashboard counters (Total, High Risk, Low Risk,            │
          │    Avg Glucose, Avg BMI, Avg Age) — populated via JS          │
          │ 9. Risk Distribution donut chart via Chart.js                 │
          │ 10. Neural Workflow section (3-step explanation)              │
          │ 11. Key Risk Factors section (8 cards, one per metric)        │
          │ 12. Platform Capabilities grid (6 feature cards)              │
          │ 13. Diagnostic Analysis form (9 fields + submit)              │
          │ 14. AI Health Assistant chatbot (terminal-style)              │
          └────────────────────────────────────────────────────────────────┘
                │
                ▼
          Browser executes script.js:
          ┌────────────────────────────────────────────────────────────────┐
          │ DOMContentLoaded handler:                                     │
          │ 1. Initialize Lenis smooth scroll engine                      │
          │ 2. Initialize Three.js scene with 800 particles               │
          │    • Scene background: #FFFFFF                                │
          │    • Gradient colors: #2563EB → #0891B2                      │
          │    • Particles rotate slowly, respond to scroll position      │
          │    • Camera moves with scroll (parallax effect)               │
          │ 3. GSAP ScrollTrigger animations:                             │
          │    • .clip-reveal — text reveals when hero scrolls into view  │
          │    • .scroll-fade — fade + blur + y-offset on scroll          │
          │    • .scroll-fade-up — fade + scale + blur on scroll          │
          │    • .scroll-scale-x — horizontal line scale animation        │
          │    • Dashboard counters — animate from 0 to target value      │
          │ 4. Chart.js risk distribution chart — fetch /api/dashboard    │
          │ 5. Prediction form validation + submission handler            │
          │ 6. AI chatbot toggle + message handler — fetch /api/chat     │
          │ 7. Mouse parallax effect on hero text                         │
          │ 8. Scroll progress bar                                        │
          └────────────────────────────────────────────────────────────────┘
                │
                ▼
          Page is fully interactive
```

---

### 4. Complete Prediction Flow — User Submits Biometric Form

```
User fills 9 fields:
┌─────────────────────────────────────────────────────────────────────┐
│ Patient Name:    "John Doe"                                         │
│ Glucose:         150 mg/dL     (range: 0-300)                       │
│ BMI:             32.5          (range: 0-100)                       │
│ Age:             55 yrs        (range: 0-120)                       │
│ Blood Pressure:  85 mmHg       (range: 0-300)                       │
│ Insulin:         120 IU/mL     (range: 0-1000)                      │
│ Skin Thickness:  25 mm         (range: 0-100)                       │
│ Pregnancies:     3             (range: 0-20)                        │
│ Pedigree Function: 0.8         (range: 0-10)                        │
└─────────────────────────────────────────────────────────────────────┘
        │
        ▼
  JavaScript validates each field on blur:
  - Checks value is not empty
  - Checks value is within min/max range
  - Adds red border + error message if invalid
        │
        ▼
  Form submitted → e.preventDefault()
        │
        ├── Collect all field values via FormData
        │
        ├── Show loading state:
        │     Button text: "Generating Report..."
        │     Icon: spinner
        │     Button disabled
        │
        ▼
  fetch POST /predict  (Content-Type: multipart/form-data)
        │
        ▼
  Flask route: @app.route('/predict', methods=['POST'])
        │
        ├── Check model_data is not None (loaded at startup)
        │
        ├── Parse request:
        │     payload = request.get_json(silent=True)
        │     or payload = request.form.to_dict()
        │
        ├── Call run_prediction(payload)
        │   ┌──────────────────────────────────────────────────────────────┐
        │   │ run_prediction(payload):                                     │
        │   │                                                              │
        │   │ Step 1: Normalize field names to lowercase                   │
        │   │   { 'name': 'John Doe', 'glucose': '150', ... }             │
        │   │                                                              │
        │   │ Step 2: Extract biometric values                             │
        │   │   For each column in COLUMNS_V1:                             │
        │   │     input_values['glucose'] = float('150')                   │
        │   │     input_values['bmi'] = float('32.5')                      │
        │   │     ... (all 8 fields)                                       │
        │   │                                                              │
        │   │ Step 3: Build feature vector in model's expected order       │
        │   │   The model was trained on specific feature names            │
        │   │   (e.g., 'pregnancies', 'glucose', ...). These are stored    │
        │   │   in model_data['features']. We reorder input values to      │
        │   │   match this exact order using a feature_map:                │
        │   │                                                              │
        │   │   input_data = [                                             │
        │   │     input_values['pregnancies'],       → 3.0                 │
        │   │     input_values['glucose'],           → 150.0               │
        │   │     input_values['bloodPressure'],     → 85.0                │
        │   │     input_values['skinThickness'],     → 25.0                │
        │   │     input_values['insulin'],           → 120.0               │
        │   │     input_values['bmi'],               → 32.5                │
        │   │     input_values['diabetesPedigreeFunction'], → 0.8          │
        │   │     input_values['age']                → 55.0                │
        │   │   ]                                                          │
        │   │                                                              │
        │   │ Step 4: Standardize (same transform as training)             │
        │   │   For each of the 8 features:                                │
        │   │     scaled[i] = (input_data[i] - mean[i]) / scale[i]        │
        │   │                                                              │
        │   │   Example for glucose:                                       │
        │   │     mean[glucose] = 120.9, scale[glucose] = 31.97            │
        │   │     scaled[glucose] = (150.0 - 120.9) / 31.97 = 0.91         │
        │   │                                                              │
        │   │   Result: scaled_input = [                                   │
        │   │     -0.25,   ← pregnancies standardized                      │
        │   │      0.91,   ← glucose standardized                           │
        │   │      0.82,   ← bloodPressure standardized                     │
        │   │      0.28,   ← skinThickness standardized                     │
        │   │      0.35,   ← insulin standardized                           │
        │   │      0.08,   ← bmi standardized                              │
        │   │      0.99,   ← diabetesPedigreeFunction standardized          │
        │   │      1.85    ← age standardized                               │
        │   │   ]                                                           │
        │   │                                                              │
        │   │ Step 5: Compute linear combination (z-score)                 │
        │   │   z = Σ(scaled[i] × weight[i]) + intercept                   │
        │   │                                                              │
        │   │   z = (-0.25 × 0.321) + (0.91 × 0.892) + (0.82 × 0.214)    │
        │   │     + (0.28 × 0.184) + (0.35 × 0.312) + (0.08 × 0.541)     │
        │   │     + (0.99 × 0.234) + (1.85 × 0.423) + (-5.124)            │
        │   │                                                              │
        │   │   z = -0.080 + 0.812 + 0.175 + 0.052 + 0.109               │
        │   │     + 0.043 + 0.232 + 0.783 - 5.124                         │
        │   │                                                              │
        │   │   z = -2.998                                                 │
        │   │                                                              │
        │   │ Step 6: Apply sigmoid activation                             │
        │   │   probability = 1 / (1 + e^(-z))                             │
        │   │   probability = 1 / (1 + e^(2.998))                          │
        │   │   probability = 1 / (1 + 20.04)                              │
        │   │   probability = 0.0475  (4.75%)                              │
        │   │                                                              │
        │   │ Step 7: Threshold classification                             │
        │   │   if probability >= 0.5: prediction = 1 (High Risk)          │
        │   │   if probability < 0.5:  prediction = 0 (Low Risk)           │
        │   │                                                              │
        │   │   Here: 0.0475 < 0.5 → prediction = 0 (Low Risk)            │
        │   │                                                              │
        │   │ Step 8: Generate message                                     │
        │   │   "Based on the data, John Doe is predicted to not           │
        │   │    have diabetes."                                           │
        │   │                                                              │
        │   │ Step 9: Save to database                                     │
        │   │   INSERT INTO predictions                                    │
        │   │   (name, prediction, probability, timestamp, message,        │
        │   │    user_id, pregnancies, glucose, bloodPressure,             │
        │   │    skinThickness, insulin, bmi,                              │
        │   │    diabetesPedigreeFunction, age)                            │
        │   │   VALUES                                                     │
        │   │   ('John Doe', 0, 0.0475, '2026-07-06 21:30:00',            │
        │   │    'Based on...,', NULL,                                      │
        │   │    3.0, 150.0, 85.0, 25.0, 120.0, 32.5, 0.8, 55.0)          │
        │   │                                                              │
        │   │ Step 10: Return result dictionary                            │
        │   │   {                                                          │
        │   │     'id': 1,                                                 │
        │   │     'name': 'John Doe',                                      │
        │   │     'prediction': 0,                                         │
        │   │     'probability': 0.0475,                                   │
        │   │     'message': 'Based on the data, John Doe is predicted     │
        │   │                to not have diabetes.',                       │
        │   │     'timestamp': '2026-07-06 21:30:00',                     │
        │   │     'glucose': 150.0, 'bmi': 32.5, ... (all 8 values)       │
        │   │   }                                                          │
        │   └──────────────────────────────────────────────────────────────┘
        │
        ├── Return JSON response to frontend
        │
        ▼
  Frontend receives response:
        │
        ├── Call showResult(response, inputData)
        │   ┌────────────────────────────────────────────────────────────────┐
        │   │ 1. Animate form out: opacity→0, x→-50 (GSAP)                  │
        │   │ 2. Hide form, show resultArea div                              │
        │   │ 3. Animate probability counter: 0% → 4.8% (GSAP 2s ease)      │
        │   │ 4. Set verdict text: "NOMINAL RANGE"                          │
        │   │ 5. Set verdict color: #0891B2 (cyan)                          │
        │   │ 6. Display message text                                        │
        │   │ 7. Render radar chart with biometric values                    │
        │   └────────────────────────────────────────────────────────────────┘
        │
        ▼
  Radar chart renders (Chart.js):
        │
        ├── Canvas: document.getElementById('radarChart')
        ├── 5 axes: GLU, BMI, AGE, B.P., INS
        ├── Normalized to percentage of max healthy range:
        │     glucose% = min(150/200 × 100, 100) = 75%
        │     bmi%     = min(32.5/50 × 100, 100)  = 65%
        │     age%     = min(55/80 × 100, 100)    = 68.75%
        │     bp%      = min(85/120 × 100, 100)   = 70.83%
        │     insulin% = min(120/300 × 100, 100)  = 40%
        ├── Background: semi-transparent red or cyan
        ├── Border: matching color
        └── Point labels: GLU, BMI, AGE, B.P., INS
```

---

### 5. Full Report Page Flow

```
User clicks "Execute Analysis" on homepage
  OR submits form via POST /report
        │
        ▼
  Flask route: @app.route('/report', methods=['POST'])
        │
        ├── Same run_prediction() process as above
        │
        ├── render_template('report.html', result=result)
        │
        ▼
  report.html renders:
  ┌────────────────────────────────────────────────────────────────────┐
  │ • Header with patient name, timestamp, report ID                  │
  │ • Verdict badge: "CRITICAL RISK" (red) or "NOMINAL RANGE" (green) │
  │ • Animated probability counter (GSAP, 2.5s)                       │
  │ • Radar chart (same 5 axes as inline)                             │
  │ • Clinical metrics table (all 8 values with units)                │
  │ • Health summary & recommendations (conditional on prediction)    │
  │ • Print button → window.print()                                   │
  │ • CSV Export button → exportCSV() function                        │
  │   ┌────────────────────────────────────────────────────────────┐  │
  │   │ exportCSV():                                                │  │
  │   │ 1. Build headers: ['Metric', 'Value']                       │  │
  │   │ 2. Build rows: [                                            │  │
  │   │      ['Name', 'John Doe'],                                  │  │
  │   │      ['Prediction', 'Low Risk'],                            │  │
  │   │      ['Probability', '4.8%'],                               │  │
  │   │      ['Glucose', '150 mg/dL'],                              │  │
  │   │      ... (all 8 metrics + timestamp)                        │  │
  │   │    ]                                                         │  │
  │   │ 3. Create CSV string with newlines                          │  │
  │   │ 4. Create Blob with MIME type text/csv                      │  │
  │   │ 5. Trigger download via temporary <a> element               │  │
  │   │ 6. Revoke object URL                                        │  │
  │   └────────────────────────────────────────────────────────────┘  │
  │ • Home button → return to landing page                            │
  └────────────────────────────────────────────────────────────────────┘
```

---

### 6. Authentication & Session Flow

```
User visits /login
        │
        ▼
  GET /login → render_template('login.html')
        │
        ├── Three.js particle background (400 particles)
        ├── Glass-morphism login card
        ├── Username + password fields
        ├── Quick-fill buttons: Admin, Doctor, Patient
        └── Registration link → /register
        │
        ▼
  User submits credentials → POST /login
        │
        ├── Flask checks Content-Type for JSON or form
        ├── Query: SELECT id, username, password_hash, role
        │          FROM users WHERE username = ?
        │
        ├── If user found:
        │     check_password_hash(stored_hash, input_password)
        │     │
        │     ├── Match:
        │     │   login_user(User(id, username, role))
        │     │   → Flask-Login creates encrypted session cookie
        │     │   → Session includes user ID (serialized by user_loader)
        │     │   → Response: { success: true, redirect: '/' }
        │     │
        │     └── No match:
        │         Response: { error: 'Invalid username or password' }, 401
        │
        └── If user not found:
            Response: { error: 'Invalid username or password' }, 401
        │
        ▼
  Frontend receives response:
        ├── Success → window.location.href = '/'
        └── Error → show error message in red box
        │
        ▼
  Now current_user.is_authenticated = True
  Navbar shows username, role-specific buttons, logout
```

---

### 7. User Registration Flow

```
User visits /register → GET /register
        │
        ├── Same login.html template with register_mode=True
        ├── Additional "Role" dropdown (Patient / Doctor)
        ├── Form submits to POST /register
        │
        ▼
  Flask route: @app.route('/register', methods=['GET', 'POST'])
        │
        ├── Validate: username and password required
        ├── Validate: role is 'Patient' or 'Doctor'
        ├── Check if username already exists
        │     SELECT id FROM users WHERE username = ?
        │     → If exists: return error
        │
        ├── INSERT INTO users (username, password_hash, role)
        │     password_hash = generate_password_hash(password)
        │
        ├── If Patient:
        │     INSERT INTO profiles_patient (user_id) VALUES (?)
        │
        ├── If Doctor:
        │     INSERT INTO profiles_doctor (user_id) VALUES (?)
        │
        ├── log_audit(user_id, "User registered: ...")
        │
        └── Response: { success: true, message: 'Registration successful. Please log in.' }
        │
        ▼
  Frontend shows success message in green box
  Redirects to /login after 1.5 seconds
```

---

### 8. EMR Portal — Doctor Workflow

```
Doctor logs in with doctor / doctor123
        │
        ▼
  Navbar shows green "EMR Portal" button → /doctor
        │
        ▼
  GET /doctor → render_template('doctor_dashboard.html')
        │
        ├── Stats cards loaded via GET /api/doctor/stats:
        │     ├── Total Patients → SELECT COUNT(*) FROM users WHERE role='Patient'
        │     ├── Consultations → SELECT COUNT(*) FROM consultations WHERE doctor_id=?
        │     ├── Today's Appointments → SELECT COUNT(*) FROM appointments
        │     │                        WHERE doctor_id=? AND date(...)=date('now')
        │     └── Pending → SELECT COUNT(*) FROM appointments
        │                 WHERE doctor_id=? AND status='Scheduled'
        │
        ├── Patient Queue tab → GET /api/doctor/patients:
        │     SELECT u.id, u.username, u.email, u.phone,
        │            p.dob, p.gender, p.blood_group,
        │            (SELECT COUNT(*) FROM predictions WHERE user_id = u.id) as prediction_count,
        │            (SELECT MAX(timestamp) FROM predictions WHERE user_id = u.id) as last_prediction
        │     FROM users u
        │     LEFT JOIN profiles_patient p ON u.id = p.user_id
        │     WHERE u.role = 'Patient'
        │     ORDER BY u.username
        │
        │   Each patient row has a "View" button → opens Patient Detail Modal:
        │     ├── Fetches GET /api/doctor/predictions/<patient_id>
        │     │     → Shows prediction history table (date, risk, probability, glucose, BMI, age)
        │     │
        │     └── Fetches GET /api/doctor/consultations?patient_id=<id>
        │           → Shows consultation history (date, symptoms, diagnosis, notes, prescriptions)
        │
        ├── Consultations tab → GET /api/doctor/consultations:
        │     SELECT c.*, u.username as patient_name
        │     FROM consultations c
        │     JOIN users u ON c.patient_id = u.id
        │     ORDER BY c.date DESC
        │
        │   Each consultation shows date, patient, symptoms, diagnosis, prescription pills
        │
        └── New Consultation button → Opens modal:
              ├── Patient dropdown (fetched from /api/doctor/patients)
              ├── Date field (defaults to today)
              ├── Symptoms textarea
              ├── Diagnosis textarea
              ├── Notes textarea
              ├── Prescriptions section (dynamic rows):
              │     Medicine name | Dosage | Duration
              │     + "Add Medicine" button
              │
              └── Submit → POST /api/doctor/consultations
                    INSERT INTO consultations (patient_id, doctor_id, date,
                                               symptoms, diagnosis, notes)
                    For each prescription:
                      INSERT INTO prescriptions (consultation_id, medicine_name,
                                                  dosage, duration)
                    INSERT INTO audit_logs
                    Response: { success: true, id: <consultation_id> }
```

---

### 9. Admin Dashboard — System Management

```
Admin logs in with admin / admin123
        │
        ▼
  Navbar shows "HMS Admin" button → /admin
        │
        ▼
  GET /admin → render_template('admin_dashboard.html')
        │
        ├── Stats cards loaded via GET /api/admin/stats:
        │     ├── Total Patients → COUNT WHERE role='Patient'
        │     ├── Total Doctors → COUNT WHERE role='Doctor'
        │     ├── Appointments Today → COUNT WHERE date(...)=date('now')
        │     ├── Predictions Completed → COUNT FROM predictions
        │     ├── Hospital Occupancy → min(predictions / (patients+doctors) × 100, 100)%
        │     └── Recent Activity → SELECT action, timestamp FROM audit_logs ORDER BY id DESC LIMIT 10
        │
        ├── Overview tab:
        │     ├── Recent Activity list (from audit_logs)
        │     └── System Stats (occupancy, total users, platform status)
        │
        ├── Patients tab:
        │     ├── Table: ID, Username, Email, Phone, DOB, Gender, Blood Group
        │     └── "Add Patient" button → modal → POST /api/admin/patients
        │
        └── Doctors tab:
              ├── Table: ID, Username, Email, Phone, Specialization, Department
              └── "Add Doctor" button → modal → POST /api/admin/doctors
```

---

### 10. Analysis Dashboard — Prediction History

```
User visits /analysis (authenticated)
        │
        ▼
  GET /analysis → render_template('analysis.html')
        │
        ├── Sidebar loads predictions via GET /api/history:
        │     │
        │     ├── If Admin or Doctor:
        │     │     SELECT ... FROM predictions ORDER BY id DESC LIMIT 100
        │     │
        │     ├── If Patient:
        │     │     SELECT ... FROM predictions WHERE user_id = ? ORDER BY id DESC LIMIT 100
        │     │
        │     └── If unauthenticated:
        │           SELECT ... FROM predictions WHERE user_id IS NULL ORDER BY id DESC LIMIT 10
        │
        ├── Search bar filters predictions by name (client-side)
        │
        ├── Click a prediction → selectPrediction(pred) renders:
        │     ├── Patient name & timestamp
        │     ├── Verdict badge (CRITICAL RISK / NOMINAL RANGE)
        │     ├── Probability score with color
        │     ├── Donut chart: probability-weighted risk distribution
        │     │     • High Risk slice = prediction ? probability% : (1-probability)%
        │     │     • Low Risk slice = prediction ? (1-probability)% : probability%
        │     ├── Bar chart: all 8 metrics normalized to percentage of max
        │     │     • glucose% = value/200 × 100
        │     │     • bmi% = value/50 × 100
        │     │     • age% = value/80 × 100
        │     │     • bloodPressure% = value/120 × 100
        │     │     • insulin% = value/300 × 100
        │     │     • skinThickness% = value/60 × 100
        │     │     • pregnancies% = value/15 × 100
        │     │     • pedigree% = value/2.5 × 100
        │     ├── Metrics table (all 8 values with units)
        │     ├── "Reopen" button:
        │     │     → Sets URL hash with all field values
        │     │     → Navigates to /#field1=val1&field2=val2...
        │     │     → index.html pre-fills the prediction form from hash
        │     │     → Scrolls to analysis section
        │     └── "Delete" button:
        │           → DELETE /api/prediction/<id>
        │           → Removes from list, shows "No Assessment Selected"
        │
        └── Charts use Chart.js with proper instance management
              (destroy previous instance before creating new one)
```

---

### 11. AI Health Assistant Flow

```
User clicks chat bubble → terminal opens
        │
        ▼
  User types: "What is a normal glucose level?"
        │
        ▼
  POST /api/chat → { message: "What is a normal glucose level?" }
        │
        ▼
  Flask route: @app.route('/api/chat', methods=['POST'])
        │
        ├── Parse message, convert to lowercase
        ├── Keyword matching:
        │     ├── 'diabetes' or 'risk' → diabetes risk explanation
        │     ├── 'glucose' or 'sugar' → normal glucose range info
        │     ├── 'bmi' or 'weight' → healthy BMI range info
        │     ├── 'hello' or 'hi' → greeting
        │     └── default → general health disclaimer
        │
        └── Response: { reply: "Normal fasting blood glucose levels..." }
        │
        ▼
  Frontend appends response to chat with "SYS>" prefix
  Auto-scrolls to bottom
```

---

### 12. Database Schema & Relationships

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│   ┌──────────┐     ┌──────────────────┐     ┌──────────────┐                           │
│   │  users   │────→│ profiles_doctor   │     │ appointments │                           │
│   │          │     │                  │     │              │                           │
│   │ id (PK)  │     │ id               │     │ id           │                           │
│   │ username │     │ user_id (FK)─────┘     │ patient_id   │                           │
│   │ password │     │ specialization        │ doctor_id    │                           │
│   │ role     │     │ department            │ date         │                           │
│   │ email    │     └──────────────────┘     │ status       │                           │
│   │ phone    │                              └──────────────┘                           │
│   └────┬─────┘                                                                         │
│        │                                                                               │
│        │     ┌──────────────────┐     ┌────────────────┐                               │
│        └────→│ profiles_patient │     │ consultations  │                               │
│              │                  │     │                │                               │
│              │ id               │     │ id             │                               │
│              │ user_id (FK)─────┘     │ patient_id (FK)────┐                           │
│              │ dob                    │ doctor_id (FK)────┐ │                           │
│              │ gender                │ date              │ │                           │
│              │ blood_group           │ symptoms          │ │                           │
│              └──────────────────┘     │ diagnosis         │ │                           │
│                                       │ notes             │ │                           │
│                                       └────────┬──────────┘ │                           │
│                                                │            │                           │
│   ┌────────────────┐         ┌─────────────────┘            │                           │
│   │ prescriptions  │         │                              │                           │
│   │                │         │                              │                           │
│   │ id             │         │                              │                           │
│   │ consultation_  │◄────────┘                              │                           │
│   │   id (FK)      │                                       │                           │
│   │ medicine_name  │                                       │                           │
│   │ dosage         │                                       │                           │
│   │ duration       │                                       │                           │
│   └────────────────┘                                       │                           │
│                                                             │                           │
│   ┌──────────────┐     ┌──────────────────┐                 │                           │
│   │ predictions  │     │   audit_logs     │                 │                           │
│   │              │     │                  │                 │                           │
│   │ id           │     │ id               │                 │                           │
│   │ name         │     │ user_id (FK)─────┘                 │                           │
│   │ prediction   │     │ action                              │                           │
│   │ probability  │     │ timestamp                           │                           │
│   │ timestamp    │     └──────────────────┘                  │                           │
│   │ message      │                                           │                           │
│   │ user_id (FK)─┘                                           │                           │
│   │ + 8 biometric cols                                       │                           │
│   └──────────────┘                                           │                           │
│                                                              │                           │
│   All foreign key relationships reference users(id)          │                           │
│   Consultations link patients AND doctors to users           │                           │
│   Prescriptions link to consultations (not directly to users)│                           │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 13. Data Formats & Validation Rules

| Field | Type | Range | Unit | Description |
|-------|------|-------|------|-------------|
| Glucose | float | 0-300 | mg/dL | Fasting blood sugar level |
| BMI | float | 0-100 | kg/m² | Body Mass Index |
| Age | int | 0-120 | years | Patient age |
| Blood Pressure | float | 0-300 | mmHg | Diastolic blood pressure |
| Insulin | float | 0-1000 | IU/mL | Serum insulin level |
| Skin Thickness | float | 0-100 | mm | Triceps skin fold thickness |
| Pregnancies | int | 0-20 | count | Number of pregnancies |
| Pedigree Function | float | 0-10 | score | Diabetes pedigree function |
| Prediction | int | 0 or 1 | binary | 0 = Low Risk, 1 = High Risk |
| Probability | float | 0.0-1.0 | ratio | Sigmoid output (0-100%) |

---

### 14. Security & Access Control

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Flask-Login @login_required decorator                                    │
│                                                                          │
│ Route              │ Allowed Roles          │ Redirect if Unauthorized   │
│────────────────────┼────────────────────────┼────────────────────────────┤
│ /                  │ Public                 │ -                          │
│ /login             │ Public                 │ -                          │
│ /register          │ Public                 │ -                          │
│ /analysis          │ Authenticated          │ Redirect to /login         │
│ /admin             │ Admin only             │ Redirect to /              │
│ /doctor            │ Doctor only            │ Redirect to /              │
│ /api/admin/*       │ Admin only             │ 403 JSON error             │
│ /api/doctor/*      │ Doctor only            │ 403 JSON error             │
│ /api/history       │ Authenticated          │ Limited results            │
│ /predict           │ Public                 │ -                          │
│ /api/chat          │ Public                 │ -                          │
│ /api/dashboard     │ Public                 │ -                          │
└─────────────────────────────────────────────────────────────────────────┘

Password Security:
  - All passwords hashed via werkzeug.security.generate_password_hash()
  - Uses pbkdf2:sha256 with random salt
  - Authentication via check_password_hash()

Session Security:
  - Flask-Login encrypted session cookies
  - Secret key for session signing
  - Session cleared on logout
```

---

## Quick Start

```bash
pip install -r requirements.txt
python model.py          # Train the ML model (one-time)
python app.py            # Start the server
```

Open `http://127.0.0.1:5000`

### Default Accounts

| Role    | Username  | Password   |
|---------|-----------|------------|
| Admin   | admin     | admin123   |
| Doctor  | doctor    | doctor123  |
| Patient | patient   | patient123 |

---

## API Endpoints

### Public
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Landing page |
| GET/POST | `/login` | Authentication |
| GET/POST | `/register` | User registration |
| POST | `/predict` | JSON prediction API |
| POST | `/report` | HTML report page |
| POST | `/api/chat` | AI assistant chat |

### Authenticated
| Method | Route | Role | Description |
|--------|-------|------|-------------|
| GET | `/analysis` | Any | Analysis dashboard |
| GET | `/api/history` | Any | Prediction history |
| GET/DELETE/PUT | `/api/prediction/<id>` | Any | Single prediction CRUD |
| GET | `/api/dashboard` | Any | Dashboard statistics |

### Admin
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/admin` | HMS dashboard |
| GET | `/api/admin/stats` | System stats + recent activity |
| GET/POST | `/api/admin/patients` | Patient management |
| GET/POST | `/api/admin/doctors` | Doctor management |

### Doctor
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/doctor` | EMR Portal |
| GET | `/api/doctor/stats` | Doctor dashboard stats |
| GET | `/api/doctor/patients` | Patient list with prediction counts |
| GET/POST | `/api/doctor/consultations` | Consultation CRUD with prescriptions |
| GET | `/api/doctor/predictions/<id>` | Patient prediction history |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask, Flask-Login, Werkzeug |
| ML | scikit-learn (SGDClassifier), NumPy, Pandas |
| Database | SQLite3 (8 tables, relational) |
| Frontend | TailwindCSS, Three.js, GSAP, Chart.js, Lenis |
| Auth | bcrypt password hashing, session-based |
