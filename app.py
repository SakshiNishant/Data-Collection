import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    
    if not creds_json:
        return None, "GOOGLE_CREDENTIALS variable missing in Vercel settings!"
    
    try:
        creds_dict = json.loads(creds_json)
        return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope), None
    except Exception as e:
        return None, f"JSON Parsing Error: {str(e)}"

@app.route('/')
def index():
    villages_data = {'नांदगाव': [], 'मालेगाव': []}
    files = {'नांदगाव': 'Nandgaon.txt', 'मालेगाव': 'Malegaon.txt'}
    
    for taluka, filename in files.items():
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                villages_data[taluka] = [line.strip() for line in f if line.strip()]
    
    return render_template('index.html', villages_data=villages_data)

@app.route('/submit', methods=['POST'])
def submit():
    creds, error_msg = get_gspread_client()
    if error_msg:
        return f"<h2 style='color:red;'>Auth Error: {error_msg}</h2>"
    
    try:
        client = gspread.authorize(creds)
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
        return "<h2>यशस्वीरित्या जतन झाले!</h2><a href='/'>परत जा</a>"
    except Exception as e:
        return f"<h2 style='color:red;'>Sheet Error: {str(e)}</h2>"

if __name__ == '__main__':
    app.run(debug=True)
