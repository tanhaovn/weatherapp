from flask import Flask, request, render_template
import requests
from datetime import datetime

app = Flask(__name__)

def translate_description(desc):
    mapping = {
        "clear sky": "Trời trong",
        "few clouds": "Ít mây",
        "scattered clouds": "Mây rải rác",
        "broken clouds": "Mây từng đám",
        "overcast clouds": "Mây đen u ám",
        "light rain": "Mưa nhẹ",
        "moderate rain": "Mưa vừa",
        "heavy intensity rain": "Mưa to",
        "thunderstorm": "Giông bão",
        "snow": "Tuyết rơi",
        "mist": "Sương mù"
    }
    return mapping.get(desc.lower(), desc.capitalize())

def get_weather_data(city_name):
    api_key = "208eb580ea30520ea4ac21973145a060"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city_name}&appid={api_key}&units=metric"

    response = requests.get(complete_url)
    data = response.json()

    if response.status_code == 200:
        main = data["main"]
        sys = data["sys"]
        weather = data["weather"][0]
        wind = data["wind"]
        visibility = data.get("visibility", 0) / 1000 
        feels_like = main["feels_like"]
        temp_min = main["temp_min"]
        temp_max = main["temp_max"]
        dew_point = main["temp"] - ((100 - main["humidity"]) / 5)
        now = datetime.now()
        date_part = now.strftime('%Y-%m-%d')
        time_part = now.strftime('%H:%M:%S')

        weather_data = {
            "location_name": f"{data['name']}, {sys['country']}",
            "temperature": main["temp"],
            "feels_like": feels_like,
            "temp_min": temp_min,
            "temp_max": temp_max,
            "weather_description": translate_description(weather["description"]),
            "humidity": main["humidity"],
            "wind_speed": wind["speed"],
            "visibility": round(visibility, 1),
            "dew_point": round(dew_point, 2),
            "date": date_part,
            "time": time_part
        }
        return weather_data
    else:
        return None

def get_forecast_data(city_name):
    api_key = "208eb580ea30520ea4ac21973145a060"
    base_url = "http://api.openweathermap.org/data/2.5/forecast?"
    complete_url = f"{base_url}q={city_name}&appid={api_key}&units=metric"
    response = requests.get(complete_url)
    data = response.json()

    if response.status_code == 200:
        forecast_list = []
        seen_dates = set()
        for item in data["list"]:
            dt_txt = item["dt_txt"]
            date = dt_txt.split(" ")[0]
            if "12:00:00" in dt_txt and date not in seen_dates:
                forecast = {
                    "date": date,
                    "temp": item["main"]["temp"],
                    "description": item["weather"][0]["description"].capitalize(),
                    "icon": item["weather"][0]["icon"]
                }
                forecast_list.append(forecast)
                seen_dates.add(date)
            if len(forecast_list) == 6:
                break
        return forecast_list
    else:
        return None



@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    forecast_data = None
    error = None

    if request.method == "POST":
        city_name = request.form["city_name"]
        weather_data = get_weather_data(city_name)
        forecast_data = get_forecast_data(city_name)

        if weather_data and forecast_data:
            today_forecast = {
                "date": weather_data["date"],
                "temp": weather_data["temperature"],
                "description": weather_data["weather_description"],
                "icon": "01d" 
            }
            forecast_data.insert(0, today_forecast)
        elif weather_data is None:
            error = "City not found or API error"

    return render_template("index.html", weather_data=weather_data, forecast_data=forecast_data, error=error)



if __name__ == "__main__":
    app.run(debug=True)
