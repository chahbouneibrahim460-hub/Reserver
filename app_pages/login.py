import streamlit as st
from utils.auth import process_login_request, is_authenticated

st.header("🔑 Login / Identity")

if is_authenticated():
    st.success(f"You are already logged in as {st.session_state.group_name}.")
    st.info("You can go to the Reservation page to make a booking.")
    if st.button("Go to Reservation"):
        st.switch_page("app_pages/reservation.py")
else:
    tab1, tab2 = st.tabs(["PLBD Groups", "Bachelor Groups"])
    
    with tab1:
        st.subheader("PLBD Student Login")
        st.write("Enter your school email to receive a login link.")
        email = st.text_input("School Email", placeholder="first.last@centrale-casablanca.ma")
        
        if st.button("Send Login Link"):
            if email:
                # We need the base URL for the login link
                # In Streamlit Cloud, it's the public URL.
                # For local testing, it's usually http://localhost:8501
                # We can try to get it from context or just ask the user to provide it in secrets
                base_url = st.secrets.get("general", {}).get("base_url", "http://localhost:8501")
                
                success, message = process_login_request(email, base_url)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.warning("Please enter an email address.")

    with tab2:
        st.subheader("Bachelor Student Identity")
        st.write("Bachelor groups do not require a login. Please select your group.")
        bachelor_group = st.selectbox("Select Group", ["Bachelor 1", "Bachelor 2", "Bachelor 3", "Bachelor 4"])
        
        if st.button("Set Identity"):
            st.session_state.logged_in = False
            st.session_state.is_bachelor = True
            st.session_state.group_name = bachelor_group
            st.session_state.group_type = "bachelor"
            st.session_state.user_email = None
            st.success(f"Identity set to {bachelor_group}. You can now make reservations.")
            st.rerun()

st.divider()
st.info("Note: PLBD groups are limited to 3 reservations on weekdays and 5 on weekends. Bachelor groups are limited to 5 on weekdays and 6 on weekends.")
