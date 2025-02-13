from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import pygame
import os
import sys
import traceback
import socket
import creds

# Configuration
UPLOAD_FOLDER = "./sounds"
ALLOWED_EXTENSIONS = {"mp3", "wav", "ogg"}
USERNAME = creds.username
PASSWORD = creds.password

# Flask setup
app = Flask(__name__)
app.config["SECRET_KEY"] = creds.supersecretkey
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

class User(UserMixin):
    id = 1

@login_manager.user_loader
def load_user(user_id):
    return User() if user_id == "1" else None

# Pygame initialization
try:
    pygame.mixer.init()
    print("[INFO] Pygame initialized")
except Exception as e:
    print("[ERROR] Pygame initialization failed:")
    traceback.print_exc()

def get_sounds():
    """Get a list of available sound files."""
    try:
        return [f for f in os.listdir(UPLOAD_FOLDER) if f.split('.')[-1] in ALLOWED_EXTENSIONS]
    except Exception as e:
        print("[ERROR] Failed to read sound files:")
        traceback.print_exc()
        return []

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Main webpage with play buttons and file upload."""
    return render_template("index.html", sounds=get_sounds())

@app.route("/play/<sound>")
@login_required
def play_sound(sound):
    """Play a sound file."""
    sound_path = os.path.join(UPLOAD_FOLDER, sound)
    if os.path.exists(sound_path):
        try:
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play()
            print(f"[INFO] Playing: {sound}")
            return f"Playing: {sound}"
        except Exception as e:
            print(f"[ERROR] Failed to play {sound}:")
            traceback.print_exc()
            return "Error", 500
    print(f"[ERROR] Sound file {sound} not found")
    return "Sound not found", 404

@app.route("/upload", methods=["POST"])
@login_required
def upload_file():
    """Handle file uploads."""
    if "file" not in request.files:
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "":
        return redirect(url_for("index"))

    if file and allowed_file(file.filename):
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        try:
            file.save(filepath)
            print(f"[INFO] Uploaded file: {file.filename}")
        except Exception as e:
            print(f"[ERROR] Failed to upload {file.filename}:")
            traceback.print_exc()

    return redirect(url_for("index"))

@app.route("/login", methods=["GET", "POST"])
def login():
    """User login."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == USERNAME and password == PASSWORD:
            login_user(User())
            print(f"[INFO] Successful login: {username}")
            return redirect(url_for("index"))
        print("[ERROR] Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    """User logout."""
    logout_user()
    print("[INFO] Logged out")
    return redirect(url_for("login"))

# Get local IP address
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

if __name__ == "__main__":
    ip_address = get_local_ip()
    port = 5000
    print(f"[INFO] Server started at: http://{ip_address}:{port}/")
    try:
        app.run(host="0.0.0.0", port=port, debug=True)
    except Exception as e:
        print("[ERROR] Server startup failed:")
        traceback.print_exc()
