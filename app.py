import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request, session, redirect
from datetime import datetime
from collections import Counter

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "supersecretkey"


# 🔹 Google Sheets
def get_gspread_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_json = os.environ.get('GOOGLE_CREDENTIALS')

    if not creds_json:
        return None

    creds_dict = json.loads(creds_json)
    return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)


# 🔹 Home
@app.route('/')
def index():
    return render_template('index.html')


# 🔹 Submit
@app.route('/submit', methods=['POST'])
def submit():
    mobile = request.form.get('mobile')

    if not mobile or len(mobile) != 10:
        return "Invalid Mobile"

    creds = get_gspread_client()
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

    return redirect('/')


# 🔥 Birthday
@app.route('/birthdays')
def birthdays():
    creds = get_gspread_client()
    client = gspread.authorize(creds)
    sheet = client.open("Data Collection").sheet1

    data = sheet.get_all_values()

    today = datetime.now()
    birthday_list = []

    for i in range(1, len(data)):
        row = data[i]

        try:
            try:
                dob = datetime.strptime(row[2], "%Y-%m-%d")
            except:
                dob = datetime.strptime(row[2], "%d-%m-%Y")

            if dob.day == today.day and dob.month == today.month:
                birthday_list.append(row)

        except:
            pass

    return render_template("birthdays.html", data=birthday_list)


# 🔐 Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == "admin" and request.form['password'] == "1234":
            session['admin'] = True
            return redirect('/admin')
    return render_template("login.html")


# 🔥 ADMIN DASHBOARD (PREMIUM)
@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/login')

    creds = get_gspread_client()
    client = gspread.authorize(creds)
    sheet = client.open("Data Collection").sheet1

    data = sheet.get_all_values()

    total = len(data) - 1
    today = datetime.now()

    birthday_count = 0
    villages = []
    genders = []

    for row in data[1:]:
        villages.append(row[5])
        genders.append(row[6])

        try:
            dob = datetime.strptime(row[2], "%d-%m-%Y")
            if dob.day == today.day and dob.month == today.month:
                birthday_count += 1
        except:
            pass

    village_stats = Counter(villages)
    gender_stats = Counter(genders)

    return render_template("admin.html",
                           data=data,
                           total=total,
                           birthday_count=birthday_count,
                           village_stats=village_stats,
                           gender_stats=gender_stats)


# ❌ Delete
@app.route('/delete/<int:row_id>')
def delete(row_id):
    if not session.get('admin'):
        return redirect('/login')

    creds = get_gspread_client()
    client = gspread.authorize(creds)
    sheet = client.open("Data Collection").sheet1

    sheet.delete_rows(row_id)
    return redirect('/admin')


# 🚪 Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == "__main__":
    app.run(debug=True)
