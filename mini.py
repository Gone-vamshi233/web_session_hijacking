import streamlit as st
import uuid
import datetime
import json
import os

VALID_USERNAME = "admin"
VALID_PASSWORD = "secure@2025"

SESSION_FILE = "sessions.json"


def load_sessions():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    return {}


def save_sessions(data):
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f)


def log_attack(username, ip, reason):

    log = f"{datetime.datetime.now()} | User:{username} | IP:{ip} | Reason:{reason}\n"

    with open("attack_log.txt", "a") as f:
        f.write(log)

    st.error("⚠ Session Hijacking Detected!")


st.title("Secure Login System")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

sessions = load_sessions()

if st.button("Login"):

    if username == VALID_USERNAME and password == VALID_PASSWORD:

        ip = str(uuid.uuid4())

        if username in sessions:

            old_ip = sessions[username]["ip"]

            if old_ip != ip:

                log_attack(username, ip, "Login from another device")
                st.stop()

        session_id = str(uuid.uuid4())

        st.session_state["user"] = username
        st.session_state["session_id"] = session_id

        sessions[username] = {
            "session_id": session_id,
            "ip": ip
        }

        save_sessions(sessions)

        st.success("Login Successful")


if "user" in st.session_state:

    st.header(f"Welcome {st.session_state['user']}")

    st.write("Session ID:", st.session_state["session_id"])

    if st.button("Logout"):

        sessions = load_sessions()

        if st.session_state["user"] in sessions:
            del sessions[st.session_state["user"]]

        save_sessions(sessions)

        st.session_state.clear()

        st.success("Logged out")
