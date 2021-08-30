
from flask import Flask, request, render_template,Response,jsonify
from camera import VideoCamera
from flask_cors import CORS
import firebase_admin
from firebase_admin import firestore
import qrcode
import dateutil
from dateutil import parser
from datetime import datetime
import smtplib
import ssl
from textblob import TextBlob

cred_obj = firebase_admin.credentials.Certificate(
    'techblazers-293ce-firebase-adminsdk-r9ll9-a478a1ae50.json')
default_app = firebase_admin.initialize_app(cred_obj)

app = Flask(__name__, static_url_path='/static')
CORS(app)

@app.route('/')
def serve_login():
    return render_template("main_page.html")

@app.route('/register')
def serve_register():
    return render_template("register.html")


@app.route("/makeqrcodeandsetupfirebase", methods=["POST"])
def make_database_from_info_and_return_the_qrcode():
    todays_date = datetime.today().strftime('%Y-%m-%d')
    dob, email, gender, height, id, name, photoURL, weight = request_fields_from_form()
    db = firestore.client()

    doc_ref = db.collection(u'users').document(id)

    data = {
        u'name': name,
        u'dob': dob,
        u'gender': gender,
        u'height': height,
        u'weight': weight,
        u'photoURL': photoURL,
        u'email': email,
        u'date_updated': todays_date,
        u'last_feedback_polarity': 0,
        u'total_messages': 0,
        u'total_feedback_polarity': 0,
        u'list_of_messages': []
    }
    doc_ref.set(data)
    make_qr_codes(id)
    print("Made qr code")
    return "Made Image"


def request_fields_from_form():
    name = request.form["name"]
    dob = request.form["dob"]
    gender = request.form["gender"]
    height = request.form["height"]
    weight = request.form["weight"]
    id = request.form["id"]
    photoURL = request.form["photoURL"]
    email = request.form["email"]
    return dob, email, gender, height, id, name, photoURL, weight


def make_qr_codes(id):
    import os
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(id)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    path_to_save_image = os.path.join(
        os.getcwd(), "static", "id_images", f'{id}.png')
    img.save(path_to_save_image)


@app.route('/management')
def serve_management():
    db = firestore.client()
    doc_ref = db.collection(u'users').stream()
    all_users = []
    for users in doc_ref:
        all_users.append(users.to_dict())
    return render_template("management.html", users=all_users)

@app.route('/details')
def serve_details():
    return render_template("details.html")

@app.route('/profile/<id>', methods=['GET'])
def serve_profile(id):
    existing_data = get_dict_for_document_and_collection(id, 'users')
    return render_template("profile.html", data=existing_data)

def get_dict_for_document_and_collection(document, collection):
    db = firestore.client()
    doc_ref = db.collection(collection).document(document)
    doc = doc_ref.get()
    existing_data = doc.to_dict()
    return existing_data

@app.route('/camera')
def index():
    return render_template('camera.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/emoji')
def emoji():
    return render_template('emoji.html')

def emoji_gen(camera):
    while True:
        frame = camera.get_emoji()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/emoji_video_feed')
def emoji_video_feed():
    return Response(emoji_gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    
@app.route('/chat')
def server_chat():
    return render_template('chat.html')


@app.route('/analyze_text',methods=['POST'])
def analyse_and_add_data():
    db = firestore.client()
    message_content = request.form["chat"]
    id = request.form["id"]
    author_name = request.form["author_name"]
    email = request.form["email"]
    doc_ref = db.collection(u'messages').document(str(id))
    if not doc_ref.get().exists:
        print("data not in ")
        send_data_to_server(doc_ref, 0, 0, 0, author_name, [])
    data_user = doc_ref.get().to_dict()
    feedback_polarity = TextBlob(message_content).sentiment.polarity
    last_feedback_polarity = float(data_user['last_feedback_polarity'])
    total_feedback_polarity = last_feedback_polarity+feedback_polarity
    total_messages = int(data_user['total_messages'])+1
    list_of_messages = list(data_user['list_of_messages'])
    list_of_messages.append(message_content)
    send_data_to_server(
        doc_ref, feedback_polarity, total_messages, total_feedback_polarity, author_name, list_of_messages)
    if total_messages > 4 and total_feedback_polarity < 0:
        send_email(email,
                        f'{author_name} is feeling down', 'mental health app alert')
    return jsonify(feedback_polarity=feedback_polarity)
    
def send_data_to_server(doc_ref, feedback_polarity, total_messages, total_feedback_polarity, author_name, list_of_messages):
    data = {
        u'last_feedback_polarity': feedback_polarity,
        u'total_messages': total_messages,
        u'total_feedback_polarity': total_feedback_polarity,
        u'person_name': author_name,
        u'list_of_messages': list_of_messages
    }
    doc_ref.set(data, merge=True)
    print("data sent:", data)
    return doc_ref

def send_email(email, message, SUBJECT):
    port = 587  
    smtp_server = "smtp.gmail.com"
    sender_email = 'pogchampvignesh123@gmail.com'
    receiver_email = email
    password = "vigneshisbae123"
    message = message
    message = 'Subject: {}\n\n{}'.format(SUBJECT, message)

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
if __name__ == '__main__':
    app.run(debug=True)
