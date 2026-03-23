import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request, session, redirect, send_file
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "supersecretkey"


# 🔹 Google Sheets Connection
def get_gspread_client():
    try:
        creds_json = os.environ.get('GOOGLE_CREDENTIALS')

        if not creds_json:
            print("No credentials found")
            return None

        creds_dict = json.loads(creds_json)

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

    except Exception as e:
        print("Credential Error:", e)
        return None


# 🔹 HOME
@app.route('/')
def index():
    villages_data = {'नांदगाव': [], 'मालेगाव': []}

    try:
        if os.path.exists('Nandgaon.txt'):
            with open('Nandgaon.txt', 'r', encoding='utf-8') as f:
                villages_data['नांदगाव'] = [line.strip() for line in f if line.strip()]

        if os.path.exists('Malegaon.txt'):
            with open('Malegaon.txt', 'r', encoding='utf-8') as f:
                villages_data['मालेगाव'] = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print("File Error:", e)

    return render_template('index.html', villages_data=villages_data)


# 🔹 SUBMIT (Duplicate Check)
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('full_name').strip().lower()
    mobile = request.form.get('mobile').strip()
    village = request.form.get('village').strip().lower()

    if not mobile or len(mobile) != 10:
        return "<h2>चूक: मोबाईल नंबर १० अंकी असावा!</h2><a href='/'>परत जा</a>"

    creds = get_gspread_client()
    if not creds:
        return "<h2>Google Credentials Missing ❌</h2>"

    try:
        client = gspread.authorize(creds)
        sheet = client.open("Data Collection").sheet1

        data = sheet.get_all_values()

        # 🔥 Duplicate check
        for row in data[1:]:
            try:
                if (
                    name == row[1].strip().lower() and
                    mobile == row[3].strip() and
                    village == row[5].strip().lower()
                ):
                    return "<h2>❌ ही माहिती आधीच नोंदलेली आहे!</h2><a href='/'>परत जा</a>"
            except:
                continue

        row = [
            datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            request.form.get('full_name'),
            request.form.get('dob'),
            mobile,
            request.form.get('taluka'),
            request.form.get('village'),
            request.form.get('gender'),
            request.form.get('occupation')
        ]

        sheet.append_row(row)

        return "<h2>✅ माहिती जतन झाली!</h2><a href='/'>परत जा</a>"

    except Exception as e:
        return f"<h2>Error: {str(e)}</h2>"


# 🔐 LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == "admin" and request.form.get('password') == "1234":
            session['admin'] = True
            return redirect('/admin')
        else:
            return "Wrong Credentials ❌"

    return render_template("login.html")


# 🎂 ADMIN (Only Birthday)
@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/login')

    creds = get_gspread_client()
    if not creds:
        return "Google Credentials Missing ❌"

    client = gspread.authorize(creds)
    sheet = client.open("Data Collection").sheet1
    data = sheet.get_all_values()

    today = datetime.now()
    birthday_list = []

    for i, row in enumerate(data[1:], start=2):
        try:
            dob_str = row[2]

            try:
                dob = datetime.strptime(dob_str, "%Y-%m-%d")
            except:
                try:
                    dob = datetime.strptime(dob_str, "%d-%m-%Y")
                except:
                    continue

            if dob.day == today.day and dob.month == today.month:
                birthday_list.append({
                    "row_id": i,
                    "name": row[1],
                    "mobile": row[3],
                    "village": row[5]
                })
        except:
            continue

    return render_template("admin.html", birthdays=birthday_list)


# 🎨 BANNER (10 Templates)
@app.route('/banner/<int:template_id>/<name>')
def banner(template_id, name):
    try:
        path = f"static/templates/template{template_id}.png"
        img = Image.open(path)
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = None

        positions = {
            1: (200, 800),
            2: (300, 700),
            3: (250, 750),
            4: (200, 780),
            5: (300, 820),
            6: (250, 760),
            7: (220, 800),
            8: (270, 770),
            9: (240, 790),
            10: (260, 810)
        }

        pos = positions.get(template_id, (200, 800))

        draw.text(pos, name, fill="white", font=font)

        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)

        return send_file(img_io, mimetype='image/png')

    except Exception as e:
        return f"Banner Error: {str(e)}"


# 🚪 LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# 🔥 VERCEL ENTRY
app = app
