import nltk
import openai
openai.api_key = "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"
def get_factual_answer(query):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # or "gpt-3.5-turbo" for more powerful models
            prompt=query,
            max_tokens=150,  # Limit the number of tokens (words/characters)
            n=1,  # Only return 1 answer
            stop=None,
            temperature=0.5,  # Control the randomness of the response (0 to 1)
        )
        return response.choices[0].text.strip()  # Extract the answer text from the response
    except Exception as e:
        return f"Error with OpenAI API: {e}"

from nltk.chat.util import Chat, reflections
import datetime
import requests
import json
from textblob import TextBlob

# Configuration
WOLFRAM_API_KEY = "LWP4GW-J75WY65WUR" # Replace with your WolframAlpha API key
WEATHER_API_KEY = "c94f98bac986a3f0a62c7c88a91bf377" # Replace with your OpenWeatherMap API key
TODO_FILE = "tasks.json"  # File to store to-do list persistently

# To-Do List
todo_list = []

# Reflections
reflections.update({
    "i'm": "you are",
    "was": "were",
    "i": "you",
    "my": "your",
    "am": "are",
    "you": "me",
    "are": "am"
})

# Load To-Do List
def load_tasks():
    global todo_list
    try:
        with open(TODO_FILE, "r") as file:
            todo_list = json.load(file)
    except FileNotFoundError:
        todo_list = []

# Save To-Do List
def save_tasks():
    with open(TODO_FILE, "w") as file:
        json.dump(todo_list, file)

# Sentiment Analysis
def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0:
        return "positive"
    elif polarity < 0:
        return "negative"
    else:
        return "neutral"

# Fetch Weather Data
def get_weather(city, forecast_date=None):
    try:
        base_url = f"http://api.openweathermap.org/data/2.5/"
        if forecast_date:  # For future weather forecasts
            url = f"{base_url}forecast?q={city}&appid={WEATHER_API_KEY}&units=metric"
            response = requests.get(url)
            data = response.json()
            if "list" in data:
                for forecast in data["list"]:
                    forecast_time = datetime.datetime.strptime(forecast["dt_txt"], "%Y-%m-%d %H:%M:%S")
                    if forecast_time.date() == forecast_date.date():
                        temp = forecast["main"]["temp"]
                        description = forecast["weather"][0]["description"]
                        return f"The weather in {city} on {forecast_date.strftime('%Y-%m-%d')} will be {description} with a temperature of {temp}°C."
        else:  # Current weather
            url = f"{base_url}weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
            response = requests.get(url)
            data = response.json()
            if data["cod"] == 200:
                temp = data["main"]["temp"]
                description = data["weather"][0]["description"]
                return f"The current weather in {city} is {description} with a temperature of {temp}°C."
        return f"Sorry, I couldn't find weather information for {city}."
    except Exception as e:
        return "Error fetching weather data. Please try again later."

# Fetch Factual Data
def get_factual_answer(query):
    try:
        import wolframalpha
        client = wolframalpha.Client(WOLFRAM_API_KEY)
        res = client.query(query)
        return next(res.results).text
    except Exception:
        return "I couldn't find an answer to that question."

# Chatbot Class
class EnhancedChatbot(Chat):
    def converse(self, quit="quit"):
        print("Chatbot: Hi! Type 'quit' to exit.")
        load_tasks()  # Load tasks at the start
        while True:
            user_input = input("You: ").lower()
            if user_input == quit:
                print("Chatbot: Goodbye! Take care.")
                save_tasks()  # Save tasks on exit
                break

            sentiment = analyze_sentiment(user_input)
            if sentiment == "positive":
                print("Chatbot: You seem happy!")
            elif sentiment == "negative":
                print("Chatbot: I'm here to help. What's wrong?")

            # Weather Query
            if "weather in" in user_input:
                city = user_input.split("weather in")[-1].strip()
                forecast_date = None
                if "tomorrow" in user_input:
                    forecast_date = datetime.datetime.now() + datetime.timedelta(days=1)
                print(f"Chatbot: {get_weather(city, forecast_date)}")
                continue

            # Factual Query
            elif "factual question" in user_input:
                query = user_input.split("factual question")[-1].strip()
                print(f"Chatbot: {get_factual_answer(query)}")
                continue

            # To-Do List Management
            elif "add task" in user_input:
                task = user_input.split("add task")[-1].strip()
                todo_list.append(task)
                print(f"Chatbot: Task '{task}' added.")
                continue

            elif "view tasks" in user_input:
                if todo_list:
                    print("Chatbot: Here are your tasks:")
                    for i, task in enumerate(todo_list, start=1):
                        print(f"{i}. {task}")
                else:
                    print("Chatbot: Your to-do list is empty.")
                continue

            elif "delete task" in user_input:
                task = user_input.split("delete task")[-1].strip()
                if task in todo_list:
                    todo_list.remove(task)
                    print(f"Chatbot: Task '{task}' removed.")
                else:
                    print(f"Chatbot: Task '{task}' not found.")
                continue

            # Standard Responses
            response = self.respond(user_input)
            print(f"Chatbot: {response}")

# Enhanced Pairs
pairs = [
    [r"hi|hello|hey", ["Hello! How can I assist you?", "Hi there! What's on your mind?"]],
    [r"what is your name ?", ["I am SmartBot. What's your name?", "You can call me SmartBot!"]],
    [r"my name is (.*)", ["Nice to meet you, %1! How can I assist you today?"]],
    [r"(.*) time", [f"The current time is {datetime.datetime.now().strftime('%H:%M:%S')}."]],
    [r"(.*) date", [f"Today's date is {datetime.datetime.now().strftime('%Y-%m-%d')}"]],
    [r"(.*) joke", ["Why don't programmers like nature? It has too many bugs!", "Why do Java developers wear glasses? Because they don’t C#!"]],
    [r"quit", ["Goodbye! Have a great day!", "See you later!"]],
    [r"(.*)", ["I didn't understand that. Can you rephrase?"]],
]

# Run Chatbot
if __name__ == "__main__":
    chatbot = EnhancedChatbot(pairs, reflections)
    chatbot.converse()
