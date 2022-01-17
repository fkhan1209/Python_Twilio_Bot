import os
from dotenv import load_dotenv
from pyngrok import ngrok
from twilio.rest import Client
from flask import Flask, request
from twilio.twiml.messaging_response import Message, MessagingResponse
import wolframalpha
import wikipedia
import yweather

app = Flask(__name__)

wolfram_app_id = "R2RG6H-9RUGG8EX3Y"
wolf = wolframalpha.Client(wolfram_app_id)
weath = yweather.Client()
    
@app.route('/', methods=['POST'])
def sms():
    message_body = request.form['Body']

    resp = MessagingResponse()
    
    replyText = getReply(message_body)
    resp.message('Hi Farib!\n' + replyText )
    return str(resp)

def start_ngrok():
    url = ngrok.connect(5000).public_url
    print(' * Tunnel URL:', url)
    account_sid = 'AC51fd0dfd7df94596da4a88fc018f1084'
    auth_token = '1f693b12d366e8f20999b3a97f80031c' 
    client = Client(account_sid, auth_token)
    client.incoming_phone_numbers.list(
        phone_number=os.environ.get('TWILIO_PHONE_NUMBER'))[0].update(
            sms_url=url)

def removeHead(fromThis, removeThis):
    if fromThis.endswith(removeThis):
        fromThis = fromThis[:-len(removeThis)].strip()
    elif fromThis.startswith(removeThis):
        fromThis = fromThis[len(removeThis):].strip()
    
    return fromThis

def getReply(message):
    
    message = message.lower().strip()
    answer = ""
    if "schedule" in message:
        if "monday" in message:
            answer = "Your Monday schedule:\n9:00 AM to 10:15 AM: Monday Morning Kickoff\n10:30 AM to 11:45 AM: CIS403 \n11:45 AM to 12:30 PM: Lunch \n12:30 PM to 1:45 PM: COM150 \n2:00 PM to 3:15 PM: LLT \n3:30 PM to 4:45 PM: CIS303"
        elif "tuesday" in message:
            answer = "Your Tuesday schedule:\n9:00 AM to 10:15 AM: CIS403 \n10:30 AM to 11:45 AM: CIS404 \n11:45 AM to 12:30 PM: Lunch \n12:30 PM to 1:45 PM: COM150 \n2:00 PM to 3:15 PM: BUS103 \n3:30 PM to 4:45 PM: CIS303"
        elif "wednesday" in message:
            answer = "Your Wednesday schedule:\n9:00 AM to 10:15 AM: CIS403 \n10:30 AM to 11:45 AM: CIS404 \n11:45 AM to 12:30 PM: Lunch \n12:30 PM to 1:45 PM: COM150"
        elif "thursday" in message:
            answer = "Your Thursday schedule:\n9:00 AM to 10:15 AM: CIS404 \n10:30 AM to 11:45 AM: CIS403 \n11:45 AM to 12:30 PM: Lunch \n12:30 PM to 1:45 PM: COM150 \n2:00 PM to 3:15 PM: CIS303 (Asynchronous) \n3:30 PM to 4:45 PM: CIS404"
        elif "friday" in message:
            answer = "Your Friday schedule:\n9:00 AM to 10:00 AM: Instructor Office Hours \n10:00 AM to 11:30 AM: Friday Feedback \n11:45 AM to 12:45 PM: Developing YU Series"
            
    elif "wolfram" in message:
        message = removeHead(message, "wolfram")
        
        res = wolf.query(message)
        try:
            answer = next(res.results).text
        except:
            answer = "Request was not found using wolfram. Be more specific?"
    
    elif "wiki" in message:
        message = removeHead(message, "wiki")
        try:
            answer = wikipedia.summary(message)
        except:
            answer = "Request was not found using wiki. Be more specific?"

    elif "weather" in message:

        message = removeHead(message, "weather").trim()
        message = removeHead(message, "for").trim()
        
        try:
            woeID = weath.fetch_woeid(message)
            lid = weath.fetch_lid(woeID)
            myWeather = weath.fetch_weather(lid)
            answer = "" + myWeather["title"] + "\n" + myWeather["condition"]["temp"] + "\n" + myWeather["condition"]["text"] + "\n" + "Humidity: " + myWeather["atmosphere"]["humidity"] + "\n" + "Wind: " + myWeather["wind"]["speed"] + "\n" + "Wind chill: " + myWeather["wind"]["chill"] + "\n"
        except:
            answer = "Something went wrong while getting the weather."
    
    else:
        answer = "\n Welcome! These are the commands you may use: \nSCHEDULE + \"day\" + DAY\nWOLFRAM \"wolframalpha request\" \nWIKI \"wikipedia request\"\nWEATHER \"place\"\n"
    
    if len(answer) > 1500:
        answer = answer[0:1500] + "..."
    return answer

if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        start_ngrok()
    app.run()