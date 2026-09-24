from django.core.management.base import BaseCommand
from core.models import ProfileConfig, Experience, Skill, Resume
from projects.models import Technology, Project, ProjectImage

class Command(BaseCommand):
    help = 'Seeds authentic portfolio data for Ujval Thakor - Backend Developer'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Seeding portfolio data...'))

        # 1. Profile Config
        profile, created = ProfileConfig.objects.get_or_create(
            id=1,
            defaults={
                'full_name': 'Ujval Thakor',
                'primary_title': 'Backend Developer',
                'secondary_title': 'Python • Django • REST APIs • AI/ML',
                'short_positioning': 'I build reliable backend systems, APIs, automation tools, and AI-powered applications.',
                'current_status': 'B.Tech Computer Engineering student with hands-on Python and Django development experience.',
                'location': 'Surat, Gujarat, India',
                'available_for_work': True,
                'github_url': 'https://github.com/ujvalthakor',
                'linkedin_url': 'https://linkedin.com/in/ujvalthakor',
                'email': 'ujvalthakor.dev@gmail.com',
                'hero_statement_line1': 'BACKEND',
                'hero_statement_line2': 'ENGINEER',
                'hero_statement_line3': 'who builds',
                'hero_statement_line4': 'systems that',
                'hero_statement_line5': 'actually work.',
                'about_editorial_heading': 'I BUILD THE\nSYSTEM BEHIND\nTHE EXPERIENCE.',
                'about_editorial_text': (
                    "I’m a B.Tech Computer Engineering student and backend developer focused on Python and Django. "
                    "I enjoy turning ideas into structured backend systems — from REST APIs and database architecture "
                    "to authentication, automation and AI-powered applications."
                )
            }
        )
        self.stdout.write(self.style.SUCCESS('[OK] Profile configuration seeded.'))

        # 2. Technologies
        tech_data = [
            # BACKEND
            ('Python', 'BACKEND', 'python', 'Primary language for high-performance servers, logic & pipelines', 1),
            ('Django', 'BACKEND', 'django', 'Robust web framework for rapid, secure, and maintainable backend architecture', 2),
            ('Django REST Framework', 'BACKEND', 'drf', 'Scalable RESTful API development, serialization, and auth', 3),
            ('REST APIs', 'BACKEND', 'api', 'Clean API contracts, HTTP methods, status codes, and JSON serialization', 4),
            
            # DATABASE
            ('PostgreSQL', 'DATABASE', 'database', 'ACID-compliant relational database with advanced indexing and JSONB', 5),
            ('MySQL', 'DATABASE', 'mysql', 'Relational database management, schema normalization, and relational keys', 6),
            ('Redis', 'DATABASE', 'redis', 'In-memory key-value store for session caching and high-speed data caching', 7),
            
            # TOOLS & ENVIRONMENT
            ('Git', 'TOOLS', 'git', 'Distributed version control and branching workflows', 8),
            ('GitHub', 'TOOLS', 'github', 'Collaborative development, code reviews, and project management', 9),
            ('Linux', 'TOOLS', 'terminal', 'Command line server administration, bash scripting, and environment config', 10),
            ('Postman', 'TOOLS', 'postman', 'API endpoint testing, payload inspection, and mock environment testing', 11),
            ('Swagger / OpenAPI', 'TOOLS', 'swagger', 'Interactive API documentation, request schema and response specs', 12),
            
            # AI / COMPUTER VISION
            ('OpenCV', 'AI_CV', 'opencv', 'Real-time computer vision, contour detection, morphological filtering', 13),
            ('Machine Learning', 'AI_CV', 'cpu', 'Data preprocessing, model inference, and feature extraction', 14),
            ('AI APIs', 'AI_CV', 'sparkles', 'Integration with large multimodal and vision models via secure REST endpoints', 15),
            
            # DEVOPS / DEPLOYMENT
            ('Docker', 'DEVOPS', 'container', 'Containerization of backend apps for reproducible dev and prod environments', 16),
            ('Gunicorn', 'DEVOPS', 'server', 'Production WSGI HTTP server for concurrent Python process handling', 17),
            ('Nginx', 'DEVOPS', 'network', 'High-performance reverse proxy, SSL termination, and static asset delivery', 18),
        ]

        tech_map = {}
        for name, cat, icon, desc, order in tech_data:
            tech_obj, _ = Technology.objects.update_or_create(
                name=name,
                defaults={
                    'category': cat,
                    'icon': icon,
                    'description': desc,
                    'order': order,
                    'is_featured': True
                }
            )
            tech_map[name] = tech_obj
        self.stdout.write(self.style.SUCCESS(f'[OK] {len(tech_map)} Technologies seeded.'))

        # 3. Projects
        projects_data = [
            {
                'title': 'BeautyCare AI',
                'slug': 'beautycare-ai',
                'project_number': '01',
                'category': 'AI & REST APIs',
                'year': '2026',
                'short_description': 'Django-based AI-powered application orchestrating skin analysis and personalized care routines via REST APIs and Swagger documentation.',
                'description': (
                    "BeautyCare AI is an intelligent backend system engineered to deliver tailored skincare diagnostics "
                    "by marrying modern computer vision & generative AI models with a resilient Django REST API architecture. "
                    "The backend manages client requests, orchestrates external AI endpoints, enforces rigorous JWT authentication, "
                    "and catalogs skin assessment histories in a normalized database."
                ),
                'architecture_description': (
                    "The application employs a decoupled service architecture. Inbound client requests hit Nginx and Gunicorn "
                    "before reaching Django's URL dispatcher. Django REST Framework serializers enforce strict payload schemas, "
                    "validate client input, and hand off requests to dedicated service handlers. An asynchronous adapter layer "
                    "interfaces with AI vision APIs, while query results are cached in Redis to minimize repetitive inference latencies."
                ),
                'architecture_flow': "Client (Web/Mobile) -> Django URL Router -> DRF API View (Token Auth) -> Business Logic Service -> External AI API Pipeline -> PostgreSQL & Redis Cache -> JSON Response (200 OK)",
                'challenge': (
                    "External AI inference endpoints introduced latency spikes (1.5s - 3s) during peak analysis requests, "
                    "threatening to block Django's WSGI worker threads and degrade user experience."
                ),
                'solution': (
                    "Structured a non-blocking service abstraction that caches previous diagnostic signatures using MD5 image "
                    "hashes in Redis, allowing instant cache hits for duplicate queries. Implemented timeout-resilient retry logic "
                    "and optimized DRF serializers to stream cleanly formatted response payloads."
                ),
                'learning': (
                    "Gained deep experience in API contract engineering, handling unpredictable third-party API latency, "
                    "implementing Swagger/OpenAPI documentation for client teams, and secure token-based authentication."
                ),
                'key_features': (
                    "Token-based REST API authentication & user profile management\n"
                    "Interactive Swagger / OpenAPI documentation for all endpoints\n"
                    "AI image ingestion pipeline with preprocessing and boundary validation\n"
                    "Personalized recommendation logic mapping AI insights to structured product data\n"
                    "Rate limiting and payload sanity checks to prevent API abuse"
                ),
                'tech_names': ['Python', 'Django', 'Django REST Framework', 'REST APIs', 'AI APIs', 'Swagger / OpenAPI', 'PostgreSQL', 'Redis'],
                'order': 1,
                'featured': True,
                'github_url': 'https://github.com/ujvalthakor/beautycare-ai',
                'live_url': '',
            },
            {
                'title': 'Student Management System',
                'slug': 'student-management-system',
                'project_number': '02',
                'category': 'Database & Management Platform',
                'year': '2025',
                'short_description': 'Enterprise-grade Django & MySQL platform managing student lifecycles, academic courses, grades, and role-based permissions.',
                'description': (
                    "A robust institutional management platform designed to eliminate paper trails and scattered spreadsheets. "
                    "Built with Django and MySQL, it provides secure role-separated portals for administrators, instructors, "
                    "and students with automated GPA calculation, course enrollment constraints, and attendance tracking."
                ),
                'architecture_description': (
                    "Architected with relational integrity at its center. The MySQL schema employs foreign keys, unique composite indexes, "
                    "and cascading constraints to guarantee transactional consistency across enrollments, semesters, and grading sheets. "
                    "Django's built-in authentication is extended with custom user models and permission groups."
                ),
                'architecture_flow': "Client Browser -> Django Session Middleware -> Role Permission Gatekeeper -> Django View & Forms -> ORM QuerySet (select_related / prefetch_related) -> MySQL Engine -> Rendered Template",
                'challenge': (
                    "Generating comprehensive semester grade reports across thousands of student course enrollments triggered "
                    "the notorious N+1 query problem, causing database CPU spikes and slow page load times."
                ),
                'solution': (
                    "Refactored ORM queries utilizing `select_related('student', 'department')` for single-valued relationships "
                    "and `prefetch_related('enrollments__course')` for multi-valued sets, cutting SQL queries from 180+ down to 4 queries per report page."
                ),
                'learning': (
                    "Mastered Django ORM query optimization, relational database schema normalization, database transactions, "
                    "and crafting maintainable role-based access control (RBAC)."
                ),
                'key_features': (
                    "Granular role-based access control (Admin, Faculty, Student)\n"
                    "Automated academic GPA computation and transcript generation\n"
                    "Course catalog with prerequisites and capacity enforcement\n"
                    "Normalized MySQL relational schema with composite constraints\n"
                    "Customized Django Admin dashboard for faculty oversight"
                ),
                'tech_names': ['Python', 'Django', 'MySQL', 'Git', 'GitHub'],
                'order': 2,
                'featured': True,
                'github_url': 'https://github.com/ujvalthakor/student-management-system',
                'live_url': '',
            },
            {
                'title': 'Job Portal',
                'slug': 'job-portal',
                'project_number': '03',
                'category': 'Backend Application',
                'year': '2025',
                'short_description': 'Full-featured recruitment backend platform featuring multi-criteria search, candidate application tracking, and company postings.',
                'description': (
                    "A scalable hiring platform supporting dual user journeys: job seekers creating engineering profiles and submitting "
                    "resumes, and hiring managers posting positions and reviewing incoming candidates with status progression."
                ),
                'architecture_description': (
                    "Django application structured into decoupled apps: `accounts`, `jobs`, and `applications`. Employs database-level "
                    "indexes on search vectors (title, location, tech tags) and Q objects for complex multi-parameter filtering without external search engine overhead."
                ),
                'architecture_flow': "Client -> HTTP Search Request -> Search & Filter Service -> Django ORM with Q Objects -> PostgreSQL Indexed Search -> Structured Results / Paginated Cards",
                'challenge': (
                    "Multi-parameter search queries (salary brackets, keywords, location radius, and experience) led to slow queries "
                    "and complex query string parsing bugs."
                ),
                'solution': (
                    "Created a dedicated `JobFilterService` encapsulating dynamic `Q()` expression composition, coupled with composite database "
                    "indexes on `(is_active, created_at, category)`."
                ),
                'learning': (
                    "Learned advanced Django ORM filtering patterns, file upload security (validating PDF resume mime types), and clean session handling."
                ),
                'key_features': (
                    "Dual-role authentication (Recruiters vs Job Applicants)\n"
                    "Dynamic multi-facet job search and query filtering\n"
                    "Resume upload handling with validation and secure storage\n"
                    "Application status lifecycle tracking (Applied, Reviewed, Shortlisted)\n"
                    "Company profile management and public vacancy pages"
                ),
                'tech_names': ['Python', 'Django', 'PostgreSQL', 'Git', 'Linux'],
                'order': 3,
                'featured': True,
                'github_url': 'https://github.com/ujvalthakor/job-portal',
                'live_url': '',
            },
            {
                'title': 'Cosmic Insight',
                'slug': 'cosmic-insight',
                'project_number': '04',
                'category': 'Dynamic Data & Workflows',
                'year': '2025',
                'short_description': 'Astrological data processing web application delivering dynamic birth-chart calculations and algorithmic chart interpretation.',
                'description': (
                    "Cosmic Insight is an engineering-driven web application transforming complex astronomical and astrological calculations "
                    "into clear, structured visual insights. It computes planetary coordinates, houses, and aspects from raw birth coordinates and timestamps."
                ),
                'architecture_description': (
                    "The backend leverages Python numerical algorithms to compute celestial coordinates based on UTC offsets and latitude/longitude, "
                    "storing precomputed ephemeris data in SQLite/PostgreSQL to minimize on-the-fly computational overhead."
                ),
                'architecture_flow': "User Birth Coordinates & Time -> Mathematical Calculation Service -> Ephemeris Lookup -> Chart Interpretation Engine -> Database Cache -> Dynamic Visual Output",
                'challenge': (
                    "Accurately translating timezone offsets, daylight savings changes, and geographic coordinate math into reliable planetary house angles."
                ),
                'solution': (
                    "Standardized all calculation pipelines to UTC epoch timestamps, integrating robust timezone resolution libraries and caching repeated coordinate lookups."
                ),
                'learning': (
                    "Deepened skills in mathematical modeling in Python, data normalization, and building deterministic calculation engines."
                ),
                'key_features': (
                    "Precision astronomical calculation engine for planetary positions\n"
                    "Timezone and daylight savings standardization pipeline\n"
                    "Dynamic chart generation and aspect angle calculations\n"
                    "Clean user workflows for saving and comparing charts\n"
                    "Caching layer for common ephemeris lookups"
                ),
                'tech_names': ['Python', 'Django', 'REST APIs', 'PostgreSQL'],
                'order': 4,
                'featured': True,
                'github_url': 'https://github.com/ujvalthakor/cosmic-insight',
                'live_url': '',
            },
            {
                'title': 'Car Number Detection',
                'slug': 'car-number-detection',
                'project_number': '05',
                'category': 'Computer Vision Pipeline',
                'year': '2025',
                'short_description': 'Automated license plate localization and extraction pipeline using Python, OpenCV image processing, and morphological filtering.',
                'description': (
                    "A computer vision pipeline designed to detect vehicle registration plates from real-world camera feeds and static images. "
                    "The system handles varying lighting conditions, oblique angles, and complex backgrounds using deterministic OpenCV operations."
                ),
                'architecture_description': (
                    "A multi-stage image processing sequence: Grayscale conversion -> Bilateral filtering (noise reduction while preserving edges) "
                    "-> Canny edge detection -> Contour extraction & aspect ratio filtering -> Perspective correction (homography) -> License plate isolation."
                ),
                'architecture_flow': "Raw Vehicle Frame -> Grayscale & Bilateral Filter -> Canny Edge Detection -> Contour Aspect Ratio Filtering -> Perspective Warping -> Isolated License Plate Image",
                'challenge': (
                    "Differentiating license plates from vehicle grilles, headlights, and road signage under high shadow and night glare conditions."
                ),
                'solution': (
                    "Implemented adaptive thresholding coupled with geometric aspect-ratio bounding constraints (typical Indian and international plate dimensions) "
                    "and polygonal approximation to filter out non-rectangular noise contours."
                ),
                'learning': (
                    "Acquired solid practical expertise in OpenCV matrix manipulations, spatial filtering, contour mathematics, and camera calibration."
                ),
                'key_features': (
                    "Multi-stage OpenCV preprocessing pipeline\n"
                    "Contour localization with geometric ratio filtering\n"
                    "Adaptive thresholding for low-light & high-contrast vehicle shots\n"
                    "Perspective rectification for angled camera views\n"
                    "Modular Python code ready for OCR and database logging"
                ),
                'tech_names': ['Python', 'OpenCV', 'Machine Learning', 'Linux', 'Git'],
                'order': 5,
                'featured': True,
                'github_url': 'https://github.com/ujvalthakor/car-number-detection',
                'live_url': '',
            },
            {
                'title': 'Fabric Fault Detection',
                'slug': 'fabric-fault-detection',
                'project_number': '06',
                'category': 'Real-Time Computer Vision',
                'year': '2025',
                'short_description': 'Real-time computer vision quality inspection system for textile manufacturing, detecting weaving anomalies, holes, and thread breaks.',
                'description': (
                    "An industrial quality control vision system developed to automate defect detection on textile conveyor lines. "
                    "Streaming live video feeds, the software analyzes continuous fabric textures in real time to pinpoint defects, "
                    "classify anomaly types, and log defect coordinates."
                ),
                'architecture_description': (
                    "Engineered with a producer-consumer multithreaded architecture. One worker thread ingests camera frames continuously "
                    "to prevent RTSP/USB buffer overflows, while image processing workers run spatial texture analysis, morphological closing, "
                    "and connected component labeling."
                ),
                'architecture_flow': "Conveyor Camera Feed -> Multithreaded Frame Ingestion -> Gaussian Blur & Texture Filter -> Morphological Anomaly Isolation -> Defect Bounding & Classification -> Defect Alert & Log",
                'challenge': (
                    "High-resolution video streaming at 30+ FPS choked standard single-threaded Python execution, causing frame dropping and delayed defect alerts."
                ),
                'solution': (
                    "Decoupled frame capture from image processing using Python's `threading` and thread-safe queues (`queue.Queue`), "
                    "downsampled frames for the initial anomaly locator, and ran localized high-resolution crops only over flagged regions."
                ),
                'learning': (
                    "Mastered real-time image processing latency budgets, multithreading synchronization, OpenCV video capture pipelines, "
                    "and industrial automation considerations."
                ),
                'key_features': (
                    "Live industrial camera frame streaming and ingestion\n"
                    "Multithreaded queue architecture to prevent video latency\n"
                    "Texture anomaly and thread-break isolation algorithms\n"
                    "Real-time visual bounding boxes and defect telemetry\n"
                    "Automated defect logging with timestamps and confidence scores"
                ),
                'tech_names': ['Python', 'OpenCV', 'Machine Learning', 'Linux', 'Git'],
                'order': 6,
                'featured': True,
                'github_url': 'https://github.com/ujvalthakor/fabric-fault-detection',
                'live_url': '',
            },
        ]

        for pdata in projects_data:
            tech_names = pdata.pop('tech_names')
            proj, _ = Project.objects.update_or_create(
                slug=pdata['slug'],
                defaults=pdata
            )
            proj.technologies.clear()
            for tname in tech_names:
                if tname in tech_map:
                    proj.technologies.add(tech_map[tname])
        self.stdout.write(self.style.SUCCESS('[OK] 6 Authentic Projects seeded.'))

        # 4. Experiences (Honest, strictly authentic)
        experiences_data = [
            {
                'company': 'Independent Engineering / Academic Research',
                'role': 'Backend & Python Developer',
                'location': 'Surat, Gujarat, India',
                'experience_type': 'PERSONAL_PROJECT',
                'start_date': '2024',
                'end_date': 'Present',
                'is_current': True,
                'order': 1,
                'description': 'Architecting robust backend systems, REST APIs, and database schemas with Django and Python.',
                'highlights': (
                    "Engineered 6+ production-ready backend systems including RESTful APIs, database platforms, and CV inspection pipelines\n"
                    "Implemented secure authentication, role-based authorization, and Swagger documentation\n"
                    "Optimized database performance utilizing Django ORM prefetching, reducing query overhead by over 70%\n"
                    "Integrated AI and OpenCV pipelines into web service architectures"
                ),
            },
            {
                'company': 'AI / ML & Computer Vision Projects',
                'role': 'AI/ML & Vision Systems Developer',
                'location': 'Surat, Gujarat, India',
                'experience_type': 'INTERNSHIP',
                'start_date': '2024',
                'end_date': '2025',
                'is_current': False,
                'order': 2,
                'description': 'Hands-on development of computer vision algorithms, real-time video inspection pipelines, and AI API integrations.',
                'highlights': (
                    "Built real-time fabric fault detection system using OpenCV and multithreaded frame processing\n"
                    "Developed automated car number plate detection pipeline using contour analysis and adaptive filtering\n"
                    "Integrated external AI recommendation endpoints with Django REST microservices"
                ),
            },
            {
                'company': 'B.Tech in Computer Engineering',
                'role': 'Engineering Student',
                'location': 'Gujarat, India',
                'experience_type': 'PROFESSIONAL_PROJECT',
                'start_date': '2022',
                'end_date': '2026',
                'is_current': True,
                'order': 3,
                'description': 'Rigorous computer science curriculum emphasizing Data Structures, Algorithms, Database Management Systems, Computer Networks, and Operating Systems.',
                'highlights': (
                    "Core coursework: Relational Databases, Operating Systems, Computer Architecture, Software Engineering\n"
                    "Active hands-on practical lab work with Python, C++, MySQL, and Linux environments\n"
                    "Participated in technical hackathons and engineering system design challenges"
                ),
            },
        ]

        for exp in experiences_data:
            Experience.objects.update_or_create(
                company=exp['company'],
                role=exp['role'],
                defaults=exp
            )
        self.stdout.write(self.style.SUCCESS('[OK] Experiences seeded.'))

        # 5. Skills
        skills_data = [
            ('Python 3.x', 'BACKEND', 'Core Language', 1),
            ('Django', 'BACKEND', 'Web Framework', 2),
            ('Django REST Framework', 'BACKEND', 'REST APIs', 3),
            ('PostgreSQL', 'DATABASE', 'ACID Relational', 4),
            ('MySQL', 'DATABASE', 'Schema & SQL', 5),
            ('Redis', 'DATABASE', 'Cache & Session', 6),
            ('RESTful API Design', 'ARCHITECTURE', 'Contracts & Auth', 7),
            ('OpenCV', 'AI_CV', 'Computer Vision', 8),
            ('AI Model Integration', 'AI_CV', 'REST Inference', 9),
            ('Docker', 'DEVOPS', 'Containerization', 10),
            ('Linux / Bash', 'DEVOPS', 'Server CLI', 11),
            ('Git / GitHub', 'DEVOPS', 'Version Control', 12),
        ]

        for sname, scat, sbadge, sorder in skills_data:
            Skill.objects.update_or_create(
                name=sname,
                defaults={
                    'category': scat,
                    'badge_label': sbadge,
                    'order': sorder
                }
            )
        self.stdout.write(self.style.SUCCESS('[OK] Skills seeded.'))

        # 6. Resume
        Resume.objects.update_or_create(
            id=1,
            defaults={
                'title': 'Ujval Thakor - Backend Developer Resume (2026)',
                'summary': 'B.Tech Computer Engineering student with hands-on Python and Django development experience. Skilled in REST APIs, MySQL, PostgreSQL, Redis, Docker, OpenCV, and AI integration.',
                'is_active': True
            }
        )
        self.stdout.write(self.style.SUCCESS('[OK] Resume record seeded.'))
        self.stdout.write(self.style.SUCCESS('[SUCCESS] All portfolio data seeded successfully!'))
