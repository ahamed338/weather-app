import os
import redis
from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Rate limiter: max 100 requests per hour per IP
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)
limiter.init_app(app)

# Load env variables
API_KEY = os.getenv("WEATHER_API_KEY")
REDIS_CONN = os.getenv("REDIS_CONNECTION_STRING", "redis://localhost:6379/0")

# Initialize Redis client with client-side caching enabled
redis_client = redis.Redis.from_url(REDIS_CONN, decode_responses=True)
redis_client.client_tracking(on=True)  # Enable client-side caching tracking

CACHE_EXPIRATION = 12 * 60 * 60  # 12 hours in seconds

@app.route("/weather/hardcoded", methods=["GET"])
def hardcoded_weather():
    response = {
        "city": "Bengaluru",
        "temperature_celsius": 28,
        "description": "Clear sky",
        "humidity": 60
    }
    return jsonify(response), 200

@app.route("/weather", methods=["GET"])
@limiter.limit("50 per hour")
def get_weather():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "Missing required query parameter: city"}), 400

    # Check Redis cache (with client-side caching)
    cached_data = redis_client.get(city.lower())
    if cached_data:
        return jsonify({"source": "cache", "data": eval(cached_data)}), 200

    try:
        # Call Visual Crossing Weather API
        url = (
            f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
            f"{city}?unitGroup=metric&key={API_KEY}&contentType=json"
        )
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()

        if "days" not in data or not data["days"]:
            return jsonify({"error": "City not found or no weather data available"}), 404

        today_weather = data["days"][0]
        weather_response = {
            "city": data.get("address", city),
            "temperature_celsius": today_weather.get("temp", None),
            "description": today_weather.get("conditions", ""),
            "humidity": today_weather.get("humidity", None)
        }

        # Cache response in Redis
        redis_client.set(city.lower(), str(weather_response), ex=CACHE_EXPIRATION)

        return jsonify({"source": "api", "data": weather_response}), 200

    except requests.exceptions.Timeout:
        return jsonify({"error": "The external weather service timed out"}), 504
    except requests.exceptions.RequestException:
        return jsonify({"error": "There was an error contacting the weather service"}), 503
    except Exception:
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True)
