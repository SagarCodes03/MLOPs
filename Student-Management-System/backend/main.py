import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.database import engine, Base
from backend.app.seed_data import seed_database
from backend.app.routers import auth_router, student_router, teacher_router, notes_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB & Seed data on startup
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield

app = FastAPI(
    title="Student Management System REST API",
    description="Role-based REST API for Students & Teachers with Attendance, Marks, Behavioral Feedback & Subject Notes (MLOps, DL)",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend and API testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router.router)
app.include_router(student_router.router)
app.include_router(teacher_router.router)
app.include_router(notes_router.router)

# Mount Frontend static files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/", tags=["Frontend"])
    async def serve_index():
        return FileResponse(os.path.join(frontend_dir, "index.html"))

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "Student Management System API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

