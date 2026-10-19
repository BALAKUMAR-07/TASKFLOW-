# TaskFlow — Python Full-Stack Task Management Web Application

TaskFlow is a production-grade, responsive task management web application built from scratch with Python, Django, MySQL 8, Bootstrap 5, and vanilla JavaScript. It helps individuals and teams organize, prioritize, track, and manage their daily workflow with persistent data storage and strict per-user security.

---

## 🌟 Key Features

### 🔐 1. User Authentication & Authorization
- **Registration & Login**: Secure account creation with email uniqueness validation and password hashing (PBKDF2 with SHA256).
- **Session Security**: Protected views using `@login_required` decorators and CSRF protection on all state-changing forms.
- **Strict Data Isolation**: Every task query is scoped to `request.user`. Users can never view, edit, or delete tasks belonging to other accounts (HTTP 403 Forbidden enforcement).

### 📋 2. Comprehensive Task Management (CRUD)
- **Create**: Add tasks with title, optional description, priority, status, and due dates.
- **Read**: View tasks in a clean list or view deep task details with formatting and metadata.
- **Update**: Edit existing task details with pre-filled forms and custom validation.
- **Delete**: Safe two-step deletion workflow with confirmation dialog (never deletes on `GET`).

### 📊 3. Interactive Real-Time Dashboard
- **Live Metric Cards**: Instantly view Total Tasks, Pending Tasks, To Do, In Progress, Completed, and Overdue Tasks calculated from live database records.
- **Visual Progress Bar**: Real-time completion percentage based on finished vs. total tasks.
- **Priority Watchlist**: Quick-access panel showing top high-priority incomplete tasks.
- **Recent Activity**: Last 5 created tasks for fast navigation.

### 🔍 4. Search, Filtering & Sorting
- **Keyword Search**: Filter tasks by title or description using Django ORM `Q` queries.
- **Status Filter**: Quickly inspect `TODO`, `IN_PROGRESS`, or `COMPLETED` tasks.
- **Priority Filter**: Focus on `LOW`, `MEDIUM`, or `HIGH` priority items.
- **Overdue Detection**: One-click checkbox filter to isolate overdue tasks (`due_date < today` and not completed).
- **Custom Sorting**: Sort dynamically by newest first, oldest first, due date (ascending/descending), priority, or title (A–Z).
- **Pagination**: Clean 10-task-per-page pagination preserving active search/filter parameters across page navigation.

### 🎨 5. Modern Responsive UI/UX
- **Mobile First**: Built with Bootstrap 5.3 and custom CSS design tokens.
- **Dynamic Feedback**: Auto-dismissing flash alert messages and live character counters.
- **Unsaved Changes Warning**: Client-side dirty-form detection warns users before navigating away from partially edited forms.
- **Empty States**: Engaging zero-state cards guiding users to create their first task.

---

## 🛠️ Technology Stack

| Layer | Technology | Details |
|---|---|---|
| **Backend Language** | Python 3.12 / 3.13 | High-performance, clean object-oriented Python |
| **Web Framework** | Django (5.x / 6.x LTS compatible) | MVT architecture, ORM, Auth, Messages, CSRF |
| **Database** | MySQL 8.x / MariaDB | Relational database with indexed foreign keys & statuses |
| **Database Connectors**| `mysqlclient` & `PyMySQL` | High-performance C connector with pure-Python fallback |
| **Frontend Styling** | Bootstrap 5.3 + Custom CSS | Responsive grid, cards, badges, and modals |
| **Frontend Scripting**| Vanilla JavaScript (ES6+) | No heavy frontend frameworks required |
| **Configuration** | `python-decouple` | Twelve-factor app security via `.env` files |

---

## 📁 Project Directory Structure

```text
TaskFlow-Task Management Application/
├── manage.py                     # Django management utility
├── requirements.txt              # Production and development dependencies
├── .env.example                  # Environment variable configuration template
├── .gitignore                    # Git rules ignoring credentials, venv, and cache
├── README.md                     # Comprehensive project documentation
├── taskflow/                     # Core project configuration package
│   ├── __init__.py
│   ├── asgi.py                   # ASGI config for async deployment
│   ├── wsgi.py                   # WSGI config for web servers
│   ├── urls.py                   # Root URL router
│   └── settings.py               # Application settings and database setup
├── tasks/                        # Main tasks application
│   ├── __init__.py
│   ├── admin.py                  # Django Admin customization
│   ├── apps.py                   # App configuration
│   ├── forms.py                  # TaskForm & CustomUserCreationForm
│   ├── models.py                 # Task model with status/priority choices & indexes
│   ├── urls.py                   # Application routes
│   ├── views.py                  # Functional views with authentication & queries
│   ├── tests.py                  # 39 automated unit & integration test cases
│   ├── migrations/               # Database migration files
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   └── templates/tasks/          # App-specific HTML templates
│       ├── dashboard.html
│       ├── task_list.html
│       ├── task_detail.html
│       ├── task_form.html
│       └── task_confirm_delete.html
├── templates/                    # Project-level templates
│   ├── base.html                 # Master layout with responsive navbar & messages
│   └── registration/             # Django authentication templates
│       ├── login.html
│       └── register.html
└── static/                       # Static assets
    ├── css/
    │   └── style.css             # Custom design tokens, badge styles & transitions
    └── js/
        └── main.js               # Client-side auto-dismiss alerts, dirty forms, etc.
```

---

## 🚀 Step-by-Step Installation & Setup Guide

### 1. Prerequisites
Ensure you have the following installed on your machine:
- **Python 3.10+** (verify with `python --version`)
- **MySQL Server 8.0+** (or MySQL via XAMPP / WampServer)
- **Git** (verify with `git --version`)

---

### 2. Clone or Extract the Project
Open PowerShell or Terminal and navigate to your project directory:
```bash
cd "TaskFlow-Task Management Application"
```

---

### 3. Create and Activate Virtual Environment

#### On Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If PowerShell displays an execution policy error, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

#### On Windows (Command Prompt `cmd`):
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

#### On macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 4. Install Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

### 5. Configure MySQL Database

#### Option A: Using MySQL Command Line or MySQL Workbench
1. Log into your MySQL console:
   ```sql
   mysql -u root -p
   ```
2. Create the database with UTF-8 character encoding:
   ```sql
   CREATE DATABASE taskflow_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   EXIT;
   ```

#### Option B: Using XAMPP / WAMP
1. Start the **Apache** and **MySQL** modules from the XAMPP Control Panel.
2. Open `http://localhost/phpmyadmin` in your browser.
3. Click **New** and name the database `taskflow_db` with collation `utf8mb4_unicode_ci`.

---

### 6. Set Up Environment Variables (`.env`)
Create a `.env` file in the root project folder (next to `manage.py`) by copying `.env.example`:

#### On Windows PowerShell:
```powershell
Copy-Item .env.example .env
```

#### On Linux / macOS:
```bash
cp .env.example .env
```

Edit `.env` to match your MySQL credentials:
```env
SECRET_KEY=django-insecure-taskflow-dev-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database Configuration
USE_SQLITE=False
DB_NAME=taskflow_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

> **Note**: If you want to run quick local tests without running a MySQL server, you can set `USE_SQLITE=True` in `.env`.

---

### 7. Run Database Migrations
Create the database tables and schema:
```bash
python manage.py migrate
```

---

### 8. Create a Superuser (Admin Account)
Create an administrative account to access the Django Admin portal:
```bash
python manage.py createsuperuser
```
Follow the prompts to enter a username, email, and password.

---

### 9. Start the Development Server
```bash
python manage.py runserver
```

Open your browser and navigate to:
- **Application**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Admin Panel**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🧪 Automated Testing

TaskFlow includes a comprehensive automated test suite with **39 test cases** covering:
- User registration, login, logout, and duplicate email prevention.
- Task CRUD lifecycle (creation, viewing, editing, deletion confirmation).
- Access control and strict per-user ownership checks (ensuring users cannot view or modify others' tasks).
- Model-level and form-level validation (preventing past due dates, requiring titles).
- Filter combinations (search keywords, status, priority, and overdue filtering).
- Dashboard statistical calculation accuracy.
- Overdue boundary conditions (tasks due today vs. past vs. no due date).

To run all automated tests:
```bash
python manage.py test tasks -v 2
```

All 39 tests should pass with `OK`.

---

## 🔒 Security Best Practices Implemented

1. **Environment Variables**: No sensitive passwords, database credentials, or secret keys are committed to Git.
2. **CSRF Protection**: All POST forms include `{% csrf_token %}` tokens.
3. **Password Security**: Uses Django's PBKDF2 password hasher with automatic salt generation.
4. **No GET Deletes**: Destructive actions (deletions) require an explicit POST request with confirmation.
5. **SQL Injection Defense**: All database interactions utilize Django ORM parameterized queries.
6. **XSS Protection**: Django template engine auto-escapes user-submitted HTML.

---

## ❓ Troubleshooting & Common Errors

| Issue | Cause | Solution |
|---|---|---|
| `OperationalError: (2002, "Can't connect to server on '127.0.0.1'")` | MySQL server is stopped or port 3306 is blocked | Start the MySQL service via Windows Services or XAMPP Control Panel. Alternatively, set `USE_SQLITE=True` in `.env` for offline development. |
| `Access denied for user 'root'@'localhost'` | Incorrect MySQL password in `.env` | Update `DB_PASSWORD` in `.env` with your actual MySQL root password. |
| `django.core.exceptions.DisallowedHost` | Accessing via non-whitelisted domain | Add your hostname to `ALLOWED_HOSTS` in `.env`. |
| `Cannot load mysqlclient` | Missing C++ compiler on Windows | `PyMySQL` is pre-configured as an automatic fallback in `settings.py`. Ensure `PyMySQL` is installed in your virtual environment. |

---

## 📦 How to Push to GitHub

1. Initialize git (if not already initialized):
   ```bash
   git init
   ```
2. Verify `.env` is ignored:
   ```bash
   git status
   ```
   *(Ensure `.env` does not appear in untracked files!)*
3. Add files and make your initial commit:
   ```bash
   git add .
   git commit -m "Initial commit: Complete TaskFlow full-stack task management application"
   ```
4. Link your GitHub repository and push:
   ```bash
   git branch -M main
   git remote add origin https://github.com/your-username/TaskFlow.git
   git push -u origin main
   ```

---

## 📜 License
This project is open-source and available under the MIT License.
