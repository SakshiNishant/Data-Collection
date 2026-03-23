import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')


# 🔹 Google Sheets कनेक्शन
def get_gspread_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_json = os.environ.get('GOOGLE_CREDENTIALS')

    if not creds_json:
        return None

    try:
        creds_dict = json.loads(creds_json)
        return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    except Exception as e:
        print(f"Credentials Error: {e}")
        return None


# 🔹 Home Page
@app.route('/')
def index():
    villages_data = {'नांदगाव': [], 'मालेगाव': []}
    file_paths = {'नांदगाव': 'Nandgaon.txt', 'मालेगाव': 'Malegaon.txt'}

    for taluka, file_name in file_paths.items():
        if os.path.exists(file_name):
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    villages_data[taluka] = [line.strip() for line in f if line.strip()]
            except Exception as e:
                print(f"Error reading {file_name}: {e}")

    return render_template('index.html', villages_data=villages_data)


# 🔹 Form Submit
@app.route('/submit', methods=['POST'])
def submit():
    mobile = request.form.get('mobile')

    if not mobile or len(mobile) != 10:
        return "<h2>चूक: मोबाईल नंबर १० अंकी असावा!</h2><a href='/'>परत जा</a>"

    creds = get_gspread_client()
    if not creds:
        return "<h2>Error: Google Credentials सापडले नाहीत!</h2>"

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
        return f"<h2>चूक झाली: {str(e)}</h2>"


# 🔥 Birthday Route
@app.route('/birthdays')
def birthdays():
    creds = get_gspread_client()
    if not creds:
        return "<h2>Google Credentials सापडले नाहीत!</h2>"

    try:
        client = gspread.authorize(creds)
        sheet = client.open("Data Collection").sheet1

        data = sheet.get_all_values()

        today = datetime.now()
        birthday_list = []

        for i in range(1, len(data)):
            row = data[i]

            try:
                dob_str = row[2]

                try:
                    dob = datetime.strptime(dob_str, "%Y-%m-%d")
                except:
                    dob = datetime.strptime(dob_str, "%d-%m-%Y")

                if dob.day == today.day and dob.month == today.month:
                    birthday_list.append({
                        "name": row[1],
                        "mobile": row[3],
                        "village": row[5],
                        "gender": row[6],
                        "occupation": row[7],
                        "dob": dob_str
                    })

            except Exception as e:
                print("DOB Error:", e)

        return render_template("birthdays.html", birthdays=birthday_list)

    except Exception as e:
        return f"<h2>Error: {str(e)}</h2>"


# 🔹 Run
if __name__ == "__main__":
    app.run(debug=True)
