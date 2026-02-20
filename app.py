import streamlit as st
import requests

st.set_page_config(page_title="Cyber Security AI", page_icon="🛡️")
st.title("🛡️ Cyber Security Assistant")

# --- CONFIGURATION ---
# Replace this with your actual Vercel URL
# Example: https://cyber-safe-girl.vercel.app/api/chat
VERCEL_BACKEND_URL = "https://your-project-name.vercel.app/api/chat"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask about cyber security..."):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Call your Vercel FastAPI backend
    try:
        # Send "message" to match your Backend's ChatInput class
        payload = {"message": prompt}
        
        # We use a timeout to ensure the app doesn't hang if the backend is sleeping
        response = requests.post(VERCEL_BACKEND_URL, json=payload, timeout=30)

        if response.status_code == 200:
            # Look for "reply" to match your backend's return statement
            data = response.json()
            answer = data.get("reply", "No reply key found in response.")
            
            with st.chat_message("assistant"):
                st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            st.error(f"Error {response.status_code}: {response.text}")

    except requests.exceptions.Timeout:
        st.error("The server took too long to respond. It might be waking up—please try again in a moment.")
    except Exception as e:
        st.error(f"Connection failed: {e}")