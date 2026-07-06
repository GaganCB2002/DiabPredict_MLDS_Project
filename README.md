# DiabPredict AI — Medical Intelligence Platform

A full-stack Hospital Management System with AI-powered diabetes prediction, EMR portal, role-based access, and interactive analytics dashboard.

Built with Flask, Logistic Regression (SGD), SQLite, TailwindCSS, Three.js, and Chart.js.

---

## Project Structure

```text
├── app.py                     # Flask application — routing, auth, database, ML inference
├── model.py                   # Logistic Regression model trainer (SGDClassifier)
├── diabetes.csv               # PIMA Indians Diabetes Dataset
├── model_parameters.csv       # Trained weights, means, and scales
├── requirements.txt           # Python dependencies
├── Procfile                   # Cloud Deployment (Render/Heroku)
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

```mermaid
flowchart TD
    A[diabetes.csv] --> B[model.py]
    B --> C[Step 1: Load CSV via pandas]
    C --> D[Step 2: Separate Features & Target]
    D --> E[Step 3: Standardize Features]
    E --> F[Step 4: Train Logistic Regression SGD]
    F --> G[Step 5: Evaluate Accuracy]
    G --> H[Step 6: Export model_parameters.csv]
```

### 2. Application Startup & Database Initialization

```mermaid
flowchart TD
    A[python app.py] --> B[Imports & Flask Setup]
    B --> C[load_model: Reads CSV weights]
    C --> D[init_db: Connects to SQLite]
    D --> E[Create Tables & Run Migrations]
    E --> F[Seed Default Users admin, doctor, patient]
    F --> G[Flask Server Starts on port 5000]
```

### 3. Complete Request Lifecycle — Landing Page

```mermaid
flowchart TD
    A[Browser GET /] --> B[app.py home function]
    B --> C[render_template index.html]
    C --> D[Load CDNs Tailwind, GSAP, Three.js, Chart.js]
    C --> E[Check Authentication Status]
    C --> F[Render UI Sections]
    F --> G[script.js DOMContentLoaded]
    G --> H[Initialize Lenis Smooth Scroll]
    G --> I[Initialize Three.js Engine]
    G --> J[Initialize GSAP ScrollTriggers]
```

### 3.5 Cinematic UI & Animation Architecture (Three.js & GSAP)

DiabPredict AI features an award-winning cinematic UI built to run at 60 FPS using GPU acceleration.

```mermaid
sequenceDiagram
    participant U as User (Mouse/Trackpad)
    participant L as Lenis (Smooth Scroll)
    participant G as GSAP ScrollTrigger
    participant T as Three.js WebGL

    U->>L: Scrolls Down Page
    L-->>G: Emits Scroll Event (Scrub Progress)
    L-->>T: Updates Global ScrollY Variable
    
    rect rgb(240, 248, 255)
    Note over G: CSS & DOM Animations
    G->>G: Moves background coding text (Right to Left)
    G->>G: Reverse text marquee strips
    G->>G: Tilts Glass Cards dynamically (X/Y axes)
    G->>G: Reverses entrance animations cleanly when scrolling up
    end
    
    rect rgb(230, 250, 240)
    Note over T: 3D DNA Helix Pipeline
    T->>T: Evaluates parametric equations
    T->>T: Rotates Double Helix strictly tied to ScrollY
    T->>T: Tilts and Zooms 3D Camera based on Scroll Velocity
    T-->>U: Renders organic Medical Intelligence atmosphere
    end
```

### 4. Complete Prediction Flow — User Submits Biometric Form

```mermaid
sequenceDiagram
    participant U as User
    participant JS as Frontend script.js
    participant F as Flask /predict
    participant DB as SQLite
    
    U->>JS: Submits 9 Biometric Fields
    JS->>JS: Validates inputs locally
    JS->>F: POST /predict (FormData)
    F->>F: Reorder & Standardize inputs
    F->>F: Compute z-score & apply Sigmoid
    F->>DB: INSERT into predictions table
    F-->>JS: Returns JSON result (Probability)
    JS->>JS: Animate GSAP Counters & Reveal UI
    JS->>JS: Render Chart.js Radar Chart
```

### 5. Full Report Page Flow

```mermaid
flowchart LR
    A[Execute Analysis] --> B[POST /report]
    B --> C[run_prediction Engine]
    C --> D[render_template report.html]
    D --> E[Render Verdict & Animations]
    D --> F[Render Chart.js Radar]
    D --> G[Generate Clinical Metrics Table]
    D --> H[Export CSV / Print Document]
```

### 6. Authentication & Session Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Flask /login
    participant DB as SQLite users table
    
    U->>F: POST /login (username, password)
    F->>DB: SELECT password_hash
    DB-->>F: Returns stored hash
    F->>F: werkzeug check_password_hash()
    alt Match
        F->>F: login_user() creates session cookie
        F-->>U: 200 OK Redirect to /
    else No Match
        F-->>U: 401 Unauthorized Error
    end
```

### 7. User Registration Flow

```mermaid
flowchart TD
    A[POST /register] --> B{Check username exists?}
    B -- Yes --> C[Return 409 Conflict Error]
    B -- No --> D[generate_password_hash]
    D --> E[INSERT into users]
    E --> F{What is the Role?}
    F -- Patient --> G[INSERT into profiles_patient]
    F -- Doctor --> H[INSERT into profiles_doctor]
    G --> I[Write to audit_logs]
    H --> I
    I --> J[Return 200 OK Success]
```

### 8. EMR Portal — Doctor Workflow

```mermaid
flowchart TD
    A[Doctor visits /doctor] --> B[Fetch Stats API]
    A --> C[Fetch Patient Queue API]
    A --> D[Fetch Consultations API]
    C --> E[View Patient History Modal]
    E --> F[GET /api/doctor/predictions]
    E --> G[GET /api/doctor/consultations]
    D --> H[New Consultation Modal]
    H --> I[POST clinical notes & prescriptions]
```

### 9. Admin Dashboard — System Management

```mermaid
flowchart LR
    A[Admin Dashboard] --> B[System Overview]
    A --> C[Patients CRUD]
    A --> D[Doctors CRUD]
    B --> E[Audit Logs Stream]
    B --> F[Hospital Occupancy Stats]
    C --> G[POST /api/admin/patients]
    D --> H[POST /api/admin/doctors]
```

### 10. Analysis Dashboard — Prediction History

```mermaid
flowchart TD
    A[User visits /analysis] --> B[GET /api/history]
    B --> C[Populate Sidebar List]
    C --> D[Select Specific Prediction]
    D --> E[Render Donut Chart (Risk %)]
    D --> F[Render Bar Chart (Metrics)]
    D --> G[Reopen in Predictor (URL Hash)]
    D --> H[Delete API Request]
```

### 11. AI Health Assistant Flow

```mermaid
sequenceDiagram
    participant U as User
    participant JS as Frontend Terminal
    participant F as Flask /api/chat
    
    U->>JS: Types question (e.g. "glucose level")
    JS->>F: POST {message: text}
    F->>F: Lowercase & Regex Keyword Matching
    F-->>JS: Returns specific medical context reply
    JS->>U: Appends to terminal UI & Auto-scrolls
```

### 12. Database Schema & Relationships (ERD)

```mermaid
erDiagram
    USERS ||--o{ PROFILES_DOCTOR : has
    USERS ||--o{ PROFILES_PATIENT : has
    USERS ||--o{ PREDICTIONS : creates
    USERS ||--o{ AUDIT_LOGS : tracks
    PROFILES_PATIENT ||--o{ APPOINTMENTS : books
    PROFILES_DOCTOR ||--o{ APPOINTMENTS : receives
    PROFILES_PATIENT ||--o{ CONSULTATIONS : undergoes
    PROFILES_DOCTOR ||--o{ CONSULTATIONS : conducts
    CONSULTATIONS ||--o{ PRESCRIPTIONS : includes

    USERS {
        int id PK
        string username
        string password_hash
        string role
    }
    PREDICTIONS {
        int id PK
        int user_id FK
        float probability
        float glucose
        float bmi
    }
```
