import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

# १. फाईल पाथ अचूक मिळवण्यासाठी बेस डिरेक्टरी
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# २. Google Sheet कनेक्शन फंक्शन
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    
    if not creds_json:
        return None, "Vercel Settings मध्ये GOOGLE_CREDENTIALS सापडले नाहीत!"
    
    try:
        creds_dict = json.loads(creds_json)
        return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope), None
    except Exception as e:
        return None, f"JSON Key Error: {str(e)}"

@app.route('/')
def index():
    villages_data = {'नांदगाव': [], 'मालेगाव': []}
    
    # ३. .txt फाईल्सचे अचूक पाथ शोधणे
    files = {
        'नांदगाव': os.path.join(BASE_DIR, 'Nandgaon.txt'),
        'मालेगाव': os.path.join(BASE_DIR, 'Malegaon.txt')
    }
    
    # फाईल्स वाचणे
    for taluka, file_path in files.items():
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    villages_data[taluka] = [line.strip() for line in f if line.strip()]
            except Exception as e:
                print(f"Error reading {taluka}: {e}")
        else:
            print(f"File not found: {file_path}")
    
    # ४. 'templates' फोल्डरमधील index.html लोड करणे
    try:
        return render_template('index.html', villages_data=villages_data)
    except Exception as e:
        return f"<h2>Template Error: templates फोल्डरमध्ये index.html सापडली नाही!</h2><p>{str(e)}</p>"

@app.route('/submit', methods=['POST'])
def submit():
    creds, error_msg = get_gspread_client()
    if error_msg:
        return f"<h2 style='color:red;'>Auth Error: {error_msg}</h2>"
    
    try:
        client = gspread.authorize(creds)
        # तुमच्या शीटचे नाव बरोबर "Data Collection" असल्याची खात्री करा
        sheet = client.open("Data Collection").sheet1
        
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
        return f"<h2 style='color:red;'>Sheet Error: {str(e)}</h2><p>टीप: तुम्ही तुमची गुगल शीट Service Account ईमेलसोबत शेअर केली आहे का?</p>"

if __name__ == '__main__':
    app.run(debug=True)
