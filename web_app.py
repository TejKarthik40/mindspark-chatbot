import streamlit as st
from chat_logic import (
    detect_mood, 
    check_for_crisis,
    ai_response,
    get_media_and_tips,
    generate_story, 
    get_exercise_suggestion, 
    CRISIS_MESSAGE
)
import random

# --- 1. Streamlit UI Setup: Purple & Black Theme ---
st.set_page_config(
    page_title="MindSpark Companion ✨💜",
    layout="centered",
    initial_sidebar_state="auto"
)

# Sophisticated, Calming Purple & Black Palette
COLOR_PRIMARY = "#8A2BE2"  # Blue Violet (Deep Purple for buttons/accents)
COLOR_BACKGROUND = "#F5F0FF" # Very Light Lavender/Off-White
COLOR_BOT_BUBBLE = "#E6E6FA" # Lavender Blush (Soft Bot Background)
COLOR_USER_BUBBLE = "#DDA0DD" # Plum/Pale Violet Red (User Input Background)
COLOR_TEXT = "#1C1C1C"    # Near Black
COLOR_ACCENT = "#5E35B1"   # Deep Purple for headers

# Custom CSS for the "Wow" Purple & Black look
st.markdown(f"""
<style>
/* 1. MAIN PAGE STYLES */
.stApp {{
    background-color: {COLOR_BACKGROUND};
}}

/* 2. HEADER AND TITLE */
.big-font {{
    font-size: 32px !important;
    font-weight: 700;
    color: {COLOR_ACCENT};
    padding-bottom: 10px;
    border-bottom: 3px solid {COLOR_PRIMARY}40; /* Subtle purple line */
}}
header {{ visibility: hidden; }}

/* 3. CHAT BUBBLES */
.stChatMessage {{
    padding: 15px;
    border-radius: 20px;
    margin-bottom: 15px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    color: {COLOR_TEXT};
}}
/* Bot Messages (Assistant) */
.stChatMessage[data-testid="stChatMessage"]:nth-child(even) {{
    background-color: {COLOR_BOT_BUBBLE};
    border-top-left-radius: 5px; 
    border-top-right-radius: 20px;
}}
/* User Messages */
.stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {{
    background-color: {COLOR_USER_BUBBLE};
    text-align: right;
    border-top-right-radius: 5px;
    border-top-left-radius: 20px;
}}

/* 4. SUGGESTION BOX (The WOW Factor) */
.suggestion-box {{
    background-color: white;
    padding: 15px;
    border-radius: 15px;
    border: 1px solid {COLOR_PRIMARY}50; 
    border-left: 6px solid {COLOR_ACCENT}; /* Deep purple accent bar */
    margin-top: 15px;
    font-size: 15px;
    font-weight: 500;
    color: {COLOR_TEXT};
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}}

/* 5. BUTTONS (Quick Actions) */
.stButton>button {{
    background-color: {COLOR_PRIMARY};
    color: white;
    font-weight: bold;
    border-radius: 12px;
    border: none;
    padding: 10px 15px;
    margin: 5px 0;
    transition: background-color 0.3s;
}}
.stButton>button:hover {{
    background-color: {COLOR_ACCENT}; /* Deep purple hover */
}}
</style>
""", unsafe_allow_html=True)

# Application Title and Tagline
st.markdown('<p class="big-font">MindSpark Companion 💜</p>', unsafe_allow_html=True)
st.caption("Your friend for emotional support and mood boosting. **Wellness focused, always here to listen.**")

# --- 2. Initialize Session State (NO FUNCTIONALITY CHANGE) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "last_mood" not in st.session_state:
    st.session_state.last_mood = ("Neutral", "😐")
if "awaiting_command" not in st.session_state:
    st.session_state.awaiting_command = None


# --- 3. Role Selection and Initialization ---

def set_role(role):
    st.session_state.user_role = role
    st.session_state.messages = [{"role": "assistant", "content": f"Hello! I see you've identified as a **{role}**. How are you feeling right now? I'm here to listen."}]

if st.session_state.user_role is None:
    st.header("Who are you talking to?")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.button("Student 👨‍🎓", on_click=set_role, args=("Student",), use_container_width=True)
    with col2:
        st.button("Professional 👩‍💼", on_click=set_role, args=("Working Professional",), use_container_width=True)
    with col3:
        st.button("General Public 🏠", on_click=set_role, args=("General Public",), use_container_width=True)
        
    st.stop()


# --- 4. Suggestion/Command Execution (NO FUNCTIONALITY CHANGE) ---

def execute_suggestion(command, display_text):
    """Executes the media/exercise command based on the last detected mood."""
    
    # 1. Acknowledge the user's button click
    st.session_state.messages.append({"role": "user", "content": display_text})
    
    # 2. Reset the awaiting command state
    st.session_state.awaiting_command = None
    
    # 3. Proceed with execution
    mood, _ = st.session_state.last_mood
    
    # Command 1: Story (Uses Gemini API/Fallback)
    if command == "story":
        st.session_state.messages.append({"role": "assistant", "content": f"That's a lovely idea! Let me tell you a story for your **{mood}** mood..."})
        story = generate_story(mood) 
        st.session_state.messages.append({"role": "assistant", "content": f"📖 **Story Time:**\n\n{story}"})
        
    # Command 2: Exercise
    elif command == "exercise":
        exercise = get_exercise_suggestion("Stressed")
        if exercise:
            st.session_state.messages.append({"role": "assistant", "content": f"Absolutely! Let's try the **{exercise['title']}** technique to recenter ourselves:"})
            exercise_steps = "\n".join(exercise['steps'])
            st.session_state.messages.append({"role": "suggestion", "content": f"🧘 **Exercise Steps**:\n\n{exercise_steps}"})
        else:
            st.session_state.messages.append({"role": "assistant", "content": "I'm sorry, I don't have a specific exercise right now, but a simple stretch or getting a glass of water can always help!"})
            
    # Command 3, 4, 5: Media (Song, Video, or General Yes)
    elif command in ["song", "video", "movie", "yes"]:
        quote, song_link, movie, contextual_tip, video_link = get_media_and_tips(mood, st.session_state.user_role)
        
        st.session_state.messages.append({"role": "assistant", "content": f"Here is a suggestion to help shift your **{mood}** mood:"})
        
        suggestions = f"**{quote}**"
        if contextual_tip:
            suggestions += f" | {contextual_tip}"
        
        if video_link:
            mood_action = 'calmer' if mood in ['Angry', 'Stressed', 'Fear'] else 'happier'
            suggestions += f"\n\n💡 **Mood Shifter:** Try watching **[This Video on YouTube]({video_link})** to help you feel {mood_action}."
        elif song_link and movie:
            suggestions += f"\n\n💡 **Try a mood boost:** Maybe watch **{movie}** or listen to **[This Song on YouTube]({song_link})**."

        st.session_state.messages.append({"role": "suggestion", "content": suggestions})
        
    # Note: st.rerun() is intentionally REMOVED from the callback to avoid the warning


# --- 5. Main Chat Loop ---

def handle_user_input(prompt):
    """Processes user input and generates the assistant's response."""
    
    # 1. CRISIS CHECK
    if check_for_crisis(prompt):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "suggestion", "content": CRISIS_MESSAGE})
        st.session_state.awaiting_command = None
        st.rerun()
        return

    # 2. Handle System Commands
    if prompt.lower() == "role":
        st.session_state.user_role = None
        st.session_state.messages = []
        st.rerun()
        return
    
    # 3. Handle Previous Command Request (from text input)
    if st.session_state.awaiting_command and any(cmd in prompt.lower() for cmd in ["story", "exercise", "song", "video", "yes"]):
        command = next((c for c in ["story", "exercise", "song", "video", "yes"] if c in prompt.lower()), "yes")
        execute_suggestion(command, prompt)
        return

    # 4. Standard Flow: Process new input
    st.session_state.messages.append({"role": "user", "content": prompt})
    mood, emoji = detect_mood(prompt)
    st.session_state.last_mood = (mood, emoji)
    
    # 5. Decide Next Step (Dialogue and Prompt)
    
    # Negative Moods: Offer direct intervention (Story or Exercise)
    if mood in ["Angry", "Sad", "Depressed"]:
        reply = ai_response(f"chat: responded to {mood}")
        st.session_state.messages.append({"role": "assistant", "content": reply})
        
        st.session_state.messages.append({"role": "assistant", "content": "I'm here for you. Take a moment, and let's find something to lift your spirits."})
        st.session_state.awaiting_command = mood

    # Stress/Fear Moods: Offer a quick solution
    elif mood in ["Stressed", "Fear"]:
        reply = ai_response(f"chat: responded to {mood}")
        st.session_state.messages.append({"role": "assistant", "content": reply})
        
        st.session_state.messages.append({"role": "assistant", "content": "That sounds rough. Let's find a way to center your mind right now."})
        st.session_state.awaiting_command = mood

    # Neutral/Positive Moods: Ask if they want a suggestion
    else:
        reply = ai_response(f"chat: responded to {mood}")
        st.session_state.messages.append({"role": "assistant", "content": reply})
        
        st.session_state.messages.append({"role": "assistant", "content": f"That's great! Let's boost that wonderful **{mood}** feeling even more."})
        st.session_state.awaiting_command = mood
    
    st.rerun() # Trigger a rerun to show the new chat message and the buttons


# --- 6. Display Chat History ---
for message in st.session_state.messages:
    if message["role"] == "user":
        mood_text, emoji = st.session_state.last_mood
        with st.chat_message("user"):
            st.markdown(f"{message['content']} {emoji}")
    elif message["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(message["content"])
    elif message["role"] == "suggestion":
        with st.container():
             st.markdown(f'<div class="suggestion-box">{message["content"]}</div>', unsafe_allow_html=True)


# --- 7. Dynamic Input and Buttons ---

prompt = st.chat_input(f"Chat as a {st.session_state.user_role}...")

if prompt:
    handle_user_input(prompt)

# Display dynamic buttons for quick interaction if a command is awaited
if st.session_state.awaiting_command:
    mood = st.session_state.awaiting_command
    
    with st.container():
        st.write("---")
        st.markdown("##### 💜 Quick Actions:")
        
        if mood in ["Angry", "Sad", "Depressed"]:
            cols = st.columns(3)
            cols[0].button("Story 📖", on_click=execute_suggestion, args=("story", "I need a story."), use_container_width=True)
            cols[1].button("Exercise 🧘", on_click=execute_suggestion, args=("exercise", "I'll try an exercise."), use_container_width=True)
            cols[2].button("Song/Video ▶️", on_click=execute_suggestion, args=("song", "I'd like a song or video."), use_container_width=True)

        elif mood in ["Stressed", "Fear"]:
            cols = st.columns(3)
            cols[0].button("Calming Video 📽️", on_click=execute_suggestion, args=("video", "I need a calming video."), use_container_width=True)
            cols[1].button("Exercise 🧘", on_click=execute_suggestion, args=("exercise", "I'll try an exercise."), use_container_width=True)
            cols[2].button("Quick Tip 🧠", on_click=execute_suggestion, args=("yes", "Give me a quick tip."), use_container_width=True)

        elif mood in ["Happy", "Neutral", "Cheerful"]:
            cols = st.columns(3)
            cols[0].button("Song 🎶", on_click=execute_suggestion, args=("song", "Yes, recommend a song."), use_container_width=True)
            cols[1].button("Movie 🎬", on_click=execute_suggestion, args=("movie", "Yes, recommend a movie."), use_container_width=True)
            cols[2].button("Story 📝", on_click=execute_suggestion, args=("story", "Yes, tell me a story."), use_container_width=True)