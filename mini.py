import streamlit as st
import uuid
import datetime
import sqlite3
from streamlit.web.server.websocket_headers import _get_websocket_headers

# ----------------------------
# DATABASE SETUP
# ----------------------------

conn = sqlite3.connect("sessions.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sessions(
username TEXT,
session_id TEXT,
ip TEXT,
user_agent TEXT
)
""")

conn.commit()

# ----------------------------
# Login credentials
# ----------------------------

VALID_USERNAME = "admin"
VALID_PASSWORD = "secure@2026"

# ----------------------------
# Get real IP address
# ----------------------------

def get_client_ip():
    try:
        headers = _get_websocket_headers()
        if headers:
            ip = headers.get("X-Forwarded-For", headers.get("X-Real-Ip", "Unknown"))
            if ip and "," in ip:
                ip = ip.split(",")[0].strip()
            return ip
    except:
        pass
    return "Unknown"

# ----------------------------
# Get user agent
# ----------------------------

def get_user_agent():
    try:
        headers = _get_websocket_headers()
        if headers:
            return headers.get("User-Agent", "Unknown")
    except:
        pass
    return "Unknown"

# ----------------------------
# Attack log
# ----------------------------

def log_attack(username, ip, reason):

    log = f"{datetime.datetime.now()} | User:{username} | IP:{ip} | Reason:{reason}\n"

    with open("attack_log.txt", "a") as f:
        f.write(log)

    st.error(f"""
🚨 SECURITY ALERT 🚨

User: **{username}**

IP Address: **{ip}**

Reason: **{reason}**
""")

# ----------------------------
# Main title
# ----------------------------

st.title("🔒 Session Hijacking Detection System")

# ----------------------------
# Sidebar
# ----------------------------

if "user" in st.session_state:

    with st.sidebar:

        st.success(f"Logged in as: {st.session_state['user']}")

        st.write(f"Session ID: {st.session_state.get('session_id','N/A')[:8]}...")

        st.write(f"Your IP: {get_client_ip()}")

        st.write(f"Browser: {get_user_agent()[:50]}")

        if st.button("Logout"):

            username = st.session_state["user"]

            cursor.execute("DELETE FROM sessions WHERE username=?", (username,))
            conn.commit()

            st.session_state.clear()

            st.rerun()

# ----------------------------
# USER LOGGED IN
# ----------------------------

if "user" in st.session_state:

    username = st.session_state["user"]

    st.header(f"Welcome {username} 👋")

    current_ip = get_client_ip()
    current_agent = get_user_agent()

    cursor.execute("SELECT * FROM sessions WHERE username=?", (username,))
    stored = cursor.fetchone()

    if stored:

        stored_ip = stored[2]
        stored_agent = stored[3]

        # IP change detection
        if stored_ip != current_ip:

            log_attack(username, current_ip,
                       f"IP changed from {stored_ip} to {current_ip}")

            st.warning("Session terminated due to security risk")

            if st.button("Return to Login"):
                st.session_state.clear()
                st.rerun()

            st.stop()

        # Browser change detection
        if stored_agent != current_agent:

            log_attack(username, current_ip,
                       "Browser/User-Agent changed")

            st.warning("Session terminated due to browser change")

            if st.button("Return to Login"):
                st.session_state.clear()
                st.rerun()

            st.stop()

    st.success("✅ Your session is secure")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("IP Address", current_ip)

    with col2:
        st.metric("Session ID", st.session_state["session_id"][:8] + "...")

    st.info(f"Browser: {current_agent}")

# ----------------------------
# LOGIN PAGE
# ----------------------------

else:

    st.subheader("🔐 Login")

    st.info("""
Demo Credentials

Username: admin
Password: secure@2026
""")

    with st.form("login_form"):

        username = st.text_input("Username")

        password = st.text_input("Password", type="password")

        submit = st.form_submit_button("Login")

        if submit:

            if username == VALID_USERNAME and password == VALID_PASSWORD:

                ip = get_client_ip()
                agent = get_user_agent()

                cursor.execute(
                    "SELECT * FROM sessions WHERE username=?", (username,))
                existing = cursor.fetchone()

                # Detect concurrent login
                if existing:

                    old_ip = existing[2]
                    old_agent = existing[3]

                    if old_ip != ip or old_agent != agent:

                        reason = f"Concurrent login attempt. Old IP: {old_ip}, New IP: {ip}"

                        log_attack(username, ip, reason)

                        st.stop()

                session_id = str(uuid.uuid4())

                cursor.execute("DELETE FROM sessions WHERE username=?", (username,))
                cursor.execute("INSERT INTO sessions VALUES(?,?,?,?)",
                               (username, session_id, ip, agent))
                conn.commit()

                st.session_state["user"] = username
                st.session_state["session_id"] = session_id

                st.success("Login Successful")

                st.rerun()

            else:

                st.error("Invalid username or password")

# ----------------------------
# Footer
# ----------------------------

st.markdown("---")
st.caption("Session Hijacking Detection System | Monitors IP and Browser changes")
