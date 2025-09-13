import streamlit as st
import google.generativeai as genai
import datetime

# --- Step 1: Configuration and Initialization ---

# Configure the Gemini API using Streamlit's secrets management
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("API key not found. Please add it to your .streamlit/secrets.toml file.")
    st.stop()

# Define the system instruction for the chatbot's persona
system_instruction = """
You are Arogya-Mitra, an empathetic, confidential, and supportive AI assistant for young people in India.
Your purpose is to provide a non-judgmental space for them to discuss their mental wellness concerns.

You have two modes of interaction:
1. 'Chai-pe-Charcha' Mode: In this mode, you act as a friendly and casual companion. Use a conversational, warm tone and Indian idioms where appropriate. Do not give direct advice, but instead, gently encourage self-reflection and share relatable anecdotes or open-ended questions.
2. 'Disha' Mode: In this mode, you act as a structured guide. You will lead the user through specific, simple mental wellness exercises. Your tone should be encouraging and clear.

Always start by asking the user which mode they'd like to use. If they don't specify, begin in 'Chai-pe-Charcha' mode.

IMPORTANT: If a user expresses thoughts of self-harm, suicide, or severe crisis, you MUST immediately provide a crisis helpline number and a clear safety message. Do not attempt to counsel them yourself. The safety message is: "If you are in immediate distress or crisis, please seek professional help immediately. You can contact a helpline like **TELE MANAS at 1-800 891 4416**. Your life is valuable, and help is available."
"""

# Use Streamlit's cache to initialize the model only once
@st.cache_resource(show_spinner=False)
def get_model():
    return genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=system_instruction
    )

model = get_model()

# --- Step 2: Helper Functions for Features ---

def crisis_detected(user_input):
    crisis_keywords = ["suicide", "end my life", "kill myself", "want to die", "hopeless", "can't go on", "self-harm"]
    return any(keyword in user_input.lower() for keyword in crisis_keywords)

def generate_journal_prompt(user_problem):
    prompt = f"Generate a short (1-2 sentence) journaling prompt for a young person in India who is feeling {user_problem}. The prompt should be encouraging and empathetic."
    response = model.generate_content(prompt)
    return response.text

def explain_concept(concept):
    prompt = f"Explain the concept of '{concept}' to a young Indian person in a simple, non-clinical way. Use a relatable analogy from daily life. Keep it brief, in just 2-3 sentences."
    response = model.generate_content(prompt)
    return response.text

def generate_creative_response(user_emotion):
    prompt = f"A young person is feeling {user_emotion}. Write a short, empathetic poem (4-6 lines) that they could relate to. Use a simple, comforting tone and imagery."
    response = model.generate_content(prompt)
    return response.text

# --- Step 3: Streamlit Interface and Chat Logic ---

st.title("🌱 Arogya-Mitra: Your Mental Wellness Friend")

# Initialize chat history in a Streamlit session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome! I'm Arogya-Mitra. How can I help you today?"}]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Main chat input and logic ---
# ... (all your existing imports and helper functions) ...

# --- Main chat input and logic ---
if user_input := st.chat_input("How can I help you today?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Use a container for the assistant's response to keep things clean
    with st.chat_message("assistant"):
        # Place the spinner here to indicate the AI is thinking
        # The spinner will display until the code block is finished
        with st.spinner("Arogya-Mitra is thinking..."): 
            # Handle special commands or crisis detection
            if crisis_detected(user_input):
                response_text = "If you are in immediate distress or crisis, please seek professional help immediately. You can contact a helpline like **TELE MANAS at 1-800 891 4416**. Your life is valuable, and help is available."
            elif "journal prompt" in user_input.lower():
                prompt_problem = user_input.replace("journal prompt", "").strip()
                response_text = generate_journal_prompt(prompt_problem or "stress")
            elif "explain" in user_input.lower():
                concept = user_input.replace("explain", "").strip()
                response_text = explain_concept(concept or "anxiety")
            elif "poem" in user_input.lower():
                emotion = user_input.replace("poem", "").strip()
                response_text = generate_creative_response(emotion or "calm")
            else:
                # Default chat response with history
                history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages]
                try:
                    response = model.generate_content(history)
                    response_text = response.text
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    response_text = "I'm sorry, I'm having trouble responding right now. Please try again."

            # Display the generated response
            st.markdown(response_text)

    # Add the assistant's response to chat history after it's been generated
    st.session_state.messages.append({"role": "assistant", "content": response_text})