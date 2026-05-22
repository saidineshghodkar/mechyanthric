from copy import deepcopy
from datetime import datetime
from functools import wraps
import json
import os
import uuid

from flask import Flask, abort, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_FILE = os.path.join(BASE_DIR, "content.json")
REGISTRATIONS_FILE = os.path.join(BASE_DIR, "registrations.json")
CONTACTS_FILE = os.path.join(BASE_DIR, "contacts.json")
USERS_FILE = os.path.join(BASE_DIR, "users.json")

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "mechyanthrics-dev-secret")


DEFAULT_CONTENT = {
    "brand": {
        "name": "MECHYANTHRICS",
        "tagline": "Mechanical Intelligence | Digital Systems | Creative Execution",
    },
    "theme": {
        "accent": "#dbe1e8",
        "accent_secondary": "#7f8897",
        "panel": "rgba(18, 22, 29, 0.84)",
        "panel_strong": "rgba(24, 28, 36, 0.96)",
        "glow": "rgba(219, 225, 232, 0.28)",
    },
    "hero": {
        "eyebrow": "Futuristic engineering company",
        "title": "Engineering the future with intelligence, precision, and cinematic execution.",
        "subtitle": (
            "Mechyanthrics combines mechanical design, AI systems, electronics, "
            "interiors, animation tools, CA services, and delivery operations "
            "into one premium technology company."
        ),
        "primary_cta": "Request a Project",
        "secondary_cta": "Open Portals",
        "visual_url": (
            "https://images.unsplash.com/photo-1518770660439-4636190af475"
            "?auto=format&fit=crop&w=1200&q=80"
        ),
        "floating_points": [
            "Master command center",
            "Domain-wise dashboards",
            "Freelancer opportunity hub",
            "Animated premium UX",
        ],
    },
    "about": {
        "headline": "Built for companies that need engineering depth and launch-ready execution.",
        "text": (
            "Mechyanthrics is designed as a multi-domain execution company where "
            "mechanical innovation, electronics, AI software, robotics, interiors, "
            "animation tooling, and CA support work inside one operating system. "
            "The goal is simple: fewer handoffs, faster delivery, stronger quality."
        ),
    },
    "stats": [
        {"value": "07", "label": "Domain verticals"},
        {"value": "24/7", "label": "Live work visibility"},
        {"value": "92%", "label": "Prototype retention"},
        {"value": "03", "label": "Secure portal layers"},
    ],
    "services": [
        {
            "slug": "mechanical-systems",
            "title": "Mechanical Systems",
            "department": "Mechanical",
            "summary": "Design, prototyping, simulation, and production planning for physical systems.",
            "headline": "Mechanical products that move from concept sketch to real-world hardware.",
            "focus": ["CAD/CAM", "Stress simulation", "Tooling design", "Prototype planning"],
            "deliverables": [
                "Concept modeling",
                "Production drawings",
                "Tolerance and materials plan",
                "Prototype validation roadmap",
            ],
            "process": [
                "Requirement mapping",
                "Design and iteration",
                "Simulation review",
                "Prototype handoff",
            ],
            "industries": ["Mobility", "Manufacturing", "Fitness", "Product engineering"],
        },
        {
            "slug": "ai-software-platforms",
            "title": "AI & Software Platforms",
            "department": "AI & Software",
            "summary": "Dashboards, automation, AI workflows, and full-stack business systems.",
            "headline": "Software ecosystems with analytics, automation, and client-ready polish.",
            "focus": ["Web apps", "AI workflows", "Automation", "Analytics dashboards"],
            "deliverables": [
                "Platform architecture",
                "Admin and role dashboards",
                "Automation pipelines",
                "Data visualization systems",
            ],
            "process": [
                "Workflow discovery",
                "System mapping",
                "Sprint buildout",
                "Monitoring and iteration",
            ],
            "industries": ["Enterprise", "Operations", "Startups", "Internal tooling"],
        },
        {
            "slug": "electronics-iot",
            "title": "Electronics & IoT",
            "department": "Electronics",
            "summary": "Embedded intelligence, PCB thinking, sensor systems, and connected devices.",
            "headline": "Electronics that bridge hardware, signals, and smart product behavior.",
            "focus": ["Embedded logic", "Sensors", "IoT telemetry", "Control systems"],
            "deliverables": [
                "Circuit planning",
                "Sensor integration map",
                "Telemetry dashboard logic",
                "Testing and calibration notes",
            ],
            "process": [
                "Signal strategy",
                "Interface definition",
                "Validation setup",
                "Field optimization",
            ],
            "industries": ["Smart devices", "Automation", "Robotics", "Tracking systems"],
        },
        {
            "slug": "robotics-automation",
            "title": "Robotics & Automation",
            "department": "Robotics",
            "summary": "Automation logic, motion systems, robotic workflows, and industrial support.",
            "headline": "Robotics programs built for repeatability, motion accuracy, and scale.",
            "focus": ["Motion control", "Robotic flows", "Automation logic", "Industrial validation"],
            "deliverables": [
                "Workflow design",
                "Control sequence planning",
                "Testing checklist",
                "Performance optimization path",
            ],
            "process": [
                "Task decomposition",
                "Control mapping",
                "Safety and validation",
                "Deployment support",
            ],
            "industries": ["Factories", "Labs", "Warehousing", "R&D operations"],
        },
        {
            "slug": "interiors-renovation",
            "title": "Interiors & Renovation",
            "department": "Interior Design",
            "summary": "Interior systems, renovation concepts, and detail-rich spatial execution.",
            "headline": "Interior projects with engineering discipline and premium visual finishing.",
            "focus": ["Interior concepts", "Renovation planning", "Execution support", "Material moodboards"],
            "deliverables": [
                "Space planning",
                "Visual references",
                "Execution sequence",
                "Material and lighting notes",
            ],
            "process": [
                "Space audit",
                "Mood and planning",
                "Execution phasing",
                "Quality walkthrough",
            ],
            "industries": ["Residential", "Commercial", "Studios", "Retail"],
        },
        {
            "slug": "animation-media-tools",
            "title": "Animation & Media Tools",
            "department": "Animation & Media",
            "summary": "AI-assisted animation pipelines, motion assets, and premium media delivery.",
            "headline": "Visual systems that make products, brands, and launches feel alive.",
            "focus": ["Motion design", "AI-assisted animation", "3D visual direction", "Launch media"],
            "deliverables": [
                "Motion identity system",
                "Campaign visuals",
                "Animation production kit",
                "Content rollout assets",
            ],
            "process": [
                "Narrative planning",
                "Look development",
                "Motion build",
                "Export and optimization",
            ],
            "industries": ["Branding", "Product launch", "Media", "Digital campaigns"],
        },
        {
            "slug": "ca-services",
            "title": "CA Services",
            "department": "CA Services",
            "summary": "Compliance, structure, and finance support for growing technical businesses.",
            "headline": "Operational finance and compliance support that keeps growth clean.",
            "focus": ["GST and filings", "Business structuring", "Financial hygiene", "Advisory support"],
            "deliverables": [
                "Compliance schedule",
                "Entity support",
                "Financial review checklist",
                "Advisory meeting notes",
            ],
            "process": [
                "Financial intake",
                "Compliance mapping",
                "Documentation support",
                "Ongoing review",
            ],
            "industries": ["SMBs", "Studios", "Agencies", "Tech ventures"],
        },
    ],
    "projects": [
        {
            "slug": "mechanical-cycle",
            "title": "Mechanical Cycle",
            "status": "Concept to prototype",
            "department": "Mechanical",
            "timeline": "Q3 2026",
            "summary": "A modular mobility concept with precision drivetrain exploration and lightweight fabrication planning.",
        },
        {
            "slug": "scientific-calculator",
            "title": "Scientific Calculator",
            "status": "Embedded product study",
            "department": "Electronics",
            "timeline": "Q3 2026",
            "summary": "A smart calculator concept blending electronics, interface logic, and student-focused usability.",
        },
        {
            "slug": "interior-renovation-suite",
            "title": "Interior Designs and Renovations",
            "status": "Execution roadmap",
            "department": "Interior Design",
            "timeline": "Q4 2026",
            "summary": "A premium interior and renovation system for residential and commercial upgrades.",
        },
        {
            "slug": "gym-fitness-tools",
            "title": "Gym Fitness Tools",
            "status": "Mechanical R&D",
            "department": "Mechanical",
            "timeline": "Q4 2026",
            "summary": "A portfolio of durable, ergonomic fitness tools with fabrication-ready mechanical plans.",
        },
        {
            "slug": "tracking-system",
            "title": "Tracking System",
            "status": "Platform build",
            "department": "AI & Software",
            "timeline": "Q3 2026",
            "summary": "An intelligent tracking platform for operations visibility, alerts, telemetry, and workforce movement.",
        },
        {
            "slug": "ai-animation-tools",
            "title": "AI Based Animation Tools",
            "status": "Creative lab pipeline",
            "department": "Animation & Media",
            "timeline": "Q1 2027",
            "summary": "A next-gen content toolkit for motion systems, AI-assisted scene generation, and export automation.",
        },
    ],
    "departments": [
        {
            "slug": "mechanical",
            "title": "Mechanical",
            "head": "Arjun Dev",
            "summary": "Hardware systems, product mechanics, and fabrication-aware execution.",
            "employee_count": 18,
            "active_projects": 6,
            "upcoming": ["Mechanical Cycle", "Gym Fitness Tools"],
            "current": ["Fixture redesign sprint", "Gearbox audit", "Prototype tolerance review"],
            "team": [
                {"name": "Varun K", "role": "Design Lead", "status": "On track"},
                {"name": "Preethi M", "role": "Simulation Engineer", "status": "Reviewing"},
                {"name": "Sandeep V", "role": "Prototype Specialist", "status": "In field"},
            ],
            "metrics": [
                {"label": "On-time tasks", "value": "94%"},
                {"label": "Prototype readiness", "value": "88%"},
                {"label": "Open blockers", "value": "03"},
            ],
        },
        {
            "slug": "ai-software",
            "title": "AI & Software",
            "head": "Nisha Rao",
            "summary": "Dashboards, AI systems, APIs, automation, and data-driven product delivery.",
            "employee_count": 21,
            "active_projects": 8,
            "upcoming": ["Tracking System", "Master portal upgrade"],
            "current": ["Ops dashboard build", "Chatbot orchestration", "Analytics instrumentation"],
            "team": [
                {"name": "Ritwik S", "role": "Platform Architect", "status": "On track"},
                {"name": "Harini P", "role": "AI Engineer", "status": "Reviewing"},
                {"name": "Joel N", "role": "Full-stack Lead", "status": "Shipping"},
            ],
            "metrics": [
                {"label": "Deployment cadence", "value": "2.4/wk"},
                {"label": "Automation coverage", "value": "81%"},
                {"label": "Incidents", "value": "01"},
            ],
        },
        {
            "slug": "electronics",
            "title": "Electronics",
            "head": "Dharani K",
            "summary": "Embedded logic, sensor systems, device interfaces, and telemetry design.",
            "employee_count": 12,
            "active_projects": 4,
            "upcoming": ["Scientific Calculator", "Sensor mesh upgrade"],
            "current": ["Telemetry module tuning", "Power rail validation", "Field test planning"],
            "team": [
                {"name": "Sai Tej", "role": "Embedded Engineer", "status": "On track"},
                {"name": "Moksha B", "role": "Validation Specialist", "status": "Testing"},
                {"name": "Aneesh R", "role": "IoT Analyst", "status": "Reviewing"},
            ],
            "metrics": [
                {"label": "Signal stability", "value": "97%"},
                {"label": "Bench tests", "value": "14"},
                {"label": "Field units", "value": "09"},
            ],
        },
        {
            "slug": "robotics",
            "title": "Robotics",
            "head": "Farhan Ali",
            "summary": "Automation sequences, motion systems, and robotic workflow design.",
            "employee_count": 10,
            "active_projects": 3,
            "upcoming": ["Automation cell v2", "Motion stack audit"],
            "current": ["Pick-path calibration", "Control loop cleanup", "Safety simulation"],
            "team": [
                {"name": "Isha G", "role": "Automation Lead", "status": "On track"},
                {"name": "Manoj L", "role": "Control Engineer", "status": "Reviewing"},
                {"name": "Tenzin P", "role": "Field Integrator", "status": "On site"},
            ],
            "metrics": [
                {"label": "Cycle efficiency", "value": "89%"},
                {"label": "Robot uptime", "value": "96%"},
                {"label": "Safety issues", "value": "00"},
            ],
        },
        {
            "slug": "interior-design",
            "title": "Interior Design",
            "head": "Aishwarya J",
            "summary": "Interior concepts, renovation planning, execution support, and spatial detailing.",
            "employee_count": 9,
            "active_projects": 4,
            "upcoming": ["Interior renovation suite", "Workspace relaunch concept"],
            "current": ["Lighting revision", "Material board finalization", "Client walkthrough prep"],
            "team": [
                {"name": "Kavya S", "role": "Spatial Designer", "status": "On track"},
                {"name": "Devan P", "role": "Execution Planner", "status": "Reviewing"},
                {"name": "Lina T", "role": "Visual Stylist", "status": "Delivering"},
            ],
            "metrics": [
                {"label": "Approvals closed", "value": "11"},
                {"label": "Vendor readiness", "value": "84%"},
                {"label": "Live sites", "value": "02"},
            ],
        },
        {
            "slug": "ca-services",
            "title": "CA Services",
            "head": "Karthik Iyer",
            "summary": "Finance operations, compliance, business setup, and advisory support.",
            "employee_count": 6,
            "active_projects": 11,
            "upcoming": ["Quarter close system", "Entity restructure review"],
            "current": ["GST schedule", "Vendor ledger cleanup", "Audit prep"],
            "team": [
                {"name": "Sharanya V", "role": "Compliance Lead", "status": "On track"},
                {"name": "Mitesh K", "role": "Advisory Analyst", "status": "Reviewing"},
                {"name": "Rhea P", "role": "Accounts Specialist", "status": "Delivering"},
            ],
            "metrics": [
                {"label": "Compliance health", "value": "99%"},
                {"label": "Open notices", "value": "00"},
                {"label": "Review calls", "value": "07"},
            ],
        },
        {
            "slug": "animation-media",
            "title": "Animation & Media",
            "head": "Neel Roy",
            "summary": "Motion systems, launch media, animation tools, and creative production operations.",
            "employee_count": 14,
            "active_projects": 5,
            "upcoming": ["AI animation tools", "Launch trailer system"],
            "current": ["Motion identity kit", "Scene automation test", "Campaign asset pass"],
            "team": [
                {"name": "Pooja C", "role": "Motion Director", "status": "On track"},
                {"name": "Rehaan S", "role": "Creative Technologist", "status": "Reviewing"},
                {"name": "Anvita M", "role": "Video Editor", "status": "Delivering"},
            ],
            "metrics": [
                {"label": "Asset velocity", "value": "28/wk"},
                {"label": "Revision cycle", "value": "1.8"},
                {"label": "Ready exports", "value": "43"},
            ],
        },
    ],
    "opportunities": [
        {
            "slug": "ops-tracking-ui",
            "title": "Tracking System UI + AI Logic",
            "department": "AI & Software",
            "budget": "₹1.8L - ₹3.2L",
            "mode": "Hybrid",
            "summary": "Build tracking dashboards, alert flows, and operator visibility for a high-scale system.",
        },
        {
            "slug": "fitness-tool-prototype",
            "title": "Gym Fitness Tool Prototype Support",
            "department": "Mechanical",
            "budget": "₹95K - ₹1.7L",
            "mode": "On-site + remote",
            "summary": "Support fixture detailing, ergonomics review, and prototype optimization for fitness hardware.",
        },
        {
            "slug": "ai-motion-pack",
            "title": "AI Motion Pack Production",
            "department": "Animation & Media",
            "budget": "₹70K - ₹1.4L",
            "mode": "Remote",
            "summary": "Create launch-ready AI-assisted motion scenes and branded animation exports.",
        },
    ],
    "testimonials": [
        {
            "quote": "Mechyanthrics gave us one execution partner across engineering, software, and launch creative.",
            "author": "Kiran Rao",
            "role": "Operations Director",
        },
        {
            "quote": "Their team thinks like product builders, not just service vendors. That changed our speed completely.",
            "author": "Lavanya Shah",
            "role": "Founder, Studio Venture",
        },
        {
            "quote": "The domain-wise visibility and freelancer pipeline made coordination dramatically easier.",
            "author": "Rahul Menon",
            "role": "Program Lead",
        },
    ],
    "faqs": [
        {
            "question": "What is the difference between master, domain, and freelancer logins?",
            "answer": "Master login controls settings, users, theme, approvals, and platform visibility. Domain login is restricted to official department heads. Freelancer login is open to approved talent who want to apply for work and maintain their profile.",
        },
        {
            "question": "Can freelancers apply for projects directly from the dashboard?",
            "answer": "Yes. Approved freelancers can view active opportunities and apply from their dashboard with a short note and portfolio references.",
        },
        {
            "question": "Which services are available under Mechyanthrics?",
            "answer": "Mechanical systems, AI software, electronics, robotics, interiors, animation and media tooling, CA services, and business execution support.",
        },
        {
            "question": "Do domain heads see only their own teams?",
            "answer": "Yes. Each domain dashboard is limited to that department's people, active work, upcoming pipeline, and delivery metrics.",
        },
        {
            "question": "Can the website style and colors be changed without touching code?",
            "answer": "Yes. The master dashboard includes a settings panel for hero content, contact details, and metallic theme accents.",
        },
        {
            "question": "Is there support for project consultation before starting work?",
            "answer": "Yes. Public visitors can submit a project request, and the team can respond with scope, timeline, and the right domain alignment.",
        },
    ],
    "contact": {
        "email": "hello@mechyanthrics.com",
        "phone": "+91 93470 51097",
        "location": "Bengaluru, India",
        "map_url": (
            "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!"
            "1d3888.0745889318464!2d77.584787!3d12.9645311!2m3!1f0!2f0!"
            "3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3bae15d8c47e37f9%3A"
            "0x83d6d1240f7f7c1a!2sBengaluru%2C%20Karnataka!5e0!3m2!1sen!"
            "2sin!4v1710000000000!5m2!1sen!2sin"
        ),
        "whatsapp": "+919347051097",
    },
}

DEFAULT_REGISTRATIONS = {
    "clients": [],
    "project_requests": [],
    "freelancers": [],
    "applications": [],
}


def build_seed_users():
    seed_specs = [
        {
            "email": "master@mechyanthrics.com",
            "username": "master",
            "password": "Master@123",
            "role": "master",
            "approved": True,
            "full_name": "System Master",
            "title": "Platform Controller",
            "department": "Executive",
            "phone": "+91 90000 10001",
            "location": "Bengaluru",
            "bio": "Owns the entire operating system, approvals, visual settings, and control center.",
            "skills": ["Operations strategy", "Platform governance", "Delivery oversight"],
            "experience": "Enterprise control systems and multi-team execution leadership.",
            "portfolio": "Master portal oversight and brand operations.",
            "availability": "Always available",
            "socials": {"linkedin": "#", "website": "#"},
        },
        {
            "email": "mechanical.head@mechyanthrics.com",
            "username": "mechanical.head",
            "password": "Domain@123",
            "role": "domain",
            "approved": True,
            "full_name": "Arjun Dev",
            "title": "Domain Head, Mechanical",
            "department": "Mechanical",
            "phone": "+91 90000 10002",
            "location": "Bengaluru",
            "bio": "Leads product mechanics, hardware execution, and fabrication-aligned delivery.",
            "skills": ["CAD/CAM", "Simulation", "Prototype strategy"],
            "experience": "8 years in mechanical product design and prototyping.",
            "portfolio": "Mobility systems, tooling, and structural hardware programs.",
            "availability": "Department-only access",
            "socials": {"linkedin": "#", "website": "#"},
        },
        {
            "email": "software.head@mechyanthrics.com",
            "username": "software.head",
            "password": "Domain@123",
            "role": "domain",
            "approved": True,
            "full_name": "Nisha Rao",
            "title": "Domain Head, AI & Software",
            "department": "AI & Software",
            "phone": "+91 90000 10003",
            "location": "Hyderabad",
            "bio": "Leads AI systems, dashboards, automation, and platform delivery.",
            "skills": ["System architecture", "AI workflows", "Data products"],
            "experience": "9 years in platform engineering and automation systems.",
            "portfolio": "Ops platforms, internal tools, and AI-enabled products.",
            "availability": "Department-only access",
            "socials": {"linkedin": "#", "website": "#"},
        },
        {
            "email": "electronics.head@mechyanthrics.com",
            "username": "electronics.head",
            "password": "Domain@123",
            "role": "domain",
            "approved": True,
            "full_name": "Dharani K",
            "title": "Domain Head, Electronics",
            "department": "Electronics",
            "phone": "+91 90000 10004",
            "location": "Chennai",
            "bio": "Leads embedded systems, sensor products, and telemetry operations.",
            "skills": ["Embedded systems", "IoT", "Validation"],
            "experience": "7 years in device systems and electronics validation.",
            "portfolio": "Telemetry stacks, devices, and controller systems.",
            "availability": "Department-only access",
            "socials": {"linkedin": "#", "website": "#"},
        },
        {
            "email": "robotics.head@mechyanthrics.com",
            "username": "robotics.head",
            "password": "Domain@123",
            "role": "domain",
            "approved": True,
            "full_name": "Farhan Ali",
            "title": "Domain Head, Robotics",
            "department": "Robotics",
            "phone": "+91 90000 10005",
            "location": "Pune",
            "bio": "Runs automation, control logic, and field robotics execution.",
            "skills": ["Automation", "Control loops", "Field integration"],
            "experience": "8 years across motion systems and robotics.",
            "portfolio": "Automation cells, motion testing, and deployment.",
            "availability": "Department-only access",
            "socials": {"linkedin": "#", "website": "#"},
        },
        {
            "email": "interiors.head@mechyanthrics.com",
            "username": "interiors.head",
            "password": "Domain@123",
            "role": "domain",
            "approved": True,
            "full_name": "Aishwarya J",
            "title": "Domain Head, Interior Design",
            "department": "Interior Design",
            "phone": "+91 90000 10006",
            "location": "Bengaluru",
            "bio": "Owns premium renovation, interior planning, and execution sequencing.",
            "skills": ["Spatial design", "Execution planning", "Material systems"],
            "experience": "6 years in interiors and renovation delivery.",
            "portfolio": "Residential, retail, and workspace transformations.",
            "availability": "Department-only access",
            "socials": {"linkedin": "#", "website": "#"},
        },
        {
            "email": "ca.head@mechyanthrics.com",
            "username": "ca.head",
            "password": "Domain@123",
            "role": "domain",
            "approved": True,
            "full_name": "Karthik Iyer",
            "title": "Domain Head, CA Services",
            "department": "CA Services",
            "phone": "+91 90000 10007",
            "location": "Chennai",
            "bio": "Oversees compliance, finance operations, and business advisory.",
            "skills": ["Compliance", "Financial systems", "Advisory"],
            "experience": "10 years in business finance and compliance advisory.",
            "portfolio": "SME finance operations and compliance programs.",
            "availability": "Department-only access",
            "socials": {"linkedin": "#", "website": "#"},
        },
        {
            "email": "media.head@mechyanthrics.com",
            "username": "media.head",
            "password": "Domain@123",
            "role": "domain",
            "approved": True,
            "full_name": "Neel Roy",
            "title": "Domain Head, Animation & Media",
            "department": "Animation & Media",
            "phone": "+91 90000 10008",
            "location": "Mumbai",
            "bio": "Directs animation tooling, launch media, and AI-assisted production systems.",
            "skills": ["Motion systems", "Creative ops", "Launch content"],
            "experience": "7 years in animation production and digital content systems.",
            "portfolio": "Motion identity, product launch media, and AI content workflows.",
            "availability": "Department-only access",
            "socials": {"linkedin": "#", "website": "#"},
        },
        {
            "email": "freelancer@mechyanthrics.com",
            "username": "freelancer.demo",
            "password": "Freelancer@123",
            "role": "freelancer",
            "approved": True,
            "full_name": "Riya Sharma",
            "title": "Freelance Product Visualizer",
            "department": "Freelancer Network",
            "phone": "+91 90000 10009",
            "location": "Remote",
            "bio": "Helps build product visuals, concept decks, and launch-ready presentation assets.",
            "skills": ["Presentation design", "Motion visuals", "Creative systems"],
            "experience": "5 years building launch assets for technical products.",
            "portfolio": "Portfolio available on request.",
            "availability": "20 hrs/week",
            "socials": {"linkedin": "#", "website": "#"},
        },
    ]
    seeds = []
    for spec in seed_specs:
        user = deepcopy(spec)
        password = user.pop("password")
        user["password_hash"] = generate_password_hash(password)
        user["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        seeds.append(user)
    return seeds


def load_json(path, fallback):
    if not os.path.exists(path):
        return deepcopy(fallback)
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, OSError):
        return deepcopy(fallback)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)


def deep_merge(default, current):
    if isinstance(default, dict):
        merged = deepcopy(default)
        if isinstance(current, dict):
            for key, value in current.items():
                merged[key] = deep_merge(default.get(key), value) if key in default else value
        return merged
    if current is None:
        return deepcopy(default)
    return current


def ensure_data_files():
    content = deep_merge(DEFAULT_CONTENT, load_json(CONTENT_FILE, DEFAULT_CONTENT))
    write_json(CONTENT_FILE, content)

    registrations = load_json(REGISTRATIONS_FILE, DEFAULT_REGISTRATIONS)
    if "project_requests" not in registrations:
        registrations["project_requests"] = registrations.get("clients", [])
    if "clients" not in registrations:
        registrations["clients"] = registrations["project_requests"]
    registrations.setdefault("freelancers", [])
    registrations.setdefault("applications", [])
    write_registrations(registrations)

    contacts = load_json(CONTACTS_FILE, [])
    write_json(CONTACTS_FILE, contacts)

    users = load_json(USERS_FILE, [])
    known_emails = {user.get("email") for user in users}
    for seed_user in build_seed_users():
        if seed_user["email"] not in known_emails:
            users.append(seed_user)
    write_json(USERS_FILE, users)


def read_content():
    return load_json(CONTENT_FILE, DEFAULT_CONTENT)


def write_content(data):
    write_json(CONTENT_FILE, data)


def read_registrations():
    data = load_json(REGISTRATIONS_FILE, DEFAULT_REGISTRATIONS)
    if "project_requests" not in data:
        data["project_requests"] = data.get("clients", [])
    if "clients" not in data:
        data["clients"] = data["project_requests"]
    data.setdefault("freelancers", [])
    data.setdefault("applications", [])
    return data


def write_registrations(data):
    data["clients"] = data.get("project_requests", [])
    write_json(REGISTRATIONS_FILE, data)


def read_contacts():
    return load_json(CONTACTS_FILE, [])


def write_contacts(data):
    write_json(CONTACTS_FILE, data)


def read_users():
    return load_json(USERS_FILE, [])


def write_users(data):
    write_json(USERS_FILE, data)


def current_user():
    email = session.get("user_email")
    if not email:
        return None
    return next((user for user in read_users() if user.get("email") == email), None)


def split_csv(value):
    if not value:
        return []
    if isinstance(value, list):
        return [item for item in value if item]
    return [item.strip() for item in value.split(",") if item.strip()]


def find_user(identifier):
    if not identifier:
        return None
    return next(
        (
            user
            for user in read_users()
            if user.get("email") == identifier or user.get("username") == identifier
        ),
        None,
    )


def get_department(content, department_name):
    return next(
        (
            department
            for department in content.get("departments", [])
            if department.get("title") == department_name or department.get("slug") == department_name
        ),
        None,
    )


def profile_completion(user):
    checks = [
        user.get("full_name"),
        user.get("title"),
        user.get("phone"),
        user.get("location"),
        user.get("bio"),
        user.get("experience"),
        user.get("portfolio"),
        user.get("skills"),
    ]
    filled = sum(1 for item in checks if item)
    return int((filled / len(checks)) * 100)


def public_user(user):
    if not user:
        return None
    cleaned = {key: value for key, value in user.items() if key != "password_hash"}
    cleaned["skills"] = split_csv(cleaned.get("skills") or [])
    cleaned["socials"] = cleaned.get("socials") or {}
    return cleaned


def dashboard_route_for(role):
    if role == "master":
        return url_for("master_dashboard")
    if role == "domain":
        return url_for("domain_dashboard")
    if role == "freelancer":
        return url_for("freelancer_dashboard")
    return url_for("login_page")


def auth_required(*roles):
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            user = current_user()
            if not user:
                return redirect(url_for("login_page"))
            if roles and user.get("role") not in roles:
                abort(403)
            return func(*args, **kwargs)

        return wrapped

    return decorator


def api_auth_required(*roles):
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            user = current_user()
            if not user:
                return jsonify({"status": "error", "message": "Unauthorized"}), 401
            if roles and user.get("role") not in roles:
                return jsonify({"status": "error", "message": "Forbidden"}), 403
            return func(*args, **kwargs)

        return wrapped

    return decorator


@app.context_processor
def inject_site_context():
    return {
        "site": read_content(),
        "current_user": public_user(current_user()),
        "session_role": session.get("user_role"),
    }


ensure_data_files()


@app.route("/")
def index():
    return render_template("index.html", page_id="home")


@app.route("/login")
def login_page():
    default_role = request.args.get("role", "freelancer")
    if default_role not in {"master", "domain", "freelancer"}:
        default_role = "freelancer"
    return render_template("login.html", page_id="login", default_role=default_role)


@app.route("/register/freelancer")
def freelancer_register_page():
    return render_template("register_freelancer.html", page_id="freelancer-register")


@app.route("/register/client")
def client_register_alias():
    return redirect(url_for("request_project_page"))


@app.route("/request-project")
def request_project_page():
    return render_template("request_project.html", page_id="request-project")


@app.route("/services/<slug>")
def service_detail(slug):
    content = read_content()
    service = next((item for item in content.get("services", []) if item.get("slug") == slug), None)
    if not service:
        abort(404)
    related_department = get_department(content, service.get("department"))
    return render_template(
        "service_detail.html",
        page_id="service-detail",
        service=service,
        related_department=related_department,
    )


@app.route("/dashboard")
@auth_required("master", "domain", "freelancer")
def dashboard():
    return redirect(dashboard_route_for(session.get("user_role")))


@app.route("/admin")
@auth_required("master")
def admin_alias():
    return redirect(url_for("master_dashboard"))


@app.route("/dashboard/master")
@auth_required("master")
def master_dashboard():
    content = read_content()
    users = [public_user(user) for user in read_users()]
    registrations = read_registrations()
    contacts = read_contacts()
    metrics = [
        {"label": "Total users", "value": str(len(users)).zfill(2)},
        {
            "label": "Domain heads",
            "value": str(sum(1 for user in users if user.get("role") == "domain")).zfill(2),
        },
        {
            "label": "Pending freelancers",
            "value": str(
                sum(
                    1
                    for user in users
                    if user.get("role") == "freelancer" and not user.get("approved", False)
                )
            ).zfill(2),
        },
        {"label": "Project requests", "value": str(len(registrations.get("project_requests", []))).zfill(2)},
        {"label": "Applications", "value": str(len(registrations.get("applications", []))).zfill(2)},
        {"label": "Messages", "value": str(len(contacts)).zfill(2)},
    ]
    return render_template(
        "admin_dashboard.html",
        page_id="master-dashboard",
        metrics=metrics,
        users=users,
        registrations=registrations,
        contacts=contacts,
        theme=content.get("theme", {}),
        hero=content.get("hero", {}),
        brand=content.get("brand", {}),
        contact=content.get("contact", {}),
    )


@app.route("/dashboard/domain")
@auth_required("domain")
def domain_dashboard():
    content = read_content()
    user = current_user()
    department = get_department(content, user.get("department"))
    if not department:
        abort(404)
    return render_template(
        "domain_dashboard.html",
        page_id="domain-dashboard",
        user=public_user(user),
        department=department,
    )


@app.route("/dashboard/freelancer")
@auth_required("freelancer")
def freelancer_dashboard():
    content = read_content()
    user = current_user()
    registrations = read_registrations()
    my_apps = [
        app_item
        for app_item in registrations.get("applications", [])
        if app_item.get("user_email") == user.get("email")
    ]
    return render_template(
        "freelancer_dashboard.html",
        page_id="freelancer-dashboard",
        user=public_user(user),
        opportunities=content.get("opportunities", []),
        applications=my_apps,
        completion=profile_completion(user),
    )


@app.route("/profile")
@auth_required("master", "domain", "freelancer")
def profile_page():
    user = current_user()
    return render_template(
        "profile.html",
        page_id="profile",
        user=public_user(user),
        completion=profile_completion(user),
    )


@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    data = request.get_json(silent=True) or {}
    identifier = (data.get("identifier") or data.get("email") or data.get("username") or "").strip()
    password = data.get("password", "")
    expected_role = data.get("role")
    user = find_user(identifier)

    if not user or not check_password_hash(user.get("password_hash", ""), password):
        return jsonify({"status": "error", "message": "Invalid username/email or password."}), 401

    if expected_role and user.get("role") != expected_role:
        return jsonify({"status": "error", "message": "This account does not match the selected portal."}), 403

    if not user.get("approved", False):
        return jsonify({"status": "error", "message": "Account is waiting for master approval."}), 403

    session["user_email"] = user["email"]
    session["user_role"] = user["role"]
    return jsonify({"status": "success", "role": user["role"], "next": dashboard_route_for(user["role"])})


@app.route("/api/login", methods=["POST"])
def legacy_master_login():
    data = request.get_json(silent=True) or {}
    identifier = data.get("username") or data.get("email") or "master"
    password = data.get("password")
    user = find_user(identifier)
    if not user or user.get("role") != "master":
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401
    if not check_password_hash(user.get("password_hash", ""), password or ""):
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401
    session["user_email"] = user["email"]
    session["user_role"] = "master"
    return jsonify({"status": "success", "next": url_for("master_dashboard")})


@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    session.clear()
    return jsonify({"status": "success"})


@app.route("/api/user/logout", methods=["POST"])
def legacy_user_logout():
    session.clear()
    return jsonify({"status": "success"})


@app.route("/api/register/freelancer", methods=["POST"])
def register_freelancer():
    form = request.form.to_dict()
    email = (form.get("email") or "").strip().lower()
    password = form.get("password", "")
    confirm_password = form.get("confirm_password", "")
    if not email or not password:
        return jsonify({"status": "error", "message": "Email and password are required."}), 400
    if password != confirm_password:
        return jsonify({"status": "error", "message": "Passwords do not match."}), 400
    if find_user(email):
        return jsonify({"status": "error", "message": "Email is already registered."}), 400

    user = {
        "email": email,
        "username": email.split("@")[0],
        "password_hash": generate_password_hash(password),
        "role": "freelancer",
        "approved": False,
        "full_name": form.get("full_name") or form.get("fullName") or "",
        "title": form.get("title") or "Freelancer",
        "department": "Freelancer Network",
        "phone": form.get("phone") or "",
        "location": form.get("location") or "",
        "bio": form.get("bio") or "",
        "skills": split_csv(form.get("skills") or ""),
        "experience": form.get("experience") or "",
        "portfolio": form.get("portfolio") or "",
        "availability": form.get("availability") or "",
        "socials": {
            "linkedin": form.get("linkedin") or "",
            "website": form.get("website") or "",
            "github": form.get("github") or "",
        },
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    users = read_users()
    users.append(user)
    write_users(users)

    registrations = read_registrations()
    registrations["freelancers"].append(
        {
            "full_name": user["full_name"],
            "email": user["email"],
            "phone": user["phone"],
            "skills": user["skills"],
            "experience": user["experience"],
            "portfolio": user["portfolio"],
            "availability": user["availability"],
            "approved": False,
            "submitted_at": user["created_at"],
        }
    )
    write_registrations(registrations)
    return jsonify({"status": "success", "message": "Registration submitted. Wait for master approval."})


@app.route("/api/project-request", methods=["POST"])
def create_project_request():
    form = request.form.to_dict()
    payload = {
        "id": str(uuid.uuid4()),
        "contact_name": form.get("contact_name") or form.get("fullName") or "",
        "company": form.get("company") or form.get("company_name") or "",
        "email": form.get("email") or "",
        "phone": form.get("phone") or "",
        "service": form.get("service") or form.get("projectType") or "",
        "budget": form.get("budget") or "",
        "timeline": form.get("timeline") or "",
        "requirements": form.get("requirements") or form.get("message") or "",
        "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    registrations = read_registrations()
    registrations["project_requests"].append(payload)
    write_registrations(registrations)
    return jsonify({"status": "success", "message": "Project request submitted successfully."})


@app.route("/api/register/client", methods=["POST"])
def legacy_project_request():
    return create_project_request()


@app.route("/api/contact", methods=["POST"])
def create_contact_message():
    form = request.form.to_dict()
    payload = {
        "name": form.get("name") or "",
        "email": form.get("email") or "",
        "message": form.get("message") or "",
        "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    contacts = read_contacts()
    contacts.append(payload)
    write_contacts(contacts)
    return jsonify({"status": "success", "message": "Message sent successfully."})


@app.route("/api/profile", methods=["GET"])
@api_auth_required("master", "domain", "freelancer")
def get_profile():
    return jsonify(public_user(current_user()))


@app.route("/api/profile", methods=["POST"])
@api_auth_required("master", "domain", "freelancer")
def update_profile():
    payload = request.get_json(silent=True) or {}
    users = read_users()
    email = session.get("user_email")
    editable_fields = {
        "full_name",
        "title",
        "phone",
        "location",
        "bio",
        "experience",
        "portfolio",
        "availability",
    }
    social_fields = {"linkedin", "website", "github", "behance"}

    updated_user = None
    for user in users:
        if user.get("email") != email:
            continue
        for field in editable_fields:
            if field in payload:
                user[field] = payload[field]
        if "skills" in payload:
            user["skills"] = split_csv(payload["skills"])
        user.setdefault("socials", {})
        for field in social_fields:
            if field in payload:
                user["socials"][field] = payload[field]
        updated_user = user
        break

    if not updated_user:
        return jsonify({"status": "error", "message": "User not found."}), 404

    write_users(users)
    return jsonify({"status": "success", "message": "Profile updated.", "user": public_user(updated_user)})


@app.route("/api/applications", methods=["POST"])
@api_auth_required("freelancer")
def apply_for_project():
    payload = request.get_json(silent=True) or {}
    project_slug = payload.get("project_slug")
    if not project_slug:
        return jsonify({"status": "error", "message": "Project slug is required."}), 400

    user = current_user()
    registrations = read_registrations()
    existing = next(
        (
            item
            for item in registrations.get("applications", [])
            if item.get("project_slug") == project_slug and item.get("user_email") == user.get("email")
        ),
        None,
    )
    if existing:
        return jsonify({"status": "error", "message": "You already applied for this opportunity."}), 400

    application = {
        "id": str(uuid.uuid4()),
        "project_slug": project_slug,
        "project_title": payload.get("project_title") or "Opportunity",
        "user_email": user.get("email"),
        "user_name": user.get("full_name"),
        "status": "Under review",
        "note": payload.get("note") or "",
        "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    registrations["applications"].append(application)
    write_registrations(registrations)
    return jsonify({"status": "success", "message": "Application submitted successfully."})


@app.route("/api/admin/users/approve", methods=["POST"])
@api_auth_required("master")
def approve_user():
    payload = request.get_json(silent=True) or {}
    email = payload.get("email")
    approved = bool(payload.get("approved"))

    users = read_users()
    updated_user = None
    for user in users:
        if user.get("email") == email:
            user["approved"] = approved
            updated_user = user
            break

    if not updated_user:
        return jsonify({"status": "error", "message": "User not found."}), 404

    registrations = read_registrations()
    for freelancer in registrations.get("freelancers", []):
        if freelancer.get("email") == email:
            freelancer["approved"] = approved
    write_users(users)
    write_registrations(registrations)
    return jsonify({"status": "success", "message": "Approval updated."})


@app.route("/api/admin/settings", methods=["POST"])
@api_auth_required("master")
def update_settings():
    payload = request.get_json(silent=True) or {}
    content = read_content()

    content.setdefault("brand", {})
    content.setdefault("hero", {})
    content.setdefault("theme", {})
    content.setdefault("contact", {})

    mappings = {
        ("brand", "name"): payload.get("brand_name"),
        ("brand", "tagline"): payload.get("brand_tagline"),
        ("hero", "title"): payload.get("hero_title"),
        ("hero", "subtitle"): payload.get("hero_subtitle"),
        ("hero", "visual_url"): payload.get("visual_url"),
        ("theme", "accent"): payload.get("accent"),
        ("theme", "accent_secondary"): payload.get("accent_secondary"),
        ("contact", "email"): payload.get("contact_email"),
        ("contact", "phone"): payload.get("contact_phone"),
        ("contact", "location"): payload.get("contact_location"),
    }

    for (section, key), value in mappings.items():
        if value is not None and str(value).strip():
            content[section][key] = value.strip()

    write_content(content)
    return jsonify({"status": "success", "message": "Website settings updated."})


@app.route("/api/contacts", methods=["GET"])
@api_auth_required("master")
def get_contacts():
    return jsonify(read_contacts())


@app.route("/api/registrations", methods=["GET"])
@api_auth_required("master")
def get_registrations():
    registrations = read_registrations()
    reg_type = request.args.get("type")
    if reg_type == "freelancers":
        return jsonify(registrations.get("freelancers", []))
    if reg_type in {"clients", "project_requests"}:
        return jsonify(registrations.get("project_requests", []))
    if reg_type == "applications":
        return jsonify(registrations.get("applications", []))
    return jsonify(registrations)


if __name__ == "__main__":
    app.run(debug=True)
