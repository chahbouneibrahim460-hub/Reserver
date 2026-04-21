import json
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta
from urllib.parse import quote, unquote

COOKIE_NAME = "minifablab_session"
COOKIE_EXPIRY_DAYS = 30

def save_session_cookie():
    """Save current session state to a browser cookie using JavaScript."""
    session_data = {
        "logged_in": st.session_state.get("logged_in", False),
        "is_bachelor": st.session_state.get("is_bachelor", False),
        "user_email": st.session_state.get("user_email"),
        "group_type": st.session_state.get("group_type"),
        "group_index": st.session_state.get("group_index"),
    }
    cookie_value = quote(json.dumps(session_data))
    expiry_days = COOKIE_EXPIRY_DAYS
    
    # Inject JavaScript to set the cookie
    js = f"""
    <script>
        var d = new Date();
        d.setTime(d.getTime() + ({expiry_days} * 24 * 60 * 60 * 1000));
        document.cookie = "{COOKIE_NAME}=" + "{cookie_value}" + ";expires=" + d.toUTCString() + ";path=/;SameSite=Strict";
    </script>
    """
    components.html(js, height=0, width=0)

def clear_session_cookie():
    """Clear the session cookie using JavaScript."""
    js = f"""
    <script>
        document.cookie = "{COOKIE_NAME}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;SameSite=Strict";
    </script>
    """
    components.html(js, height=0, width=0)

def load_session_from_cookie():
    """Restore session state from a browser cookie. Returns True if session was restored."""
    try:
        # Read cookies from Streamlit's request headers
        headers = st.context.headers
        cookie_header = headers.get("Cookie", "")
        
        if not cookie_header:
            return False
        
        # Parse cookies manually
        cookies = {}
        for item in cookie_header.split(";"):
            item = item.strip()
            if "=" in item:
                key, value = item.split("=", 1)
                cookies[key.strip()] = value.strip()
        
        cookie_value = cookies.get(COOKIE_NAME)
        if not cookie_value:
            return False
        
        session_data = json.loads(unquote(cookie_value))
        
        # Only restore if there's actual session data
        if not session_data.get("group_type"):
            return False
        
        st.session_state.logged_in = session_data.get("logged_in", False)
        st.session_state.is_bachelor = session_data.get("is_bachelor", False)
        st.session_state.user_email = session_data.get("user_email")
        st.session_state.group_type = session_data.get("group_type")
        st.session_state.group_index = session_data.get("group_index")
        return True
    except Exception:
        return False
