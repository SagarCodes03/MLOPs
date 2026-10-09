import uvicorn
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app.seed_data import seed_database

if __name__ == "__main__":
    print("=" * 60)
    print(" ACADEX | Student Management & Academic Intelligence System")
    print("=" * 60)
    
    # Initialize DB & Seed Data
    seed_database()

    print("\n[+] Server is starting up...")
    print("    - Web UI:               http://127.0.0.1:8000")
    print("    - Swagger API Docs:     http://127.0.0.1:8000/docs")
    print("    - Postman Collection:   postman/Student_Management_System_API.postman_collection.json")
    print("\n[+] Demo Credentials:")
    print("    * Student 1: username='student_aarav'  password='student123' (Aarav Patel - 92.8% Att)")
    print("    * Student 2: username='student_rohan'  password='student123' (Rohan Gupta - 66.7% Att)")
    print("    * Teacher 1: username='teacher_priya'  password='teacher123' (Dr. Priya Sharma - MLOps)")
    print("    * Teacher 2: username='teacher_rajesh' password='teacher123' (Prof. Rajesh Verma - DL)")
    print("=" * 60 + "\n")

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("backend.main:app", host=host, port=port, reload=False)

