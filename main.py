from customtkinter import *
import random
import requests
import json
import pyttsx3
import threading

base_window = CTk()
base_window.geometry("1280x720")
# base_window.state("zoomed")  # Enable full screen mode
base_window.title("AI Chatbot")
base_window.configure(expand=True)

# Font objects
default_font = CTkFont(family="Poppins", size=30)
title_font = CTkFont(family="Ubuntu Bold", size=50)
chat_font = CTkFont(family="Ubuntu Regular", size=20)
input_font = CTkFont(family="Ubuntu Bold", size=15)

# Configure the grid layout
base_window.grid_rowconfigure(0, weight=0)
base_window.grid_rowconfigure(1, weight=1)
base_window.grid_columnconfigure(0, weight=1)

# Theme toggle
is_dark_mode = False
def theme_change():
    global is_dark_mode
    if is_dark_mode:
        set_appearance_mode("light")
        theme_btn.configure(text="☀")
    else:
        set_appearance_mode("dark")
        theme_btn.configure(text="🌙")
    is_dark_mode = not is_dark_mode

CHAT_HISTORY_FILE = "chat_history.txt"

def save_chats():
    with open(CHAT_HISTORY_FILE, "w") as file:
        for chat in chat_history:
            # Extract the content and format it as a string
            role = chat["role"]
            content = chat["content"][0]["text"]
            file.write(f"{role.capitalize()}: {content}\n")


def load_chats():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r") as file:
            chats.configure(state="normal")
            chats.insert("1.0", file.read())
            chats.configure(state="disabled")

# Show menu
def show_menu():
    menu_btn.configure(state="disabled")
    menu_frame = CTkToplevel(base_window)
    menu_frame.geometry("200x300")
    menu_frame.title("Menu")
    menu_frame.transient(base_window)
    menu_label = CTkLabel(master=menu_frame, text="Menu Bar", font=default_font)
    menu_label.pack(pady=10)
    save_this_chat = CTkButton(master=menu_frame, text="Save Chat",command=save_chats)
    save_this_chat.pack(pady=10)
    load_chat = CTkButton(master=menu_frame, text="Load Previous Chats",command=load_chats)
    load_chat.pack(pady=10)
    close_menu = CTkButton(master=menu_frame, text="Close Menu", command=menu_frame.destroy)
    close_menu.pack(pady=10)
    menu_frame.wait_window()
    menu_btn.configure(state="normal")

# Text-to-speech functionality
def text_to_speech():
    if tts_switch.get() == 1:
        tts_switch.configure(text="ON")
    else:
        tts_switch.configure(text="OFF")

chat_history = []
# Main chat function that will be threaded
def threaded_chat():
    global chat_history
    enter_button.bind("<Return>")
    chats.configure(state="normal")
    chats.insert(END, f"\n🧏🏻: {user_inp.get()}\n")
    chats.configure(state="disabled")
    user_inp.configure()
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)

    url = "https://lokiai.vercel.app/api/v1/chat/completions"
    api_key = "HEET-NI-CHEESEWADI-API-KEY"

    # global chat_history
    input_u = user_inp.get()
    if "bye" in input_u or "exit" in input_u:
        chats.configure(state="normal")
        chats.insert("0.0", "🤖: Goodbye!")
        chats.configure(state="disabled")
        engine.say("Goodbye!")
        engine.runAndWait()
        return

    chat_history.append({"role": "user", "content": [{"type": "text", "text": input_u}]})
    payload = {
        "messages": chat_history,
        "model": model_selector.get()
    }

    response = requests.post(
        url,
        headers={"Authorization": api_key, "Content-Type": "application/json"},
        data=json.dumps(payload)
    )

    response_data = response.json()
    if "choices" in response_data and len(response_data["choices"]) > 0:
        answer = response_data["choices"][0]["message"]["content"]
        chats.configure(state="normal")
        user_inp.delete(0,END)
        # chats.insert(END, f"\nUser: {user_inp.get()}\n")
        chats.insert(END, f"\n🤖: {answer}\n")
        chats.configure(state="disabled")
        engine.say(answer)
        engine.runAndWait() if tts_switch.get() == 1 else None
        chat_history.append({"role": "assistant", "content": [{"type": "text", "text": answer}]})
    else:
        chats.configure(state="normal")
        chats.insert("0.0", "🤖: Error: Could not retrieve a response from the API.\n")
        chats.configure(state="disabled")

# enter key binding
def enter_key(event):
    start_chat_thread()
base_window.bind("<Return>",enter_key)

# Function to start the chat in a new thread
def start_chat_thread():
    threading.Thread(target=threaded_chat).start()

# Clear chats function
def delete():
    chats.configure(state="normal")
    chats.delete("1.0", END)
    chats.configure(state="disabled")
    user_inp.delete(0, END)

# Frame 1 for title and theme/menu buttons
frame1 = CTkFrame(master=base_window, height=70)
frame1.grid(row=0, column=0, sticky="ew", padx=10)
frame1.grid_columnconfigure(0, weight=1)
frame1.grid_columnconfigure(1, weight=1)
frame1.grid_columnconfigure(2, weight=1)

theme_btn = CTkButton(master=frame1, command=theme_change, text="🌙", fg_color="#3D3D3D", hover_color="#5D5D5D", height=50, width=50)
theme_btn.grid(row=0, column=2, padx=10, sticky="e")
title_name = CTkLabel(master=frame1, text="Neon AI", font=title_font)
title_name.grid(row=0, column=1, padx=10, sticky="ns")
menu_btn = CTkButton(master=frame1, command=show_menu, text="☰", fg_color="#3D3D3D", hover_color="#5D5D5D", height=50, width=50)
menu_btn.grid(row=0, column=0, sticky="w", padx=10)

# Frame 2 for chat display
chats = CTkTextbox(master=base_window, font=chat_font, state="normal")
chats.grid(row=1, column=0, sticky="nsew", padx=10)
greeting_lines = [
    "Hey there! How can I assist you today?",
    "Hello! Ready to tackle some questions?",
    "Hi, friend! What would you like to chat about?"
]
chats.insert("0.0", f"🤖: {random.choice(greeting_lines)}\n")
chats.configure(state="disabled")

# Frame 3 for user input and controls
frame3 = CTkFrame(master=base_window, height=50)
frame3.grid(row=2, column=0, sticky="ew", padx=10)
frame3.grid_columnconfigure(0, weight=1)
frame3.grid_columnconfigure(1, weight=1)
frame3.grid_columnconfigure(2, weight=1)
frame3.grid_columnconfigure(3, weight=1)
frame3.grid_columnconfigure(4, weight=1)

user_inp = CTkEntry(master=frame3, height=50, corner_radius=25, width=500, border_width=0, font=input_font, placeholder_text="Ask Neon !!")
user_inp.grid(pady=10, padx=10, row=0, column=2, sticky="nsew")

tts_switch = CTkSwitch(master=frame3, text="TEXT TO SPEECH", command=text_to_speech)
tts_switch.grid(row=0, column=0, padx=10)

model_list = ["gpt-4o", "gpt-4o-mini", "llama-3.1-405b"]
model_selector = CTkOptionMenu(master=frame3, values=model_list)
model_selector.grid(row=0, column=1, padx=10, sticky="w")

enter_button = CTkButton(master=frame3, text="🔍", command=enter_key, height=50, width=50, border_width=0, fg_color="#3D3D3D", hover_color="#5D5D5D", corner_radius=25, font=chat_font)
enter_button.grid(row=0, column=3, sticky="e")

delete_button = CTkButton(master=frame3, text="🚮", command=delete, height=50, width=50, border_width=0, fg_color="#3D3D3D", hover_color="#5D5D5D", corner_radius=25, font=chat_font)
delete_button.grid(row=0, column=4, padx=10)

# Run the app
base_window.mainloop()
