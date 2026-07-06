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

## Features

### ML Prediction Engine
- Logistic regression trained on the PIMA Indians dataset via SGD optimization
- 8 biometric inputs: Glucose, BMI, Age, Blood Pressure, Insulin, Skin Thickness, Pregnancies, Pedigree Function
- Real-time inference with sigmoid-activated probability scoring
- Full prediction history with CRUD operations

### Role-Based Access
- **Admin** — Hospital Management dashboard with patient/doctor management and system audit logs
- **Doctor** — EMR Portal with patient queue, consultation records, and prescription management
- **Patient** — Prediction history and diagnostic reports

### EMR Portal
- Patient queue with prediction history and clinical records
- Consultation logging with symptoms, diagnosis, and notes
- Prescription management (medicine name, dosage, duration)
- View patient prediction history alongside consultations

### Analysis Dashboard
- Sidebar with searchable prediction history
- Donut chart showing risk probability distribution
- Normalized bar chart comparing all 8 biometric metrics
- Reopen button pre-fills the prediction form with past data
- Delete assessments with one click

### Diagnostic Reports
- Full-page printable report with probability score, verdict, and biometric profile
- Radar chart visualizing 5 key metrics (GLU, BMI, AGE, B.P., INS)
- CSV export for electronic health records
- Animated probability counter

### AI Health Assistant
- Context-aware chatbot answering questions about diabetes, glucose, BMI, etc.
- Terminal-style UI with typewriter responses

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
