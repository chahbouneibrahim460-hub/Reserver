import json
import streamlit as st
import extra_streamlit_components as stx
from datetime import datetime, timedelta

COOKIE_NAME = "minifablab_session"
COOKIE_EXPIRY_DAYS = 30

@st.cache_resource
def get_cookie_manager():
    return stx.CookieManager()

def save_session_cookie(cookie_manager):
    """Save current session state to a browser cookie."""
    session_data = {
        "logged_in": st.session_state.get("logged_in", False),
        "is_bachelor": st.session_state.get("is_bachelor", False),
        "user_email": st.session_state.get("user_email"),
        "group_type": st.session_state.get("group_type"),
        "group_index": st.session_state.get("group_index"),
    }
    cookie_manager.set(
        COOKIE_NAME,
        json.dumps(session_data),
        expires_at=datetime.now() + timedelta(days=COOKIE_EXPIRY_DAYS),
        key="set_session_cookie"
    )

def load_session_from_cookie(cookie_manager):
    """Restore session state from a browser cookie. Returns True if session was restored."""
    cookie_value = cookie_manager.get(COOKIE_NAME)
    
    if not cookie_value:
        return False
    
    try:
        if isinstance(cookie_value, str):
            session_data = json.loads(cookie_value)
        else:
            session_data = cookie_value
        
        # Only restore if there's actual session data
        if not session_data.get("group_type"):
            return False
        
        st.session_state.logged_in = session_data.get("logged_in", False)
        st.session_state.is_bachelor = session_data.get("is_bachelor", False)
        st.session_state.user_email = session_data.get("user_email")
        st.session_state.group_type = session_data.get("group_type")
        st.session_state.group_index = session_data.get("group_index")
        return True
    except (json.JSONDecodeError, TypeError):
        return False

def clear_session_cookie(cookie_manager):
    """Clear the session cookie on logout."""
    cookie_manager.delete(COOKIE_NAME, key="delete_session_cookie")
