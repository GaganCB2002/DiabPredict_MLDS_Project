# 🚀 Running diabpredict: Complete Beginner Guide

Welcome to the **diabpredict System**. If you have never worked on this project before, this guide will walk you through exactly how to set it up from absolute scratch. 

We will not skip a single step. Follow these instructions exactly.

---

## 📖 Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Clone Repository](#2-clone-repository)
3. [Open the Project](#3-open-the-project)
4. [Python Environment Setup](#4-python-environment-setup)
5. [Database Setup](#5-database-setup)
6. [Machine Learning Setup](#6-machine-learning-setup)
7. [Running the Application](#7-running-the-application)
8. [Verify Everything](#8-verify-everything)
9. [Common Errors & Troubleshooting](#9-common-errors--troubleshooting)

---

## 1. Prerequisites

Before doing anything, you must install the following tools on your machine.

### 🐍 Python 3.9+
- **Why it is required:** The backend API and Machine Learning models run entirely on Python.
- **Where to get it:** Download it from [python.org/downloads](https://www.python.org/downloads/). 
- **Important:** During installation on Windows, you **MUST** check the box that says `"Add Python to PATH"`.

### 🐙 Git
- **Why it is required:** Git is used to download (clone) the project code and track changes.
- **Where to get it:** Download from [git-scm.com/downloads](https://git-scm.com/downloads).

### 💻 VS Code (Visual Studio Code)
- **Why it is required:** This is our primary Code Editor (IDE).
- **Where to get it:** Download from [code.visualstudio.com](https://code.visualstudio.com/).

*(Note: Node.js, Docker, PostgreSQL, etc., mentioned in the prompt are NOT required for the local development of this specific monolithic Flask/SQLite architecture, keeping setup extremely fast).*

---

## 2. Clone Repository

We need to download the source code to your computer.

1. Open your Terminal (Mac/Linux) or Command Prompt / PowerShell (Windows).
2. Navigate to the folder where you want to save the project. (e.g., `cd Documents`)
3. Run the following command:
   ```bash
   git clone <REPOSITORY_URL_HERE>
   ```
4. **What this does:** It connects to GitHub (or your Git provider) and downloads the entire `diabpredict` folder to your local machine.

---

## 3. Open the Project

1. Open **Visual Studio Code**.
2. Click on **File** in the top left corner.
3. Click **Open Folder...**
4. Select the `diabpredict` folder that was just downloaded.
5. Trust the authors if prompted.

Now, open a Terminal inside VS Code by pressing `` Ctrl + ` `` (Backtick) or clicking **Terminal > New Terminal** in the top menu.

---

## 4. Python Environment Setup

To avoid conflicting with other Python projects on your computer, we create an isolated "Virtual Environment".

### Create the Environment
In your VS Code terminal, run:
```bash
python -m venv .venv
```
*This creates a folder called `.venv` which acts as an isolated Python container.*

### Activate the Environment
You must activate this environment every time you open the project.

- **On Windows:**
  ```powershell
  .venv\Scripts\activate
  ```
- **On Mac / Linux:**
  ```bash
  source .venv/bin/activate
  ```
*(You will know it worked if your terminal prompt now starts with `(.venv)`)*

### Install Dependencies
With the environment active, install the project packages:
```bash
pip install -r requirements.txt
```
*This installs Flask, Pandas, Numpy, and Werkzeug required by the project.*

---

## 5. Database Setup

diabpredict uses SQLite, which means **you do not need to install a database server**. The database is just a file (`hms.db`).

The application automatically creates the database and seeds the default users the first time you run it. **You do not need to run manual migration commands.**

*When you start the server (Step 7), `app.py` runs `init_db()`, which safely creates all tables (Users, Consultations, etc.) and injects default accounts.*

---

## 6. Machine Learning Setup

The backend requires the ML model weights to run predictions.

Run the ML training script to generate the `model_parameters.csv` file:
```bash
python model.py
```
**Expected Output:**
```text
Accuracy: 0.7727272727272727
Model parameters saved to model_parameters.csv
```
*If you see this, the AI is ready.*

---

## 7. Running the Application

Now we start the Flask web server. 

In your activated terminal, run:
```bash
python app.py
```

**Expected Output:**
```text
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

Open your web browser (Chrome, Safari, Edge) and go to:
👉 **[http://localhost:5000](http://localhost:5000)**

---

## 8. Verify Everything

You must verify the system works. Follow this exact startup order.

### Verify Patient Role
1. Go to `http://localhost:5000`. You should see the landing page.
2. Click **Login** in the top right.
3. Enter Username: `patient`, Password: `patient123`.
4. Run an AI Prediction using the form. Ensure you get a result.

### Verify Doctor Role (EMR)
1. Click **Logout**.
2. Click **Login**.
3. Enter Username: `doctor`, Password: `doctor123`.
4. Click the green **EMR Portal** button in the navbar.
5. Verify you see the Patient Queue. Click a patient and ensure the clinical record loads.

### Verify Admin Role (HMS)
1. Click **Logout**.
2. Click **Login**.
3. Enter Username: `admin`, Password: `admin123`.
4. Click the blue **HMS Admin** button.
5. Verify you see hospital statistics and can view the Patient/Doctor tables.

---

## 9. Common Errors & Troubleshooting

### ❌ Error: `Port 5000 is already in use`
**Cause:** Another app (like Control Center on Mac, or another web server) is using port 5000.
**Fix:** Open `app.py`, scroll to the absolute bottom, and change `port=5000` to `port=5001`.
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)
```

### ❌ Error: `ModuleNotFoundError: No module named 'flask'`
**Cause:** Your virtual environment is not activated, or dependencies failed to install.
**Fix:** Run `source .venv/bin/activate` (Mac) or `.venv\Scripts\activate` (Win), then run `pip install -r requirements.txt` again.

### ❌ Error: `Model not loaded on the server.`
**Cause:** The application cannot find `model_parameters.csv`.
**Fix:** Stop the server (`Ctrl + C`), run `python model.py`, then start the server again with `python app.py`.

### ❌ Error: `Database locked`
**Cause:** SQLite only allows one write operation at a time. A previous process crashed while holding a lock.
**Fix:** Stop the server (`Ctrl + C`). Delete `hms.db`. Start the server again to regenerate a fresh database.

---
*If you encounter an error not listed here, please open an Issue on GitHub.*
