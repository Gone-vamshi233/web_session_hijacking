import streamlit as st
import uuid
import datetime
from streamlit.web.server.websocket_headers import _get_websocket_headers

# -------------------------------
# LOGIN CREDENTIALS
# -------------------------------
VALID_USERNAME = "admin"
VALID_PASSWORD = "secure@20"

# -------------------------------
# SESSION STORAGE
# -------------------------------
if "user_sessions" not in st.session_state:
    st.session_state.user_sessions = {}

# -------------------------------
# GET CLIENT IP
# -------------------------------
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

# -------------------------------
# GET USER AGENT
# -------------------------------
def get_user_agent():
    try:
        headers = _get_websocket_headers()
        if headers:
            return headers.get("User-Agent", "Unknown")
    except:
        pass
    return "Unknown"

# -------------------------------
# ATTACK LOGGER
# -------------------------------
def log_attack(username, ip, reason):

    log = f"{datetime.datetime.now()} | USER:{username} | IP:{ip} | REASON:{reason}\n"

    with open("attack_log.txt", "a") as f:
        f.write(log)

    # RED ALERT MESSAGE
    st.error(
        f"""
🚨 SECURITY ALERT 🚨

User: **{username}**

IP Address: **{ip}**

Reason: **{reason}**
"""
    )


# -------------------------------
# APP TITLE
# -------------------------------
st.title("🔒 Session Hijacking Detection System")

# -------------------------------
# SIDEBAR SESSION INFO
# -------------------------------
if "user" in st.session_state:

    with st.sidebar:

        st.success(f"Logged in as: {st.session_state['user']}")

        st.write("### Session Details")

        st.write(f"Session ID: {st.session_state.get('session_id','N/A')[:8]}...")

        st.write(f"IP Address: {get_client_ip()}")

        st.write(f"Browser: {get_user_agent()[:50]}")

        if st.button("🚪 Logout"):

            username = st.session_state.get("user")

            if username in st.session_state.user_sessions:
                del st.session_state.user_sessions[username]

            st.session_state.clear()

            st.rerun()

# -------------------------------
# IF USER LOGGED IN
# -------------------------------
if "user" in st.session_state:

    username = st.session_state["user"]

    st.header(f"Welcome {username} 👋")

    current_ip = get_client_ip()

    current_agent = get_user_agent()

    # -------------------------------
    # VERIFY SESSION SECURITY
    # -------------------------------
    if username in st.session_state.user_sessions:

        stored = st.session_state.user_sessions[username]

        # IP CHANGE DETECTION
        if stored["ip"] != current_ip:

            reason = f"IP changed from {stored['ip']} to {current_ip}"

            log_attack(username, current_ip, reason)

            st.warning("Session terminated due to security risk")

            if st.button("Return to Login"):
                st.session_state.clear()
                st.rerun()

            st.stop()

        # BROWSER CHANGE DETECTION
        if stored["user_agent"] != current_agent:

            reason = "Browser/User-Agent changed"

            log_attack(username, current_ip, reason)

            st.warning("Session terminated due to browser change")

            if st.button("Return to Login"):
                st.session_state.clear()
                st.rerun()

            st.stop()

    # -------------------------------
    # SESSION SAFE MESSAGE
    # -------------------------------
    st.success("✅ Your session is secure")

    st.subheader("Current Session Info")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("IP Address", current_ip)

    with col2:
        st.metric("Session ID", st.session_state.get("session_id")[:8] + "...")

    st.info(f"Browser: {current_agent}")

    # -------------------------------
    # ADMIN ACTIVE SESSIONS
    # -------------------------------
    if st.checkbox("Show Active Sessions (Admin Only)"):

        st.subheader("Active Sessions")

        st.json(st.session_state.user_sessions)

# -------------------------------
# LOGIN PAGE
# -------------------------------
else:

    st.subheader("🔐 Login")

    st.info(
        """
Demo Credentials

Username: admin

Password: secure@2026
"""
    )

    with st.form("login_form"):

        username = st.text_input("Username")

        password = st.text_input("Password", type="password")

        submit = st.form_submit_button("Login")

        if submit:

            if username == VALID_USERNAME and password == VALID_PASSWORD:

                ip = get_client_ip()

                user_agent = get_user_agent()

                # -------------------------------
                # CHECK CONCURRENT LOGIN
                # -------------------------------
                if username in st.session_state.user_sessions:

                    old_ip = st.session_state.user_sessions[username]["ip"]

                    old_agent = st.session_state.user_sessions[username]["user_agent"]

                    if old_ip != ip or old_agent != user_agent:

                        reason = f"Concurrent login detected. Old IP: {old_ip}, New IP: {ip}"

                        log_attack(username, ip, reason)

                        st.stop()

                # -------------------------------
                # CREATE SESSION
                # -------------------------------
                session_id = str(uuid.uuid4())

                st.session_state["user"] = username

                st.session_state["session_id"] = session_id

                st.session_state.user_sessions[username] = {

                    "session_id": session_id,

                    "ip": ip,

                    "user_agent": user_agent,
                }

                st.success("Login Successful")

                st.rerun()

            else:

                st.error("Invalid Username or Password")


# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")

st.caption("Session Hijacking Detection System | Monitors IP & Browser Changes")
