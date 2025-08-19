Here is a polished README.md file tailored for your weather API project:

```markdown
# Weather API with Redis Caching

A simple Python Flask weather API that fetches live weather data from the Visual Crossing API and caches it using Redis for improved performance and reduced external API calls.

## Features

- Retrieve current weather by city name
- Hardcoded weather endpoint for quick testing
- Caching with Redis to minimize API requests
- Rate limiting set to 100 requests/hour per IP address
- Client-side Redis caching enabled for faster read access

## Requirements

- Python 3.8 or higher
- Redis server (either local or cloud)
- Virtual environment is recommended

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/ahamed338/weather-app.git
   cd weather-app
   ```

2. Create and activate a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory and add your API keys and Redis connection string:
   ```
   WEATHER_API_KEY=your_visual_crossing_api_key
   REDIS_CONNECTION_STRING=redis://localhost:6379/0
   ```

## Running the Application

1. Start your Redis server (local example for macOS):
   ```
   brew services start redis
   ```

2. Run the Flask application:
   ```
   python3 flask_app.py
   ```

3. Access the API at `http://127.0.0.1:5000`

## API Endpoints

### Hardcoded Weather Data

- `GET /weather/hardcoded`

Returns static weather data for quick testing.

### Live Weather Data

- `GET /weather?city=CITY_NAME`

Fetches current weather for the specified city. Responses are cached in Redis for 12 hours.

#### Example

```
curl "http://127.0.0.1:5000/weather?city=Bengaluru"
```

## Caching Details

- Weather data is cached in Redis with a 12-hour expiration.
- Client-side caching reduces Redis calls by locally caching keys and receiving invalidation messages.

## Rate Limiting

- The API limits requests to 100 per hour per IP by default.
- Live weather endpoint is further limited to 50 requests per hour.

## License

This project is licensed under the MIT License.

