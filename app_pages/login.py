import streamlit as st
from utils.auth import process_login_request, is_authenticated

st.header("🔑 Login / Identity")

if is_authenticated():
    group_label = f"{st.session_state.group_type} {st.session_state.group_index}"
    st.success(f"You are already logged in as {group_label}.")
    st.info("You can go to the Reservation page to make a booking.")
    if st.button("Go to Reservation"):
        st.switch_page("app_pages/reservation.py")
elif st.session_state.get("is_bachelor", False):
    group_label = f"Bachelor {st.session_state.group_index}"
    st.success(f"Identity set to {group_label}.")
    st.info("You can go to the Reservation page to make a booking.")
    if st.button("Go to Reservation"):
        st.switch_page("app_pages/reservation.py")
else:
    tab1, tab2 = st.tabs(["PLBD Groups", "Bachelor Groups"])
    
    with tab1:
        st.subheader("PLBD Student Login")
        st.write("Enter your school email to receive a login link.")
        email = st.text_input("School Email", placeholder="first.last@centrale-casablanca.ma", key="plbd_email")
        
        if st.button("Send Login Link"):
            if email:
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
        st.write("Select your group and enter your email for reservation tracking.")
        bachelor_group = st.selectbox("Select Group", [1, 2, 3, 4], format_func=lambda x: f"Bachelor {x}")
        bachelor_email = st.text_input("Your Email", placeholder="your.email@example.com", key="bachelor_email")
        
        if st.button("Set Identity"):
            if not bachelor_email:
                st.warning("Please enter your email address.")
            else:
                st.session_state.logged_in = False
                st.session_state.is_bachelor = True
                st.session_state.group_type = "bachelor"
                st.session_state.group_index = bachelor_group
                st.session_state.user_email = bachelor_email
                st.success(f"Identity set to Bachelor {bachelor_group}. You can now make reservations.")
                st.rerun()

st.divider()
st.info("Note: PLBD groups are limited to 3 reservations on weekdays and 5 on weekends. Bachelor groups are limited to 5 on weekdays and 6 on weekends.")
