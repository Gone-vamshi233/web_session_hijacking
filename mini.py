import streamlit as st
import uuid
import datetime

# login credentials
VALID_USERNAME = "admin"
VALID_PASSWORD = "secure@2026"

# store sessions
if "user_sessions" not in st.session_state:
    st.session_state.user_sessions = {}

# attack log function
def log_attack(username, ip, reason):

    log = f"{datetime.datetime.now()} | User:{username} | IP:{ip} | Reason:{reason}\n"

    with open("attack_log.txt", "a") as f:
        f.write(log)

    st.error("⚠ Session Hijacking Detected!")

# login page
st.title("Secure Login System")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):

    if username == VALID_USERNAME and password == VALID_PASSWORD:

        ip = "Simulated_IP"
        browser = "Simulated_Browser"

        if username in st.session_state.user_sessions:

            old_ip = st.session_state.user_sessions[username]["ip"]

            if old_ip != ip:

                log_attack(username, ip, "Login from different IP")
                st.stop()

        session_id = str(uuid.uuid4())

        st.session_state["user"] = username
        st.session_state["session_id"] = session_id

        st.session_state.user_sessions[username] = {
            "session_id": session_id,
            "ip": ip,
            "browser": browser
        }

        st.success("Login Successful")

# dashboard
if "user" in st.session_state:

    st.header(f"Welcome {st.session_state['user']}")

    st.write("Your session is secure.")

    st.write("Session ID:", st.session_state["session_id"])

    if st.button("Logout"):
        st.session_state.clear()
        st.success("Logged out")    