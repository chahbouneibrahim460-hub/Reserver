import streamlit as st
from utils.auth import check_auth_token, is_authenticated
from utils.session import get_cookie_manager, load_session_from_cookie, clear_session_cookie

st.set_page_config(
    page_title="MiniFabLab Reservation",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "group_type" not in st.session_state:
    st.session_state.group_type = None
if "group_index" not in st.session_state:
    st.session_state.group_index = None

# Cookie manager for persistent sessions
cookie_manager = get_cookie_manager()

# Check for token in URL (login via link)
check_auth_token()

# Restore session from cookie if not already logged in
if not st.session_state.get("group_type"):
    if load_session_from_cookie(cookie_manager):
        st.rerun()

# Store cookie manager in session state so pages can access it
st.session_state._cookie_manager = cookie_manager

# Define navigation
pages = []

# Home/Login page
pages.append(st.Page("app_pages/login.py", title="Login / Identity", icon=":material/login:"))

# Reservation page
pages.append(st.Page("app_pages/reservation.py", title="Make a Reservation", icon=":material/event:"))

# Dashboard (view all reservations)
pages.append(st.Page("app_pages/dashboard.py", title="Current Schedule", icon=":material/dashboard:"))

pg = st.navigation(pages)

# Sidebar info
with st.sidebar:
    st.title("MiniFabLab")
    if is_authenticated():
        group_label = f"{st.session_state.group_type} {st.session_state.group_index}"
        st.success(f"Logged in as: {group_label}")
        st.write(f"Email: {st.session_state.user_email}")
        if st.button("Logout"):
            clear_session_cookie(cookie_manager)
            st.session_state.logged_in = False
            st.session_state.user_email = None
            st.session_state.group_type = None
            st.session_state.group_index = None
            st.session_state.is_bachelor = False
            st.rerun()
    elif st.session_state.get("is_bachelor", False):
        group_label = f"Bachelor {st.session_state.group_index}"
        st.info(f"Identity: {group_label}")
        if st.button("Reset Identity"):
            clear_session_cookie(cookie_manager)
            st.session_state.is_bachelor = False
            st.session_state.group_type = None
            st.session_state.group_index = None
            st.session_state.user_email = None
            st.rerun()
    else:
        st.warning("Not logged in (PLBD) or Identity not set (Bachelor)")

pg.run()
