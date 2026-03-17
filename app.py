import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

# सध्याच्या फाईलचा मूळ पत्ता मिळवण्यासाठी
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    
    if creds_json:
        try:
            creds_dict = json.loads(creds_json)
            return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        except Exception as e:
            print(f"JSON Parsing Error: {e}")
    return None

@app.route('/')
def index():
    villages_data = {'नांदगाव': [], 'मालेगाव': []}
    
    # फाईल्सचे अचूक पाथ (GitHub वरील नावाप्रमाणे 'N' आणि 'M' कॅपिटल ठेवले आहेत)
    files = {
        'नांदगाव': os.path.join(BASE_DIR, 'Nandgaon.txt'),
        'मालेगाव': os.path.join(BASE_DIR, 'Malegaon.txt')
    }
    
    for taluka, file_path in files.items():
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    villages_data[taluka] = [line.strip() for line in f if line.strip()]
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    return render_template('index.html', villages_data=villages_data)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        creds = get_gspread_client()
        if not creds:
            return "<h2>गूगल क्रेडेंशियल्स सापडले नाहीत!</h2>"
            
        client = gspread.authorize(creds)
        sheet = client.open("Data Collection").sheet1
        
        data = [
            datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
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

if __name__ == '__main__':
    app.run(debug=True)
