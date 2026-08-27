from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Co-Lab API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock Database
students_db = [
    {
        "id": 1,
        "name": "Alex Johnson",
        "email": "alex@college.edu",
        "skills": ["Python", "FastAPI"],
        "projects": [
            {
                "id": 101,
                "title": "Smart Campus App",
                "repo": "https://github.com/alex/campus-app",
                "status": "Verified",
                "verified_by": "Dr. Smith"
            }
        ]
    }
]

@app.get("/")
def home():
    return {"message": "Co-Lab API is live!"}

@app.get("/api/students/portfolio")
def get_portfolio():
    return {"students": students_db}

@app.post("/api/mentor/approve/{project_id}")
def approve_project(project_id: int, mentor_name: str):
    for student in students_db:
        for project in student["projects"]:
            if project["id"] == project_id:
                project["status"] = "Verified"
                project["verified_by"] = mentor_name
                return {"message": "Project verified!", "project": project}
    return {"error": "Project not found"}