import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

# --- सुरक्षित कनेक्शन फंक्शन ---
def connect_to_sheet():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_json = os.environ.get('GOOGLE_CREDENTIALS')
        
        if not creds_json:
            return None
        
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        # तुमच्या शीटचे नाव बरोबर असल्याची खात्री करा
        return client.open("Data Collection").sheet1
    except Exception as e:
        print(f"Auth Error: {e}")
        return None

@app.route('/')
def index():
    villages_data = {'नांदगाव': [], 'मालेगाव': []}
    # फाईल पाथ तपासणे
    files = {'नांदगाव': 'Nandgaon.txt', 'मालेगाव': 'Malegaon.txt'}
    
    for taluka, filename in files.items():
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    villages_data[taluka] = [line.strip() for line in f if line.strip()]
            except:
                pass
    
    return render_template('index.html', villages_data=villages_data)

@app.route('/submit', methods=['POST'])
def submit():
    sheet = connect_to_sheet()
    if not sheet:
        return "<h2>Error: Google Sheet कनेक्शन अयशस्वी! Environment Variables तपासा.</h2>"
    
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
        return "<h2>यशस्वीरित्या जतन झाले!</h2><a href='/'>परत जा</a>"
    except Exception as e:
        return f"<h2>चूक झाली: {str(e)}</h2>"

if __name__ == '__main__':
    app.run(debug=True)
