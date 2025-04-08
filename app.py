import os
import mimetypes
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from apscheduler.schedulers.background import BackgroundScheduler
import smtplib, os
from email.message import EmailMessage
from datetime import datetime

UPLOAD_FOLDER = 'uploads'
EMAIL_ADDRESS = 'carlosroman3141@gmail.com'
EMAIL_PASSWORD = 'xwuipisdyzubddav'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs('uploads', exist_ok=True)
scheduler = BackgroundScheduler()
scheduler.start()

def send_email(to, subject, body, files=[]):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to
    msg.set_content(body)

    for file_path in files:
        try:
            ctype, encoding = mimetypes.guess_type(file_path)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)

            with open(file_path, 'rb') as f:
                file_data = f.read()
                filename = os.path.basename(file_path)
                msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=filename)
        except Exception as e:
            print(f"Error adjuntando archivo {file_path}: {e}")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print("Correo enviado con éxito.")
            
        # Eliminar los archivos después de enviar el correo
        for file_path in files:
            try:
                os.remove(file_path)
                print(f"Archivo {file_path} eliminado exitosamente.")
            except Exception as e:
                print(f"Error al eliminar el archivo {file_path}: {e}")

    except Exception as e:
        print(f"Error al enviar el correo: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        subject = request.form['subject']
        body = request.form['body']
        send_time = request.form['send_time']

        send_dt = datetime.strptime(send_time, "%Y-%m-%dT%H:%M")
        files = request.files.getlist('files')
        saved_files = []

        for file in files:
            if file.filename != '':
                filename = secure_filename(file.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(path)
                saved_files.append(path)

        # El correo siempre va al EMAIL_ADDRESS definido
        scheduler.add_job(send_email, 'date', run_date=send_dt,
                          args=[EMAIL_ADDRESS, subject, body, saved_files])

        return redirect(url_for('index'))

    return render_template('index.html')

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
