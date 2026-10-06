# Employee Management System (DevOps Project - Phase 1 & 2)

Flask + SQLite app with login, CRUD (UI + REST API), error handling,
a responsive UI, and a Jenkins CI pipeline (build, test, package).

## Run from source
    pip install -r requirements.txt
    python app.py            # http://127.0.0.1:5000   login: admin / admin123

## Run tests
    python -m pytest tests

## Build the executable
    Windows: build_exe.bat   -> dist\ems.exe
    Linux/Mac: ./build_exe.sh -> dist/ems

## REST API (login required, session cookie)
    GET/POST   /api/employees
    GET/PUT/DELETE /api/employees/<id>
    GET /health

## Phase 1 - Git
    git init
    git add . && git commit -m "Initial commit: employee management system"
    git branch -M main
    git remote add origin https://github.com/<you>/employee-management-system.git
    git push -u origin main
    git checkout -b feature/add-search      # create branch
    git checkout main && git merge feature/add-search   # merge

## Phase 2 - Jenkins
    New Item -> Pipeline -> "Pipeline script from SCM" -> Git -> repo URL
    Script Path: Jenkinsfile. Jenkins agent needs python3, python3-venv, pip.
