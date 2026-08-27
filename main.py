from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI(title="Co-Lab API")


# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Mock Database
# -----------------------------

students_db = [
    {
        "id": 1,
        "name": "Alex Johnson",
        "email": "alex@college.edu",
        "skills": [],
        "verified_skills": [],
        "projects": [
            {
                "id": 101,
                "title": "Smart Campus App",
                "description": "A campus management application.",
                "repo": "https://github.com/alex/campus-app",
                "status": "Verified",
                "verified_by": "Dr. Smith",
                "skill": "Python",
            }
        ],
    }
]


# -----------------------------
# Assessment Data
# -----------------------------

python_questions = [
    {
        "id": 1,
        "question": "Which keyword is used to define a function in Python?",
        "options": ["function", "def", "fun", "define"],
        "answer": "def",
    },
    {
        "id": 2,
        "question": "Which data type is used to store a collection of key-value pairs?",
        "options": ["List", "Tuple", "Dictionary", "Set"],
        "answer": "Dictionary",
    },
    {
        "id": 3,
        "question": "What is the output of len([10, 20, 30])?",
        "options": ["2", "3", "4", "30"],
        "answer": "3",
    },
    {
        "id": 4,
        "question": "Which symbol is used to start a comment in Python?",
        "options": ["//", "#", "/*", "--"],
        "answer": "#",
    },
    {
        "id": 5,
        "question": "Which keyword is used to create a loop over a sequence?",
        "options": ["repeat", "loop", "for", "iterate"],
        "answer": "for",
    },
]


# -----------------------------
# Request Models
# -----------------------------

class AssessmentSubmission(BaseModel):
    student_id: int
    skill: str
    answers: dict[int, str]


class ProjectSubmission(BaseModel):
    student_id: int
    title: str
    description: str
    github_url: str


# -----------------------------
# Basic API
# -----------------------------

@app.get("/")
def home():
    return {"message": "Co-Lab API is live!"}


# -----------------------------
# Student Portfolio
# -----------------------------

@app.get("/api/students/portfolio")
def get_portfolio():
    return {"students": students_db}


# -----------------------------
# Assessment
# -----------------------------

@app.get("/api/assessment/questions")
def get_assessment_questions(skill: str = "Python"):
    if skill.lower() != "python":
        return {
            "skill": skill,
            "questions": [],
            "message": "Only Python assessment is available for the demo."
        }

    questions = []

    for question in python_questions:
        questions.append(
            {
                "id": question["id"],
                "question": question["question"],
                "options": question["options"],
            }
        )

    return {
        "skill": "Python",
        "total_questions": len(questions),
        "questions": questions,
    }


@app.post("/api/assessment/submit")
def submit_assessment(submission: AssessmentSubmission):
    if submission.skill.lower() != "python":
        return {
            "error": "Only Python assessment is available for the demo."
        }

    score = 0

    for question in python_questions:
        question_id = question["id"]

        if submission.answers.get(question_id) == question["answer"]:
            score += 1

    total_questions = len(python_questions)

    if score >= 3:
        result = "Pass"
        skill_gap = False
        message = "You passed the Python assessment."
        suggested_project = None
    else:
        result = "Skill Gap Detected"
        skill_gap = True
        message = "Your Python skill needs improvement. Complete the suggested project to build practical experience."
        suggested_project = {
            "title": "Python Student Skill Builder",
            "description": "Build a Python-based student management application with CRUD operations, file handling, and basic data processing."
        }

    return {
        "student_id": submission.student_id,
        "skill": "Python",
        "score": score,
        "total": total_questions,
        "result": result,
        "skill_gap": skill_gap,
        "message": message,
        "suggested_project": suggested_project,
    }


# -----------------------------
# Project Submission
# -----------------------------

@app.post("/api/student/project")
def submit_project(submission: ProjectSubmission):
    for student in students_db:
        if student["id"] == submission.student_id:

            new_project_id = 1

            for existing_student in students_db:
                for project in existing_student["projects"]:
                    if project["id"] >= new_project_id:
                        new_project_id = project["id"] + 1

            new_project = {
                "id": new_project_id,
                "title": submission.title,
                "description": submission.description,
                "repo": submission.github_url,
                "status": "Pending Approval",
                "verified_by": None,
                "skill": "Python",
            }

            student["projects"].append(new_project)

            return {
                "message": "Project submitted successfully.",
                "project": new_project,
            }

    return {
        "error": "Student not found."
    }


# -----------------------------
# Mentor Approval
# -----------------------------

@app.post("/api/mentor/approve/{project_id}")
def approve_project(project_id: int, mentor_name: str):
    for student in students_db:
        for project in student["projects"]:

            if project["id"] == project_id:

                project["status"] = "Verified"
                project["verified_by"] = mentor_name

                skill = project.get("skill")

                if skill and skill not in student["verified_skills"]:
                    student["verified_skills"].append(skill)

                if skill and skill not in student["skills"]:
                    student["skills"].append(skill)

                return {
                    "message": "Project verified and skill endorsed!",
                    "student_id": student["id"],
                    "verified_skill": skill,
                    "project": project,
                }

    return {
        "error": "Project not found."
    }


# -----------------------------
# Recruiter Search
# -----------------------------

@app.get("/api/recruiter/search")
def recruiter_search(skill: str):
    matching_students = []

    for student in students_db:
        verified_skills = student.get("verified_skills", [])

        if any(
            verified_skill.lower() == skill.lower()
            for verified_skill in verified_skills
        ):
            matching_students.append(
                {
                    "id": student["id"],
                    "name": student["name"],
                    "email": student["email"],
                    "verified_skills": student["verified_skills"],
                    "projects": [
                        project
                        for project in student["projects"]
                        if project["status"] == "Verified"
                    ],
                }
            )

    return {
        "skill": skill,
        "students": matching_students,
        "count": len(matching_students),
    }