# YouTube Video Fetcher

This project fetches the latest videos from YouTube based on a search query and displays them on a frontend interface. It consists of a Flask backend and a Next.js frontend.

## Project Structure


**Clone the Repository**:

First, clone the CodeTerm repository to your local machine using the following command:

```sh
git clone https://github.com/Dhruv1969Karnwal/YouTube-Video-Fetcher.git
cd YouTube-Video-Fetcher

```


## Backend Setup (Flask)

1. Navigate to the server directory:

```sh
cd server
```


2. Create a virtual environment and activate it:

```sh
python -m venv venv
```

#### On MacOs/linus:
```sh
source venv/bin/activate
```
#### On Windows:  

```sh
venv\Scripts\activate
```


3. Install dependencies:

```sh
pip install -r requirements.txt
```


4. Set up environment variables:
Create a `.env` file in the server directory and add your YouTube API keys and database URL:

```sh
YOUTUBE_API_KEYS=key1,key2,key3
MONGO_URI=mongodb+srv://<user_name>:<password>@cluster0.lkxrn.mongodb.net/you-tube?retryWrites=true&w=majority
```


5. Run the Flask application:

```sh
python app.py
```



## Frontend Setup (Next.js + ShadCN)

1. Navigate to the frontend directory:

```sh
cd frontend
```


2. Install dependencies:

```sh
npm install
```



3. Run the development server:

```sh
npm run dev
```