import json
import re
import secrets
from datetime import datetime, timedelta
import streamlit as st
from utils.db import save_token, verify_token
from utils.email_utils import send_login_link

def load_plbd_emails():
    try:
        with open("plbd_emails.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def get_group_by_email(email):
    """Returns (group_type, group_index) or (None, None)."""
    plbd_data = load_plbd_emails()
    for group_key, emails in plbd_data.items():
        if email.lower() in [e.lower() for e in emails]:
            # Extract index from group key like "plbd7" -> 7
            match = re.search(r'\d+', group_key)
            group_index = int(match.group()) if match else 0
            return "plbd", group_index
    
    return None, None

def generate_login_token(email):
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=1)
    save_token(email, token, expires_at)
    return token

def process_login_request(email, base_url):
    group_type, group_index = get_group_by_email(email)
    if not group_type:
        return False, "Email not found in PLBD groups. If you are a Bachelor student, no login is required."
    
    token = generate_login_token(email)
    login_link = f"{base_url}?token={token}"
    
    if send_login_link(email, login_link):
        return True, "Login link sent to your email. Please check your inbox (and spam folder)."
    else:
        return False, "Failed to send email. Please try again later."

def check_auth_token():
    """Check query params for token and restore session. Saves cookie for persistence."""
    token = st.query_params.get("token")
    if token:
        email = verify_token(token)
        if email:
            group_type, group_index = get_group_by_email(email)
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.session_state.group_type = group_type
            st.session_state.group_index = group_index
            # Save session to cookie for persistence
            from utils.session import save_session_cookie
            cookie_manager = st.session_state.get("_cookie_manager")
            if cookie_manager:
                save_session_cookie(cookie_manager)
            # Clear token from URL
            st.query_params.clear()
            return True
    return False

def is_authenticated():
    return st.session_state.get("logged_in", False)
