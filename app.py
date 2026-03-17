import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')

# Google Sheets कनेक्शन सेटअप
def get_sheet():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_json = os.environ.get('GOOGLE_CREDENTIALS')
        if not creds_json:
            return None
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        # तुमच्या शीटचे नाव "Data Collection" असल्याची खात्री करा
        return client.open("Data Collection").sheet1
    except Exception as e:
        print(f"Sheet Error: {e}")
        return None

@app.route('/')
def index():
    # डिफॉल्ट डेटा (स्क्रीन कोरी दिसू नये म्हणून)
    villages_data = {'नांदगाव': [], 'मालेगाव': []}
    
    # फाईल्स वाचणे
    for taluka in ['नांदगाव', 'मालेगाव']:
        filename = f"{taluka}.txt"
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    villages_data[taluka] = [line.strip() for line in f if line.strip()]
            except:
                pass
    
    return render_template('index.html', villages_data=villages_data)

@app.route('/submit', methods=['POST'])
def submit():
    sheet = get_sheet()
    if not sheet:
        return "<h2>Error: Google Sheet कनेक्शन अयशस्वी!</h2>"
    
    try:
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
        return "<h2>यशस्वीरित्या जतन झाले!</h2><a href='/'>परत जा</a>"
    except Exception as e:
        return f"<h2>चूक झाली: {e}</h2>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
