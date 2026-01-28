import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import threading
import requests
import pyttsx3
import speech_recognition as sr
import time
from datetime import datetime, timedelta
import os

# 🔑 PUT YOUR API KEY HERE
API_KEY = "YOUR_OPENWEATHER_API_KEY"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ✅ ICON PATHS (MATCHING YOUR GITHUB FILES)
ICON_PATHS = {
    "clear": os.path.join(BASE_DIR, "icons", "sunny.png"),
    "clouds": os.path.join(BASE_DIR, "icons", "cloudy.png"),
    "rain": os.path.join(BASE_DIR, "icons", "rainy.png"),
    "drizzle": os.path.join(BASE_DIR, "icons", "rainy.png"),
    "thunderstorm": os.path.join(BASE_DIR, "icons", "rainy.png"),
    "snow": os.path.join(BASE_DIR, "icons", "cold.png"),   # ✅ FIXED
    "mist": os.path.join(BASE_DIR, "icons", "cloudy.png"),
    "haze": os.path.join(BASE_DIR, "icons", "cloudy.png"),
    "fog": os.path.join(BASE_DIR, "icons", "cloudy.png"),
    "smoke": os.path.join(BASE_DIR, "icons", "cloudy.png"),
    "wind": os.path.join(BASE_DIR, "icons", "windy.png"),
    "default": os.path.join(BASE_DIR, "icons", "default.png")
}


def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def suggest_clothes(temp, condition):
    condition = condition.lower()

    if "snow" in condition:
        return "It's snowy! Wear a thermal coat, insulated boots, gloves, and a beanie."
    elif "rain" in condition or "drizzle" in condition or "thunderstorm" in condition:
        return "It's rainy. Wear a waterproof raincoat, non-slip boots, and carry an umbrella."
    elif "cloud" in condition or "mist" in condition or "fog" in condition:
        if temp < 15:
            return "It's chilly and cloudy. Wear a sweater, scarf, and jacket."
        return "Cloudy skies. A long-sleeve shirt or light jacket will be perfect."
    elif "clear" in condition or "sun" in condition:
        if temp < 15:
            return "It's sunny but cold. Pair a stylish coat with sunglasses."
        elif temp <= 25:
            return "Perfect clear weather! Wear breathable cotton or linen outfits."
        else:
            return "It's hot and sunny. Light-colored clothes, sunglasses, and a hat are ideal."
    elif "wind" in condition:
        return "It's windy. Wear a windbreaker or denim jacket."

    if temp < 10:
        return "It's quite cold. Layer up with thermals, a coat, and boots."
    elif temp < 20:
        return "Cool temperature. A hoodie or jacket with jeans will work."
    elif temp < 30:
        return "Mild weather. Opt for a T-shirt and light pants."
    else:
        return "Very hot. Choose breathable fabrics like cotton and stay hydrated."


class AttireForecastApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Attire Forecast")
        self.root.geometry("1000x650")
        self.root.configure(bg="black")

        self.engine = pyttsx3.init()
        self.voice_enabled = True
        self.stopped = False

        self.container = tk.Frame(self.root, bg="black")
        self.container.pack(fill="both", expand=True)

        tk.Label(
            self.container,
            text="ATTIRE FORECAST",
            font=("Segoe UI Black", 32),
            fg="white",
            bg="black"
        ).pack(pady=10)

        tk.Label(
            self.container,
            text="Where Climate Meets Comfort",
            font=("Segoe UI", 18, "italic"),
            fg="#CCCCCC",
            bg="black"
        ).pack()

        tk.Label(
            self.container,
            text="Search any city & get smart outfit recommendations",
            font=("Segoe UI", 14),
            fg="white",
            bg="black"
        ).pack(pady=10)

        self.city_entry = tk.Entry(self.container, font=("Segoe UI", 14), width=30)
        self.city_entry.pack(pady=10)

        tk.Button(
            self.container, text="🔍 Search",
            command=self.fetch_weather,
            font=("Segoe UI", 12)
        ).pack(pady=5)

        tk.Button(
            self.container, text="🎤 Voice Input",
            command=self.voice_input,
            font=("Segoe UI", 12)
        ).pack(pady=5)

        self.icon_label = tk.Label(self.container, bg="black")
        self.icon_label.pack(pady=10)
        self.update_weather_icon("default")

        self.result_label = tk.Label(
            self.container,
            text="",
            font=("Segoe UI", 14),
            fg="white",
            bg="black",
            wraplength=800,
            justify="center"
        )
        self.result_label.pack(pady=20)

    def fetch_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name.")
            return

        data = get_weather(city)
        if not data:
            self.result_label.config(text="City not found.")
            return

        condition = data["weather"][0]["description"]
        temp = data["main"]["temp"]

        dt = data["dt"]
        timezone = data["timezone"]
        local_time = datetime.utcfromtimestamp(dt) + timedelta(seconds=timezone)
        hour = local_time.hour

        if 5 <= hour < 12:
            part = "Morning"
        elif 12 <= hour < 17:
            part = "Afternoon"
        elif 17 <= hour < 21:
            part = "Evening"
        else:
            part = "Night"

        suggestion = suggest_clothes(temp, condition)

        result = (
            f"City: {city}\n"
            f"Time: {part}\n"
            f"Weather: {condition.capitalize()}\n"
            f"Temperature: {temp}°C\n\n"
            f"👗 Suggestion:\n{suggestion}"
        )

        self.update_weather_icon(condition)
        self.result_label.config(text=result)
        self.speak(result)

    def update_weather_icon(self, condition):
        condition = condition.lower()
        key = "default"

        if "clear" in condition:
            key = "clear"
        elif "rain" in condition:
            key = "rain"
        elif "cloud" in condition:
            key = "clouds"
        elif "snow" in condition:
            key = "snow"

        path = ICON_PATHS.get(key, ICON_PATHS["default"])
        img = Image.open(path).resize((100, 100))
        icon = ImageTk.PhotoImage(img)
        self.icon_label.config(image=icon)
        self.icon_label.image = icon

    def speak(self, text):
        if self.voice_enabled:
            threading.Thread(
                target=lambda: (self.engine.say(text), self.engine.runAndWait()),
                daemon=True
            ).start()

    def voice_input(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.speak("Please say the city name")
            audio = r.listen(source)
            try:
                city = r.recognize_google(audio)
                self.city_entry.delete(0, tk.END)
                self.city_entry.insert(0, city)
                self.fetch_weather()
            except:
                self.speak("Sorry, could not understand.")


if __name__ == "__main__":
    root = tk.Tk()
    app = AttireForecastApp(root)
    root.mainloop()
