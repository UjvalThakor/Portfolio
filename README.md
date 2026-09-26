# Ujval Thakor — Backend Developer Portfolio

A creative, editorial developer portfolio built with **Django**, inspired by the visual language, minimalism, typography, spacing, and interactive feel of [douglus.site](https://douglus.site/).

Tailored specifically for a **Backend Engineer** specializing in **Python, Django, Django REST Framework, REST APIs, Databases (PostgreSQL/MySQL/Redis), and AI/Computer Vision integrations**.

---

## Key Highlights & Features

- **Built with Real Django Backend**: Not a static HTML template. Every project, technology, experience record, resume, and contact submission is powered dynamically by Django models and ORM.
- **Douglus-Inspired Creative Experience**:
  - Atmospheric dark palette (`#070709`) with an electric terminal mint accent (`#0df293`).
  - Staggered entrance preloader (`INITIALIZE` -> `ENGINEER` -> `UJVAL.`).
  - Editorial, oversized typography paired with monospace metadata tags.
  - Custom cursor with lag-free follower ring and contextual hover states (`VIEW`).
- **Signature Backend Visuals**:
  - **Live Runtime Telemetry**: Real-time server status supervisor showing API gateway, database latency, and simulated curl requests.
  - **"Behind the Request"**: Interactive 7-stage API request lifecycle visualizer (Client -> Router -> View -> Serializer -> QuerySet -> Database -> 200 OK Response) with code snippets and latency inspection.
  - **Interactive Developer Terminal (`ujval@dev:~$`)**: Real CLI supporting `help`, `about`, `projects`, `stack`, `status`, `neofetch`, and `clear`.
- **6 Authentic Project Case Studies**:
  1. `BeautyCare AI` (AI & REST APIs, Django, DRF, Swagger, Token Auth)
  2. `Student Management System` (Django + MySQL, Role-based Permissions, Relational Integrity)
  3. `Job Portal` (Django, Multi-facet Filtering, Dual Roles, PostgreSQL)
  4. `Cosmic Insight` (Dynamic Data Calculations, Django, Python)
  5. `Car Number Detection` (Python, OpenCV, Morphological Pipeline)
  6. `Fabric Fault Detection` (OpenCV, Real-Time Video Inspection, Multithreaded)
- **Real Django Contact Form**: HTMX-powered asynchronous submission, server-side validation, honeypot spam protection, and database persistence.
- **Django Admin**: Full control to update projects, technologies, experience, resume file, and review contact messages.

---

## Tech Stack

- **Backend**: Python 3.12, Django 6.1.1, Django REST Framework
- **Database**: SQLite (local development) / PostgreSQL (production-ready)
- **Caching**: Redis
- **Frontend**: Django Templates, Vanilla CSS (Variables, Grid, Flexbox), Vanilla JavaScript (no bloat)
- **Micro-Interactions**: HTMX (AJAX forms & updates)
- **Deployment**: Gunicorn, Nginx, Docker & Docker Compose, WhiteNoise

---

## Quick Start (Local Development)

### 1. Prerequisites
- Python 3.12+
- Git

### 2. Setup & Installation
```bash
# Clone the repository
git clone https://github.com/ujvalthakor/portfolio.git
cd portfolio

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Seed authentic portfolio data (projects, tech, experience, profile)
python manage.py seed_portfolio

# Start development server
python manage.py runserver
```

Open your browser and visit:
- **Website**: `http://localhost:8000/`
- **Django Admin**: `http://localhost:8000/admin/`

---

## Default Admin Credentials

- **Username**: `admin`
- **Password**: `adminpassword123`

---

## Production Deployment (Docker)

```bash
# Build and run web, postgres, and redis services
docker-compose up --build -d

# Run migrations and seed data in container
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py seed_portfolio
```

---

## Contact & Credits

- **Developer**: Ujval Thakor
- **Location**: Surat, Gujarat, India
- **Email**: `ujvalthakor14@gmail.com`
- **Phone**: `+91 9104502128`
- **GitHub**: [github.com/ujvalthakor](https://github.com/ujvalthakor)
- **LinkedIn**: [linkedin.com/in/ujvalthakor](https://linkedin.com/in/ujvalthakor)
