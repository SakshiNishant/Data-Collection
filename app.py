import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')

# १. Google Sheets कनेक्शन सेटअप
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # Vercel च्या Settings मधील GOOGLE_CREDENTIALS मधून डेटा वाचणे
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    
    if not creds_json:
        return None
    
    try:
        creds_dict = json.loads(creds_json)
        return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    except Exception as e:
        print(f"Credentials Error: {e}")
        return None

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

@app.route('/submit', methods=['POST'])
def submit():
    mobile = request.form.get('mobile')
    
    # मोबाईल नंबर व्हॅलिडेशन
    if not mobile or len(mobile) != 10:
        return "<h2>चूक: मोबाईल नंबर १० अंकी असावा!</h2><a href='/'>परत जा</a>"
    
    # २. गुगल शीटमध्ये डेटा लिहिणे
    creds = get_gspread_client()
    if not creds:
        return "<h2>Error: Google Credentials सापडले नाहीत!</h2>"

    try:
        client = gspread.authorize(creds)
        # तुमच्या Google Sheet चे नाव खालील अवतरण चिन्हात अचूक लिहा (उदा. "Data Collection")
        sheet = client.open("Data Collection").sheet1
        
        # फॉर्ममधील डेटा गोळा करणे
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
        return f"<h2>चूक झाली: {str(e)}</h2><p>टीप: तुम्ही तुमची गुगल शीट Service Account ईमेलसोबत शेअर केली आहे का?</p>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
