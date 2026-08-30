# ============================================================
# Co-Lab - Multi-Skill FastAPI Backend
# Supports: Python | Java | C++ | SQL
# ============================================================

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import sqlite3
from datetime import datetime


# ============================================================
# APP CONFIGURATION
# ============================================================

app = FastAPI(
    title="Co-Lab API",
    description="Verified Skills & Dynamic Project Matching Platform",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATABASE & SCHEMA
# ============================================================

DB_NAME = "colab.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 1. STUDENTS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            college TEXT NOT NULL,
            email TEXT
        )
    """)

    # 2. ASSESSMENTS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            skill TEXT,
            score INTEGER,
            total INTEGER,
            completed_at TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)

    # 3. PROJECTS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            skill TEXT,
            title TEXT,
            description TEXT,
            repo TEXT,
            status TEXT DEFAULT 'Pending',
            verified_by TEXT,
            submitted_at TEXT,
            verified_at TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)

    # 4. VERIFIED SKILLS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verified_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            skill TEXT,
            verified_at TEXT,
            mentor_name TEXT,
            UNIQUE(student_id, skill),
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)

    # 5. MODULE PROGRESS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS module_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            skill TEXT,
            module_number INTEGER,
            completed INTEGER DEFAULT 0,
            completed_at TEXT,
            UNIQUE(student_id, skill, module_number),
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)

    # 6. STRIKES
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS strikes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            skill TEXT,
            reason TEXT,
            mentor_name TEXT,
            created_at TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)

    # Default Student Seed
    cursor.execute("""
        INSERT OR IGNORE INTO students (id, name, college, email)
        VALUES (?, ?, ?, ?)
    """, (4, "Ananya Rao", "St. Claret College", "ananya@colab.demo"))

    # Initial SQL project if table is empty
    cursor.execute("SELECT COUNT(*) FROM projects")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO projects (id, student_id, skill, title, description, repo, status, submitted_at)
            VALUES (2, 4, 'SQL', 'SQL Student Database & Analytics System', 
                    'A relational database project using SQL to manage students, courses, marks and attendance with joins, aggregate queries, constraints and database design.', 
                    'https://github.com/ananyarao/sql-student-database-analytics', 'Pending', ?)
        """, (datetime.now().isoformat(),))

    conn.commit()
    conn.close()


init_db()


# ============================================================
# CONSTANTS & SKILL MAPPING
# ============================================================

SKILLS = ["Python", "Java", "C++", "SQL"]


def normalize_skill(skill: str) -> str:
    if not skill:
        return ""
    skill = skill.strip().lower()
    mapping = {
        "python": "Python",
        "java": "Java",
        "c++": "C++",
        "cpp": "C++",
        "sql": "SQL"
    }
    return mapping.get(skill, skill)


def validate_skill(skill: str):
    skill = normalize_skill(skill)
    if skill not in SKILLS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported skill. Choose one of: {', '.join(SKILLS)}"
        )
    return skill


def calculate_trust_status(strike_count: int) -> str:
    if strike_count == 0:
        return "Good Standing"
    elif 1 <= strike_count <= 2:
        return "Warning"
    else:
        return "Review Required"


# ============================================================
# QUESTION BANK
# ============================================================

QUESTIONS = {
    "Python": [
        {"id": 1, "question": "Which Python data structure stores key-value pairs?", "options": ["List", "Tuple", "Dictionary", "Set"], "answer": "Dictionary"},
        {"id": 2, "question": "Which keyword is used to define a function in Python?", "options": ["function", "def", "func", "define"], "answer": "def"},
        {"id": 3, "question": "What is the output of len([10, 20, 30])?", "options": ["2", "3", "4", "30"], "answer": "3"},
        {"id": 4, "question": "Which Python type is immutable?", "options": ["List", "Dictionary", "Set", "Tuple"], "answer": "Tuple"},
        {"id": 5, "question": "Which keyword is used to handle exceptions in Python?", "options": ["catch", "try", "error", "exceptonly"], "answer": "try"}
    ],
    "Java": [
        {"id": 1, "question": "Which keyword is used to create a class in Java?", "options": ["class", "struct", "define", "object"], "answer": "class"},
        {"id": 2, "question": "Which method is the entry point of a Java application?", "options": ["start()", "run()", "main()", "execute()"], "answer": "main()"},
        {"id": 3, "question": "Which concept allows one class to acquire properties of another class?", "options": ["Encapsulation", "Inheritance", "Abstraction", "Compilation"], "answer": "Inheritance"},
        {"id": 4, "question": "Which keyword prevents a Java variable from being reassigned?", "options": ["static", "constant", "final", "fixed"], "answer": "final"},
        {"id": 5, "question": "Which collection does not allow duplicate elements?", "options": ["List", "Set", "ArrayList", "Vector"], "answer": "Set"}
    ],
    "C++": [
        {"id": 1, "question": "Which symbol is used to declare a pointer in C++?", "options": ["&", "*", "#", "%"], "answer": "*"},
        {"id": 2, "question": "Which feature allows the same function name with different parameters?", "options": ["Inheritance", "Overloading", "Encapsulation", "Compilation"], "answer": "Overloading"},
        {"id": 3, "question": "Which header is commonly used for input and output with cin and cout?", "options": ["stdio.h", "iostream", "string.h", "stdlib.h"], "answer": "iostream"},
        {"id": 4, "question": "Which keyword is used to allocate memory dynamically in C++?", "options": ["malloc", "alloc", "new", "create"], "answer": "new"},
        {"id": 5, "question": "Which OOP concept hides internal implementation details?", "options": ["Inheritance", "Polymorphism", "Abstraction", "Iteration"], "answer": "Abstraction"}
    ],
    "SQL": [
        {"id": 1, "question": "Which SQL command is used to retrieve data from a table?", "options": ["GET", "SELECT", "FETCH", "READ"], "answer": "SELECT"},
        {"id": 2, "question": "Which SQL clause is used to filter rows?", "options": ["ORDER BY", "GROUP BY", "WHERE", "HAVING"], "answer": "WHERE"},
        {"id": 3, "question": "Which key uniquely identifies a row in a relational table?", "options": ["Foreign Key", "Primary Key", "Candidate Group", "Index Key"], "answer": "Primary Key"},
        {"id": 4, "question": "Which SQL operation combines rows from related tables?", "options": ["MERGE", "CONNECT", "JOIN", "UNION ONLY"], "answer": "JOIN"},
        {"id": 5, "question": "Which clause is used to sort query results?", "options": ["SORT BY", "ORDER BY", "ARRANGE BY", "GROUP BY"], "answer": "ORDER BY"}
    ]
}


# ============================================================
# PROJECT TEMPLATES & MENTORS
# ============================================================

PROJECT_TEMPLATES = {
    "Python": {
        "title": "Python Student Management System",
        "description": "A Python application for managing student records using CRUD operations, file handling and Python data structures.",
        "modules": ["Python Data Structures", "File Handling", "Functions & Exception Handling", "CRUD Operations"]
    },
    "Java": {
        "title": "Java Banking Management System",
        "description": "A Java application for managing customer accounts, transactions and banking operations using OOP principles.",
        "modules": ["Java OOP Fundamentals", "Collections & Exception Handling", "Inheritance & Polymorphism", "Build a Java Project"]
    },
    "C++": {
        "title": "C++ Library Management System",
        "description": "A C++ application for managing books, members and lending operations using object-oriented programming and file handling.",
        "modules": ["C++ OOP Fundamentals", "Pointers & Memory", "STL & Data Structures", "Build a C++ Project"]
    },
    "SQL": {
        "title": "SQL Employee Database Management System",
        "description": "A relational database project for managing employees, departments, salaries and transactions using SQL queries, joins, constraints and aggregation.",
        "modules": ["SQL Queries & Filtering", "Joins & Relationships", "Aggregation & Subqueries", "Build a SQL Database Project"]
    }
}

MENTORS = [
    {"id": 1, "name": "Dr. Alan Thomas", "skills": ["Python", "Java"], "role": "Senior Software Engineering Mentor"},
    {"id": 2, "name": "Prof. Meera Nair", "skills": ["SQL"], "role": "Database & SQL Mentor"},
    {"id": 3, "name": "Dr. Rahul Menon", "skills": ["C++"], "role": "Systems & C++ Mentor"}
]


# ============================================================
# REQUEST SCHEMAS
# ============================================================

class AssessmentSubmission(BaseModel):
    student_id: int
    skill: str
    answers: Dict[str, str]

class ProjectSubmission(BaseModel):
    student_id: int
    skill: str
    title: str
    description: str
    github_url: str

class StrikeSubmission(BaseModel):
    student_id: int
    mentor_name: Optional[str] = "Dr. Alan Thomas"
    skill: Optional[str] = "General"
    reason: str


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def get_student(student_id: int):
    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    conn.close()
    return student

def get_verified_skills(student_id: int):
    conn = get_db()
    rows = conn.execute("SELECT skill FROM verified_skills WHERE student_id = ?", (student_id,)).fetchall()
    conn.close()
    return [row["skill"] for row in rows]

def get_strike_count(student_id: int):
    conn = get_db()
    row = conn.execute("SELECT COUNT(*) AS count FROM strikes WHERE student_id = ?", (student_id,)).fetchone()
    conn.close()
    return row["count"]

def add_strike(student_id: int, skill: str, reason: str, mentor_name: str = "System"):
    conn = get_db()
    conn.execute("""
        INSERT INTO strikes (student_id, skill, reason, mentor_name, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (student_id, skill, reason, mentor_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()


# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/")
def root():
    return {"platform": "Co-Lab", "message": "Verified Skills API", "version": "2.0", "supported_skills": SKILLS}

@app.get("/health")
def health():
    return {"status": "healthy", "supported_skills": SKILLS}

@app.get("/api/skills")
def get_skills():
    return {"skills": SKILLS}

@app.get("/api/skill/{skill}/template")
def get_skill_template(skill: str):
    skill = validate_skill(skill)
    template = PROJECT_TEMPLATES[skill]
    return {"skill": skill, "title": template["title"], "description": template["description"], "modules": template["modules"]}

@app.get("/api/assessment/questions")
def get_assessment_questions(skill: str = "Python"):
    skill = validate_skill(skill)
    questions = QUESTIONS[skill]
    safe_questions = [{"id": q["id"], "question": q["question"], "options": q["options"]} for q in questions]
    return {"skill": skill, "total": len(safe_questions), "questions": safe_questions}

@app.post("/api/assessment/submit")
def submit_assessment(payload: AssessmentSubmission):
    skill = validate_skill(payload.skill)
    student = get_student(payload.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    questions = QUESTIONS[skill]
    score = sum(1 for q in questions if payload.answers.get(str(q["id"])) == q["answer"])
    total = len(questions)
    percentage = round((score / total) * 100)
    skill_gap = score < 4

    if score == total:
        result, message = "Excellent", f"Outstanding {skill} performance."
    elif score >= 4:
        result, message = "Strong", f"Good {skill} foundation."
    elif score >= 3:
        result, message = "Needs Improvement", f"Some {skill} fundamentals need improvement."
    else:
        result, message = "Skill Gap Detected", f"Significant {skill} skill gap detected."

    conn = get_db()
    conn.execute("""
        INSERT INTO assessments (student_id, skill, score, total, completed_at)
        VALUES (?, ?, ?, ?, ?)
    """, (payload.student_id, skill, score, total, datetime.now().isoformat()))
    conn.commit()
    conn.close()

    if percentage < 40:
        if get_strike_count(payload.student_id) < 3:
            add_strike(payload.student_id, skill, "Assessment score below 40%", "Academic Assessment System")

    return {
        "success": True,
        "student_id": payload.student_id,
        "skill": skill,
        "score": score,
        "total": total,
        "percentage": percentage,
        "skill_gap": skill_gap,
        "result": result,
        "message": message,
        "strikes": get_strike_count(payload.student_id)
    }

@app.post("/api/student/project")
def submit_project(payload: ProjectSubmission):
    skill = validate_skill(payload.skill)
    student = get_student(payload.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if not payload.title.strip() or not payload.description.strip() or not payload.github_url.strip():
        raise HTTPException(status_code=400, detail="All project fields are required.")

    now = datetime.now().isoformat()
    conn = get_db()
    cursor = conn.execute("""
        INSERT INTO projects (student_id, skill, title, description, repo, status, submitted_at)
        VALUES (?, ?, ?, ?, ?, 'Pending', ?)
    """, (payload.student_id, skill, payload.title.strip(), payload.description.strip(), payload.github_url.strip(), now))
    project_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": f"{skill} project submitted successfully.",
        "project": {
            "id": project_id, "student_id": payload.student_id, "skill": skill,
            "title": payload.title.strip(), "description": payload.description.strip(),
            "repo": payload.github_url.strip(), "status": "Pending", "submitted_at": now
        }
    }

@app.get("/api/mentors")
def get_mentors():
    return {"mentors": MENTORS}

@app.get("/api/mentor/qualification")
def mentor_qualification(skill: str, mentor_name: str = "Dr. Alan Thomas"):
    skill = validate_skill(skill)
    mentor = next((m for m in MENTORS if m["name"].lower() == mentor_name.lower()), None)
    if not mentor:
        return {"mentor": mentor_name, "skill": skill, "qualified": False, "message": "Mentor not found."}

    qualified = skill in mentor["skills"]
    message = f"{mentor['name']} is qualified to verify {skill}." if qualified else f"{mentor['name']} is not qualified to verify {skill}."
    return {"mentor": mentor["name"], "mentor_role": mentor["role"], "skill": skill, "qualified": qualified, "message": message}

@app.get("/api/mentor/projects")
def mentor_projects():
    conn = get_db()
    rows = conn.execute("""
        SELECT p.*, s.name AS student_name, s.college AS college
        FROM projects p
        JOIN students s ON p.student_id = s.id
        ORDER BY p.id DESC
    """).fetchall()
    conn.close()
    return {"projects": [dict(r) for r in rows]}

@app.post("/api/mentor/approve/{project_id}")
def approve_project(project_id: int, mentor_name: str = "Dr. Alan Thomas"):
    conn = get_db()
    project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    conn.close()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    skill = project["skill"]
    mentor = next((m for m in MENTORS if m["name"].lower() == mentor_name.lower()), None)
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")

    if skill not in mentor["skills"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{mentor['name']} is not qualified to verify {skill} projects.")

    now = datetime.now().isoformat()
    conn = get_db()
    conn.execute("UPDATE projects SET status = 'Verified', verified_by = ?, verified_at = ? WHERE id = ?", (mentor["name"], now, project_id))
    conn.execute("INSERT OR IGNORE INTO verified_skills (student_id, skill, verified_at, mentor_name) VALUES (?, ?, ?, ?)", (project["student_id"], skill, now, mentor["name"]))
    conn.commit()
    conn.close()

    return {
        "success": True, "verified": True, "qualified": True,
        "project_id": project_id, "student_id": project["student_id"], "skill": skill,
        "mentor": mentor["name"], "project": {"id": project_id, "status": "Verified", "skill": skill, "verified_by": mentor["name"], "verified_at": now}
    }

@app.get("/api/student/modules")
def get_modules(student_id: int, skill: str):
    skill = validate_skill(skill)
    template = PROJECT_TEMPLATES[skill]
    conn = get_db()
    completed_rows = conn.execute("SELECT module_number FROM module_progress WHERE student_id = ? AND skill = ? AND completed = 1", (student_id, skill)).fetchall()
    conn.close()

    completed_numbers = {row["module_number"] for row in completed_rows}
    modules = [{"module_number": i, "title": name, "completed": i in completed_numbers} for i, name in enumerate(template["modules"], start=1)]
    completed_count = len(completed_numbers)

    return {
        "student_id": student_id, "skill": skill, "modules": modules,
        "completed": completed_count, "total": len(modules),
        "percentage": round((completed_count / len(modules)) * 100) if modules else 0
    }

@app.post("/api/student/module/{module_number}/complete")
def complete_module(module_number: int, student_id: int, skill: str):
    skill = validate_skill(skill)
    template = PROJECT_TEMPLATES[skill]
    if module_number < 1 or module_number > len(template["modules"]):
        raise HTTPException(status_code=400, detail="Invalid module number")

    if module_number > 1:
        conn = get_db()
        prev = conn.execute("SELECT completed FROM module_progress WHERE student_id = ? AND skill = ? AND module_number = ?", (student_id, skill, module_number - 1)).fetchone()
        conn.close()
        if not prev or prev["completed"] != 1:
            raise HTTPException(status_code=400, detail=f"Complete Module {module_number - 1} first.")

    now = datetime.now().isoformat()
    conn = get_db()
    conn.execute("""
        INSERT INTO module_progress (student_id, skill, module_number, completed, completed_at)
        VALUES (?, ?, ?, 1, ?)
        ON CONFLICT(student_id, skill, module_number) DO UPDATE SET completed = 1, completed_at = excluded.completed_at
    """, (student_id, skill, module_number, now))
    conn.commit()
    conn.close()
    return {"success": True, "student_id": student_id, "skill": skill, "module_number": module_number}

@app.get("/api/students/portfolio")
def get_portfolio():
    conn = get_db()
    students = conn.execute("SELECT * FROM students").fetchall()
    result = []
    for s in students:
        s_id = s["id"]
        projects = [dict(p) for p in conn.execute("SELECT * FROM projects WHERE student_id = ? ORDER BY id ASC", (s_id,)).fetchall()]
        verified_skills = [row["skill"] for row in conn.execute("SELECT skill FROM verified_skills WHERE student_id = ?", (s_id,)).fetchall()]
        assessments = [dict(a) for a in conn.execute("SELECT * FROM assessments WHERE student_id = ? ORDER BY id DESC", (s_id,)).fetchall()]
        strikes = [dict(st) for st in conn.execute("SELECT * FROM strikes WHERE student_id = ? ORDER BY id DESC", (s_id,)).fetchall()]
        result.append({
            "id": s_id, "name": s["name"], "college": s["college"], "email": s["email"],
            "verified_skills": verified_skills, "projects": projects, "assessments": assessments,
            "strikes": strikes, "strike_count": len(strikes)
        })
    conn.close()
    return {"students": result}

@app.get("/api/recruiter/search")
def recruiter_search(skill: str):
    skill = validate_skill(skill)
    conn = get_db()
    rows = conn.execute("""
        SELECT DISTINCT s.id, s.name, s.college, s.email
        FROM students s
        JOIN verified_skills vs ON s.id = vs.student_id
        WHERE LOWER(vs.skill) = LOWER(?)
    """, (skill,)).fetchall()

    candidates = []
    for s in rows:
        s_id = s["id"]
        verified_skills = [r["skill"] for r in conn.execute("SELECT skill FROM verified_skills WHERE student_id = ?", (s_id,)).fetchall()]
        projects = [dict(p) for p in conn.execute("SELECT * FROM projects WHERE student_id = ? AND LOWER(skill) = LOWER(?) AND status = 'Verified' ORDER BY id DESC", (s_id, skill)).fetchall()]
        assessment = conn.execute("SELECT * FROM assessments WHERE student_id = ? AND LOWER(skill) = LOWER(?) ORDER BY id DESC LIMIT 1", (s_id, skill)).fetchone()
        candidates.append({
            "id": s_id, "name": s["name"], "college": s["college"], "email": s["email"],
            "verified_skills": verified_skills, "assessment": dict(assessment) if assessment else None,
            "projects": projects,
            "proof": {"assessment_completed": assessment is not None, "project_verified": len(projects) > 0, "faculty_endorsed": len(projects) > 0}
        })
    conn.close()
    return {"skill": skill, "count": len(candidates), "students": candidates}

@app.get("/api/student/readiness")
def student_readiness(student_id: int, skill: str):
    skill = validate_skill(skill)
    conn = get_db()
    assessment = conn.execute("SELECT * FROM assessments WHERE student_id = ? AND LOWER(skill) = LOWER(?) ORDER BY id DESC LIMIT 1", (student_id, skill)).fetchone()
    mod_count = conn.execute("SELECT COUNT(*) AS c FROM module_progress WHERE student_id = ? AND LOWER(skill) = LOWER(?) AND completed = 1", (student_id, skill)).fetchone()["c"]
    total_mods = len(PROJECT_TEMPLATES[skill]["modules"])
    project = conn.execute("SELECT * FROM projects WHERE student_id = ? AND LOWER(skill) = LOWER(?) ORDER BY id DESC LIMIT 1", (student_id, skill)).fetchone()
    verified = conn.execute("SELECT * FROM verified_skills WHERE student_id = ? AND LOWER(skill) = LOWER(?)", (student_id, skill)).fetchone()
    conn.close()

    readiness = 0
    if assessment: readiness += 25
    if total_mods > 0: readiness += (mod_count / total_mods * 25)
    if project: readiness += 25
    if verified: readiness += 25
    readiness = min(100, round(readiness))

    return {
        "student_id": student_id, "skill": skill, "readiness": readiness,
        "assessment_completed": assessment is not None, "learning_completed": mod_count == total_mods,
        "project_submitted": project is not None, "project_verified": verified is not None,
        "verified_skill": verified is not None, "status": "Industry Ready" if readiness == 100 else "In Progress"
    }

@app.get("/api/student/strikes")
def get_strikes(student_id: int):
    conn = get_db()
    strikes = [dict(r) for r in conn.execute("SELECT * FROM strikes WHERE student_id = ? ORDER BY id DESC", (student_id,)).fetchall()]
    conn.close()
    return {"student_id": student_id, "strike_count": len(strikes), "max_strikes": 3, "status": calculate_trust_status(len(strikes)), "strikes": strikes}

@app.post("/api/mentor/strike")
def issue_mentor_strike(payload: StrikeSubmission):
    current = get_strike_count(payload.student_id)
    if current >= 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student already has 3 strikes. Review Required.")
    add_strike(payload.student_id, payload.skill or "General", payload.reason.strip(), payload.mentor_name or "Dr. Alan Thomas")
    new_count = current + 1
    return {"success": True, "student_id": payload.student_id, "strike_count": new_count, "trust_status": calculate_trust_status(new_count)}

@app.get("/api/student/{student_id}")
def student_profile(student_id: int):
    student = get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    strikes = get_strike_count(student_id)
    return {
        "id": student["id"], "name": student["name"], "college": student["college"],
        "email": student["email"], "verified_skills": get_verified_skills(student_id),
        "strike_count": strikes, "trust_status": calculate_trust_status(strikes)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)