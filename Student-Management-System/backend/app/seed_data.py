from sqlalchemy.orm import Session
from backend.app.database import SessionLocal, engine, Base
from backend.app.models import User, StudentProfile, Subject, AttendanceRecord, MarkRecord, TeacherFeedback, SubjectNote
from backend.app.auth import hash_password

def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # Check if data already exists
    if db.query(User).first():
        db.close()
        return

    print("Seeding database with initial users, subjects, marks, attendance, and notes...")

    # 1. Teachers
    teacher1 = User(
        username="teacher_priya",
        email="priya.sharma@aiml.edu",
        hashed_password=hash_password("teacher123"),
        full_name="Dr. Priya Sharma",
        role="teacher",
        avatar_url="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150"
    )
    teacher2 = User(
        username="teacher_rajesh",
        email="rajesh.verma@aiml.edu",
        hashed_password=hash_password("teacher123"),
        full_name="Prof. Rajesh Verma",
        role="teacher",
        avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150"
    )
    db.add_all([teacher1, teacher2])
    db.flush()

    # 2. Students
    student1_user = User(
        username="student_aarav",
        email="aarav.patel@student.aiml.edu",
        hashed_password=hash_password("student123"),
        full_name="Aarav Patel",
        role="student",
        avatar_url="https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150"
    )
    student2_user = User(
        username="student_diya",
        email="diya.sen@student.aiml.edu",
        hashed_password=hash_password("student123"),
        full_name="Diya Sen",
        role="student",
        avatar_url="https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150"
    )
    student3_user = User(
        username="student_rohan",
        email="rohan.gupta@student.aiml.edu",
        hashed_password=hash_password("student123"),
        full_name="Rohan Gupta",
        role="student",
        avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150"
    )
    student4_user = User(
        username="student_ananya",
        email="ananya.iyer@student.aiml.edu",
        hashed_password=hash_password("student123"),
        full_name="Ananya Iyer",
        role="student",
        avatar_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150"
    )
    db.add_all([student1_user, student2_user, student3_user, student4_user])
    db.flush()

    # Student Profiles
    sp1 = StudentProfile(
        user_id=student1_user.id,
        roll_number="AIML-2024-001",
        department="Artificial Intelligence & Machine Learning",
        semester=6,
        academic_standing="Dean's Honor List",
        gpa=9.1
    )
    sp2 = StudentProfile(
        user_id=student2_user.id,
        roll_number="AIML-2024-002",
        department="Artificial Intelligence & Machine Learning",
        semester=6,
        academic_standing="Good Standing",
        gpa=8.4
    )
    sp3 = StudentProfile(
        user_id=student3_user.id,
        roll_number="AIML-2024-003",
        department="Artificial Intelligence & Machine Learning",
        semester=6,
        academic_standing="Academic Warning (Attendance)",
        gpa=6.8
    )
    sp4 = StudentProfile(
        user_id=student4_user.id,
        roll_number="AIML-2024-004",
        department="Artificial Intelligence & Machine Learning",
        semester=6,
        academic_standing="Good Standing",
        gpa=8.8
    )
    db.add_all([sp1, sp2, sp3, sp4])
    db.flush()

    # 3. Subjects
    sub_mlops = Subject(
        code="CS601",
        name="Machine Learning Operations (MLOps)",
        credits=4,
        instructor_name="Dr. Priya Sharma"
    )
    sub_dl = Subject(
        code="CS602",
        name="Deep Learning & Neural Architectures (DL)",
        credits=4,
        instructor_name="Prof. Rajesh Verma"
    )
    sub_nlp = Subject(
        code="CS603",
        name="Natural Language Processing (NLP)",
        credits=3,
        instructor_name="Dr. Priya Sharma"
    )
    sub_cv = Subject(
        code="CS604",
        name="Computer Vision (CV)",
        credits=3,
        instructor_name="Prof. Rajesh Verma"
    )
    db.add_all([sub_mlops, sub_dl, sub_nlp, sub_cv])
    db.flush()

    # 4. Attendance Records
    # Student 1 (Aarav)
    att_s1_1 = AttendanceRecord(student_id=sp1.id, subject_id=sub_mlops.id, total_classes=42, attended_classes=39, percentage=92.8)
    att_s1_2 = AttendanceRecord(student_id=sp1.id, subject_id=sub_dl.id, total_classes=40, attended_classes=36, percentage=90.0)
    att_s1_3 = AttendanceRecord(student_id=sp1.id, subject_id=sub_nlp.id, total_classes=36, attended_classes=32, percentage=88.9)
    att_s1_4 = AttendanceRecord(student_id=sp1.id, subject_id=sub_cv.id, total_classes=38, attended_classes=35, percentage=92.1)

    # Student 2 (Diya)
    att_s2_1 = AttendanceRecord(student_id=sp2.id, subject_id=sub_mlops.id, total_classes=42, attended_classes=35, percentage=83.3)
    att_s2_2 = AttendanceRecord(student_id=sp2.id, subject_id=sub_dl.id, total_classes=40, attended_classes=34, percentage=85.0)
    att_s2_3 = AttendanceRecord(student_id=sp2.id, subject_id=sub_nlp.id, total_classes=36, attended_classes=29, percentage=80.5)
    att_s2_4 = AttendanceRecord(student_id=sp2.id, subject_id=sub_cv.id, total_classes=38, attended_classes=32, percentage=84.2)

    # Student 3 (Rohan - Low attendance)
    att_s3_1 = AttendanceRecord(student_id=sp3.id, subject_id=sub_mlops.id, total_classes=42, attended_classes=28, percentage=66.7)
    att_s3_2 = AttendanceRecord(student_id=sp3.id, subject_id=sub_dl.id, total_classes=40, attended_classes=25, percentage=62.5)
    att_s3_3 = AttendanceRecord(student_id=sp3.id, subject_id=sub_nlp.id, total_classes=36, attended_classes=26, percentage=72.2)
    att_s3_4 = AttendanceRecord(student_id=sp3.id, subject_id=sub_cv.id, total_classes=38, attended_classes=27, percentage=71.0)

    # Student 4 (Ananya)
    att_s4_1 = AttendanceRecord(student_id=sp4.id, subject_id=sub_mlops.id, total_classes=42, attended_classes=40, percentage=95.2)
    att_s4_2 = AttendanceRecord(student_id=sp4.id, subject_id=sub_dl.id, total_classes=40, attended_classes=37, percentage=92.5)
    att_s4_3 = AttendanceRecord(student_id=sp4.id, subject_id=sub_nlp.id, total_classes=36, attended_classes=34, percentage=94.4)
    att_s4_4 = AttendanceRecord(student_id=sp4.id, subject_id=sub_cv.id, total_classes=38, attended_classes=36, percentage=94.7)

    db.add_all([att_s1_1, att_s1_2, att_s1_3, att_s1_4,
                att_s2_1, att_s2_2, att_s2_3, att_s2_4,
                att_s3_1, att_s3_2, att_s3_3, att_s3_4,
                att_s4_1, att_s4_2, att_s4_3, att_s4_4])

    # 5. Marks Records (midterm max 30, assignment max 20, lab max 20, final max 30)
    # Aarav
    m_s1_1 = MarkRecord(student_id=sp1.id, subject_id=sub_mlops.id, midterm_score=28.5, assignment_score=19.0, lab_score=19.5, final_score=28.0, total_score=95.0, grade="A+")
    m_s1_2 = MarkRecord(student_id=sp1.id, subject_id=sub_dl.id, midterm_score=27.0, assignment_score=18.5, lab_score=19.0, final_score=27.5, total_score=92.0, grade="A+")
    m_s1_3 = MarkRecord(student_id=sp1.id, subject_id=sub_nlp.id, midterm_score=26.0, assignment_score=18.0, lab_score=18.0, final_score=26.0, total_score=88.0, grade="A")
    m_s1_4 = MarkRecord(student_id=sp1.id, subject_id=sub_cv.id, midterm_score=27.5, assignment_score=19.0, lab_score=18.5, final_score=27.0, total_score=92.0, grade="A+")

    # Diya
    m_s2_1 = MarkRecord(student_id=sp2.id, subject_id=sub_mlops.id, midterm_score=25.0, assignment_score=17.0, lab_score=17.5, final_score=25.5, total_score=85.0, grade="A")
    m_s2_2 = MarkRecord(student_id=sp2.id, subject_id=sub_dl.id, midterm_score=24.5, assignment_score=16.5, lab_score=18.0, final_score=24.0, total_score=83.0, grade="B+")
    m_s2_3 = MarkRecord(student_id=sp2.id, subject_id=sub_nlp.id, midterm_score=25.0, assignment_score=18.0, lab_score=17.0, final_score=25.0, total_score=85.0, grade="A")
    m_s2_4 = MarkRecord(student_id=sp2.id, subject_id=sub_cv.id, midterm_score=26.0, assignment_score=17.5, lab_score=18.0, final_score=26.5, total_score=88.0, grade="A")

    # Rohan
    m_s3_1 = MarkRecord(student_id=sp3.id, subject_id=sub_mlops.id, midterm_score=18.0, assignment_score=13.0, lab_score=14.0, final_score=20.0, total_score=65.0, grade="C+")
    m_s3_2 = MarkRecord(student_id=sp3.id, subject_id=sub_dl.id, midterm_score=19.0, assignment_score=14.0, lab_score=13.5, final_score=21.5, total_score=68.0, grade="C+")
    m_s3_3 = MarkRecord(student_id=sp3.id, subject_id=sub_nlp.id, midterm_score=20.0, assignment_score=15.0, lab_score=15.0, final_score=22.0, total_score=72.0, grade="B")
    m_s3_4 = MarkRecord(student_id=sp3.id, subject_id=sub_cv.id, midterm_score=19.5, assignment_score=14.5, lab_score=14.0, final_score=21.0, total_score=69.0, grade="B-")

    # Ananya
    m_s4_1 = MarkRecord(student_id=sp4.id, subject_id=sub_mlops.id, midterm_score=27.0, assignment_score=18.5, lab_score=19.0, final_score=27.5, total_score=92.0, grade="A+")
    m_s4_2 = MarkRecord(student_id=sp4.id, subject_id=sub_dl.id, midterm_score=26.0, assignment_score=18.0, lab_score=18.5, final_score=26.5, total_score=89.0, grade="A")
    m_s4_3 = MarkRecord(student_id=sp4.id, subject_id=sub_nlp.id, midterm_score=26.5, assignment_score=18.5, lab_score=18.0, final_score=27.0, total_score=90.0, grade="A+")
    m_s4_4 = MarkRecord(student_id=sp4.id, subject_id=sub_cv.id, midterm_score=27.0, assignment_score=18.0, lab_score=18.5, final_score=26.5, total_score=90.0, grade="A+")

    db.add_all([m_s1_1, m_s1_2, m_s1_3, m_s1_4,
                m_s2_1, m_s2_2, m_s2_3, m_s2_4,
                m_s3_1, m_s3_2, m_s3_3, m_s3_4,
                m_s4_1, m_s4_2, m_s4_3, m_s4_4])

    # 6. Teacher Feedback & Behavioral Remarks
    f1 = TeacherFeedback(
        student_id=sp1.id,
        teacher_name="Dr. Priya Sharma",
        subject="MLOps",
        category="Academic Suggestion",
        feedback_text="Exceptional understanding of CI/CD orchestration and DVC versioning. Suggested to explore Kubeflow and BentoML containerization for the capstone project.",
        behavior_tag="Proactive & Collaborative"
    )
    f2 = TeacherFeedback(
        student_id=sp1.id,
        teacher_name="Prof. Rajesh Verma",
        subject="Deep Learning",
        category="Lab Performance",
        feedback_text="Mastered PyTorch automatic differentiation and ResNet implementation with custom skip connections. Demonstrated strong peer mentoring in lab hours.",
        behavior_tag="Strong Analytical Skills"
    )
    f3 = TeacherFeedback(
        student_id=sp2.id,
        teacher_name="Dr. Priya Sharma",
        subject="MLOps",
        category="Behavior & Conduct",
        feedback_text="Active participation in interactive system design discussions. Needs slight improvement in automated test coverage for ML data drift pipelines.",
        behavior_tag="Good Engagement"
    )
    f4 = TeacherFeedback(
        student_id=sp3.id,
        teacher_name="Prof. Rajesh Verma",
        subject="Deep Learning",
        category="Academic Suggestion",
        feedback_text="Attendance has dropped below 65%. Needs to complete pending lab submissions on Backprop derivations and attend remedial doubt-clearing sessions.",
        behavior_tag="Attendance Attention Needed"
    )
    db.add_all([f1, f2, f3, f4])

    # 7. Subject Notes (MLOps & Deep Learning)
    # MLOps Notes
    n_mlops_1 = SubjectNote(
        subject_name="MLOps",
        title="Unit 1: The MLOps Lifecycle & Technical Debt in AI",
        unit="Unit 1: Foundations",
        summary="Understanding the transition from experimental Jupyter notebooks to production-grade ML microservices.",
        content_markdown="""# Unit 1: The MLOps Lifecycle & Technical Debt

### 1. What is MLOps?
MLOps (Machine Learning Operations) is a paradigm that aims to deploy and maintain machine learning models in production reliably and efficiently. It unifies **Machine Learning**, **Software Engineering (DevOps)**, and **Data Engineering**.

### 2. The Hidden Technical Debt in Machine Learning
In Google's seminal paper *"Hidden Technical Debt in Machine Learning Systems"*, ML code represents only a tiny black box in the center (often < 5% of the codebase).
The surrounding infrastructure includes:
- **Configuration & Hyperparameter Management**
- **Data Collection, Cleaning & Verification**
- **Feature Extraction & Feature Store (e.g., Feast)**
- **Resource Management (GPUs/TPUs)**
- **Analysis, Monitoring, and Alerting**

### 3. Key Stages of the MLOps Pipeline
1. **Data Ingestion & Verification**: Schema validation with Great Expectations.
2. **Experiment Tracking**: Logging code, parameters, metrics, and weights with MLflow or Weights & Biases.
3. **Continuous Training (CT)**: Automated retraining triggers upon drift detection.
4. **Model Registry & Staging**: Versioned artifacts with staging -> production transition gates.
5. **Model Serving & Monitoring**: Real-time low-latency REST/gRPC inference with drift alarms.
""",
        resource_url="https://ml-ops.org/",
        tags="Lifecycle, Technical Debt, Architecture, Best Practices",
        author_name="Dr. Priya Sharma"
    )

    n_mlops_2 = SubjectNote(
        subject_name="MLOps",
        title="Unit 2: Data & Model Versioning with DVC & MLflow",
        unit="Unit 2: Version Control & Tracking",
        summary="Decoupling large datasets and model artifacts from Git using Data Version Control (DVC) and MLflow tracking.",
        content_markdown="""# Unit 2: Data & Model Version Control

### 1. The Challenge of Versioning Data in Git
Git is optimized for textual source code. Storing gigabytes of training data (`.parquet`, `.csv`, `.h5`) in Git causes repository bloat and slows checkouts.

### 2. How DVC (Data Version Control) Works
DVC stores data hashes in tiny `.dvc` pointer files that live inside Git, while the actual binary payloads reside in remote object storage (AWS S3, MinIO, Google Cloud Storage, or local NAS):
```bash
# Initialize DVC in existing git repo
dvc init

# Track large dataset
dvc add data/raw_training_data.csv
git add data/raw_training_data.csv.dvc .gitignore

# Push actual dataset to remote storage
dvc remote add -d myremote s3://my-mlops-bucket/data
dvc push
```

### 3. MLflow Tracking & Registry
- **Parameters**: `mlflow.log_param("learning_rate", 0.001)`
- **Metrics**: `mlflow.log_metric("val_f1_score", 0.942, step=epoch)`
- **Artifacts**: `mlflow.log_model(pytorch_model, "resnet_classifier")`
- **Model Registry Stages**: `None` -> `Staging` -> `Production` -> `Archived`.
""",
        resource_url="https://dvc.org/doc",
        tags="DVC, MLflow, Versioning, S3, Experiments",
        author_name="Dr. Priya Sharma"
    )

    n_mlops_3 = SubjectNote(
        subject_name="MLOps",
        title="Unit 3: Containerization & Model Serving (FastAPI + Docker)",
        unit="Unit 3: Serving & Packaging",
        summary="Packaging deep learning models into lightweight container images for reproducible deployment with FastAPI.",
        content_markdown="""# Unit 3: Containerized Model Serving

### 1. REST API Design for ML Inference
FastAPI provides high-throughput asynchronous execution and automatic schema validation via Pydantic:

```python
from fastapi import FastAPI
from pydantic import BaseModel
import torch

app = FastAPI(title="MLOps Classifier API")

class PredictionRequest(BaseModel):
    features: list[float]

@app.post("/predict")
def predict(payload: PredictionRequest):
    tensor_input = torch.tensor(payload.features).unsqueeze(0)
    with torch.no_grad():
        preds = model(tensor_input)
    return {"prediction": int(preds.argmax()), "confidence": float(preds.max())}
```

### 2. Multi-Stage Dockerfile Best Practices
1. Use lightweight base images (e.g. `python:3.11-slim`).
2. Cache dependencies before copying code.
3. Run as non-root user for enterprise security.
4. Pre-download weights into the image or volume mount.
""",
        resource_url="https://fastapi.tiangolo.com/",
        tags="FastAPI, Docker, Microservices, Inference",
        author_name="Dr. Priya Sharma"
    )

    # Deep Learning Notes
    n_dl_1 = SubjectNote(
        subject_name="Deep Learning",
        title="Unit 1: Automatic Differentiation & Backpropagation",
        unit="Unit 1: Foundations & Optimization",
        summary="Detailed derivation of gradient descent, computation graphs, and matrix calculus in modern deep learning.",
        content_markdown="""# Unit 1: Foundations of Deep Learning & Backprop

### 1. Computation Graphs & The Chain Rule
In deep learning, every neural network is formulated as a directed acyclic graph (DAG) of composite mathematical operations:
$$\\hat{y} = f(W_2 \\cdot \\sigma(W_1 x + b_1) + b_2)$$

### 2. Gradient Calculation via Reverse Mode Autodiff
For an intermediate layer activation $z^{[l]} = W^{[l]} a^{[l-1]} + b^{[l]}$ and loss function $\\mathcal{L}$:
$$\\frac{\\partial \\mathcal{L}}{\\partial W^{[l]}} = \\frac{\\partial \\mathcal{L}}{\\partial z^{[l]}} \\cdot (a^{[l-1]})^T$$
$$\\frac{\\partial \\mathcal{L}}{\\partial b^{[l]}} = \\frac{\\partial \\mathcal{L}}{\\partial z^{[l]}}$$

### 3. Optimization Algorithms
- **SGD with Momentum**: Accelerates vectors in persistent gradient directions while dampening oscillations:
  $$v_t = \\beta v_{t-1} + (1-\\beta) \\nabla_{\\theta} \\mathcal{L}$$
- **Adam (Adaptive Moment Estimation)**: Computes adaptive learning rates for each parameter using exponentially decaying averages of past squared gradients ($v_t$) and past gradients ($m_t$).
""",
        resource_url="https://pytorch.org/tutorials/",
        tags="Backpropagation, Autodiff, Adam, PyTorch, Math",
        author_name="Prof. Rajesh Verma"
    )

    n_dl_2 = SubjectNote(
        subject_name="Deep Learning",
        title="Unit 2: Convolutional Neural Networks & ResNet Architecture",
        unit="Unit 2: Spatial Feature Extraction",
        summary="Convolution arithmetic, receptive fields, batch normalization, and solving vanishing gradients with residual shortcuts.",
        content_markdown="""# Unit 2: Convolutional Neural Networks (CNNs)

### 1. Convolution Arithmetic
Output spatial dimensions for input dimension $W$, filter size $K$, padding $P$, and stride $S$:
$$W_{out} = \\left\\lfloor \\frac{W - K + 2P}{S} \\right\\rfloor + 1$$

### 2. Why Residual Connections (ResNet)?
As networks grow deeper (e.g. 50+ layers), training accuracy degrades due to the vanishing/exploding gradient problem.
ResNet solves this by introducing identity shortcut connections:
$$\\mathcal{H}(x) = \\mathcal{F}(x, \\{W_i\\}) + x$$
The gradient flow during backpropagation contains an uninterrupted highway:
$$\\frac{\\partial \\mathcal{E}}{\\partial x} = \\frac{\\partial \\mathcal{E}}{\\partial \\mathcal{H}} \\left( \\frac{\\partial \\mathcal{F}}{\\partial x} + I \\right)$$
Even if $\\frac{\\partial \\mathcal{F}}{\\partial x} \\approx 0$, gradients flow intact via the identity matrix $I$.
""",
        resource_url="https://arxiv.org/abs/1512.03385",
        tags="CNN, ResNet, Computer Vision, Skip Connections",
        author_name="Prof. Rajesh Verma"
    )

    n_dl_3 = SubjectNote(
        subject_name="Deep Learning",
        title="Unit 3: The Transformer & Multi-Head Self-Attention",
        unit="Unit 3: Sequence Modeling & Attention",
        summary="From RNN bottlenecks to parallelized self-attention: Queries, Keys, Values, and positional embeddings.",
        content_markdown="""# Unit 3: Transformers & Self-Attention

### 1. The Bottleneck of RNNs / LSTMs
Recurrent networks process tokens sequentially ($h_t = f(h_{t-1}, x_t)$), preventing parallelization during training and suffering from memory compression on long contexts.

### 2. Scaled Dot-Product Attention
Given input representations projected into queries $Q$, keys $K$, and values $V$:
$$\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right) V$$
- $QK^T$ calculates token-to-token similarity matrix.
- Division by $\\sqrt{d_k}$ prevents dot products from growing excessively large, avoiding vanishing gradients in the softmax.

### 3. Multi-Head Attention
$$\\text{MultiHead}(Q, K, V) = \\text{Concat}(\\text{head}_1, \\dots, \\text{head}_h) W^O$$
where each $\\text{head}_i = \\text{Attention}(Q W_i^Q, K W_i^K, V W_i^V)$.
""",
        resource_url="https://arxiv.org/abs/1706.03762",
        tags="Transformers, Attention, Self-Attention, LLMs",
        author_name="Prof. Rajesh Verma"
    )

    db.add_all([n_mlops_1, n_mlops_2, n_mlops_3, n_dl_1, n_dl_2, n_dl_3])

    db.commit()
    db.close()
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()

