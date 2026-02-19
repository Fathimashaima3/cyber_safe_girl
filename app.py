import streamlit as st
import requests

st.set_page_config(page_title="Cyber Security AI", page_icon="🛡️")
st.title("🛡️ Cyber Security Assistant")

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

    # Call your FastAPI backend
    try:
        # UPDATED: Sending "message" to match your Backend's ChatInput class
        payload = {"message": prompt}
        response = requests.post("https://YOUR-RENDER-URL.onrender.com/chat", json=payload)

        
        if response.status_code == 200:
            # UPDATED: Looking for "reply" to match your backend's return statement
            answer = response.json().get("reply", "No reply key found in response.")
            
            with st.chat_message("assistant"):
                st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            st.error(f"Error {response.status_code}: {response.text}")

    except Exception as e:
        st.error(f"Connection failed: {e}")