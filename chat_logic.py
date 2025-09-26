import re
import json
import random
from transformers import pipeline
import time 
import warnings 

# --- Import Gemini Client and Types ---
from google import genai
from google.genai import types
from google.genai.errors import APIError

import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv() 
# --- END ADDITION ---

import re
import json
# Suppress warnings from the generation pipeline for a cleaner console
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")

# --- 1. Load Resources and Initialize Gemini Client ---

try:
    with open("resources/mood_media.json", "r", encoding="utf-8") as f:
        MEDIA_DATA = json.load(f)
    with open("resources/quotes.json", "r", encoding="utf-8") as f:
        QUOTES = json.load(f)
    with open("exercises.json", "r", encoding="utf-8") as f:
        EXERCISES = json.load(f)
except FileNotFoundError as e:
    print(f"ERROR: Resource file not found: {e}. Check your file structure.")
    MEDIA_DATA, QUOTES, EXERCISES = {}, {}, {}


# Initialize Gemini Client
client = None
try:
    # Client automatically uses GEMINI_API_KEY environment variable
    client = genai.Client()
    print("INFO: Gemini client initialized successfully.")
except Exception as e:
    print(f"WARNING: Gemini client failed to initialize. Dynamic content will use fallback mock logic. Error: {e}")


# --- CRISIS DATA and Mood Emojis (Remain the same) ---
CRISIS_KEYWORDS = ["hurt myself", "end my life", "suicide", "want to die", "kill myself", "crisis"]
CRISIS_MESSAGE = (
    "🚨 **IMMEDIATE ATTENTION REQUIRED** 🚨\n\n"
    "I am an AI companion, not a substitute for professional care. "
    "If you are in danger, please reach out now:\n"
    "\n"
    "📞 **Crisis Hotline (US):** 988\n"
    "📞 **Emergency Services:** 911 (or your local equivalent)\n"
    "\n"
    "Your safety is paramount. I am here when you are ready, but please seek immediate help."
)


# --- 2. Input Processing and Mood Detection (No Change) ---

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

def check_for_crisis(user_input):
    clean_input = user_input.lower()
    for keyword in CRISIS_KEYWORDS:
        if keyword in clean_input:
            return True
    return False

# Load emotion detection pipeline (assuming transformers is installed)
try:
    EMOTION_DETECTOR = pipeline(
        "text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=False
    )
except Exception:
    EMOTION_DETECTOR = None

def detect_mood(user_input):
    # (Full logic is assumed to be present and remains the same)
    clean_input = clean_text(user_input)
    if "stress" in clean_input: return "Stressed", "😫"
    if "sad" in clean_input or "depress" in clean_input: return "Depressed", "😔"
    if "happy" in clean_input or "joy" in clean_input: return "Happy", "😀"
    if "angry" in clean_input: return "Angry", "😡"
    
    if EMOTION_DETECTOR:
        try:
            HUGGINGFACE_TO_CHATBOT_MOOD = {
                "anger": ("Angry", "😡"), "fear": ("Fear", "😨"), "sadness": ("Sad", "😔"),
                "joy": ("Happy", "😀"), "neutral": ("Neutral", "😐"), "surprise": ("Happy", "🤩"),
                "disgust": ("Angry", "😠"), "trust": ("Neutral", "😌")
            }
            result = EMOTION_DETECTOR(user_input)[0]
            dominant_emotion = result['label']
            return HUGGINGFACE_TO_CHATBOT_MOOD.get(dominant_emotion, ("Neutral", "😐"))
        except:
             pass
    return "Neutral", "😐"


# --- 3. Generative AI Functions (Specific Integration) ---

def _get_mock_story(mood):
    """Fallback story if the Gemini API call fails or is unavailable."""
    if mood == "Angry" or mood == "Stressed":
        return "The Whispering Stream: Once, a small stone was constantly buffeted by a river's current... **Remember to let go and find your stillness.**"
    elif mood == "Sad" or mood == "Depressed":
        return "The Sun Under the Clouds: A little candle felt hopeless because a thick, dark cloud covered the whole sky... **Your light is important; never let it dim.**"
    else:
        return "The small turtle worried about the finish line... **Remember, your strength comes from within, every step of the way.**"


def ai_response(prompt):
    """Handles fast, fixed conversational responses (No Gemini for general chat)."""
    # This remains fixed for performance and reliability on general chat
    if "sad" in prompt.lower() or "depressed" in prompt.lower():
        return "I hear you, friend. It takes courage to share that feeling. I'm here to listen without judgment. Tell me more, or we can just sit quietly together."
    if "happy" in prompt.lower() or "joy" in prompt.lower():
        return "That's fantastic news! I love hearing you sound so happy! What's the best part of your day so far? Let's celebrate it!"
    return "Thanks for sharing. What's on your mind right now? I'm all ears."


def generate_story(mood):
    """Generates a dynamic story using the Gemini API."""
    if client is None:
        return _get_mock_story(mood)

    story_prompt = f"Write a one-paragraph, uplifting, metaphorical story about coping with {mood.lower()} that ends with a single, clear positive takeaway sentence."

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=story_prompt,
            config=types.GenerateContentConfig(
                temperature=0.8,
                system_instruction="You are an empathetic, concise storyteller."
            )
        )
        return response.text
    except APIError:
        # Fallback to mock if API call fails
        return _get_mock_story(mood) 

def generate_contextual_tip(mood, user_role):
    """Generates a brief, personalized mental health tip using Gemini."""
    if client is None:
        if user_role == "Student":
            return "Tip: Try the Pomodoro Technique to manage study stress efficiently."
        return "Tip: Focus on small, manageable steps today. You can do it!"

    tip_prompt = f"Give a single, concise, actionable mental health tip for a {user_role} feeling {mood}."
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=tip_prompt,
            config=types.GenerateContentConfig(
                temperature=0.4, # Lower temperature for facts/tips
                system_instruction="You are a supportive coach. Respond with only the tip, starting with 'Tip: '"
            )
        )
        # Clean up output to ensure it's just the tip
        tip = response.text.split('\n')[0].strip()
        return tip if tip.startswith("Tip:") else "Tip: Focus on small, manageable steps today."
    except APIError:
        # Use fixed fallback
        if user_role == "Student":
            return "Tip: Try the Pomodoro Technique to manage study stress efficiently."
        return "Tip: Focus on small, manageable steps today. You can do it!"


# --- 4. Retrieval and Main Response Generator (Updated for Gemini Tip) ---

# (Helper functions for media links and exercise suggestions remain the same)
def get_song_link(song_name):
    if song_name:
        return f"https://www.youtube.com/results?search_query={song_name.replace(' ', '+')}"
    return None

def get_video_link(video_name):
    if video_name:
        return f"https://www.youtube.com/results?search_query={video_name.replace(' ', '+')}"
    return None

def get_exercise_suggestion(mood):
    for key, ex in EXERCISES.items():
        if mood in ex.get("target_moods", []):
            return ex
    return None

def get_related_moods(mood):
    mood_map = {
        "Sad": ["Sad", "Neutral", "Cheerful"],
        "Depressed": ["Sad", "Neutral", "Cheerful"],
        "Angry": ["Angry", "Neutral", "Happy"],
        "Fear": ["Fear", "Neutral", "Happy"],
        "Stressed": ["Stressed", "Neutral", "Happy"],
        "Guilt": ["Guilt", "Neutral", "Happy"],
        "Lonely": ["Lonely", "Neutral", "Cheerful"]
    }
    return mood_map.get(mood, [mood, "Neutral", "Happy"])


def get_media_and_tips(mood, user_role="General Public"):
    """Retrieves motivational media, quotes, and contextual tips based on mood."""
    
    # 1. Get Quote (ROBUST RETRIEVAL)
    quote_list = QUOTES.get(mood)
    if not quote_list:
        quote_list = QUOTES.get("Neutral")
    if not quote_list:
        quote_list = ["Stay positive!", "You are stronger than you think!"]
        
    quote = random.choice(quote_list)

    # 2. Get Media (Broad Selection)
    related_moods = get_related_moods(mood)
    all_songs, all_movies, all_videos = [], [], []

    for related_mood in related_moods:
        if related_mood in MEDIA_DATA:
            all_songs.extend(MEDIA_DATA[related_mood].get("songs", []))
            all_movies.extend(MEDIA_DATA[related_mood].get("movies", []))
            all_videos.extend(MEDIA_DATA[related_mood].get("videos", []))

    all_songs = list(set(all_songs))
    all_movies = list(set(all_movies))
    all_videos = list(set(all_videos))

    song_name = random.choice(all_songs) if all_songs else None
    movie = random.choice(all_movies) if all_movies else None
    video_name = random.choice(all_videos) if all_videos else None 

    song_link = get_song_link(song_name)
    video_link = get_video_link(video_name)
    
    # 3. Get Contextual Tip (DYNAMICALLY GENERATED by Gemini)
    contextual_tip = generate_contextual_tip(mood, user_role)
        
    return quote, song_link, movie, contextual_tip, video_link