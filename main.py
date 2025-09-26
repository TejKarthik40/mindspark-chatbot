import tkinter as tk
from tkinter import scrolledtext, messagebox
from chat_logic import detect_mood, generate_reply_and_suggestions, generate_story, get_exercise_suggestion, EXERCISES

# --- Constants for Professional UI ---
COLOR_BG = "#E8F8F5"       # Light Mint Green/Aqua
COLOR_TEXT = "#17202A"     # Dark Gray
COLOR_BOT_BUBBLE = "#D1F2EB" # Pale Aqua
COLOR_USER_BUBBLE = "#A3E4D7" # Medium Aqua
FONT_FAMILY = "Segoe UI"
FONT_SIZE = 10
FONT_SIZE_TITLE = 14
PADDING_X = 10
PADDING_Y = 5


class MentalHealthCompanion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MindSpark Companion ✨")
        self.geometry("600x750")
        self.configure(bg=COLOR_BG)
        
        self.user_role = None # State to track user role
        
        # --- Start with Role Selection Screen ---
        self.show_role_selection()


    def show_role_selection(self):
        """Displays the initial screen to select user role."""
        
        # Clear any previous widgets
        for widget in self.winfo_children():
            widget.destroy()

        self.role_frame = tk.Frame(self, bg=COLOR_BG, padx=30, pady=100)
        self.role_frame.pack(expand=True)

        tk.Label(self.role_frame, text="Hello! To offer the best advice, tell me:", 
                 bg=COLOR_BG, fg=COLOR_TEXT, font=(FONT_FAMILY, FONT_SIZE_TITLE, "bold")).pack(pady=20)
        
        roles = ["Student 👨‍🎓", "Working Professional 👩‍💼", "General Public 🏠"]
        
        for role_text in roles:
            role_key = role_text.split(" ")[0] # Get the simple role name
            
            button = tk.Button(self.role_frame, text=role_text,
                               command=lambda r=role_key: self.set_role_and_start(r),
                               bg=COLOR_USER_BUBBLE, fg=COLOR_TEXT, 
                               font=(FONT_FAMILY, FONT_SIZE, "bold"),
                               relief=tk.FLAT, bd=0, padx=20, pady=10, width=30)
            button.pack(pady=10)
            
        tk.Label(self.role_frame, text="You can change this later by typing 'role'.", 
                 bg=COLOR_BG, fg=COLOR_TEXT, font=(FONT_FAMILY, FONT_SIZE - 2, "italic")).pack(pady=30)


    def set_role_and_start(self, role):
        """Sets the user role and transitions to the main chat window."""
        self.user_role = role
        self.show_main_chat()
        

    def show_main_chat(self):
        """Displays the main professional chat interface."""
        
        # Clear role selection widgets
        for widget in self.winfo_children():
            widget.destroy()
            
        # --- 1. Chat Display Area ---
        self.chat_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, bg=COLOR_BOT_BUBBLE, fg=COLOR_TEXT, 
                                                   font=(FONT_FAMILY, FONT_SIZE), 
                                                   padx=PADDING_X, pady=PADDING_Y, state=tk.DISABLED)
        self.chat_area.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Apply tags for styling (professional chat bubbles)
        self.chat_area.tag_configure('bot', foreground=COLOR_TEXT, background=COLOR_BOT_BUBBLE, font=(FONT_FAMILY, FONT_SIZE, "bold"))
        self.chat_area.tag_configure('user', foreground=COLOR_TEXT, background=COLOR_USER_BUBBLE, justify='right')
        self.chat_area.tag_configure('suggestion', foreground="#2ECC71", font=(FONT_FAMILY, FONT_SIZE, "italic")) # Green for suggestions
        
        # --- 2. Input Frame ---
        input_frame = tk.Frame(self, bg=COLOR_BG)
        input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.user_input = tk.Entry(input_frame, bg="white", fg=COLOR_TEXT, 
                                   font=(FONT_FAMILY, FONT_SIZE), bd=1, relief=tk.FLAT)
        self.user_input.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 5), ipady=5)
        self.user_input.bind("<Return>", lambda event: self.send_message()) # Bind Enter key
        
        send_button = tk.Button(input_frame, text="Send 🚀", command=self.send_message, 
                                bg="#2ECC71", fg="white", font=(FONT_FAMILY, FONT_SIZE, "bold"), 
                                relief=tk.FLAT, padx=10, pady=5)
        send_button.pack(side=tk.RIGHT)
        
        # Initial greeting
        self.display_message(f"Hello! I see you've identified as a {self.user_role}. How are you feeling right now? I'm here to listen.", "bot")

    
    def display_message(self, message, sender):
        """Helper to insert message into the chat area."""
        self.chat_area.config(state=tk.NORMAL)
        
        if sender == "bot":
            prefix = "MindSpark: "
            tag = 'bot'
        else:
            prefix = "You: "
            tag = 'user'
            
        # Insert the message with the corresponding tag
        self.chat_area.insert(tk.END, prefix + message + "\n\n", tag)
        
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END) # Auto-scroll to the bottom


    def send_message(self):
        """Handles user input, calls chat logic, and displays the response."""
        user_text = self.user_input.get().strip()
        if not user_text:
            return

        self.display_message(user_text, "user")
        self.user_input.delete(0, tk.END) # Clear input field

        # --- Core Chat Logic ---
        
        # 1. Handle special commands
        if user_text.lower() in ["story", "tell a story"]:
            self.handle_story_request()
            return
        
        if "exercise" in user_text.lower() or "breathe" in user_text.lower():
            self.handle_exercise_request()
            return
            
        if user_text.lower() == "role":
            self.show_role_selection()
            return

        # 2. Get Mood
        mood = detect_mood(user_text)
        
        # 3. Generate Reply and Suggestions
        reply, quote, song_link, movie, contextual_tip = generate_reply_and_suggestions(mood, user_text, self.user_role)

        # 4. Display Bot Response
        self.display_message(reply, "bot")
        
        # 5. Display Suggestions in a distinct style
        suggestions = f"[{mood} Mood Detected] {quote}"
        if contextual_tip:
            suggestions += f" | {contextual_tip}"
        if song_link and movie:
            suggestions += f"\n💡 Try a mood boost: Maybe watch **{movie}** or listen to **{song_link}**"
            
        self.display_message(suggestions, "suggestion")

    
    def handle_story_request(self):
        """Handles the user request to tell a story."""
        # Detect mood again, or use the last known mood
        last_input = self.chat_area.get('1.0', tk.END).split('\n')[-4].replace('You: ', '').strip()
        current_mood = detect_mood(last_input) if last_input else "Neutral"
        
        self.display_message(f"That's a lovely idea! Let me find a story for your {current_mood} mood...", "bot")
        
        # Generate the story (Simulates Gemini API call)
        story = generate_story(current_mood)
        
        self.display_message(f"📖 **Story Time:**\n{story}", "bot")


    def handle_exercise_request(self):
        """Handles the user request for an exercise."""
        # Try to suggest an exercise relevant to stress/anxiety
        exercise_key = next((k for k, ex in EXERCISES.items() if any(m in ex['target_moods'] for m in ['Stressed', 'Fear'])), None)
        
        if exercise_key:
            exercise = EXERCISES[exercise_key]
            self.display_message(f"Absolutely! Let's try the **{exercise['title']}** technique to recenter ourselves:", "bot")
            exercise_steps = "\n".join(exercise['steps'])
            self.display_message(f"🧘 **Exercise Steps**:\n{exercise_steps}", "suggestion")
        else:
            self.display_message("I'm sorry, I don't have a specific exercise right now, but a simple stretch or getting a glass of water can always help!", "bot")


if __name__ == "__main__":
    app = MentalHealthCompanion()
    app.mainloop()