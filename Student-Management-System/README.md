# Acadex — Student Management & Academic Intelligence System

A full-stack, role-based Student Management System built with a **Python REST API (FastAPI + SQLite + SQLAlchemy)** and a **clean, modern UI** tailored for academic engineering departments.

---

## 🌟 Key Features

### 👨‍🎓 1. Student Portal
- **Attendance Register**: Real-time subject-by-subject attendance records, total classes conducted vs. attended, eligibility status indicators (≥85% Distinction, <75% Shortage alert).
- **Marks & Academic Progress**: Gradebook breaking down internal assessments across **Midterm (30)**, **Assignments (20)**, **Lab Practicals (20)**, and **End-Term Exams (30)** with automated Letter Grades (A+, A, B+, etc.) and Cumulative GPA.
- **Teacher Feedback & Behavioral Log**: Chronological timeline of personalized suggestions, conduct remarks, and behavioral tags (e.g. *"Proactive & Collaborative"*, *"Strong Analytical Skills"*).
- **Subject Notes Hub (MLOps & Deep Learning)**: Curated study modules with search, subject filter, and in-depth formatted Markdown reading view with formulas and code.

### 👩‍🏫 2. Teacher / Faculty Portal
- **Student Roster Management**: View all enrolled students with search and quick filters (*Attendance Warnings <75%*, *Dean's Honor List ≥9.0 GPA*).
- **Edit Student Details**:
  - **Modify Attendance**: Adjust attended vs. total classes per subject with automated percentage recomputation.
  - **Edit Marks**: Enter scores across Midterm, Assignments, Labs, and Finals with automated recalculation of total score, grade, and overall student GPA.
  - **Post Behavioral Feedback**: Submit feedback categorized under *Academic Suggestion*, *Behavior & Conduct*, or *Lab Performance* with custom behavioral badges.
- **Publish & Manage Notes**: Create, edit, and delete lecture modules for **MLOps**, **Deep Learning (DL)**, and upcoming subjects.

---

## 🏗️ Project Architecture

```
My-project/
├── backend/
│   ├── app/
│   │   ├── config.py           # JWT & App configuration
│   │   ├── database.py         # SQLAlchemy engine & SQLite session
│   │   ├── models.py           # DB models: User, Student, Subject, Attendance, Marks, Feedback, Notes
│   │   ├── schemas.py          # Pydantic schemas for request/response serialization
│   │   ├── auth.py             # JWT token generation, role verification dependencies
│   │   ├── seed_data.py        # Seed script with realistic AIML students, teachers, & notes
│   │   └── routers/
│   │       ├── auth_router.py  # /api/auth (login, me, demo-accounts)
│   │       ├── student_router.py # /api/student (dashboard, attendance, marks, feedback)
│   │       ├── teacher_router.py # /api/teacher (students roster, update marks/attendance, feedback)
│   │       └── notes_router.py   # /api/notes (MLOps & DL notes CRUD)
│   └── main.py                 # FastAPI application, CORS, static file mounting
├── frontend/
│   ├── index.html              # Modern Nordic slate dashboard UI
│   ├── style.css               # Clean typography, badge styles, markdown styling
│   └── app.js                  # Frontend client, role switcher, API integration
├── postman/
│   └── Student_Management_System_API.postman_collection.json # Complete Postman test collection
├── tests/
│   └── test_api.py             # Automated API test suite
├── requirements.txt            # Python dependencies
├── run.py                      # One-click startup script
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Virtual Environment (Already Configured)
The virtual environment has already been set up in `venv/`. If you ever need to activate it manually in a new PowerShell window:

```powershell
.\venv\Scripts\Activate.ps1
```

*(Or on Command Prompt: `venv\Scripts\activate.bat`)*

### 2. Install Dependencies (If not already installed)
```powershell
.\venv\Scripts\pip install -r requirements.txt
```

### 3. Run the Application
Run the root startup script:
```powershell
.\venv\Scripts\python run.py
```

The system will start and be available at:
- 🌐 **Web Dashboard UI**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- 📖 **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 📑 **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🐳 Running with Docker

You can build and run the application in a lightweight Docker container:

### Using Docker CLI:
```bash
# 1. Build Docker image
docker build -t acadex-sms .

# 2. Run container on port 8000
docker run -p 8000:8000 --name acadex_container acadex-sms
```

### Using Docker Compose (Recommended):
```bash
docker compose up --build
```
Access the application at [http://localhost:8000](http://localhost:8000).

---

## 🔑 Demo Login Credentials

You can use the **"Quick Switch Role"** button at the top right of the UI, or sign in manually with these accounts:

| Role | Username | Password | Profile / Notes |
| :--- | :--- | :--- | :--- |
| **Student** | `student_aarav` | `student123` | Aarav Patel — 92.8% Attendance, 9.1 GPA (Dean's List) |
| **Student** | `student_rohan` | `student123` | Rohan Gupta — 66.7% Attendance (Attendance Warning) |
| **Student** | `student_diya` | `student123` | Diya Sen — 83.3% Attendance, 8.4 GPA (Good Standing) |
| **Student** | `student_ananya`| `student123` | Ananya Iyer — 94.2% Attendance, 8.8 GPA |
| **Teacher** | `teacher_priya` | `teacher123` | Dr. Priya Sharma — MLOps & NLP Faculty |
| **Teacher** | `teacher_rajesh`| `teacher123` | Prof. Rajesh Verma — Deep Learning & CV Faculty |

---

## 📮 Testing with Postman

A ready-to-use Postman Collection is provided in `postman/Student_Management_System_API.postman_collection.json`.

### How to Import and Test:
1. Open **Postman**.
2. Click **Import** (top left).
3. Drag and drop `postman/Student_Management_System_API.postman_collection.json` (or click *Files* and navigate to this folder).
4. Run the **"Login as Student"** request — Postman will automatically capture the JWT token into the `{{student_token}}` variable.
5. Run the **"Login as Teacher"** request — Postman will capture the JWT token into the `{{teacher_token}}` variable.
6. Now you can test all endpoints in any folder:
   - `01 - Authentication`
   - `02 - Student Portal` (Dashboard, Attendance, Marks, Feedback)
   - `03 - Subject Notes (MLOps & DL)` (Get all, Filter by MLOps, Filter by DL, Read note, Create note)
   - `04 - Teacher Portal` (Roster, Edit Attendance, Edit Marks, Add Behavioral Feedback)
   - `05 - System Health`

### Automated CLI Test Suite:
You can also run the automated Python test suite at any time:
```powershell
.\venv\Scripts\python tests\test_api.py
```
All 10 endpoint test suites will verify authentication, role guards, student dashboards, and teacher modification endpoints.

