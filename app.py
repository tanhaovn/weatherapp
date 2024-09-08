from flask import Flask, request, render_template
import requests
from datetime import datetime

app = Flask(__name__)

def get_weather_data(city_name):
    api_key = "22b7f3537fa4da3978cdd4360f888378"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    
    complete_url = f"{base_url}q={city_name}&appid={api_key}&units=metric"
    response = requests.get(complete_url)
    data = response.json()
    
    if response.status_code == 200:
        main = data["main"]
        sys = data["sys"]
        weather = data["weather"][0]
        wind = data["wind"]
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        weather_data = {
            "location_name": f"{data['name']}, {sys['country']}",
            "temperature": main["temp"],
            "weather_description": weather["description"].capitalize(),
            "humidity": main["humidity"],
            "wind_speed": wind["speed"],
            "time": current_time
        }
        return weather_data
    else:
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    error = None
    if request.method == "POST":
        city_name = request.form["city_name"]
        weather_data = get_weather_data(city_name)
        if weather_data is None:
            error = "City not found or API error"
    
    return render_template("index.html", weather_data=weather_data, error=error)

if __name__ == "__main__":
    app.run(debug=True)
