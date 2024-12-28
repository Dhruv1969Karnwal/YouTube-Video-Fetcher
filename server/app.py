from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import random
from dotenv import load_dotenv
from flask_cors import CORS
from pymongo.errors import ConnectionFailure
import threading
import time

# Load environment variables from .env file for secure management of sensitive information
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) to allow the frontend to access the backend from different domains
CORS(app)

# MongoDB Atlas connection using the URI stored in the .env file
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

# YouTube API setup: store multiple API keys for handling rate-limiting (rotate between keys)
API_KEYS = os.getenv('YOUTUBE_API_KEYS').split(',')
current_key_index = 0

# List of various search topics to use for fetching YouTube videos
QUERY_LIST = [
    "football", "basketball", "technology", "music", "science", "news", "gaming", "movies",
    "fitness", "health", "politics", "art", "history", "cooking", "travel", "sports", "animals",
    "space", "environment", "nature", "culture", "education", "photography", "finance", "investing",
    "business", "startup", "entrepreneurship", "real estate", "crypto", "stocks", "marketing", "SEO",
    "web development", "app development", "coding", "AI", "machine learning", "data science", "robotics",
    "VR", "AR", "gadgets", "smartphones", "laptops", "tablets", "cars", "electric vehicles", "space exploration",
    "NASA", "astronomy", "biography", "documentaries", "comedy", "stand-up comedy", "animation", "films",
    "reviews", "reaction videos", "vlogs", "food", "recipes", "gaming tutorials", "Minecraft", "Fortnite",
    "Call of Duty", "League of Legends", "Valorant", "Counter-Strike", "PUBG", "TikTok", "Instagram",
    "YouTube growth", "podcasts", "interviews", "travel vlogs", "airplanes", "trains", "boats", "bicycles",
    "furniture", "interior design", "home improvement", "DIY", "crafts", "gardening", "sustainability",
    "renewable energy", "3D printing", "biotechnology", "genetics", "chemistry", "physics", "psychology",
    "sociology", "philosophy", "literature", "poetry", "classic literature", "novels", "mystery books",
    "self-help", "motivation", "inspiration", "mental health", "relationships", "parenting", "family",
    "life hacks", "time management", "productivity", "mindfulness", "meditation", "yoga", "sports highlights",
    "Olympics", "World Cup", "Super Bowl", "Champions League", "NBA Finals", "NFL", "NHL", "UFC", "boxing"
]

# Video model (MongoDB schema) for representing video data in the database
class Video:
    def __init__(self, _id, title, description, publish_date, thumbnail_url, channel_name):
        self._id = _id
        self.title = title
        self.description = description
        self.publish_date = publish_date
        self.thumbnail_url = thumbnail_url
        self.channel_name = channel_name

    def to_dict(self):
        # Convert the Video object into a dictionary format for JSON response
        return {
            'id': self._id,
            'title': self.title,
            'description': self.description,
            'publish_date': self.publish_date,
            'thumbnail_url': self.thumbnail_url,
            'channel_name': self.channel_name
        }

# Helper function to initialize YouTube API client using the current API key
def get_youtube_service():
    global current_key_index
    youtube = build('youtube', 'v3', developerKey=API_KEYS[current_key_index])
    return youtube

# Function to fetch videos from YouTube API based on a query string
def fetch_videos(query):
    try:
        youtube = get_youtube_service()
        search_response = youtube.search().list(
            q=query,
            type='video',
            part='id,snippet',
            order='date',  # Fetch most recent videos
            maxResults=10  # Fetch up to 10 videos per request
        ).execute()

        print(f"Fetched {len(search_response['items'])} videos for query: {query}.")
        
        # If no videos found, log it
        if len(search_response['items']) == 0:
            print(f"No videos found for query: {query}")

        # Insert each video into the MongoDB database if not already present
        for item in search_response['items']:
            video_id = item['id']['videoId']
            existing_video = mongo.db.videos.find_one({"_id": video_id})

            if not existing_video:
                new_video = {
                    "_id": video_id,
                    "title": item['snippet']['title'],
                    "description": item['snippet']['description'],
                    "publish_date": item['snippet']['publishedAt'],
                    "thumbnail_url": item['snippet']['thumbnails']['default']['url'],
                    "channel_name": item['snippet']['channelTitle']
                }

                print(f"Inserting video: {new_video['title']} (ID: {video_id})")

                # Insert new video into MongoDB
                result = mongo.db.videos.insert_one(new_video)

                if result.inserted_id:
                    print(f"Successfully inserted video with ID: {result.inserted_id}")
                else:
                    print(f"Failed to insert video with ID: {video_id}")
            else:
                print(f"Video with ID: {video_id} already exists in database.")
        
        print(f"Fetch complete for query: {query}.")

    except HttpError as e:
        # If rate limit exceeded or API key quota exhausted, switch to the next key
        if e.resp.status in [403, 429]:
            global current_key_index
            current_key_index = (current_key_index + 1) % len(API_KEYS)
            print(f"Switching to API key {current_key_index}")
        else:
            print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# API route to get the list of videos from the database with pagination
@app.route('/api/videos', methods=['GET'])
def get_videos():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = request.args.get('query', '')

    # Fetch videos from MongoDB with optional query filter and pagination
    videos_query = mongo.db.videos.find().sort("publish_date", -1)

    if query:
        videos_query = mongo.db.videos.find({
            "title": {"$regex": query, "$options": "i"}
        }).sort("publish_date", -1)

    # Apply pagination and return videos
    videos_list = list(videos_query.skip((page - 1) * per_page).limit(per_page))

    total_videos = mongo.db.videos.count_documents({})
    pages = (total_videos // per_page) + (1 if total_videos % per_page > 0 else 0)

    return jsonify({
        'videos': [Video(**video).to_dict() for video in videos_list],
        'total': total_videos,
        'pages': pages,
        'current_page': page
    })

# API route to test MongoDB connection
@app.route('/test', methods=['GET'])
def test_connection():
    try:
        mongo.db.command("ping")
        return jsonify({"status": "MongoDB connection successful"})
    except ConnectionFailure as e:
        return jsonify({"status": "MongoDB connection failed", "error": str(e)}), 500
    except Exception as e:
        return jsonify({"status": "Failed to connect to MongoDB", "error": str(e)}), 500

# API route to manually trigger video fetching
@app.route('/fetch_videos', methods=['GET'])
def trigger_fetch_videos():
    try:
        fetch_videos("football")  # You can change this query if needed
        return jsonify({"status": "Video fetching started."})
    except Exception as e:
        return jsonify({"status": "Error in fetching videos", "error": str(e)}), 500

# Function to periodically fetch videos from YouTube with a random query every 10 seconds
def periodic_fetch():
    while True:
        query = random.choice(QUERY_LIST)
        print(f"Fetching videos for query: {query}")
        fetch_videos(query)
        time.sleep(10)  # Fetch every 10 seconds

# Run the Flask app with periodic fetching in a separate thread
if __name__ == '__main__':
    try:
        # Start the periodic fetch task in a separate thread
        fetch_thread = threading.Thread(target=periodic_fetch, daemon=True)
        fetch_thread.start()
        
        # Run the Flask app
        app.run(debug=True, use_reloader=False)
    except Exception as e:
        print(f"Error running the app: {e}")
