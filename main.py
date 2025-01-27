import requests
import subprocess
import time
import re
import speech_recognition as sr
import os
import pyttsx3
import webbrowser
import smtplib
import openai
import datetime
from config import apikey , email_address,email_password ,weather_api_key ,base_url


def run_movie_recommender():
    # Replace with your actual path to Streamlit and the movie recommender system directory
    streamlit_path = r"C:\Users\Kiran Dunka\AppData\Local\Programs\Python\Python39\Scripts\streamlit.exe"
    app_directory = r"C:\Users\Kiran Dunka\PycharmProjects\movies_rrecommender_system"

    try:
        # Command to run Streamlit and your application
        command = [streamlit_path, "run", "app.py"]  # Replace "app.py" with your main Streamlit script

        # Change directory to your movie recommender system directory
        os.chdir(app_directory)

        # Launch the Streamlit application
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE)

        # Wait a few seconds for Streamlit to start serving the app
        time.sleep(5)

        # Open the Streamlit app in the default browser
        os.system("start http://localhost:8501")

        print("Movie recommender system is running...")
    except Exception as e:
        print(f"Error running movie recommender system: {e}")


chatStr = ""
def chat(query):
    global chatStr
    print(chatStr)
    openai.api_key = apikey
    chatStr += f"Kiran: {query}\n senorita: "
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=chatStr,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    # todo: Wrap this inside of a  try catch block
    say(response["choices"][0]["text"])
    chatStr += f"{response['choices'][0]['text']}\n"
    return response["choices"][0]["text"]
def ai(prompt):
    openai.api_key = apikey
    text = f"openAI response for prompt: {prompt} \n**********************\n\n"

    response = openai.completions.create(
        model="davinci-002",
        prompt=prompt,
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    print(response["choices"][0]["text"])
    text += response["choices"][0]["text"]
    if not os.path.exists("Openai"):
        os.mkdir("Openai")
    with open(f"Openai/{''.join(prompt.split('intelligence')[1:]).strip()}.txt", "w") as f:
        f.write(text)


def open_and_search(query):
    for site in sites:
        if f"open {site[0]}".lower() in query.lower():
            # Extract the search term from the query
            search_term = query.lower().replace(f"open {site[0]}", "").strip()
            if search_term:
                search_url = site[1].format(search_term.replace(" ", "+"))
                say(f"Searching for {search_term} on {site[0]}")
                webbrowser.open(search_url)
            else:
                say(f"Opening {site[0]}...")
                webbrowser.open(site[1].format(""))


def sendEmail(to, content):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(email_address, email_password)
        server.sendmail(email_address, to, content)
        server.close()
        print("Email has been sent!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def kelvin_to_celsius(kelvin):
    return kelvin - 273.15

def get_weather(city_name):
    try:
        complete_url = f"{base_url}weather?q={city_name}&appid={weather_api_key}"
        response = requests.get(complete_url)
        data = response.json()

        if data['cod'] != '404':
            main = data['main']
            weather = data['weather'][0]
            temperature = kelvin_to_celsius(main['temp'])
            pressure = main['pressure']
            humidity = main['humidity']
            description = weather['description']

            weather_report = (
                f"Weather in {city_name}:\n"
                f"Temperature: {temperature:.2f}°C\n"
                f"Pressure: {pressure} hPa\n"
                f"Humidity: {humidity}%\n"
                f"Description: {description.capitalize()}"
            )
            return weather_report
        else:
            return "City not found."

    except Exception as e:
        return f"Error occurred: {e}"

# def list_voices(): # this method is only to genrtate the key or value path  of the voices
#     engine = pyttsx3.init()
#     voices = engine.getProperty('voices')
#     for voice in voices:
#         print(f"Voice ID: {voice.id}")
#         print(f"Name: {voice.name}")
#         print(f"Languages: {voice.languages}")
#         print(f"Gender: {voice.gender}")
#         print(f"Age: {voice.age}\n")
#
# list_voices()


def say(text):
    engine = pyttsx3.init()

    # Set the female voice by specifying the voice ID for Microsoft Zira Desktop
    engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0')

    # Set the speech rate and volume if needed
    engine.setProperty('rate', 150)  # Speed of speech (default is usually around 200)
    engine.setProperty('volume', 1.0)  # Volume level (0.0 to 1.0)

    engine.say(text)
    engine.runAndWait()

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        # print("Adjusting for ambient noise...")
        r.adjust_for_ambient_noise(source, duration=1)  # Helps with background noise
        # r.pause_threshold = 0.2
        audio = r.listen(source)
        try:
            print("Recognizing.....")
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query
        except Exception as e:
            return "Some error occurred, sorry from senorita."



if __name__ == '__main__':
    print('PyCharm')
    say("hello this is senorita AI how can i help you")
    while True:
        print("Listining...")
        query = takeCommand()
        # sites = [["youtube","https://youtube.com"] , ["wikipedia","https://wekipedia.com"], ["google","https://google.com"]]
        sites = [
            ["youtube", "https://www.youtube.com/results?search_query={}"],
            ["wikipedia", "https://en.wikipedia.org/wiki/{}"],
            ["google", "https://www.google.com/search?q={}"]

        ]


        open_and_search(query)


        if "the time".lower() in query.lower():
            hour = datetime.datetime.now().strftime("%H")
            min = datetime.datetime.now().strftime("%M")
            say(f"the time is{hour} hour and {min} minutes dear...")

        elif "hello".lower() in query.lower():
            say("Hello! How can I help you today?")

        elif "weather" in query.lower():

            match = re.search(r"weather (in|for|at|of|in the city of)\s*([\w\s]+)", query.lower())

            if match:
                city_name = match.group(2).strip()  # Capture and strip any extra spaces from the city name
                weather_report = get_weather(city_name)
                print(weather_report)
            else:
                print("Please specify a city name.")


        elif "email".lower() in query.lower():
            try:
                say("What should i say?")
                content = takeCommand()
                to = "gauthamboolu@gmail.com"
                sendEmail(to , content)
                say("Email has been sent!")
            except Exception as e:
                print(e)
                say("Sorry the email has not been sent!")

        elif "open movie recommender".lower() in query.lower():

            run_movie_recommender()

        elif "using artificial intelligence".lower() in query.lower():
            ai(prompt=query)

        elif " exit".lower() in query.lower():
            say("Bye have a good day")
            exit()


        # else:
        #     print("Chatting...")
        #     chat(query)

        # say(query)


