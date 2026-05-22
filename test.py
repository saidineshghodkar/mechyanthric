from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# ---------- JSON DATA FILES ----------
CONTENT_FILE = 'content.json'
REGISTRATIONS_FILE = 'registrations.json'
CONTACTS_FILE = 'contacts.json'          # new file for contact messages

def init_files():
    if not os.path.exists(CONTENT_FILE):
        default_content = {
            "hero": {
                "title": "Build with Precision, Craft with Passion",
                "subtitle": "Multi-Engineering & Creative Freelance Hub — Hire top talent or find work."
            },
            "about": {
                "image": "https://images.unsplash.com/photo-1581091226033-d5c48150dbaa?w=600",
                "text": "MEC WORKS connects top engineering and creative freelancers with clients. We vet every professional to ensure quality and timely delivery. From code to construction, we've got you covered. Our platform simplifies hiring and project management for both parties."
            },
            "contact": {
                "email": "hello@mecworks.in",
                "phone": "+91 98765 43210",
                "location": "Bangalore, India",
                "map_url": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3887.977289580237!2d77.594562314822!3d12.971598790844!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3bae1673e7d0672f%3A0xc62d6a7c2cfd3c6!2sBangalore%2C%20Karnataka!5e0!3m2!1sen!2sin!4v1645432167890!5m2!1sen!2sin"
            },
            "projects": [
                {
                    "image": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400",
                    "title": "Students Career Prediction",
                    "description": "AI-powered platform to guide students towards optimal career paths based on skills and interests.",
                    "date": "15 Mar 2026"
                },
                {
                    "image": "https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=400",
                    "title": "E-commerce Website",
                    "description": "Full‑featured online store with secure payments and inventory management for local artisans.",
                    "date": "10 Mar 2026"
                },
                {
                    "image": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400",
                    "title": "Labour's Adda",
                    "description": "Mobile app connecting skilled labour with construction and industrial projects.",
                    "date": "05 Mar 2026"
                },
                {
                    "image": "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=400",
                    "title": "Corporate Website",
                    "description": "Modern, responsive website for a leading engineering consultancy.",
                    "date": "28 Feb 2026"
                },
                {
                    "image": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=400",
                    "title": "Interior Projects",
                    "description": "Complete interior design and execution for a luxury apartment complex.",
                    "date": "20 Feb 2026"
                }
            ]
        }
        with open(CONTENT_FILE, 'w') as f:
            json.dump(default_content, f, indent=2)

    if not os.path.exists(REGISTRATIONS_FILE):
        with open(REGISTRATIONS_FILE, 'w') as f:
            json.dump({"clients": [], "freelancers": []}, f, indent=2)

    if not os.path.exists(CONTACTS_FILE):          # initialize contacts file
        with open(CONTACTS_FILE, 'w') as f:
            json.dump([], f, indent=2)

init_files()

# ---------- HELPER FUNCTIONS ----------
def read_content():
    with open(CONTENT_FILE, 'r') as f:
        return json.load(f)

def write_content(data):
    with open(CONTENT_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def read_registrations():
    with open(REGISTRATIONS_FILE, 'r') as f:
        return json.load(f)

def write_registrations(data):
    with open(REGISTRATIONS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def read_contacts():                               # new helper
    with open(CONTACTS_FILE, 'r') as f:
        return json.load(f)

def write_contacts(data):
    with open(CONTACTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# ---------- ROUTES ----------
@app.route('/')
def index():
    content = read_content()
    return render_template_string(HTML_INDEX, content=content)

@app.route('/register/client')
def register_client():
    return render_template_string(HTML_REGISTER_CLIENT)

@app.route('/register/freelancer')
def register_freelancer():
    return render_template_string(HTML_REGISTER_FREELANCER)

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('index'))
    content = read_content()
    return render_template_string(HTML_ADMIN, content=content)

# ---------- API ENDPOINTS ----------
@app.route('/api/content', methods=['GET'])
def get_content():
    return jsonify(read_content())

@app.route('/api/content', methods=['POST'])
@login_required
def update_content():
    data = request.json
    write_content(data)
    return jsonify({"status": "success"})

@app.route('/api/register/client', methods=['POST'])
def register_client_post():
    data = request.form.to_dict()
    data['approved'] = False
    reg = read_registrations()
    reg['clients'].append(data)
    write_registrations(reg)
    return jsonify({"status": "success", "message": "Client registration received"})

@app.route('/api/register/freelancer', methods=['POST'])
def register_freelancer_post():
    data = request.form.to_dict()
    data['approved'] = False
    reg = read_registrations()
    reg['freelancers'].append(data)
    write_registrations(reg)
    return jsonify({"status": "success", "message": "Freelancer registration received"})

@app.route('/api/registrations', methods=['GET'])
@login_required
def get_registrations():
    type = request.args.get('type')
    reg = read_registrations()
    if type == 'clients':
        return jsonify(reg['clients'])
    elif type == 'freelancers':
        return jsonify(reg['freelancers'])
    return jsonify([])

@app.route('/api/registrations/delete', methods=['POST'])
@login_required
def delete_registration():
    data = request.json
    type = data.get('type')
    index = data.get('index')
    reg = read_registrations()
    if type == 'client' and 0 <= index < len(reg['clients']):
        del reg['clients'][index]
        write_registrations(reg)
        return jsonify({"status": "success"})
    elif type == 'freelancer' and 0 <= index < len(reg['freelancers']):
        del reg['freelancers'][index]
        write_registrations(reg)
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid index or type"}), 400

@app.route('/api/registrations/approve', methods=['POST'])
@login_required
def approve_registration():
    data = request.json
    type = data.get('type')
    index = data.get('index')
    reg = read_registrations()
    if type == 'client' and 0 <= index < len(reg['clients']):
        reg['clients'][index]['approved'] = not reg['clients'][index].get('approved', False)
        write_registrations(reg)
        return jsonify({"status": "success", "approved": reg['clients'][index]['approved']})
    elif type == 'freelancer' and 0 <= index < len(reg['freelancers']):
        reg['freelancers'][index]['approved'] = not reg['freelancers'][index].get('approved', False)
        write_registrations(reg)
        return jsonify({"status": "success", "approved": reg['freelancers'][index]['approved']})
    return jsonify({"status": "error", "message": "Invalid index or type"}), 400

# ---------- NEW CONTACT API ----------
@app.route('/api/contact', methods=['POST'])
def contact_post():
    data = request.form.to_dict()
    data['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    contacts = read_contacts()
    contacts.append(data)
    write_contacts(contacts)
    return jsonify({"status": "success", "message": "Message sent successfully!"})

@app.route('/api/contacts', methods=['GET'])
@login_required
def get_contacts():
    return jsonify(read_contacts())

@app.route('/api/contacts/delete', methods=['POST'])
@login_required
def delete_contact():
    data = request.json
    index = data.get('index')
    contacts = read_contacts()
    if 0 <= index < len(contacts):
        del contacts[index]
        write_contacts(contacts)
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid index"}), 400

@app.route('/api/login', methods=['POST'])
def login():
    creds = request.json
    if creds.get('username') == 'sai' and creds.get('password') == 'pass':
        session['admin_logged_in'] = True
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('admin_logged_in', None)
    return jsonify({"status": "success"})

# ---------- EMBEDDED HTML TEMPLATES ----------
HTML_INDEX = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MEC WORKS · Multi Engineering Craft · labours adda</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root { --gold: #C8993E; --dark: #0A0A0A; --glass: rgba(255, 255, 255, 0.03); }
        body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: var(--dark); color: #E2E8F0; overflow-x: hidden; }
        .text-gold { color: var(--gold); } .bg-gold { background-color: var(--gold); } .border-gold { border-color: var(--gold); }
        .glass { background: var(--glass); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
        .hero-gradient { background: linear-gradient(135deg, #FFFFFF 0%, var(--gold) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .animate-rotate { animation: rotate 20s linear infinite; }
        .carousel { transition: transform 0.5s ease; }
        .carousel-item { flex: 0 0 100%; }
        @media (min-width: 768px) { .carousel-item { flex: 0 0 33.333%; } }
        .service-card:hover { transform: translateY(-10px); border-color: var(--gold); box-shadow: 0 10px 30px -10px rgba(200, 153, 62, 0.3); }
        .hover-svg svg { transition: transform 0.4s ease; }
        .service-card:hover .hover-svg svg { transform: rotate(30deg) scale(1.1); fill: var(--gold); stroke: var(--gold); }
        .floating-shape { animation: float 6s ease-in-out infinite; }
        @keyframes float { 0% { transform: translateY(0px); } 50% { transform: translateY(-15px); } 100% { transform: translateY(0px); } }
        .fade-up { animation: fadeUp 0.8s ease-out; }
        @keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        .social-icon { transition: all 0.2s; }
        .social-icon:hover { transform: scale(1.2); filter: brightness(1.2); }
        .fab-chat {
            position: fixed; bottom: 30px; right: 30px; background-color: var(--gold); color: black;
            width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3); z-index: 100; transition: transform 0.3s; cursor: pointer;
        }
        .fab-chat:hover { transform: scale(1.1); background-color: white; }
        .chat-popup {
            position: fixed; bottom: 100px; right: 30px; width: 320px; background: #111; border: 1px solid #333;
            border-radius: 24px; z-index: 101; box-shadow: 0 20px 40px rgba(0,0,0,0.6); display: none;
        }
        .chat-popup.show { display: block; }
    </style>
</head>
<body class="bg-[#0A0A0A]">

<!-- Navigation -->
<nav id="navbar" class="fixed w-full z-50 transition-all duration-500 py-6">
    <div class="max-w-7xl mx-auto px-6 flex justify-between items-center">
        <a href="/" class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-gold rounded flex items-center justify-center shadow-[0_0_15px_rgba(200,153,62,0.4)]">
                <svg class="w-6 h-6 text-black" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
                </svg>
            </div>
            <div class="flex flex-col">
                <span class="text-xl font-extrabold tracking-tighter text-white">MEC<span class="text-gold">WORKS</span></span>
                <span class="text-[0.6rem] uppercase tracking-[0.3em] text-gray-500 font-bold">Multi Engineering</span>
            </div>
        </a>
        <div class="hidden md:flex space-x-10">
            <a href="#home" class="text-xs uppercase tracking-widest font-bold hover:text-gold">Home</a>
            <a href="#about" class="text-xs uppercase tracking-widest font-bold hover:text-gold">About</a>
            <a href="#services" class="text-xs uppercase tracking-widest font-bold hover:text-gold">Crafts</a>
            <a href="#non-engineering" class="text-xs uppercase tracking-widest font-bold hover:text-gold">Non-ENG</a>
            <a href="#news" class="text-xs uppercase tracking-widest font-bold hover:text-gold">News</a>
            <a href="#contact" class="text-xs uppercase tracking-widest font-bold hover:text-gold">Contact</a>
        </div>
        <div class="flex items-center space-x-4">
            <a href="/register/client" class="border border-gold text-gold px-4 py-2 rounded-full text-xs font-bold uppercase hover:bg-gold hover:text-black">Client</a>
            <a href="/register/freelancer" class="bg-gold text-black px-4 py-2 rounded-full text-xs font-bold uppercase hover:bg-white">Freelancer</a>
            <button id="adminLoginBtn" class="text-gray-400 hover:text-gold text-sm">Admin</button>
        </div>
    </div>
</nav>

<!-- Hero with animated background -->
<section id="home" class="relative min-h-screen flex items-center pt-20 overflow-hidden">
    <!-- Animated rotating gears -->
    <div class="absolute inset-0 opacity-10 pointer-events-none">
        <div class="absolute top-20 left-20 animate-rotate">
            <svg width="200" height="200" viewBox="0 0 100 100" fill="white"><circle cx="50" cy="50" r="40" stroke="white" stroke-width="2" fill="none"/><circle cx="50" cy="50" r="10" fill="white"/><line x1="50" y1="10" x2="50" y2="30" stroke="white" stroke-width="2"/><line x1="50" y1="70" x2="50" y2="90" stroke="white"/><line x1="10" y1="50" x2="30" y2="50" stroke="white"/><line x1="70" y1="50" x2="90" y2="50" stroke="white"/></svg>
        </div>
        <div class="absolute bottom-20 right-20 animate-rotate" style="animation-duration: 30s;">
            <svg width="200" height="200" viewBox="0 0 100 100" fill="white"><circle cx="50" cy="50" r="40" stroke="white" stroke-width="2" fill="none"/><circle cx="50" cy="50" r="10" fill="white"/><line x1="50" y1="10" x2="50" y2="30" stroke="white" stroke-width="2"/><line x1="50" y1="70" x2="50" y2="90" stroke="white"/><line x1="10" y1="50" x2="30" y2="50" stroke="white"/><line x1="70" y1="50" x2="90" y2="50" stroke="white"/></svg>
        </div>
    </div>
    <div class="max-w-7xl mx-auto px-6 relative z-10 fade-up">
        <div class="max-w-3xl">
            <span class="text-gold text-sm font-bold uppercase tracking-[0.3em]">Engineering · Creativity · Labour</span>
            <h1 id="hero-title" class="text-5xl md:text-7xl font-black mt-6 leading-[1.1]">{{ content.hero.title }}</h1>
            <p id="hero-subtitle" class="text-xl text-gray-400 mt-6 max-w-xl">{{ content.hero.subtitle }}</p>
            <div class="flex gap-4 mt-10">
                <a href="#services" class="bg-gold text-black px-8 py-4 rounded-full font-bold text-sm uppercase tracking-widest">Explore Crafts</a>
                <a href="#contact" class="border border-gold text-gold px-8 py-4 rounded-full font-bold text-sm uppercase tracking-widest hover:bg-gold hover:text-black">Hire Now</a>
            </div>
        </div>
    </div>
</section>

<!-- About Section (with image) -->
<section id="about" class="py-32 bg-[#0d0d0d]">
    <div class="max-w-7xl mx-auto px-6">
        <div class="grid md:grid-cols-2 gap-12 items-center">
            <div class="fade-up">
                <h2 class="text-gold text-sm font-bold uppercase tracking-[0.4em] mb-4">Our Story</h2>
                <h3 class="text-4xl md:text-5xl font-black mb-8">Where <span class="text-gray-500">engineering</span> meets creativity</h3>
                <p id="about-text" class="text-gray-400 text-lg leading-relaxed">{{ content.about.text }}</p>
            </div>
            <div class="glass p-4 rounded-3xl fade-up" style="animation-delay:0.2s">
                <img src="{{ content.about.image }}" alt="About us" class="rounded-2xl w-full h-auto">
            </div>
        </div>
    </div>
</section>

<!-- Services / Crafts (unchanged) -->
<section id="services" class="py-32 bg-[#0d0d0d]">
    <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-20">
            <h2 class="text-gold text-sm font-bold uppercase tracking-[0.4em] mb-4">The Four Pillars</h2>
            <h3 class="text-4xl md:text-5xl font-black">Our Multi-Engineering <span class="text-gray-500">Crafts.</span></h3>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <!-- CSE -->
            <div class="service-card glass p-8 rounded-3xl group fade-up">
                <div class="hover-svg w-14 h-14 bg-blue-500/10 text-blue-400 rounded-2xl flex items-center justify-center mb-8 floating-shape">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
                </div>
                <h4 class="text-2xl font-bold mb-4">IT & Software</h4>
                <p class="text-gray-500 text-sm leading-relaxed mb-6">AI, Web, cloud, cyber security.</p>
                <ul class="text-xs text-gray-400 space-y-2"><li>• AI & ML</li><li>• Full-stack</li><li>• Cybersecurity</li></ul>
            </div>
            <!-- ECE -->
            <div class="service-card glass p-8 rounded-3xl group fade-up" style="animation-delay:0.1s">
                <div class="hover-svg w-14 h-14 bg-purple-500/10 text-purple-400 rounded-2xl flex items-center justify-center mb-8 floating-shape" style="animation-delay:0.5s">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor"><rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/></svg>
                </div>
                <h4 class="text-2xl font-bold mb-4">Electronics</h4>
                <p class="text-gray-500 text-sm leading-relaxed mb-6">IoT, embedded, PCB, signal.</p>
                <ul class="text-xs text-gray-400"><li>• Embedded</li><li>• IoT</li><li>• VLSI</li></ul>
            </div>
            <!-- MECH -->
            <div class="service-card glass p-8 rounded-3xl group fade-up" style="animation-delay:0.2s">
                <div class="hover-svg w-14 h-14 bg-orange-500/10 text-orange-400 rounded-2xl flex items-center justify-center mb-8 floating-shape" style="animation-delay:1s">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>
                </div>
                <h4 class="text-2xl font-bold mb-4">Mechanical & Robotics</h4>
                <p class="text-gray-500 text-sm leading-relaxed mb-6">CAD, automation, prototyping.</p>
                <ul class="text-xs text-gray-400"><li>• CAD/CAM</li><li>• Robotics</li><li>• 3D printing</li></ul>
            </div>
            <!-- CIVIL -->
            <div class="service-card glass p-8 rounded-3xl group fade-up" style="animation-delay:0.3s">
                <div class="hover-svg w-14 h-14 bg-green-500/10 text-green-400 rounded-2xl flex items-center justify-center mb-8 floating-shape" style="animation-delay:1.5s">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor"><rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4"/></svg>
                </div>
                <h4 class="text-2xl font-bold mb-4">Construction & Interiors</h4>
                <p class="text-gray-500 text-sm leading-relaxed mb-6">Smart architecture, project mgmt.</p>
                <ul class="text-xs text-gray-400"><li>• BIM</li><li>• Structural</li><li>• Interior</li></ul>
            </div>
        </div>
    </div>
</section>

<!-- Non-Engineering Crafts (Detailed) -->
<section id="non-engineering" class="py-32 bg-black/50">
    <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-20">
            <h2 class="text-gold text-sm font-bold uppercase tracking-[0.4em] mb-4">CREATIVE HUB</h2>
            <h3 class="text-4xl md:text-5xl font-black">Non‑Engineering <span class="text-gray-500">Crafts.</span></h3>
            <p class="text-gray-400 mt-4">Art, media & digital experiences</p>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <!-- PROMOTIONS AND DIGITAL MARKETING -->
            <div class="service-card glass p-6 rounded-3xl group fade-up">
                <div class="hover-svg w-12 h-12 bg-pink-500/10 text-pink-400 rounded-2xl flex items-center justify-center mb-4 floating-shape">
                    <svg width="24" height="24" fill="none" stroke="currentColor"><path d="M4 7h16M4 12h16M4 17h10"/></svg>
                </div>
                <h4 class="text-xl font-bold">Promotions & Digital Marketing</h4>
                <p class="text-xs text-gray-400 mt-2">Strategic social media campaigns to boost brand visibility.</p>
                <ul class="text-xs text-gray-400 mt-4 space-y-1"><li>• Instagram Marketing</li><li>• Facebook Advertising</li><li>• TikTok Content Creation</li></ul>
            </div>
            <!-- CONTENT CREATIONS -->
            <div class="service-card glass p-6 rounded-3xl group fade-up" style="animation-delay:0.1s">
                <div class="hover-svg w-12 h-12 bg-yellow-500/10 text-yellow-400 rounded-2xl flex items-center justify-center mb-4 floating-shape" style="animation-delay:0.2s">
                    <svg width="24" height="24" fill="none" stroke="currentColor"><path d="M12 5v14M5 12h14"/></svg>
                </div>
                <h4 class="text-xl font-bold">Content Creations</h4>
                <p class="text-xs text-gray-400 mt-2">Professional content creation for digital media.</p>
                <ul class="text-xs text-gray-400 mt-4 space-y-1"><li>• Video Editing</li><li>• Graphic Design</li><li>• Copywriting</li></ul>
            </div>
            <!-- PHOTOGRAPHY & VIDEO EDITING -->
            <div class="service-card glass p-6 rounded-3xl group fade-up" style="animation-delay:0.2s">
                <div class="hover-svg w-12 h-12 bg-blue-500/10 text-blue-400 rounded-2xl flex items-center justify-center mb-4 floating-shape" style="animation-delay:0.4s">
                    <svg width="24" height="24" fill="none" stroke="currentColor"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
                </div>
                <h4 class="text-xl font-bold">Photography & Video Editing</h4>
                <p class="text-xs text-gray-400 mt-2">Professional photography and video editing.</p>
                <ul class="text-xs text-gray-400 mt-4 space-y-1"><li>• Video Editing</li><li>• Graphic Design</li><li>• Copywriting</li></ul>
            </div>
            <!-- THUMANIAL CREATIONS -->
            <div class="service-card glass p-6 rounded-3xl group fade-up" style="animation-delay:0.3s">
                <div class="hover-svg w-12 h-12 bg-purple-500/10 text-purple-400 rounded-2xl flex items-center justify-center mb-4 floating-shape" style="animation-delay:0.6s">
                    <svg width="24" height="24" fill="none" stroke="currentColor"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                </div>
                <h4 class="text-xl font-bold">Thumanial Creations</h4>
                <p class="text-xs text-gray-400 mt-2">Human‑centered design for unique experiences.</p>
                <ul class="text-xs text-gray-400 mt-4 space-y-1"><li>• UI/UX Design</li><li>• Brand Identity</li><li>• User Research</li></ul>
            </div>
            <!-- ART WORKS -->
            <div class="service-card glass p-6 rounded-3xl group fade-up" style="animation-delay:0.4s">
                <div class="hover-svg w-12 h-12 bg-red-500/10 text-red-400 rounded-2xl flex items-center justify-center mb-4 floating-shape" style="animation-delay:0.8s">
                    <svg width="24" height="24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="10"/><path d="M12 2v20M2 12h20"/></svg>
                </div>
                <h4 class="text-xl font-bold">Art Works</h4>
                <p class="text-xs text-gray-400 mt-2">Creative and artistic services.</p>
                <ul class="text-xs text-gray-400 mt-4 space-y-1"><li>• Digital Art</li><li>• Illustration</li><li>• Graphic Design</li></ul>
            </div>
            <!-- LOGO DESIGN -->
            <div class="service-card glass p-6 rounded-3xl group fade-up" style="animation-delay:0.5s">
                <div class="hover-svg w-12 h-12 bg-indigo-500/10 text-indigo-400 rounded-2xl flex items-center justify-center mb-4 floating-shape" style="animation-delay:1s">
                    <svg width="24" height="24" fill="none" stroke="currentColor"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
                </div>
                <h4 class="text-xl font-bold">Logo Design</h4>
                <p class="text-xs text-gray-400 mt-2">Professional logo design for businesses.</p>
                <ul class="text-xs text-gray-400 mt-4 space-y-1"><li>• Brand Identity</li><li>• Logo Creation</li><li>• Visual Identity</li></ul>
            </div>
            <!-- GRAPHIC DESIGN & ANIMATIONS -->
            <div class="service-card glass p-6 rounded-3xl group fade-up" style="animation-delay:0.6s">
                <div class="hover-svg w-12 h-12 bg-teal-500/10 text-teal-400 rounded-2xl flex items-center justify-center mb-4 floating-shape" style="animation-delay:1.2s">
                    <svg width="24" height="24" fill="none" stroke="currentColor"><rect x="2" y="2" width="20" height="20" rx="2.18"/><path d="M7 2v20M17 2v20M2 12h20M2 7h5M2 17h5M17 17h5M17 7h5"/></svg>
                </div>
                <h4 class="text-xl font-bold">Graphic Design & Animations</h4>
                <p class="text-xs text-gray-400 mt-2">Creative graphic design and animation.</p>
                <ul class="text-xs text-gray-400 mt-4 space-y-1"><li>• Graphic Design</li><li>• Animation</li><li>• Visual Effects</li></ul>
            </div>
            <!-- labours adda promo (extra) -->
            <div class="service-card glass p-6 rounded-3xl border-gold/30 flex flex-col items-center justify-center group fade-up" style="animation-delay:0.7s">
                <span class="text-gold text-3xl mb-2">🛠️</span>
                <h4 class="text-xl font-bold">labours adda</h4>
                <p class="text-xs text-center text-gray-400">Skilled labour app • coming soon</p>
                <div class="mt-2 text-[0.6rem] bg-gold/20 px-3 py-1 rounded-full">Android/iOS</div>
            </div>
        </div>
    </div>
</section>

<!-- Projects Carousel (formerly News) -->
<section id="news" class="py-32 bg-[#0d0d0d]">
    <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-16">
            <h2 class="text-gold text-sm font-bold uppercase tracking-[0.4em] mb-4">WHAT'S NEW</h2>
            <h3 class="text-4xl md:text-5xl font-black">Recent <span class="text-gray-500">News & Updates</span></h3>
        </div>
        <div class="relative overflow-hidden">
            <div id="carousel" class="flex transition-transform duration-500 ease-in-out">
                {% for item in content.projects %}
                <div class="carousel-item flex-shrink-0 w-full md:w-1/3 px-3">
                    <div class="glass p-4 rounded-2xl h-full flex flex-col">
                        <img src="{{ item.image }}" alt="{{ item.title }}" class="w-full h-40 object-cover rounded-xl mb-4">
                        <h4 class="text-xl font-bold text-gold">{{ item.title }}</h4>
                        <p class="text-gray-400 mt-2 flex-grow">{{ item.description }}</p>
                        <span class="text-xs text-gray-500 mt-4 block">{{ item.date }}</span>
                    </div>
                </div>
                {% endfor %}
            </div>
            <!-- Manual navigation arrows -->
            <button id="prevBtn" class="absolute left-0 top-1/2 transform -translate-y-1/2 bg-gold/80 hover:bg-gold text-black w-10 h-10 rounded-full flex items-center justify-center text-2xl z-10">❮</button>
            <button id="nextBtn" class="absolute right-0 top-1/2 transform -translate-y-1/2 bg-gold/80 hover:bg-gold text-black w-10 h-10 rounded-full flex items-center justify-center text-2xl z-10">❯</button>
        </div>
        <!-- Dots indicator -->
        <div id="dots" class="flex justify-center mt-6 space-x-2">
            {% for item in content.projects %}
            <button class="dot w-3 h-3 rounded-full bg-gray-500 hover:bg-gold transition-colors" data-index="{{ loop.index0 }}"></button>
            {% endfor %}
        </div>
    </div>
</section>

<!-- Contact Section with Google Maps -->
<section id="contact" class="py-32 bg-black/50">
    <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-16">
            <h2 class="text-gold text-sm font-bold uppercase tracking-[0.4em] mb-4">Get in touch</h2>
            <h3 class="text-4xl md:text-5xl font-black">Contact <span class="text-gray-500">Us</span></h3>
        </div>
        <div class="grid md:grid-cols-2 gap-12">
            <div class="glass p-8 rounded-3xl fade-up">
                <h4 class="text-2xl font-bold mb-6">Send a message</h4>
                <form id="contactForm">
                    <input type="text" name="name" placeholder="Your Name" required class="w-full bg-white/5 border border-white/10 rounded-xl px-5 py-4 mb-4">
                    <input type="email" name="email" placeholder="Email Address" required class="w-full bg-white/5 border border-white/10 rounded-xl px-5 py-4 mb-4">
                    <textarea name="message" rows="4" placeholder="Your Message" required class="w-full bg-white/5 border border-white/10 rounded-xl px-5 py-4 mb-4"></textarea>
                    <button type="submit" class="bg-gold text-black font-bold py-4 px-8 rounded-xl">Send Message</button>
                </form>
                <div id="contactSuccess" class="hidden mt-4 text-green-500 text-sm">Message sent successfully!</div>
            </div>
            <div class="space-y-6 fade-up" style="animation-delay:0.2s">
                <div class="flex items-center space-x-4"><span class="text-gold text-xl">📧</span><span id="contact-email">{{ content.contact.email }}</span></div>
                <div class="flex items-center space-x-4"><span class="text-gold text-xl">📞</span><span id="contact-phone">{{ content.contact.phone }}</span></div>
                <div class="flex items-center space-x-4"><span class="text-gold text-xl">📍</span><span id="contact-location">{{ content.contact.location }}</span></div>
                <!-- Google Maps Embed -->
                <div class="mt-6 rounded-2xl overflow-hidden h-64">
                    <iframe src="{{ content.contact.map_url }}" width="100%" height="100%" style="border:0;" allowfullscreen="" loading="lazy"></iframe>
                </div>
            </div>
        </div>
    </div>
</section>

<!-- Footer with Quick Links & Social Icons -->
<footer class="py-16 border-t border-white/5 bg-[#0d0d0d]">
    <div class="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-4 gap-8">
        <div>
            <div class="flex items-center space-x-2 mb-4">
                <div class="w-8 h-8 bg-gold rounded flex items-center justify-center">
                    <svg class="w-5 h-5 text-black" viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
                </div>
                <span class="text-lg font-black tracking-widest text-white">MEC WORKS</span>
            </div>
            <p class="text-gray-500 text-sm">Multi Engineering Craft & Creative Hub</p>
        </div>
        <div>
            <h5 class="font-bold text-gold mb-4">Quick Links</h5>
            <ul class="space-y-2 text-sm">
                <li><a href="#home" class="text-gray-400 hover:text-gold">Home</a></li>
                <li><a href="#about" class="text-gray-400 hover:text-gold">About</a></li>
                <li><a href="#services" class="text-gray-400 hover:text-gold">Crafts</a></li>
                <li><a href="#non-engineering" class="text-gray-400 hover:text-gold">Non-ENG</a></li>
                <li><a href="#news" class="text-gray-400 hover:text-gold">News</a></li>
                <li><a href="#contact" class="text-gray-400 hover:text-gold">Contact</a></li>
            </ul>
        </div>
        <div>
            <h5 class="font-bold text-gold mb-4">Legal</h5>
            <ul class="space-y-2 text-sm">
                <li><a href="#" class="text-gray-400 hover:text-gold">Terms of Service</a></li>
                <li><a href="#" class="text-gray-400 hover:text-gold">Privacy Policy</a></li>
                <li><a href="#" class="text-gray-400 hover:text-gold">Cookie Policy</a></li>
            </ul>
        </div>
        <div>
            <h5 class="font-bold text-gold mb-4">Follow Us</h5>
            <div class="flex space-x-4">
                <a href="#" class="social-icon"><svg class="w-6 h-6 text-gray-400 hover:text-gold" fill="currentColor" viewBox="0 0 24 24"><path d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.879v-6.99h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.99C18.343 21.128 22 16.991 22 12z"/></svg></a>
                <a href="#" class="social-icon"><svg class="w-6 h-6 text-gray-400 hover:text-gold" fill="currentColor" viewBox="0 0 24 24"><path d="M12.315 2c2.43 0 2.784.013 3.808.06 1.064.049 1.791.218 2.427.465.69.267 1.302.637 1.868 1.156.586.519 1.043 1.152 1.394 1.865.311.663.512 1.357.581 2.19.042.873.06 1.252.06 3.291v.306c0 2.04-.018 2.418-.06 3.291-.07.833-.27 1.527-.58 2.19-.35.713-.808 1.346-1.394 1.865-.566.52-1.179.89-1.868 1.156-.636.247-1.363.416-2.427.465-1.024.047-1.379.06-3.808.06-2.43 0-2.784-.013-3.808-.06-1.064-.049-1.791-.218-2.427-.465a5.226 5.226 0 0 1-1.868-1.156 5.413 5.413 0 0 1-1.394-1.865c-.311-.663-.512-1.357-.581-2.19-.042-.873-.06-1.252-.06-3.291v-.306c0-2.04.018-2.418.06-3.291.07-.833.27-1.527.58-2.19.35-.713.808-1.346 1.394-1.865.566-.52 1.179-.89 1.868-1.156.636-.247 1.363-.416 2.427-.465 1.024-.047 1.379-.06 3.808-.06zM12 6.865a5.135 5.135 0 1 0 0 10.27 5.135 5.135 0 0 0 0-10.27zm0 1.73a3.405 3.405 0 1 1 0 6.81 3.405 3.405 0 0 1 0-6.81zm5.338-3.63a1.2 1.2 0 1 0 2.4 0 1.2 1.2 0 0 0-2.4 0z"/></svg></a>
                <a href="#" class="social-icon"><svg class="w-6 h-6 text-gray-400 hover:text-gold" fill="currentColor" viewBox="0 0 24 24"><path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0 0 22 5.92a8.19 8.19 0 0 1-2.357.646 4.118 4.118 0 0 0 1.804-2.27 8.224 8.224 0 0 1-2.605.996 4.107 4.107 0 0 0-6.993 3.743 11.65 11.65 0 0 1-8.457-4.287 4.106 4.106 0 0 0 1.27 5.477A4.072 4.072 0 0 1 2.8 9.713v.052a4.105 4.105 0 0 0 3.292 4.022 4.095 4.095 0 0 1-1.853.07 4.108 4.108 0 0 0 3.834 2.85A8.233 8.233 0 0 1 2 18.407a11.616 11.616 0 0 0 6.29 1.84"/></svg></a>
                <a href="#" class="social-icon"><svg class="w-6 h-6 text-gray-400 hover:text-gold" fill="currentColor" viewBox="0 0 24 24"><path d="M20 3H4a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h16a1 1 0 0 0 1-1V4a1 1 0 0 0-1-1zM8.339 18.337H5.667v-8.59h2.672v8.59zM7.003 8.574a1.548 1.548 0 1 1 0-3.096 1.548 1.548 0 0 1 0 3.096zm11.335 9.763h-2.669V14.16c0-.996-.018-2.277-1.388-2.277-1.39 0-1.601 1.086-1.601 2.207v4.248h-2.667v-8.59h2.56v1.174h.037c.356-.675 1.227-1.387 2.524-1.387 2.698 0 3.196 1.778 3.196 4.09v4.713z"/></svg></a>
                <a href="#" class="social-icon"><svg class="w-6 h-6 text-gray-400 hover:text-gold" fill="currentColor" viewBox="0 0 24 24"><path d="M23.498 6.186a2.996 2.996 0 0 0-2.11-2.11C19.528 3.5 12 3.5 12 3.5s-7.528 0-9.388.576a2.996 2.996 0 0 0-2.11 2.11C0 8.048 0 12 0 12s0 3.952.502 5.814a2.996 2.996 0 0 0 2.11 2.11c1.86.576 9.388.576 9.388.576s7.528 0 9.388-.576a2.996 2.996 0 0 0 2.11-2.11C24 15.952 24 12 24 12s0-3.952-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg></a>
            </div>
            <p class="text-gray-500 text-sm mt-4">© 2026 MEC WORKS. All rights reserved.</p>
        </div>
    </div>
</footer>

<!-- Floating Chatbot FAB -->
<div class="fab-chat" id="chatFab">
    <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
</div>
<div class="chat-popup glass" id="chatPopup">
    <div class="p-6 border-b border-white/10 flex justify-between items-center">
        <span class="font-bold text-gold">🤖 FAQ Assistant</span>
        <button id="closeChat" class="text-gray-400 hover:text-white">✕</button>
    </div>
    <div class="p-6 space-y-4 max-h-96 overflow-y-auto">
        <div class="glass p-3 rounded-2xl text-sm">❓ How do I register as freelancer? → Click 'Freelancer' button and fill the detailed form.</div>
        <div class="glass p-3 rounded-2xl text-sm">❓ What is labours adda? → Our app for skilled labour hiring (launching soon).</div>
        <div class="glass p-3 rounded-2xl text-sm">❓ Client agreement process? → After matching, digital agreement is generated.</div>
        <div class="glass p-3 rounded-2xl text-sm">❓ Non-engineering crafts? → Scroll to 'Non-ENG Crafts' section.</div>
        <div class="text-gold text-xs mt-4">*For detailed help, contact admin</div>
    </div>
</div>

<!-- Admin Login Modal -->
<div id="adminLoginModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm hidden items-center justify-center z-[200]">
    <div class="glass p-8 rounded-3xl max-w-md w-full">
        <h2 class="text-3xl font-black mb-6">🔐 ADMIN LOGIN</h2>
        <input type="text" id="adminUser" placeholder="Username" class="w-full bg-white/5 border border-white/10 rounded-xl px-5 py-4 mb-4">
        <input type="password" id="adminPass" placeholder="Password" class="w-full bg-white/5 border border-white/10 rounded-xl px-5 py-4 mb-6">
        <button id="loginSubmit" class="w-full bg-gold text-black font-bold py-4 rounded-xl">Login</button>
        <p class="text-xs text-gray-400 mt-4 text-center">default: sai / pass</p>
        <button id="closeAdminLogin" class="absolute top-5 right-5 text-gray-400 hover:text-white text-2xl">&times;</button>
    </div>
</div>

<script>
    // Projects Carousel with manual controls and auto-scroll
    const carousel = document.getElementById('carousel');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const dots = document.querySelectorAll('.dot');
    let currentIndex = 0;
    const totalItems = {{ content.projects|length }};

    function getStepPercent() {
        return window.innerWidth < 768 ? 100 : 33.333;
    }

    function updateCarousel(index) {
        if (index < 0) index = totalItems - 1;
        if (index >= totalItems) index = 0;
        const step = getStepPercent();
        carousel.style.transform = `translateX(-${index * step}%)`;
        dots.forEach((dot, i) => {
            dot.classList.toggle('bg-gold', i === index);
            dot.classList.toggle('bg-gray-500', i !== index);
        });
        currentIndex = index;
    }

    prevBtn.addEventListener('click', () => updateCarousel(currentIndex - 1));
    nextBtn.addEventListener('click', () => updateCarousel(currentIndex + 1));
    dots.forEach((dot, i) => dot.addEventListener('click', () => updateCarousel(i)));

    window.addEventListener('resize', () => updateCarousel(currentIndex));
    setInterval(() => updateCarousel(currentIndex + 1), 5000);

    // Navbar scroll effect
    const nav = document.getElementById('navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            nav.classList.add('glass', 'shadow-2xl', 'py-4');
            nav.classList.remove('py-6');
        } else {
            nav.classList.remove('glass', 'shadow-2xl', 'py-4');
            nav.classList.add('py-6');
        }
    });

    // Chatbot FAB
    const chatFab = document.getElementById('chatFab');
    const chatPopup = document.getElementById('chatPopup');
    const closeChat = document.getElementById('closeChat');
    chatFab.onclick = () => chatPopup.classList.toggle('show');
    closeChat.onclick = () => chatPopup.classList.remove('show');

    // Admin login modal
    const adminBtn = document.getElementById('adminLoginBtn');
    const modal = document.getElementById('adminLoginModal');
    const closeModal = document.getElementById('closeAdminLogin');
    const loginSubmit = document.getElementById('loginSubmit');
    adminBtn.onclick = () => modal.classList.add('flex', '!flex');
    closeModal.onclick = () => modal.classList.remove('flex', '!flex');
    window.onclick = (e) => { if (e.target === modal) modal.classList.remove('flex', '!flex'); };

    loginSubmit.onclick = async () => {
        const username = document.getElementById('adminUser').value;
        const password = document.getElementById('adminPass').value;
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await res.json();
        if (data.status === 'success') {
            window.location.href = '/admin';
        } else {
            alert('Invalid credentials');
        }
    };

    // Contact form submission
    const contactForm = document.getElementById('contactForm');
    const contactSuccess = document.getElementById('contactSuccess');
    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(contactForm);
        const res = await fetch('/api/contact', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        if (data.status === 'success') {
            contactForm.reset();
            contactSuccess.classList.remove('hidden');
            setTimeout(() => contactSuccess.classList.add('hidden'), 5000);
        } else {
            alert('Error sending message. Please try again.');
        }
    });
</script>
</body>
</html>
'''

HTML_REGISTER_CLIENT = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Client Registration · MEC WORKS</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>body{font-family:'Plus Jakarta Sans',sans-serif;background:#0A0A0A;color:#E2E8F0;}</style>
</head>
<body class="p-6">
    <div class="max-w-4xl mx-auto glass p-8 rounded-3xl my-8">
        <h1 class="text-3xl font-black mb-8">Client <span class="text-gold">Registration</span></h1>
        <form id="clientForm" class="space-y-6">
            <div class="grid md:grid-cols-2 gap-6">
                <input type="text" name="fullName" placeholder="Full Name *" required class="bg-white/5 border border-white/10 rounded-xl px-5 py-4 w-full">
                <input type="text" name="company" placeholder="Company / Organization" class="bg-white/5 border border-white/10 rounded-xl px-5 py-4 w-full">
                <input type="email" name="email" placeholder="Email *" required class="bg-white/5 border border-white/10 rounded-xl px-5 py-4 w-full">
                <input type="tel" name="phone" placeholder="Phone *" required class="bg-white/5 border border-white/10 rounded-xl px-5 py-4 w-full">
                <input type="text" name="projectType" placeholder="Project Type (e.g., Web Dev, Construction) *" required class="bg-white/5 border border-white/10 rounded-xl px-5 py-4 w-full">
                <input type="text" name="budget" placeholder="Budget Range (₹)" class="bg-white/5 border border-white/10 rounded-xl px-5 py-4 w-full">
                <textarea name="requirements" placeholder="Detailed Requirements *" rows="4" required class="bg-white/5 border border-white/10 rounded-xl px-5 py-4 w-full md:col-span-2"></textarea>
                <textarea name="timeline" placeholder="Expected Timeline" rows="2" class="bg-white/5 border border-white/10 rounded-xl px-5 py-4 w-full md:col-span-2"></textarea>
                <div class="md:col-span-2 border border-dashed border-gold/40 rounded-xl p-6 text-center">
                    <span class="text-gray-400">Attach any document (optional)</span>
                    <input type="file" name="document" class="mt-2 w-full text-gold">
                </div>
                <label class="flex items-center space-x-3 md:col-span-2"><input type="checkbox" name="agree" required class="accent-gold"> <span class="text-sm">I agree to the terms and conditions</span></label>
            </div>
            <button type="submit" class="bg-gold hover:bg-gold/90 text-white font-bold py-4 px-10 rounded-xl">Submit Registration</button>
        </form>
    </div>
    <script>
        document.getElementById('clientForm').onsubmit = async (e) => {
            e.preventDefault();
            const form = e.target;
            const formData = new FormData(form);
            const res = await fetch('/api/register/client', { method: 'POST', body: formData });
            const data = await res.json();
            if (data.status === 'success') {
                alert('Registration successful! We will contact you soon.');
                window.location.href = '/';
            } else {
                alert('Error. Please try again.');
            }
        };
    </script>
</body>
</html>
'''

HTML_REGISTER_FREELANCER = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Freelancer Registration · MEC WORKS</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>body{font-family:'Plus Jakarta Sans',sans-serif;background:#0A0A0A;color:#E2E8F0;}</style>
</head>
<body class="p-6">
    <div class="max-w-5xl mx-auto glass p-8 rounded-3xl my-8">
        <h1 class="text-3xl font-black mb-8">Freelancer <span class="text-gold">Registration</span></h1>
        <form id="freelancerForm" class="space-y-6">
            <div class="grid md:grid-cols-3 gap-4">
                <input type="text" name="fullName" placeholder="Full Name *" required class="bg-white/5 border border-white/10 rounded-xl px-5 py-4">
                <input type="text" name="fatherName" placeholder="Father's Name" class="bg-white/5 border border-white/10 rounded-xl px-5 py-4">
                <input type="text" name="motherName" placeholder="Mother's Name" class="bg-white/5 border border-white/10 rounded-xl px-5 py-4">
                <input type="email" name="email" placeholder="Email *" required class="bg-white/5 border border-white/10 rounded-xl px-5 py-4">
                <input type="tel" name="phone" placeholder="Phone *" required class="bg-white/5 border border-white/10 rounded-xl px-5 py-4">
                <input type="text" name="education" placeholder="Education *" required class="bg-white/5 border border-white/10 rounded-xl px-5 py-4">
                <input type="text" name="experience" placeholder="Work experience (years)" class="bg-white/5 border border-white/10 rounded-xl px-5 py-4">
                <input type="text" name="hoursPerWeek" placeholder="Hours per week" class="bg-white/5 border border-white/10 rounded-xl px-5 py-4">
                <input type="text" name="skills" placeholder="Skills (comma separated) *" required class="bg-white/5 border border-white/10 rounded-xl px-5 py-4">
                <textarea name="projectsDone" placeholder="Projects done (descriptions)" rows="3" class="bg-white/5 border border-white/10 rounded-xl px-5 py-4 md:col-span-2"></textarea>
                <textarea name="workHistory" placeholder="Company work & timeline" rows="3" class="bg-white/5 border border-white/10 rounded-xl px-5 py-4 md:col-span-2"></textarea>
                <div class="border border-dashed border-gold/40 rounded-xl p-4 text-center">
                    <span class="text-xs">Resume (PDF) *</span>
                    <input type="file" name="resume" required class="mt-1 text-xs w-full">
                </div>
                <div class="border border-dashed border-gold/40 rounded-xl p-4 text-center">
                    <span class="text-xs">Portfolio (PDF/Images)</span>
                    <input type="file" name="portfolio" class="mt-1 text-xs w-full">
                </div>
                <div class="md:col-span-3 flex flex-wrap gap-4 items-center">
                    <label class="flex items-center space-x-2"><input type="checkbox" name="agree" required class="accent-gold"> <span class="text-xs">Agree to terms</span></label>
                    <label class="flex items-center space-x-2"><input type="checkbox" name="publicProfile" class="accent-gold"> <span class="text-xs">Display profile publicly</span></label>
                </div>
            </div>
            <button type="submit" class="bg-gold hover:bg-gold/90 text-white font-bold py-4 px-10 rounded-xl">Create Profile</button>
        </form>
    </div>
    <script>
        document.getElementById('freelancerForm').onsubmit = async (e) => {
            e.preventDefault();
            const form = e.target;
            const formData = new FormData(form);
            const res = await fetch('/api/register/freelancer', { method: 'POST', body: formData });
            const data = await res.json();
            if (data.status === 'success') {
                alert('Registration successful! We will match you with projects.');
                window.location.href = '/';
            } else {
                alert('Error. Please try again.');
            }
        };
    </script>
</body>
</html>
'''

HTML_ADMIN = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Admin Dashboard · MEC WORKS</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>body{font-family:'Plus Jakarta Sans',sans-serif;background:#0A0A0A;color:#E2E8F0;}</style>
</head>
<body class="p-6">
    <div class="max-w-7xl mx-auto glass p-8 rounded-3xl my-8">
        <div class="flex justify-between items-center mb-8">
            <h1 class="text-3xl font-black">⚙️ ADMIN <span class="text-gold">DASHBOARD</span></h1>
            <button id="logoutBtn" class="border border-gold text-gold px-4 py-2 rounded-full text-sm">Logout</button>
        </div>

        <!-- Tabs -->
        <div class="flex border-b border-white/10 mb-6">
            <button class="tab-btn px-6 py-2 font-bold text-sm text-gold border-b-2 border-gold" data-tab="editor">✎ HOME EDITOR</button>
            <button class="tab-btn px-6 py-2 font-bold text-sm" data-tab="freelancers">👥 FREELANCERS</button>
            <button class="tab-btn px-6 py-2 font-bold text-sm" data-tab="clients">🏢 CLIENTS</button>
            <button class="tab-btn px-6 py-2 font-bold text-sm" data-tab="contacts">📬 CONTACT MESSAGES</button>
        </div>

        <!-- Editor Tab -->
        <div id="editorTab" class="tab-content">
            <h3 class="text-xl font-bold mb-4">Edit Homepage Content</h3>
            <form id="editorForm" class="grid md:grid-cols-2 gap-6">
                <div><label class="text-sm">Hero Title</label><input id="heroTitle" type="text" class="w-full bg-white/5 border rounded-xl px-4 py-2 mt-1"></div>
                <div><label class="text-sm">Hero Subtitle</label><input id="heroSub" type="text" class="w-full bg-white/5 border rounded-xl px-4 py-2 mt-1"></div>
                <div class="md:col-span-2"><label class="text-sm">About Text</label><textarea id="aboutText" rows="3" class="w-full bg-white/5 border rounded-xl px-4 py-2 mt-1"></textarea></div>
                <div><label class="text-sm">About Image URL</label><input id="aboutImage" type="text" class="w-full bg-white/5 border rounded-xl px-4 py-2 mt-1"></div>
                <div><label class="text-sm">Contact Email</label><input id="contactEmail" type="email" class="w-full bg-white/5 border rounded-xl px-4 py-2 mt-1"></div>
                <div><label class="text-sm">Contact Phone</label><input id="contactPhone" type="text" class="w-full bg-white/5 border rounded-xl px-4 py-2 mt-1"></div>
                <div><label class="text-sm">Contact Location</label><input id="contactLocation" type="text" class="w-full bg-white/5 border rounded-xl px-4 py-2 mt-1"></div>
                <div><label class="text-sm">Google Maps Embed URL</label><input id="mapUrl" type="text" class="w-full bg-white/5 border rounded-xl px-4 py-2 mt-1"></div>
                <div class="md:col-span-2">
                    <h4 class="font-bold mt-4 mb-2">Projects (Carousel Items)</h4>
                    <div id="projectsFields"></div>
                    <button type="button" id="addProjectBtn" class="mt-2 bg-gold/20 text-gold px-4 py-2 rounded-xl text-sm">+ Add New Project</button>
                </div>
                <div class="md:col-span-2 mt-4">
                    <button type="submit" class="bg-gold text-black font-bold py-3 px-8 rounded-xl">Save Changes</button>
                </div>
            </form>
        </div>

        <!-- Freelancers Tab -->
        <div id="freelancersTab" class="tab-content hidden">
            <h3 class="text-xl font-bold mb-4">Freelancer Registrations</h3>
            <div id="freelancerList" class="space-y-2"></div>
        </div>

        <!-- Clients Tab -->
        <div id="clientsTab" class="tab-content hidden">
            <h3 class="text-xl font-bold mb-4">Client Registrations</h3>
            <div id="clientList" class="space-y-2"></div>
        </div>

        <!-- Contacts Tab -->
        <div id="contactsTab" class="tab-content hidden">
            <h3 class="text-xl font-bold mb-4">Contact Messages</h3>
            <div id="contactsList" class="space-y-2"></div>
        </div>
    </div>

    <script>
        let currentContent = {};

        async function loadContent() {
            const res = await fetch('/api/content');
            currentContent = await res.json();
            document.getElementById('heroTitle').value = currentContent.hero.title;
            document.getElementById('heroSub').value = currentContent.hero.subtitle;
            document.getElementById('aboutText').value = currentContent.about.text;
            document.getElementById('aboutImage').value = currentContent.about.image;
            document.getElementById('contactEmail').value = currentContent.contact.email;
            document.getElementById('contactPhone').value = currentContent.contact.phone;
            document.getElementById('contactLocation').value = currentContent.contact.location;
            document.getElementById('mapUrl').value = currentContent.contact.map_url || '';

            renderProjectsFields(currentContent.projects || []);
        }

        function renderProjectsFields(projects) {
            const container = document.getElementById('projectsFields');
            container.innerHTML = '';
            projects.forEach((item, idx) => {
                const div = document.createElement('div');
                div.className = 'grid grid-cols-1 md:grid-cols-4 gap-2 mb-4 p-4 border border-white/10 rounded-xl relative';
                div.innerHTML = `
                    <input type="text" placeholder="Title" data-index="${idx}" data-field="title" value="${item.title}" class="bg-white/5 border rounded-xl px-4 py-2">
                    <input type="text" placeholder="Description" data-index="${idx}" data-field="description" value="${item.description}" class="bg-white/5 border rounded-xl px-4 py-2">
                    <input type="text" placeholder="Date" data-index="${idx}" data-field="date" value="${item.date}" class="bg-white/5 border rounded-xl px-4 py-2">
                    <input type="text" placeholder="Image URL" data-index="${idx}" data-field="image" value="${item.image}" class="bg-white/5 border rounded-xl px-4 py-2">
                    <button type="button" class="remove-project absolute top-2 right-2 text-red-400 hover:text-red-600" data-index="${idx}">✕</button>
                `;
                container.appendChild(div);
            });

            document.querySelectorAll('.remove-project').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const idx = e.target.dataset.index;
                    const newProjects = currentContent.projects.filter((_, i) => i != idx);
                    currentContent.projects = newProjects;
                    renderProjectsFields(newProjects);
                });
            });
        }

        document.getElementById('addProjectBtn').addEventListener('click', () => {
            if (!currentContent.projects) currentContent.projects = [];
            currentContent.projects.push({
                title: "New Project",
                description: "Description",
                date: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }),
                image: "https://images.unsplash.com/photo-1581091226033-d5c48150dbaa?w=400"
            });
            renderProjectsFields(currentContent.projects);
        });

        document.getElementById('editorForm').onsubmit = async (e) => {
            e.preventDefault();
            const projectInputs = document.querySelectorAll('#projectsFields > div');
            const projects = [];
            projectInputs.forEach(div => {
                const inputs = div.querySelectorAll('input[data-field]');
                const item = {};
                inputs.forEach(inp => {
                    const field = inp.dataset.field;
                    item[field] = inp.value;
                });
                projects.push(item);
            });

            const updated = {
                hero: {
                    title: document.getElementById('heroTitle').value,
                    subtitle: document.getElementById('heroSub').value
                },
                about: {
                    image: document.getElementById('aboutImage').value,
                    text: document.getElementById('aboutText').value
                },
                contact: {
                    email: document.getElementById('contactEmail').value,
                    phone: document.getElementById('contactPhone').value,
                    location: document.getElementById('contactLocation').value,
                    map_url: document.getElementById('mapUrl').value
                },
                projects: projects
            };

            const res = await fetch('/api/content', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updated)
            });
            if (res.ok) {
                alert('Content updated successfully!');
                currentContent = updated;
            } else {
                alert('Error updating content.');
            }
        };

        // Tab switching and loading data
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('text-gold', 'border-b-2', 'border-gold'));
                btn.classList.add('text-gold', 'border-b-2', 'border-gold');
                document.querySelectorAll('.tab-content').forEach(t => t.classList.add('hidden'));
                const tabId = btn.dataset.tab;
                if (tabId === 'editor') {
                    document.getElementById('editorTab').classList.remove('hidden');
                } else if (tabId === 'freelancers') {
                    document.getElementById('freelancersTab').classList.remove('hidden');
                    loadRegistrations('freelancers');
                } else if (tabId === 'clients') {
                    document.getElementById('clientsTab').classList.remove('hidden');
                    loadRegistrations('clients');
                } else if (tabId === 'contacts') {
                    document.getElementById('contactsTab').classList.remove('hidden');
                    loadContacts();
                }
            });
        });

        async function loadRegistrations(type) {
            const listEl = type === 'freelancers' ? document.getElementById('freelancerList') : document.getElementById('clientList');
            listEl.innerHTML = '<p class="text-gray-400">Loading...</p>';
            const res = await fetch(`/api/registrations?type=${type === 'freelancers' ? 'freelancers' : 'clients'}`);
            const data = await res.json();
            listEl.innerHTML = '';
            data.forEach((item, index) => {
                const card = document.createElement('div');
                card.className = 'glass p-4 rounded-xl mb-2';
                const details = Object.entries(item).map(([k, v]) => `<span class="text-xs text-gray-400 block"><strong>${k}:</strong> ${v}</span>`).join('');
                card.innerHTML = `
                    <div class="flex justify-between items-start">
                        <div class="flex-1">${details}</div>
                        <div class="flex space-x-2">
                            <button class="approve-btn text-green-500 hover:text-green-400" data-type="${type}" data-index="${index}">✓ Approve</button>
                            <button class="delete-btn text-red-500 hover:text-red-400" data-type="${type}" data-index="${index}">✗ Delete</button>
                        </div>
                    </div>
                `;
                listEl.appendChild(card);
            });

            document.querySelectorAll('.approve-btn').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    const type = e.target.dataset.type === 'freelancers' ? 'freelancer' : 'client';
                    const index = e.target.dataset.index;
                    const res = await fetch('/api/registrations/approve', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ type, index: parseInt(index) })
                    });
                    if (res.ok) {
                        loadRegistrations(type === 'freelancer' ? 'freelancers' : 'clients');
                    }
                });
            });

            document.querySelectorAll('.delete-btn').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    const type = e.target.dataset.type === 'freelancers' ? 'freelancer' : 'client';
                    const index = e.target.dataset.index;
                    const res = await fetch('/api/registrations/delete', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ type, index: parseInt(index) })
                    });
                    if (res.ok) {
                        loadRegistrations(type === 'freelancer' ? 'freelancers' : 'clients');
                    }
                });
            });
        }

        async function loadContacts() {
            const listEl = document.getElementById('contactsList');
            listEl.innerHTML = '<p class="text-gray-400">Loading...</p>';
            const res = await fetch('/api/contacts');
            const data = await res.json();
            listEl.innerHTML = '';
            data.forEach((item, index) => {
                const card = document.createElement('div');
                card.className = 'glass p-4 rounded-xl mb-2';
                const details = Object.entries(item).map(([k, v]) => `<span class="text-xs text-gray-400 block"><strong>${k}:</strong> ${v}</span>`).join('');
                card.innerHTML = `
                    <div class="flex justify-between items-start">
                        <div class="flex-1">${details}</div>
                        <div class="flex space-x-2">
                            <button class="delete-contact text-red-500 hover:text-red-400" data-index="${index}">✗ Delete</button>
                        </div>
                    </div>
                `;
                listEl.appendChild(card);
            });

            document.querySelectorAll('.delete-contact').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    const index = e.target.dataset.index;
                    const res = await fetch('/api/contacts/delete', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ index: parseInt(index) })
                    });
                    if (res.ok) {
                        loadContacts();
                    }
                });
            });
        }

        document.getElementById('logoutBtn').onclick = async () => {
            await fetch('/api/logout', { method: 'POST' });
            window.location.href = '/';
        };

        loadContent();
    </script>
</body>
</html>
'''

def render_template_string(template, **context):
    from jinja2 import Template
    return Template(template).render(**context)

if __name__ == '__main__':
    app.run(debug=True)