import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request, session, redirect
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "supersecretkey"


# 🔹 Google Sheets Connection (SAFE)
def get_gspread_client():
    try:
        creds_json = os.environ.get('GOOGLE_CREDENTIALS')

        if not creds_json:
            print("❌ No GOOGLE_CREDENTIALS found")
            return None

        creds_dict = json.loads(creds_json)

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

    except Exception as e:
        print("❌ Credential Error:", e)
        return None


# 🔹 HOME PAGE (SAFE)
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
        print("❌ File Error:", e)

    return render_template('index.html', villages_data=villages_data)


# 🔹 FORM SUBMIT
@app.route('/submit', methods=['POST'])
def submit():
    mobile = request.form.get('mobile')

    if not mobile or len(mobile) != 10:
        return "<h2>चूक: मोबाईल नंबर १० अंकी असावा!</h2><a href='/'>परत जा</a>"

    creds = get_gspread_client()
    if not creds:
        return "<h2>Google Credentials Missing ❌</h2>"

    try:
        client = gspread.authorize(creds)
        sheet = client.open("Data Collection").sheet1

        row = [
            datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            request.form.get('full_name'),
            request.form.get('dob'),
            request.form.get('mobile'),
            request.form.get('taluka'),
            request.form.get('village'),
            request.form.get('gender'),
            request.form.get('occupation')
        ]

        sheet.append_row(row)

        return "<h2>माहिती यशस्वीरित्या जतन झाली!</h2><a href='/'>परत जा</a>"

    except Exception as e:
        return f"<h2>❌ Error: {str(e)}</h2>"


# 🔐 LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            if request.form.get('username') == "admin" and request.form.get('password') == "1234":
                session['admin'] = True
                return redirect('/admin')
            else:
                return "Wrong Credentials ❌"

        return render_template("login.html")

    except Exception as e:
        return f"Login Error: {str(e)}"


# 🎂 ADMIN (ONLY TODAY BIRTHDAYS)
@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/login')

    creds = get_gspread_client()
    if not creds:
        return "Google Credentials Missing ❌"

    try:
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
                        "village": row[5],
                        "dob": dob_str
                    })

            except Exception as e:
                print("Birthday Error:", e)

        return render_template("admin.html", birthdays=birthday_list)

    except Exception as e:
        return f"Admin Error: {str(e)}"


# ✏️ EDIT
@app.route('/edit/<int:row_id>', methods=['GET', 'POST'])
def edit(row_id):
    if not session.get('admin'):
        return redirect('/login')

    creds = get_gspread_client()
    if not creds:
        return "Google Credentials Missing ❌"

    try:
        client = gspread.authorize(creds)
        sheet = client.open("Data Collection").sheet1

        if request.method == 'POST':
            sheet.update(f"B{row_id}", request.form.get('name'))
            sheet.update(f"D{row_id}", request.form.get('mobile'))
            sheet.update(f"F{row_id}", request.form.get('village'))

            return redirect('/admin')

        row = sheet.row_values(row_id)

        return render_template("edit.html", row=row, row_id=row_id)

    except Exception as e:
        return f"Edit Error: {str(e)}"


# 🚪 LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# 🔥 VERCEL ENTRY POINT (IMPORTANT)
app = app
