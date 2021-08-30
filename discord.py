from textblob import TextBlob
import discord
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import smtplib
import ssl
cred = credentials.Certificate(
    "techblazers-293ce-firebase-adminsdk-r9ll9-a478a1ae50.json")


firebase_admin.initialize_app(cred)
TOKEN = 'ODc4NDgxOTYyNjQ4NjIxMTI2.YSB0FQ.96H6R8Ix7xqVsqETpw3bc5UA1L4'


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        author_id = message.author.id
        author_name = message.author.display_name
        if message.content:
            message_content = message.content
            mental_health = MentalHealth()
            mental_health.analyse_and_add_data(
                message_content, author_id, author_name)
        if len(message.attachments) > 0:
            attachment = message.attachments[0]
        else:
            return
        if attachment.filename.endswith(".jpg") or attachment.filename.endswith(".jpeg") or attachment.filename.endswith(".png") or attachment.filename.endswith(".webp") or attachment.filename.endswith(".gif"):
            self.image = attachment.url
        elif "https://images-ext-1.discordapp.net" in message.content or "https://tenor.com/view/" in message.content:
            self.image = message.content


class MentalHealth:
    def __init__(self):

        self.db = firestore.client()

    def analyse_and_add_data(self, message_content, author_id, author_name):

        doc_ref = self.db.collection(u'messages').document(str(author_id))
        if not doc_ref.get().exists:
            print("data not in ")
            self.send_data_to_server(doc_ref, 0, 0, 0, author_name, [])
        data_user = doc_ref.get().to_dict()
        feedback_polarity = TextBlob(message_content).sentiment.polarity
        last_feedback_polarity = float(data_user['last_feedback_polarity'])
        total_feedback_polarity = last_feedback_polarity+feedback_polarity
        total_messages = int(data_user['total_messages'])+1
        list_of_messages = list(data_user['list_of_messages'])
        list_of_messages.append(message_content)
        self.send_data_to_server(
            doc_ref, feedback_polarity, total_messages, total_feedback_polarity, author_name, list_of_messages)
        if total_messages > 10 and total_feedback_polarity < 0:
            self.send_email('themoviechannel77@gmail.com',
                            f'{author_name} is feeling down', 'mental health app alert')

    def send_data_to_server(self, doc_ref, feedback_polarity, total_messages, total_feedback_polarity, author_name, list_of_messages):
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

    def analyse_images(self, image_url):
        from fer import FER
        import matplotlib.pyplot as plt
        import urllib2
        image_steam = urllib2.urlopen(image_url)
        image = plt.imread(image_steam)
        emo_detector = FER(mtcnn=True)
        captured_emotions = emo_detector.detect_emotions(image)
        print("captured emoji", captured_emotions)



client = MyClient()
client.run(TOKEN)
