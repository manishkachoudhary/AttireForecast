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

API_KEY = "YOUR_OPENWEATHER_API_KEY"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ICON_PATHS = {
    "clear": os.path.join(BASE_DIR, "icons", "sunny.png"),
    "clouds": os.path.join(BASE_DIR, "icons", "cloudy.png"),
    "rain": os.path.join(BASE_DIR, "icons", "rainy.png"),
    "drizzle": os.path.join(BASE_DIR, "icons", "rainy.png"),
    "thunderstorm": os.path.join(BASE_DIR, "icons", "rainy.png"),
    "snow": os.path.join(BASE_DIR, "icons", "snowy.png"),
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
        return "It's windy. Wear a windbreaker or denim jacket to stay comfortable."

    if temp < 10:
        return "It's quite cold. Layer up with thermals, a coat, and boots."
    elif temp < 20:
        return "Cool temperature. A hoodie or jacket with jeans will work."
    elif temp < 30:
        return "Mild weather. Opt for a T-shirt and light pants or dress."
    else:
        return "Very hot. Choose breathable fabrics like cotton and drink plenty of water."

class AttireForecastApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Attire Forecast")
        self.root.geometry("1000x650")
        self.root.configure(bg='black')

        self.engine = pyttsx3.init()
        self.voice_enabled = True
        self.theme_color = tk.StringVar(value="dark")
        self.stopped = False
        self.speaking = False

        self.container = tk.Frame(self.root, bg='black')
        self.container.pack(fill="both", expand=True)

        self.title = tk.Label(self.container, text="ATTIRE FORECAST", font=("Segoe UI Black", 32), fg="white", bg="black")
        self.title.pack(pady=10)

        self.subtitle = tk.Label(self.container, text="Where Climate Meets Comfort", font=("Segoe UI", 18, "italic"), fg="#CCCCCC", bg="black")
        self.subtitle.pack()

        self.info = tk.Label(self.container, text="Hello! Search weather for any city and get stylish clothing suggestions.", font=("Segoe UI", 14), fg="white", bg="black")
        self.info.pack(pady=10)

        self.city_entry = tk.Entry(self.container, font=("Segoe UI", 14), width=30)
        self.city_entry.pack(pady=10)

        self.search_btn = tk.Button(self.container, text="🔍 Search", command=self.fetch_weather, font=("Segoe UI", 12), bg="#444", fg="white")
        self.search_btn.pack(pady=5)

        self.voice_btn = tk.Button(self.container, text="🎤 Voice Input", command=self.voice_input, font=("Segoe UI", 12), bg="#666", fg="white")
        self.voice_btn.pack(pady=5)

        self.voice_toggle_btn = tk.Button(self.container, text="🔊 Voice: ON", command=self.toggle_voice, font=("Segoe UI", 12), bg="#333", fg="white")
        self.voice_toggle_btn.pack(pady=5)

        self.toggle_btn = tk.Button(self.container, text="🌓 Toggle Theme", command=self.toggle_theme, font=("Segoe UI", 12), bg="#333", fg="white")
        self.toggle_btn.pack(pady=5)

        self.stop_btn = tk.Button(self.container, text="🛑 Stop", command=self.stop_forecast, font=("Segoe UI", 12), bg="red", fg="white")
        self.stop_btn.pack(pady=5)

        self.weather_icon_label = tk.Label(self.container, bg="black")
        self.weather_icon_label.pack(pady=10)

        # 🖼️ Show default icon on first launch
        self.update_weather_icon("default")

        self.result_label = tk.Label(self.container, text="", font=("Segoe UI", 14), fg="white", bg="black", wraplength=800, justify="center")
        self.result_label.pack(pady=20)

    def toggle_theme(self):
        current = self.theme_color.get()
        new_bg = "white" if current == "dark" else "black"
        new_fg = "black" if current == "dark" else "white"
        self.theme_color.set("light" if current == "dark" else "dark")
        self.root.configure(bg=new_bg)
        self.container.configure(bg=new_bg)
        for w in self.container.winfo_children():
            if isinstance(w, tk.Label):
                w.configure(bg=new_bg, fg=new_fg)
            elif isinstance(w, tk.Button):
                w.configure(bg="#DDD" if new_bg == "white" else "#444", fg=new_fg)
            elif isinstance(w, tk.Entry):
                w.configure(bg="white", fg="black")

    def toggle_voice(self):
        self.voice_enabled = not self.voice_enabled
        new_text = "🔊 Voice: ON" if self.voice_enabled else "🔇 Voice: OFF"
        self.voice_toggle_btn.config(text=new_text)

    def stop_forecast(self):
        self.stopped = True
        self.engine.stop()
        self.result_label.config(text="Forecast stopped.")
        self.speaking = False

    def speak(self, text):
        if self.voice_enabled and not self.stopped:
            def _speak():
                if not self.stopped:
                    self.speaking = True
                    try:
                        self.engine.say(text)
                        self.engine.runAndWait()
                    except RuntimeError:
                        pass
                    self.speaking = False
            threading.Thread(target=_speak, daemon=True).start()

    def fetch_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name.")
            self.update_weather_icon("default")
            self.result_label.config(text="Please enter a city name to get forecast.")
            return

        self.result_label.config(text="Loading weather data...")
        self.root.update()
        self.stopped = False

        data = get_weather(city)
        if data:
            condition = data['weather'][0]['main'].lower()
            description = data['weather'][0]['description']
            temp = data['main']['temp']

            # ⏰ Proper local time calculation
            dt = data['dt']
            timezone_offset = data['timezone']
            utc_time = datetime.utcfromtimestamp(dt)
            local_time = utc_time + timedelta(seconds=timezone_offset)
            hour = local_time.hour

            # 🕒 Accurate part of day
            if 5 <= hour < 12:
                part_of_day = "morning"
            elif 12 <= hour < 16:
                part_of_day = "afternoon"
            elif 16 <= hour < 20:
                part_of_day = "evening"
            else:
                part_of_day = "night"

            suggestion = suggest_clothes(temp, description)
            result = f"City: {city}\nTime of Day: {part_of_day}\nSky: {description.capitalize()}\nTemperature: {temp}°C\n\nStylist Suggestion: {suggestion}"

            self.update_theme_color(condition)
            self.update_weather_icon(condition)
            self.result_label.config(text="")
            self.type_text(result)
            self.speak(result)
        else:
            self.update_weather_icon("default")
            self.result_label.config(text="City not found. Please try again.")
            self.speak("City not found. Please try again.")

    def type_text(self, text):
        self.result_label.config(text="")
        for char in text:
            if self.stopped:
                break
            current = self.result_label.cget("text")
            self.result_label.config(text=current + char)
            self.root.update()
            time.sleep(0.02)

    def update_theme_color(self, condition):
        condition = condition.lower()
        bg_color = "#000000"
        fg_color = "white"
        if "clear" in condition:
            bg_color = "#1E90FF"
        elif "cloud" in condition:
            bg_color = "#444444"
        elif "rain" in condition:
            bg_color = "#2F4F4F"
        elif "snow" in condition:
            bg_color = "#B0E0E6"
            fg_color = "#000000"
        elif "mist" in condition or "haze" in condition:
            bg_color = "#708090"

        self.root.configure(bg=bg_color)
        self.container.configure(bg=bg_color)
        for w in self.container.winfo_children():
            if isinstance(w, tk.Label) or isinstance(w, tk.Button):
                w.configure(bg=bg_color, fg=fg_color)
            elif isinstance(w, tk.Entry):
                w.configure(bg="white", fg="black")

    def update_weather_icon(self, condition):
        condition = condition.lower()
        icon_key = "default"

        if "clear" in condition:
            icon_key = "clear"
        elif "rain" in condition or "drizzle" in condition or "thunderstorm" in condition:
            icon_key = "rain"
        elif "cloud" in condition:
            icon_key = "clouds"
        elif "snow" in condition:
            icon_key = "snow"
        elif "mist" in condition or "fog" in condition or "haze" in condition or "smoke" in condition:
            icon_key = "clouds"
        elif "wind" in condition:
            icon_key = "wind"

        icon_path = ICON_PATHS.get(icon_key, ICON_PATHS["default"])
        try:
            image = Image.open(icon_path).resize((100, 100), Image.Resampling.LANCZOS)
            icon = ImageTk.PhotoImage(image)
            self.weather_icon_label.config(image=icon)
            self.weather_icon_label.image = icon
        except Exception as e:
            print("Icon load failed:", e)


    def voice_input(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.speak("Please say the name of the city.")
            try:
                audio = recognizer.listen(source, timeout=5)
                city = recognizer.recognize_google(audio)
                self.city_entry.delete(0, tk.END)
                self.city_entry.insert(0, city)
                self.fetch_weather()
            except sr.UnknownValueError:
                self.speak("Sorry, I didn't catch that. Please try again.")
            except sr.RequestError:
                self.speak("Could not request results from speech recognition service.")
            except sr.WaitTimeoutError:
                self.speak("Listening timed out while waiting for phrase.")

if __name__ == '__main__':
    root = tk.Tk()
    app = AttireForecastApp(root)
    root.mainloop()
