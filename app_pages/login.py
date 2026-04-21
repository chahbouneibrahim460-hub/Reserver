import streamlit as st
from utils.auth import process_login_request, is_authenticated, get_group_by_email
from utils.session import save_session_cookie

st.header("🔑 Connexion / Identité")

if is_authenticated() or st.session_state.get("is_bachelor", False):
    # Auto-redirect to reservation page if already logged in or identity set
    st.switch_page("app_pages/reservation.py")
else:
    tab1, tab2 = st.tabs(["Groupes PLBD", "Groupes Bachelor"])
    
    with tab1:
        st.subheader("Connexion Étudiant PLBD")
        st.write("Entrez votre email de l'école pour recevoir un lien de connexion.")
        
        with st.form("plbd_login_form"):
            email = st.text_input("Email de l'école", placeholder="prenom.nom@centrale-casablanca.ma", key="plbd_email")
            submitted = st.form_submit_button("Envoyer le lien de connexion")
        
        if submitted:
            if email:
                base_url = st.secrets.get("general", {}).get("base_url", "http://localhost:8501")
                
                success, message = process_login_request(email, base_url)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.warning("Veuillez entrer une adresse email.")

    with tab2:
        st.subheader("Identité Étudiant Bachelor")
        st.write("Sélectionnez votre groupe et entrez votre email pour le suivi des réservations.")
        
        with st.form("bachelor_identity_form"):
            bachelor_group = st.selectbox("Sélectionner le Groupe", [1, 2, 3, 4], format_func=lambda x: f"Bachelor {x}")
            bachelor_email = st.text_input("Votre Email", placeholder="votre.email@example.com", key="bachelor_email")
            submitted = st.form_submit_button("Définir l'Identité")
        
        if submitted:
            if not bachelor_email:
                st.warning("Veuillez entrer votre adresse email.")
            else:
                g_type, g_idx = get_group_by_email(bachelor_email)
                if g_type == "plbd":
                    st.error(f"Cette adresse email appartient au groupe PLBD {g_idx}. Veuillez utiliser l'onglet 'Groupes PLBD' pour recevoir votre lien de connexion.")
                else:
                    st.session_state.logged_in = False
                    st.session_state.is_bachelor = True
                    st.session_state.group_type = "bachelor"
                    st.session_state.group_index = bachelor_group
                    st.session_state.user_email = bachelor_email
                    # Save session to cookie for persistence
                    save_session_cookie()
                    st.success(f"Identité définie sur Bachelor {bachelor_group}. Vous pouvez maintenant faire des réservations.")
                    st.rerun()

st.divider()
st.info("Remarque : Les groupes PLBD sont limités à 3 réservations en semaine et 5 le week-end. Les groupes Bachelor sont limités à 5 en semaine et 6 le week-end.")
