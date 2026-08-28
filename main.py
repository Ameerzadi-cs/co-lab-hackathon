from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI(title="Co-Lab API")


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# MOCK DATABASE / DEMO DATA
# ============================================================

students_db = [
    {
        "id": 1,
        "name": "Alex Johnson",
        "email": "alex@college.edu",
        "college": "St. Claret College",
        "skills": ["Python", "FastAPI"],
        "verified_skills": ["Python"],
        "projects": [
            {
                "id": 101,
                "title": "Smart Campus App",
                "description": "A campus management application.",
                "repo": "https://github.com/alex-johnson/smart-campus-app",
                "status": "Verified",
                "verified_by": "Dr. Alan Thomas",
                "skill": "Python",
            }
        ],
        "assessment_completed": True,
        "assessment_score": 5,
        "completed_modules": [
            "Python Data Structures",
            "File Handling",
            "CRUD Operations",
            "Build a Project",
        ],
    },
    {
        "id": 2,
        "name": "Priya Sharma",
        "email": "priya@college.edu",
        "college": "St. Claret College",
        "skills": ["Java", "SQL"],
        "verified_skills": ["Java"],
        "projects": [
            {
                "id": 201,
                "title": "Library Management System",
                "description": "A Java-based application for managing books and student records.",
                "repo": "https://github.com/priya-sharma/library-management",
                "status": "Verified",
                "verified_by": "Dr. Alan Thomas",
                "skill": "Java",
            }
        ],
        "assessment_completed": False,
        "assessment_score": 0,
        "completed_modules": [],
    },
    {
        "id": 3,
        "name": "Rahul Mehta",
        "email": "rahul@college.edu",
        "college": "St. Claret College",
        "skills": ["Python", "Data Analysis"],
        "verified_skills": ["Python"],
        "projects": [
            {
                "id": 301,
                "title": "Student Performance Analyzer",
                "description": "A Python project that analyzes student academic performance using data processing.",
                "repo": "https://github.com/rahul-mehta/student-performance-analyzer",
                "status": "Verified",
                "verified_by": "Dr. Alan Thomas",
                "skill": "Python",
            }
        ],
        "assessment_completed": True,
        "assessment_score": 4,
        "completed_modules": [
            "Python Data Structures",
            "File Handling",
        ],
    },
    {
        "id": 4,
        "name": "Ananya Rao",
        "email": "ananya@college.edu",
        "college": "St. Claret College",
        "skills": [],
        "verified_skills": [],
        "projects": [],
        "assessment_completed": False,
        "assessment_score": 0,
        "completed_modules": [],
    },
]


# ============================================================
# DEMO MENTOR / RECRUITER
# ============================================================

mentor_profile = {
    "id": 1,
    "name": "Dr. Alan Thomas",
    "role": "Faculty Mentor",
    "college": "St. Claret College",
}

recruiter_profile = {
    "id": 1,
    "company": "Tech Innovators Inc.",
    "name": "Tech Innovators Inc. HR",
    "role": "Recruiter",
}


# ============================================================
# LEARNING MODULES
# ============================================================

learning_modules = [
    {
        "id": 1,
        "title": "Python Data Structures",
        "description": "Lists, tuples, dictionaries and sets.",
    },
    {
        "id": 2,
        "title": "File Handling",
        "description": "Read, write and process files using Python.",
    },
    {
        "id": 3,
        "title": "CRUD Operations",
        "description": "Build practical create, read, update and delete operations.",
    },
    {
        "id": 4,
        "title": "Build a Project",
        "description": "Apply your learning through a practical Python project.",
    },
]


# ============================================================
# PYTHON ASSESSMENT
# ============================================================

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


# ============================================================
# REQUEST MODELS
# ============================================================

class AssessmentSubmission(BaseModel):
    student_id: int
    skill: str
    answers: dict[int, str]


class ProjectSubmission(BaseModel):
    student_id: int
    title: str
    description: str
    github_url: str


class ModuleCompletion(BaseModel):
    student_id: int
    module_id: int


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def find_student(student_id: int):
    for student in students_db:
        if student["id"] == student_id:
            return student

    return None


def calculate_progress(student):
    """
    Demo industry-readiness calculation.

    20%  = assessment completed
    10%  = each of the 4 learning modules
    20%  = project submitted
    20%  = mentor verification

    Total = 100%
    """

    progress = 0

    if student.get("assessment_completed"):
        progress += 20

    completed_modules = student.get("completed_modules", [])

    progress += min(len(completed_modules), 4) * 10

    if len(student.get("projects", [])) > 0:
        progress += 20

    has_verified_project = any(
        project.get("status") == "Verified"
        for project in student.get("projects", [])
    )

    if has_verified_project:
        progress += 20

    return min(progress, 100)


# ============================================================
# HOME / HEALTH CHECK
# ============================================================

@app.get("/")
def home():
    return {
        "message": "Co-Lab API is live!"
    }


# ============================================================
# STUDENT PORTFOLIO
# ============================================================

@app.get("/api/students/portfolio")
def get_portfolio():
    return {
        "students": students_db
    }


# ============================================================
# STUDENT PROGRESS
# ============================================================

@app.get("/api/student/{student_id}/progress")
def get_student_progress(student_id: int):

    student = find_student(student_id)

    if student is None:
        return {
            "error": "Student not found."
        }

    progress = calculate_progress(student)

    completed_modules = student.get("completed_modules", [])

    verified_project = any(
        project.get("status") == "Verified"
        for project in student.get("projects", [])
    )

    return {
        "student_id": student_id,
        "industry_readiness": progress,
        "assessment_completed": student.get("assessment_completed", False),
        "assessment_score": student.get("assessment_score", 0),
        "completed_modules": completed_modules,
        "total_modules": len(learning_modules),
        "project_submitted": len(student.get("projects", [])) > 0,
        "mentor_verified": verified_project,
        "verified_skills": student.get("verified_skills", []),
    }


# ============================================================
# LEARNING MODULES
# ============================================================

@app.get("/api/learning/modules")
def get_learning_modules():
    return {
        "modules": learning_modules
    }


# ============================================================
# COMPLETE LEARNING MODULE
# ============================================================

@app.post("/api/learning/complete")
def complete_learning_module(completion: ModuleCompletion):

    student = find_student(completion.student_id)

    if student is None:
        return {
            "error": "Student not found."
        }

    module = None

    for current_module in learning_modules:
        if current_module["id"] == completion.module_id:
            module = current_module
            break

    if module is None:
        return {
            "error": "Learning module not found."
        }

    if module["title"] not in student["completed_modules"]:
        student["completed_modules"].append(module["title"])

    progress = calculate_progress(student)

    return {
        "message": "Learning module completed.",
        "module": module,
        "industry_readiness": progress,
        "completed_modules": student["completed_modules"],
    }


# ============================================================
# ASSESSMENT - LOAD QUESTIONS
# ============================================================

@app.get("/api/assessment/questions")
def get_assessment_questions(skill: str = "Python"):

    if skill.lower() != "python":
        return {
            "skill": skill,
            "questions": [],
            "message": "Only Python assessment is available for the demo.",
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


# ============================================================
# ASSESSMENT - SUBMIT ANSWERS
# ============================================================

@app.post("/api/assessment/submit")
def submit_assessment(submission: AssessmentSubmission):

    if submission.skill.lower() != "python":
        return {
            "error": "Only Python assessment is available for the demo."
        }

    student = find_student(submission.student_id)

    if student is None:
        return {
            "error": "Student not found."
        }

    score = 0

    for question in python_questions:

        question_id = question["id"]

        submitted_answer = submission.answers.get(question_id)

        if submitted_answer == question["answer"]:
            score += 1

    total_questions = len(python_questions)

    if score >= 3:

        result = "Pass"
        skill_gap = False

        message = (
            "You passed the Python assessment. "
            "Continue learning and build a project to gain practical experience."
        )

    else:

        result = "Skill Gap Detected"
        skill_gap = True

        message = (
            "Your Python skill needs improvement. "
            "Complete the recommended learning modules and build the suggested project."
        )

    # Assessment is now completed.
    student["assessment_completed"] = True
    student["assessment_score"] = score

    progress = calculate_progress(student)

    return {
        "student_id": submission.student_id,
        "skill": "Python",
        "score": score,
        "total": total_questions,
        "result": result,
        "skill_gap": skill_gap,
        "message": message,
        "industry_readiness": progress,
    }


# ============================================================
# PROJECT SUBMISSION
# ============================================================

@app.post("/api/student/project")
def submit_project(submission: ProjectSubmission):

    student = find_student(submission.student_id)

    if student is None:
        return {
            "error": "Student not found."
        }

    # Generate next project ID
    new_project_id = 1

    for existing_student in students_db:

        for project in existing_student.get("projects", []):

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

    progress = calculate_progress(student)

    return {
        "message": "Project submitted successfully.",
        "project": new_project,
        "industry_readiness": progress,
    }


# ============================================================
# GET STUDENT PROJECTS
# ============================================================

@app.get("/api/student/{student_id}/projects")
def get_student_projects(student_id: int):

    student = find_student(student_id)

    if student is None:
        return {
            "error": "Student not found."
        }

    return {
        "student_id": student_id,
        "projects": student.get("projects", [])
    }


# ============================================================
# MENTOR PROFILE
# ============================================================

@app.get("/api/mentor/profile")
def get_mentor_profile():

    return mentor_profile


# ============================================================
# MENTOR PENDING PROJECTS
# ============================================================

@app.get("/api/mentor/projects")
def get_mentor_projects():

    pending_projects = []

    for student in students_db:

        for project in student.get("projects", []):

            if project.get("status") == "Pending Approval":

                pending_projects.append(
                    {
                        "student_id": student["id"],
                        "student_name": student["name"],
                        "project": project,
                    }
                )

    return {
        "projects": pending_projects
    }


# ============================================================
# MENTOR APPROVAL
# ============================================================

@app.post("/api/mentor/approve/{project_id}")
def approve_project(project_id: int, mentor_name: str):

    for student in students_db:

        for project in student.get("projects", []):

            if project["id"] == project_id:

                project["status"] = "Verified"
                project["verified_by"] = mentor_name

                skill = project.get("skill")

                # Mentor approval creates verified skill.
                if skill and skill not in student["verified_skills"]:
                    student["verified_skills"].append(skill)

                if skill and skill not in student["skills"]:
                    student["skills"].append(skill)

                progress = calculate_progress(student)

                return {
                    "message": "Project verified and skill endorsed!",
                    "student_id": student["id"],
                    "verified_skill": skill,
                    "project": project,
                    "industry_readiness": progress,
                }

    return {
        "error": "Project not found."
    }


# ============================================================
# RECRUITER PROFILE
# ============================================================

@app.get("/api/recruiter/profile")
def get_recruiter_profile():

    return recruiter_profile


# ============================================================
# RECRUITER SEARCH
# ============================================================

@app.get("/api/recruiter/search")
def recruiter_search(skill: str):

    matching_students = []

    for student in students_db:

        verified_skills = student.get("verified_skills", [])

        # Only students with verified skills appear.
        if any(
            verified_skill.lower() == skill.lower()
            for verified_skill in verified_skills
        ):

            verified_projects = [
                project
                for project in student.get("projects", [])
                if project.get("status") == "Verified"
            ]

            matching_students.append(
                {
                    "student_id": student["id"],
                    "name": student["name"],
                    "email": student["email"],
                    "college": student["college"],
                    "verified_skills": student["verified_skills"],
                    "industry_readiness": calculate_progress(student),
                    "projects": verified_projects,
                }
            )

    return {
        "skill": skill,
        "students": matching_students,
        "count": len(matching_students),
    }