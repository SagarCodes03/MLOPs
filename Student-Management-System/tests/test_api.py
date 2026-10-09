import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app
from backend.app.seed_data import seed_database

def test_api_suite():
    # Ensure database is seeded
    seed_database()
    client = TestClient(app)

    print("\n--- 1. Testing Health & Frontend Serving ---")
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
    
    res_ui = client.get("/")
    assert res_ui.status_code == 200
    assert "Acadex" in res_ui.text

    res_css = client.get("/static/style.css")
    assert res_css.status_code == 200

    res_js = client.get("/static/app.js")
    assert res_js.status_code == 200
    print("Health check & Frontend UI static assets served OK!")

    print("\n--- 2. Testing Student Login ---")
    res = client.post("/api/auth/login", json={"username": "student_aarav", "password": "student123"})
    assert res.status_code == 200, res.text
    student_data = res.json()
    student_token = student_data["access_token"]
    assert student_data["role"] == "student"
    print(f"Student login OK! Logged in as: {student_data['full_name']}")

    student_headers = {"Authorization": f"Bearer {student_token}"}

    print("\n--- 3. Testing Student Dashboard ---")
    res = client.get("/api/student/dashboard", headers=student_headers)
    assert res.status_code == 200, res.text
    dash = res.json()
    assert "profile" in dash
    assert dash["profile"]["roll_number"] == "AIML-2024-001"
    assert len(dash["attendance"]) > 0
    assert len(dash["marks"]) > 0
    print(f"Student Dashboard OK! Overall attendance: {dash['overall_attendance']}%, GPA: {dash['profile']['gpa']}")

    print("\n--- 4. Testing Student Notes (MLOps & DL) ---")
    # All notes
    res = client.get("/api/notes", headers=student_headers)
    assert res.status_code == 200
    all_notes = res.json()
    assert len(all_notes) >= 6
    print(f"Total Notes retrieved: {len(all_notes)}")

    # Filter MLOps
    res_mlops = client.get("/api/notes?subject=MLOps", headers=student_headers)
    assert res_mlops.status_code == 200
    mlops_notes = res_mlops.json()
    assert len(mlops_notes) >= 3
    assert all("MLOps" in n["subject_name"] for n in mlops_notes)
    print(f"MLOps Notes retrieved: {len(mlops_notes)}")

    # Filter Deep Learning
    res_dl = client.get("/api/notes?subject=Deep Learning", headers=student_headers)
    assert res_dl.status_code == 200
    dl_notes = res_dl.json()
    assert len(dl_notes) >= 3
    assert all("Deep Learning" in n["subject_name"] for n in dl_notes)
    print(f"Deep Learning Notes retrieved: {len(dl_notes)}")

    print("\n--- 5. Testing Teacher Login ---")
    res = client.post("/api/auth/login", json={"username": "teacher_priya", "password": "teacher123"})
    assert res.status_code == 200, res.text
    teacher_data = res.json()
    teacher_token = teacher_data["access_token"]
    assert teacher_data["role"] == "teacher"
    print(f"Teacher login OK! Logged in as: {teacher_data['full_name']}")

    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}

    print("\n--- 6. Testing Teacher Viewing Students List ---")
    res = client.get("/api/teacher/students", headers=teacher_headers)
    assert res.status_code == 200
    students = res.json()
    assert len(students) >= 4
    student_id = students[0]["id"]
    print(f"Teacher retrieved {len(students)} students.")

    print("\n--- 7. Testing Teacher Editing Student Attendance ---")
    res = client.put(
        f"/api/teacher/students/{student_id}/attendance/1",
        headers=teacher_headers,
        json={"total_classes": 45, "attended_classes": 43}
    )
    assert res.status_code == 200, res.text
    att_updated = res.json()
    assert att_updated["attended_classes"] == 43
    assert att_updated["percentage"] == 95.6
    print(f"Attendance updated: {att_updated['percentage']}% ({att_updated['attended_classes']}/{att_updated['total_classes']})")

    print("\n--- 8. Testing Teacher Editing Student Marks ---")
    res = client.put(
        f"/api/teacher/students/{student_id}/marks/1",
        headers=teacher_headers,
        json={"midterm_score": 29.0, "assignment_score": 19.5, "lab_score": 20.0, "final_score": 29.5}
    )
    assert res.status_code == 200, res.text
    marks_updated = res.json()
    assert marks_updated["total_score"] == 98.0
    assert marks_updated["grade"] == "A+"
    print(f"Marks updated: total={marks_updated['total_score']}, grade={marks_updated['grade']}")

    print("\n--- 9. Testing Teacher Adding Feedback & Behavior Remark ---")
    res = client.post(
        f"/api/teacher/students/{student_id}/feedback",
        headers=teacher_headers,
        json={
            "subject": "MLOps",
            "category": "Behavior & Conduct",
            "feedback_text": "Demonstrated proactive initiative in setting up automated GitHub Actions workflow during the lab evaluation.",
            "behavior_tag": "Leadership & Punctual"
        }
    )
    assert res.status_code == 200, res.text
    fb_created = res.json()
    assert fb_created["behavior_tag"] == "Leadership & Punctual"
    print(f"Feedback added! ID: {fb_created['id']}, Tag: {fb_created['behavior_tag']}")

    print("\n--- 10. Testing Student Authorization Guard ---")
    # Student trying to perform teacher action must get 403 Forbidden
    res = client.get("/api/teacher/students", headers=student_headers)
    assert res.status_code == 403
    print("Role-based authorization guard verified: Student blocked from Teacher endpoints (403 Forbidden).")

    print("\nALL API TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_api_suite()
