## Backend Assignment | FamPay

### Project Goal

To make an API to fetch latest videos sorted in reverse chronological order of the publishing date-time from YouTube for a given search query in paginated response

### Basic Requirements:

- Cron Job to constantly fetch data in the background in every interval
- GET API, `/api/v1/get` for fetching videos supporting options like sorting and pagination
- A basic search API to search the stored videos using their title and description.
- Dashboard to access the videos with options to filter and search

### Development

1. Clone the project

`git clone https://github.com/dDab-panda/FamPay-assignment.git`

2. Copy [.env.example](https://github.com/dDab-panda/FamPay-assignment/blob/master/.env.example) to .env

```
# MONGODB
MONGODB_URL = 

# YOUTUBE API
YOUTUBE_API_KEY =
```
You will need a YOUTUBE DATA API key in order to run this app. Follow the instructions on [this page](https://developers.google.com/youtube/v3/getting-started) to get one.

```
YOUTUBE_API_KEY = "<API_KEY1>, <API_KEY2>..."
```

1. Install dependencies

`pip install -r requirements.txt`

2. Run the server

`uvicorn main:api`

3. Hit the endpoint `/api/v1/start` to start the cron job. Currently it is set to run atmost 3 times to save on YouTube Quota

### Running with Docker Compose

When using Docker Compose, 

1. Create a `.env` file using the instructions mentioned above

2. Run:

```
docker-compose up -d
```
3. Navigate to `http://localhost:8000/app` to see the app live

### Documentation

OpenAPI Specification comes bundled with FastAPI.
You can find the documentation at `http://localhost:8000/docs`
