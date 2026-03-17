import os
from flask import Flask, render_template, request

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route('/')
def index():
    villages_data = {'नांदगाव': [], 'मालेगाव': []}
    
    # फाईल्सचे पाथ (Main directory मध्ये शोधण्यासाठी)
    file_paths = {
        'नांदगाव': 'Nandgaon.txt',
        'मालेगाव': 'Malegaon.txt'
    }
    
    for taluka, file_name in file_paths.items():
        if os.path.exists(file_name):
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    # प्रत्येक ओळीवरील गाव वाचणे आणि रिकाम्या ओळी काढणे
                    villages_data[taluka] = [line.strip() for line in f if line.strip()]
            except Exception as e:
                print(f"Error reading {file_name}: {e}")
    
    return render_template('index.html', villages_data=villages_data)

# मोबाईल नंबर व्हॅलिडेशन सबमिट करताना देखील चेक होईल
@app.route('/submit', methods=['POST'])
def submit():
    mobile = request.form.get('mobile')
    if len(mobile) != 10:
        return "<h2>चूक: मोबाईल नंबर १० अंकी असावा!</h2><a href='/'>परत जा</a>"
    
    # इथे तुमचा Google Sheets चा डेटा जतन करण्याचा कोड असेल...
    return "<h2>माहिती यशस्वीरित्या जतन झाली!</h2><a href='/'>परत जा</a>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
