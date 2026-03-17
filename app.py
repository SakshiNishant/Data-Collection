import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request
from datetime import datetime # तारीख आणि वेळेसाठी नवीन लायब्ररी

app = Flask(__name__)

# --- Google Sheet कनेक्शन सेटअप ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
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
        # १. सध्याची तारीख आणि वेळ मिळवणे (उदा. 16-03-2026 15:10:05)
        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        
        # २. फॉर्ममधून सर्व माहिती गोळा करणे
        data = [
            now, # पहिला कॉलम (तारीख आणि वेळ)
            request.form.get('full_name'),
            request.form.get('dob'),
            request.form.get('mobile'),
            request.form.get('taluka'),
            request.form.get('village'),
            request.form.get('gender'),
            request.form.get('occupation')
        ]
        
        # ३. गुगल शीटमध्ये डेटा जतन करणे
        sheet.append_row(data)
        
        return """
        <div style='text-align:center; font-family:Arial; padding-top:50px;'>
            <h2 style='color: #28a745;'>तुमची माहिती यशस्वीरित्या जतन झाली!</h2>
            <p><a href='/'>परत जा</a></p>
        </div>
        """
    except Exception as e:
        return f"<h2 style='color:red; text-align:center;'>डेटा जतन करताना चूक झाली: {e}</h2>"

if __name__ == '__main__':
    app.run(debug=True)
