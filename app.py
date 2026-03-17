import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

# --- Google Sheet कनेक्शन सेटअप (Vercel सुरक्षित पद्धत) ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Vercel Settings मधून 'GOOGLE_CREDENTIALS' नावाने डेटा वाचणे
creds_json = os.environ.get('GOOGLE_CREDENTIALS')

if creds_json:
    # जर Environment Variable असेल तर त्यातून की (Key) लोड करा
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
else:
    # स्थानिक लॅपटॉपवर चालवण्यासाठी (जर credentials.json असेल तर)
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    except Exception as e:
        print("Credentials not found!")

client = gspread.authorize(creds)
# तुमच्या Google Sheet चे नाव
sheet = client.open("Data Collection").sheet1

@app.route('/')
def index():
    villages_data = {}
    try:
        # नांदगाव गावे वाचणे
        with open('nandgaon.txt', 'r', encoding='utf-8') as f:
            villages_data['नांदगाव'] = [line.strip() for line in f if line.strip()]
        
        # मालेगाव गावे वाचणे
        with open('malegaon.txt', 'r', encoding='utf-8') as f:
            villages_data['मालेगाव'] = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"File Error: {e}")
        villages_data = {'नांदगाव': [], 'मालेगाव': []}
    
    return render_template('index.html', villages_data=villages_data)

@app.route('/submit', methods=['POST'])
def submit():
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
        
        return """
        <div style='text-align:center; font-family:Arial; padding-top:50px;'>
            <h2 style='color: #28a745;'>तुमची माहिती यशस्वीरित्या जतन झाली!</h2>
            <p><a href='/'>परत जा</a></p>
        </div>
        """
    except Exception as e:
        return f"<h2 style='color:red; text-align:center;'>डेटा जतन करताना चूक झाली: {e}</h2>"

# Vercel साठी __name__ == '__main__' ची गरज नसते, पण स्थानिक टेस्टिंगसाठी राहू द्या
if __name__ == '__main__':
    app.run(debug=True)
