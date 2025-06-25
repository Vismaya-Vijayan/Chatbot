import streamlit as st
import google.generativeai as generativeai
from datetime import datetime
import PyPDF2
import io

# Set your Gemini API key here
API_KEY = "AIzaSyBQbREljnT1QmPllc1igyBXY9YH8y8BO1w"

if not API_KEY:
    st.warning("Please set your Gemini API key in Streamlit secrets.")
    st.stop()

generativeai.configure(api_key=API_KEY)

# Initialize chat history and chat sessions
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [[]]  # Start with one empty chat
if "current_chat" not in st.session_state:
    st.session_state.current_chat = 0  # index of current chat

# Ensure messages always points to the current chat
def sync_messages_to_current_chat():
    st.session_state.messages = st.session_state.chat_history[st.session_state.current_chat]

def sync_current_chat_to_messages():
    st.session_state.chat_history[st.session_state.current_chat] = st.session_state.messages

# Sidebar with app info, new chat, reset, and chat selector
with st.sidebar:
    st.title("💬 Vismaya's Ai")
    st.markdown("A simple chat interface powered by Gemini 2.0 Flash.")
    st.markdown("---")
    # New Chat button
    if st.button("🆕 New Chat"):
        sync_current_chat_to_messages()
        st.session_state.chat_history.append([])  # Add a new empty chat
        st.session_state.current_chat = len(st.session_state.chat_history) - 1
        sync_messages_to_current_chat()
        st.rerun()

    # Chat list as independent buttons
    st.markdown("#### Chats")
    for idx, chat in enumerate(st.session_state.chat_history):
        label = f"Chat {idx+1}"
        if idx == st.session_state.current_chat:
            btn_type = "primary"
        else:
            btn_type = "secondary"
        if st.button(label, key=f"chat_{idx}", type=btn_type):
            if idx != st.session_state.current_chat:
                sync_current_chat_to_messages()
                st.session_state.current_chat = idx
                sync_messages_to_current_chat()
                st.rerun()

    # Reset button
    if st.button("🔄 Reset Chat"):
        st.session_state.chat_history[st.session_state.current_chat] = []
        sync_messages_to_current_chat()
        st.rerun()
    st.markdown("Made with [Streamlit](https://streamlit.io/) & Gemini API.")

# Ensure messages is always in sync with the current chat
sync_messages_to_current_chat()

st.markdown(
    """
    <style>
    .user-bubble {
        background-color: #DCF8C6;
        color: #222;
        padding: 0.7em 1em;
        border-radius: 1em 1em 0 1em;
        margin-bottom: 0.2em;
        display: inline-block;
        max-width: 80%;
    }
    .assistant-bubble {
        background-color: #F1F0F0;
        color: #222;
        padding: 0.7em 1em;
        border-radius: 1em 1em 1em 0;
        margin-bottom: 0.2em;
        display: inline-block;
        max-width: 80%;
    }
    .timestamp {
        font-size: 0.75em;
        color: #888;
        margin-left: 0.5em;
    }
    .floating-upload-btn {
        position: fixed;
        bottom: 32px;
        right: 32px;
        z-index: 1000;
    }
    .upload-btn-inner {
        background: #0099ff;
        color: white;
        border-radius: 50%;
        width: 56px;
        height: 56px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2em;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        cursor: pointer;
        border: none;
        outline: none;
        transition: background 0.2s;
    }
    .upload-btn-inner:hover {
        background: #0077cc;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Gemini model
if "model" not in st.session_state:
    st.session_state.model = generativeai.GenerativeModel("gemini-2.0-flash")

st.header(" Vismaya's Ai Chat")

# Display chat history using colored chat bubbles and timestamps
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    timestamp = msg.get("timestamp", "")
    if role == "user":
        with st.chat_message("user"):
            st.markdown(
                f'<div class="user-bubble">{content}<span class="timestamp">{timestamp}</span></div>',
                unsafe_allow_html=True,
            )
    else:
        with st.chat_message("assistant"):
            st.markdown(
                f'<div class="assistant-bubble">{content}<span class="timestamp">{timestamp}</span></div>',
                unsafe_allow_html=True,
            )

# Chat input for continuous conversation
user_input = st.chat_input("Type your message...")

if user_input:
    now = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "user", "content": user_input, "timestamp": now})
    with st.chat_message("user"):
        st.markdown(
            f'<div class="user-bubble">{user_input}<span class="timestamp">{now}</span></div>',
            unsafe_allow_html=True,
        )
    with st.spinner("Gemini is thinking..."):
        try:
            response = st.session_state.model.generate_content(user_input)
            answer = response.text
        except Exception as e:
            answer = f"Error: {e}"
    now = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "gemini", "content": answer, "timestamp": now})
    sync_current_chat_to_messages()
    with st.chat_message("assistant"):
        st.markdown(
            f'<div class="assistant-bubble">{answer}<span class="timestamp">{now}</span></div>',
            unsafe_allow_html=True,
        )

# --- Floating Upload Button and File Uploader ---
# Remove summary-section CSS (keep only upload button CSS)
st.markdown(
    """
    <style>
    .user-bubble {
        background-color: #DCF8C6;
        color: #222;
        padding: 0.7em 1em;
        border-radius: 1em 1em 0 1em;
        margin-bottom: 0.2em;
        display: inline-block;
        max-width: 80%;
    }
    .assistant-bubble {
        background-color: #F1F0F0;
        color: #222;
        padding: 0.7em 1em;
        border-radius: 1em 1em 1em 0;
        margin-bottom: 0.2em;
        display: inline-block;
        max-width: 80%;
    }
    .timestamp {
        font-size: 0.75em;
        color: #888;
        margin-left: 0.5em;
    }
    .floating-upload-btn {
        position: fixed;
        bottom: 32px;
        right: 32px;
        z-index: 1000;
    }
    .upload-btn-inner {
        background: #0099ff;
        color: white;
        border-radius: 50%;
        width: 56px;
        height: 56px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2em;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        cursor: pointer;
        border: none;
        outline: none;
        transition: background 0.2s;
    }
    .upload-btn-inner:hover {
        background: #0077cc;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Floating Upload Button (HTML + JS)
st.markdown(
    """
    <div class="floating-upload-btn" id="float-upload-btn">
        <button class="upload-btn-inner" onclick="window.dispatchEvent(new Event('openUploader'))">+</button>
    </div>
    <script>
    window.addEventListener('openUploader', function() {
        const uploader = document.querySelector('input[type="file"]:not([multiple])');
        if(uploader) uploader.click();
    });
    </script>
    """,
    unsafe_allow_html=True,
)

# File uploader (hidden, triggered by JS)
uploaded_file = st.file_uploader(
    "Upload PDF",
    type=["pdf"],
    accept_multiple_files=False,
    label_visibility="collapsed",
    key="pdf_upload"
)

# If a file is uploaded, process and summarize as a chat reply
if uploaded_file:
    now = datetime.now().strftime("%H:%M")
    # Add a "user" message to chat for the upload action
    st.session_state.messages.append({
        "role": "user",
        "content": f"Uploaded PDF: {uploaded_file.name}",
        "timestamp": now
    })
    with st.chat_message("user"):
        st.markdown(
            f'<div class="user-bubble">Uploaded PDF: {uploaded_file.name}<span class="timestamp">{now}</span></div>',
            unsafe_allow_html=True,
        )
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        if not text.strip():
            summary = "Could not extract text from this PDF."
        else:
            prompt = (
                "Please summarize the following PDF content in a clear, concise manner, "
                "highlighting key insights, main topics, and any action items or important data points. "
                "Make the summary easy to read and structured with bullet points or sections if appropriate.\n\n"
                f"PDF Content:\n{text[:15000]}"
            )
            with st.spinner(f"Summarizing {uploaded_file.name}..."):
                try:
                    response = st.session_state.model.generate_content(prompt)
                    summary = response.text
                except Exception as e:
                    summary = f"Error: {e}"
    except Exception as e:
        summary = f"Error reading PDF: {e}"
    now = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({
        "role": "gemini",
        "content": summary,
        "timestamp": now
    })
    sync_current_chat_to_messages()
    with st.chat_message("assistant"):
        st.markdown(
            f'<div class="assistant-bubble">{summary}<span class="timestamp">{now}</span></div>',
            unsafe_allow_html=True,
        )
