import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

# --- Google Sheet कनेक्शन ---
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    
    if creds_json:
        # Vercel Environment Variable मधून की वाचणे
        creds_dict = json.loads(creds_json)
        return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return None

try:
    creds = get_gspread_client()
    if creds:
        client = gspread.authorize(creds)
        sheet = client.open("Data Collection").sheet1
    else:
        sheet = None
except Exception as e:
    print(f"Sheet Error: {e}")
    sheet = None

@app.route('/')
def index():
    villages_data = {'नांदगाव': [], 'मालेगाव': []}
    
    # फाईल्स वाचण्यासाठी सुरक्षित पद्धत
    files = {'नांदगाव': 'nandgaon.txt', 'मालेगाव': 'malegaon.txt'}
    
    for taluka, filename in files.items():
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    villages_data[taluka] = [line.strip() for line in f if line.strip()]
            else:
                print(f"Warning: {filename} not found!")
        except Exception as e:
            print(f"File Error ({filename}): {e}")
    
    return render_template('index.html', villages_data=villages_data)

@app.route('/submit', methods=['POST'])
def submit():
    if not sheet:
        return "<h2>Error: Google Sheet शी संपर्क होऊ शकला नाही!</h2>"
    
    try:
        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        data = [
            now,
            request.form.get('full_name'),
            request.form.get('dob'),
            request.form.get('mobile'),
            request.form.get('taluka'),
            request.form.get('village'),
            request.form.get('gender'),
            request.form.get('occupation')
        ]
        sheet.append_row(data)
        return "<h2>माहिती यशस्वीरित्या जतन झाली!</h2><a href='/'>परत जा</a>"
    except Exception as e:
        return f"<h2>चूक झाली: {e}</h2>"

# Vercel साठी हे महत्त्वाचे आहे
if __name__ == '__main__':
    app.run(debug=True)import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

# --- Google Sheet कनेक्शन सेटअप ---
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    
    if creds_json:
        creds_dict = json.loads(creds_json)
        return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        # लोकल टेस्टिंगसाठी
        return ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

try:
    creds = get_gspread_client()
    client = gspread.authorize(creds)
    sheet = client.open("Data Collection").sheet1
except Exception as e:
    print(f"Google Sheet Connection Error: {e}")
    sheet = None

@app.route('/')
def index():
    villages_data = {'नांदगाव': [], 'मालेगाव': []}
    
    # फाईल्स वाचताना पाथ (path) बरोबर आहे का ते तपासणे
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    try:
        nandgaon_path = os.path.join(base_path, 'Nandgaon.txt') # तुमच्या GitHub वर 'N' कॅपिटल असू शकतो
        if os.path.exists(nandgaon_path):
            with open(nandgaon_path, 'r', encoding='utf-8') as f:
                villages_data['नांदगाव'] = [line.strip() for line in f if line.strip()]
        
        malegaon_path = os.path.join(base_path, 'Malegaon.txt') # 'M' कॅपिटल तपासा
        if os.path.exists(malegaon_path):
            with open(malegaon_path, 'r', encoding='utf-8') as f:
                villages_data['मालेगाव'] = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"File Reading Error: {e}")
    
    return render_template('index.html', villages_data=villages_data)

@app.route('/submit', methods=['POST'])
def submit():
    if sheet is None:
        return "<h2 style='color:red;'>Sheet Connection Missing!</h2>"
    
    try:
        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        data = [
            now,
            request.form.get('full_name'),
            request.form.get('dob'),
            request.form.get('mobile'),
            request.form.get('taluka'),
            request.form.get('village'),
            request.form.get('gender'),
            request.form.get('occupation')
        ]
        sheet.append_row(data)
        return "<h2>माहिती जतन झाली!</h2><a href='/'>परत जा</a>"
    except Exception as e:
        return f"<h2 style='color:red;'>चूक झाली: {e}</h2>"

if __name__ == '__main__':
    app.run(debug=True)
