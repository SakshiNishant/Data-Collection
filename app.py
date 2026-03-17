import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

# --- Google Sheet कनेक्शन सेटअप ---
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # प्राधान्य १: Vercel Environment Variable (GOOGLE_CREDENTIALS)
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    
    if creds_json:
        try:
            creds_dict = json.loads(creds_json)
            return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        except Exception as e:
            print(f"JSON Parsing Error: {e}")
            return None
            
    # प्राधान्य २: लोकल credentials.json फाईल (केवळ डेव्हलपमेंटसाठी)
    if os.path.exists('credentials.json'):
        return ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        
    return None

# ग्लोबल व्हेरिएबल म्हणून शीट सेट करणे
try:
    creds = get_gspread_client()
    if creds:
        client = gspread.authorize(creds)
        # तुमच्या Google Sheet चे नाव तपासा: "Data Collection"
        sheet = client.open("Data Collection").sheet1
    else:
        sheet = None
        print("Credentials not found in environment or file.")
except Exception as e:
    print(f"Critical Connection Error: {e}")
    sheet = None

@app.route('/')
def index():
    villages_data = {'नांदगाव': [], 'मालेगाव': []}
    
    # फाईल्सची नावे (Case-Sensitive - तुमच्या GitHub वर जशी आहेत तशी)
    # GitHub वर 'Nandgaon.txt' आणि 'Malegaon.txt' अशी आहेत
    files = {'नांदगाव': 'Nandgaon.txt', 'मालेगाव': 'Malegaon.txt'}
    
    for taluka, filename in files.items():
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    villages_data[taluka] = [line.strip() for line in f if line.strip()]
            else:
                print(f"Missing File: {filename}")
        except Exception as e:
            print(f"File Error ({filename}): {e}")
    
    return render_template('index.html', villages_data=villages_data)

@app.route('/submit', methods=['POST'])
def submit():
    if not sheet:
        return "<h2 style='color:red;'>एरर: गुगल शीटशी संपर्क होऊ शकला नाही. कृपया Environment Variables तपासा!</h2>"
    
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
        <div style='text-align:center; font-family:sans-serif; margin-top:50px;'>
            <h2 style='color:green;'>माहिती यशस्वीरित्या जतन झाली!</h2>
            <a href='/' style='text-decoration:none; color:blue;'>परत जा</a>
        </div>
        """
    except Exception as e:
        return f"<h2 style='color:red;'>डेटा सेव्ह करताना चूक झाली: {e}</h2>"

if __name__ == '__main__':
    app.run(debug=True)
