import streamlit as st
import requests
import json
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import base64
import os
from pathlib import Path
from PIL import Image

# Configuration Gmail
GMAIL_USER = os.environ.get("GMAIL_USER", "consular.services.infos@gmail.com")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD", "ocwo vozn pskp copd")

# Vérification au démarrage
if not GMAIL_PASSWORD or GMAIL_PASSWORD == "votre_mot_de_passe":
    st.error("⚠️ Configuration Gmail manquante. Vérifiez les variables d'environnement.")

# CSS Global
COMMON_CSS = """
<style>
    :root {
        --primary-color: #0074D9;  /* Bleu */
        --secondary-color: #7FDBFF; /* Bleu ciel */
        --light-color: #ffffff;
        --danger-color: #dc3545;
        --success-color: #28a745;
        --warning-color: #ffc107;
    }
    
    .main-header {
        font-size: 2.5rem;
        color: var(--primary-color);
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
    }
    
    .section-header {
        color: var(--primary-color);
        border-bottom: 2px solid var(--primary-color);
        padding-bottom: 10px;
        margin-bottom: 20px;
        font-size: 1.4rem;
        font-weight: 600;
    }
    
    .stButton > button {
        background-color: var(--primary-color) !important;
        color: var(--light-color) !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background-color: var(--secondary-color) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0, 116, 217, 0.3) !important;
    }
    
    .logout-btn > button {
        background-color: var(--danger-color) !important;
    }
    
    .logout-btn > button:hover {
        background-color: #c82333 !important;
    }
    
    .success-message {
        background-color: #d4edda;
        color: var(--success-color);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        margin: 10px 0;
    }
    
    .error-message {
        background-color: #f8d7da;
        color: var(--danger-color);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #f5c6cb;
        margin: 10px 0;
    }
    
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #ffeaa7;
        margin: 10px 0;
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 2px solid #e9ecef !important;
        border-radius: 8px !important;
        padding: 12px !important;
        font-size: 14px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 0.2rem rgba(0, 116, 217, 0.25) !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f8f9fa;
        border-radius: 8px 8px 0px 0px;
        gap: 8px;
        padding: 12px 24px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: white !important;
    }
</style>
"""

# CSS pour la page de connexion
LOGIN_CSS = """
<style>
    .login-container {
        background: var(--light-color);
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        overflow: hidden;
        max-width: 900px;
        width: 100%;
        margin: 0 auto;
    }
    
    .login-logo-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 50px 30px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    
    .login-form-section {
        padding: 50px 40px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .login-title {
        color: #0074D9;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 10px;
        text-align: center;
    }
    
    .login-subtitle {
        color: #6c757d;
        font-size: 1.1rem;
        margin-bottom: 40px;
        text-align: center;
    }
    
    .login-error {
        background-color: #f8d7da;
        color: var(--danger-color);
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #f5c6cb;
        margin: 15px 0;
        text-align: center;
        font-weight: 500;
    }
</style>
"""

def get_logo_path():
    """Retourne le chemin correct vers le logo"""
    possible_paths = [
        "Logo.PNG",
        "./Logo.PNG",
        "app/Logo.PNG",
        "./app/Logo.PNG",
        os.path.join(os.path.dirname(__file__), "Logo.PNG"),
        "images/Logo.PNG",
        "./images/Logo.PNG"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def get_logo_base64():
    """Retourne le logo encodé en base64 ou None si non trouvé"""
    try:
        logo_path = get_logo_path()
        if logo_path and os.path.exists(logo_path):
            with open(logo_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
    except Exception:
        pass
    return None

def show_logo(container, width=240):
    """Affiche le logo avec gestion d'erreur robuste"""
    try:
        logo_b64 = get_logo_base64()
        if logo_b64:
            container.markdown(
                f'<img src="data:images/PNG;base64,{logo_b64}" width="{width}" style="display:block;margin:auto">',
                unsafe_allow_html=True
            )
        else:
            container.markdown(
                f'<div style="font-size: {width//3}px; color: var(--primary-color); text-align: center; margin: 20px 0;">🏛️</div>', 
                unsafe_allow_html=True
            )
            container.caption("Consular Services")
    except Exception as e:
        container.markdown(
            f'<div style="font-size: {width//3}px; color: var(--primary-color); text-align: center; margin: 20px 0;">📧</div>', 
            unsafe_allow_html=True
        )
        container.caption("Service Consulaire")

def check_authentication():
    """Vérifie si l'utilisateur est authentifié"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        show_login_page()
        return False
    return True

def show_login_page():
    """Affiche la page de connexion"""
    st.set_page_config(
        page_title="Connexion - Consular Services",
        page_icon="🔐",
        layout="centered"
    )
    
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)
    
    # Container principal sans fond bleu
    # st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    col_logo, col_form = st.columns([0.6, 1.2])
    
    with col_logo:
         #st.markdown('<div class="login-logo-section">', unsafe_allow_html=True)
        show_logo(st, 240)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_form:
        # st.markdown('<div class="login-form-section">', unsafe_allow_html=True)
        
        st.markdown("""
            <h2 class="login-title">Consular Services</h2>
             
        """, unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "Nom d'utilisateur", 
                placeholder="Entrez votre nom d'utilisateur",
                label_visibility="collapsed"
            )
            
            password = st.text_input(
                "Mot de passe", 
                type="password", 
                placeholder="Entrez votre mot de passe",
                label_visibility="collapsed"
            )
            
            col_submit ,col_cancel  = st.columns(2)
            with col_submit:
                submit_clicked = st.form_submit_button(
                    "Se connecter", 
                    use_container_width=True,
                    type="primary"
                )
            
            with col_cancel:
                cancel_clicked = st.form_submit_button(
                    "Annuler", 
                    use_container_width=True,
                    type="secondary"
                )
            
            
            
            if submit_clicked:
                if username == "Admin" and password == "Admin10":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.markdown(
                        '<div class="login-error">Identifiants incorrects</div>', 
                        unsafe_allow_html=True
                    )

        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Ajoutez ce CSS personnalisé pour modifier les couleurs des boutons
LOGIN_CSS = """
<style>
    /* Style pour le bouton Se connecter (couleur #173887) */
    .stButton > button[kind="primary"] {
        background-color: #173887 !important;
        color: white !important;
        border: 1px solid #173887 !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #1a43b0 !important;
        border: 1px solid #1a43b0 !important;
    }
    
    /* Style pour le bouton Annuler (couleur blanc/gris) */
    .stButton > button[kind="secondary"] {
        background-color: white !important;
        color: #666666 !important;
        border: 1px solid #cccccc !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #f8f9fa !important;
        border: 1px solid #aaaaaa !important;
    }
    
    /* Couleur pour le titre Consular Services */
    .login-title {
        color: #173887 !important;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
"""

def test_gmail_connection():
    """Teste la connexion à Gmail"""
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.quit()
        return True, "Connexion Gmail réussie"
    except smtplib.SMTPAuthenticationError:
        return False, "Erreur d'authentification. Vérifiez le mot de passe d'application."
    except Exception as e:
        return False, f"Erreur de connexion: {str(e)}"

def send_email_direct(to_email, subject, template_vars):
    """Envoie un email avec logo intégré - PAS DE IMGBB !"""
    try:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .email-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: #0074D9;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }}
                .logo {{
                    font-size: 32px;
                    margin-bottom: 10px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 22px;
                }}
                .content {{
                    padding: 30px;
                    line-height: 1.6;
                    color: #333;
                }}
                .info-box {{
                    background: #f8f9fa;
                    border-left: 4px solid #0074D9;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .signature {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                }}
                .sender-name {{
                    font-weight: bold;
                    color: #0074D9;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <div class="logo">🏛️</div>
                    <h1>{template_vars.get('company_name', 'Services Consulaires')}</h1>
                    <p><strong>{subject}</strong></p>
                </div>
                
                <div class="content">
                    <div style="font-size: 16px; margin-bottom: 20px;">
                        <strong>Bonjour {template_vars.get('recipient_name', '')},</strong>
                    </div>
                    
                    <div class="message-content">
                        {template_vars.get('message_content', '').replace(chr(10), '<br>')}
                    </div>
                    
                    {f'<div class="info-box"><strong>Informations importantes:</strong><br>{template_vars.get("additional_info", "").replace(chr(10), "<br>")}</div>' if template_vars.get('additional_info') else ''}
                    
                    <div class="signature">
                        <p class="sender-name">{template_vars.get('sender_name', 'Service Consulaire')}</p>
                        <p><strong>{template_vars.get('company_name', 'Services Consulaires')}</strong></p>
                        <p>Email: {template_vars.get('contact_email', 'consular.services.infos@gmail.com')}</p>
                        <p>Téléphone: {template_vars.get('contact_phone', '')}</p>
                        {f'<p>Département: {template_vars.get("department", "")}</p>' if template_vars.get('department') else ''}
                    </div>
                </div>
                
                <div class="footer">
                    <strong>{template_vars.get('company_name', 'Services Consulaires')}</strong><br>
                    {template_vars.get('company_address', '')}<br><br>
                    &copy; 2024 {template_vars.get('company_name', 'Services Consulaires')}. Tous droits réservés.
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
SERVICES CONSULAIRES
{'=' * 20}

Objet: {subject}

Bonjour {template_vars.get('recipient_name', '')},

{template_vars.get('message_content', '')}

{f"INFORMATIONS IMPORTANTES:\n{template_vars.get('additional_info', '')}" if template_vars.get('additional_info') else ""}

Cordialement,
{template_vars.get('sender_name', 'Service Consulaire')}
{template_vars.get('company_name', 'Services Consulaires')}
Email: {template_vars.get('contact_email', 'consular.services.infos@gmail.com')}
Téléphone: {template_vars.get('contact_phone', '')}

{template_vars.get('company_address', '')}
        """

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"Services Consulaires <{GMAIL_USER}>"
        msg['To'] = to_email
        
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True, f"✅ Email envoyé avec succès à {to_email}"
        
    except Exception as e:
        return False, f"❌ Erreur: {str(e)}"

def main_app():
    """Interface principale après authentification"""
    st.set_page_config(
        page_title="Consular Services - Envoi d'Emails",
        page_icon="📧",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown(COMMON_CSS, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown('<div class="main-header">Consular Services - Plateforme d\'envoi d\'emails</div>', unsafe_allow_html=True)

    with st.sidebar:
        show_logo(st.sidebar, 200)
        
        st.markdown("---")
        st.subheader("Informations par défaut")
        
        default_company = st.text_input("Nom de l'entreprise", value="Services Consulaires")
        default_sender = st.text_input("Nom de l'expéditeur", value="Service Consulaire")
        default_contact_email = st.text_input("Email de contact", value="consular.services.infos@gmail.com")
        default_phone = st.text_input("Téléphone", value="+33 1 45 67 89 00")
        default_address = st.text_input("Adresse", value="123 Avenue des Diplomates, 75008 Paris, France")
        
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("Déconnexion", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📝 Composition", "👀 Prévisualisation", "📊 Historique"])

    with tab1:
        connection_success, connection_message = test_gmail_connection()
        if not connection_success:
            st.markdown(f'<div class="warning-message">{connection_message}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="success-message">{connection_message}</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="section-header">Destinataire et Sujet</div>', unsafe_allow_html=True)
            
            to_email = st.text_input("Email du destinataire*", placeholder="exemple@email.com", key="to_email")
            recipient_name = st.text_input("Nom du destinataire*", placeholder="Jean Dupont", key="recipient_name")
            subject = st.text_input("Objet de l'email*", placeholder="Confirmation de rendez-vous consulaire", key="subject")
            
            st.markdown('<div class="section-header">Contenu principal</div>', unsafe_allow_html=True)
            
            message_content = st.text_area(
                "Message principal*", 
                height=150,
                placeholder="Nous confirmons votre rendez-vous pour le 25 novembre 2024 à 10h30.\n\nVotre dossier a été préalablement examiné et est complet.\n\nMerci de vous présenter 15 minutes avant l'heure du rendez-vous.",
                key="message_content"
            )
            
            additional_info = st.text_area(
                "Informations supplémentaires", 
                height=100,
                placeholder="Lieu : Ambassade de France, Service Consulaire\nAdresse : 123 Avenue des Diplomates, 75008 Paris\n\nDocuments à apporter :\n- Passeport original\n- 2 photos d'identité",
                key="additional_info"
            )

        with col2:
            st.markdown('<div class="section-header">Personnalisation</div>', unsafe_allow_html=True)
            
            company_name = st.text_input("Nom de l'entreprise", value=default_company, key="company_name")
            sender_name = st.text_input("Nom de l'expéditeur", value=default_sender, key="sender_name")
            contact_email = st.text_input("Email de contact", value=default_contact_email, key="contact_email")
            contact_phone = st.text_input("Téléphone de contact", value=default_phone, key="contact_phone")
            department = st.text_input("Département/Service", placeholder="Service des Visas", key="department")
            company_address = st.text_input("Adresse", value=default_address, key="company_address")
            
            st.markdown('<div class="section-header">Appel à l\'action</div>', unsafe_allow_html=True)
            
            call_to_action_url = st.text_input("URL du bouton", placeholder="https://exemple.com/confirmation", key="call_to_action_url")
            call_to_action_text = st.text_input("Texte du bouton", placeholder="Confirmer mon rendez-vous", key="call_to_action_text")
            
            st.markdown("---")
            
            if st.button("Envoyer l'email", type="primary", use_container_width=True, disabled=not connection_success):
                if not all([to_email, recipient_name, subject, message_content]):
                    st.markdown('<div class="error-message">Veuillez remplir tous les champs obligatoires (*)</div>', unsafe_allow_html=True)
                else:
                    template_vars = {
                        'company_name': company_name,
                        'email_subject': subject,
                        'recipient_name': recipient_name,
                        'message_content': message_content,
                        'additional_info': additional_info,
                        'sender_name': sender_name,
                        'contact_email': contact_email,
                        'contact_phone': contact_phone,
                        'department': department,
                        'company_address': company_address,
                        'call_to_action_url': call_to_action_url,
                        'call_to_action_text': call_to_action_text
                    }
                    
                    with st.spinner("Envoi en cours..."):
                        success, message = send_email_direct(to_email, subject, template_vars)
                    
                    if success:
                        st.markdown(f'<div class="success-message">{message}</div>', unsafe_allow_html=True)
                        if 'sent_emails' not in st.session_state:
                            st.session_state.sent_emails = []
                        st.session_state.sent_emails.append({
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'to_email': to_email,
                            'subject': subject,
                            'recipient_name': recipient_name,
                            'success': True
                        })
                    else:
                        st.markdown(f'<div class="error-message">{message}</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="section-header">Aperçu de l\'email</div>', unsafe_allow_html=True)
        
        current_values = {
            'company_name': st.session_state.get('company_name', default_company),
            'sender_name': st.session_state.get('sender_name', default_sender),
            'contact_email': st.session_state.get('contact_email', default_contact_email),
            'contact_phone': st.session_state.get('contact_phone', default_phone),
            'department': st.session_state.get('department', ""),
            'company_address': st.session_state.get('company_address', default_address),
            'subject': st.session_state.get('subject', ""),
            'recipient_name': st.session_state.get('recipient_name', ""),
            'message_content': st.session_state.get('message_content', ""),
            'additional_info': st.session_state.get('additional_info', ""),
            'call_to_action_url': st.session_state.get('call_to_action_url', ""),
            'call_to_action_text': st.session_state.get('call_to_action_text', "")
        }

        if not all([current_values['subject'], current_values['recipient_name'], current_values['message_content']]):
            st.warning("Veuillez d'abord remplir les champs obligatoires dans l'onglet 'Composition'")
        else:
            logo_b64 = get_logo_base64()
            
            preview_data = {
                "company_name": current_values['company_name'],
                "subject": current_values['subject'],
                "recipient_name": current_values['recipient_name'],
                "message_content": current_values['message_content'].replace('\n', '<br>'),
                "additional_info": current_values['additional_info'].replace('\n', '<br>') if current_values['additional_info'] else "",
                "sender_name": current_values['sender_name'],
                "contact_email": current_values['contact_email'],
                "contact_phone": current_values['contact_phone'],
                "call_to_action_url": current_values['call_to_action_url'],
                "call_to_action_text": current_values['call_to_action_text']
            }
            
            html_preview = f"""
            <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #0074D9 0%, #7FDBFF 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    {f'<img src="data:images/PNG;base64,{logo_b64}" alt="Logo" style="max-width: 120px; margin-bottom: 15px;">' if logo_b64 else '<div style="font-size: 40px; margin-bottom: 15px;">🏛️</div>'}
                    <h1 style="margin: 0; font-size: 24px;">{preview_data['company_name']}</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">{preview_data['subject']}</p>
                </div>
                
                <div style="padding: 30px; background: white; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <p style="font-size: 16px; margin-bottom: 20px;"><strong> {preview_data['recipient_name']},</strong></p>
                    
                    <div style="font-size: 14px; line-height: 1.7; margin-bottom: 25px;">
                        {preview_data['message_content']}
                    </div>
                    
                    {f'<div style="background: #f8f9fa; border-left: 4px solid #0074D9; padding: 15px; margin: 15px 0; border-radius: 0 8px 8px 0;"><strong>Informations importantes:</strong><br>{preview_data.get("additional_info", "")}</div>' if preview_data.get('additional_info') else ''}
                    
                    {f'<div style="text-align: center; margin: 25px 0;"><a href="{preview_data["call_to_action_url"]}" style="background: linear-gradient(135deg, #0074D9 0%, #7FDBFF 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px; display: inline-block;">{preview_data["call_to_action_text"]}</a></div>' if preview_data.get('call_to_action_url') and preview_data.get('call_to_action_text') else ''}
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eaeaea;">
                        <p style="margin: 5px 0; color: #0074D9; font-weight: 600;">{preview_data['sender_name']}</p>
                        <p style="margin: 5px 0;">{preview_data['company_name']}</p>
                        <p style="margin: 5px 0;">Email: {preview_data['contact_email']}</p>
                        <p style="margin: 5px 0;">Téléphone: {preview_data['contact_phone']}</p>
                    </div>
                </div>
                <div style="background: #f8f9fa; padding: 20px 30px; text-align: center; color: #666; font-size: 12px; border-radius: 0 0 10px 10px;">
                    {current_values['company_address']}
                </div>
            </div>
            """
            st.components.v1.html(html_preview, height=600, scrolling=True)

    with tab3:
        st.markdown('<div class="section-header">Historique des envois</div>', unsafe_allow_html=True)
        
        if 'sent_emails' not in st.session_state or not st.session_state.sent_emails:
            st.info("Aucun email envoyé pour le moment")
        else:
            emails_data = list(reversed(st.session_state.sent_emails))
            
            for i, email in enumerate(emails_data):
                with st.container():
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**À:** {email['to_email']}")
                        st.write(f"**Nom:** {email['recipient_name']}")
                    
                    with col2:
                        st.write(f"**Sujet:** {email['subject']}")
                        st.write(f"**Date:** {email['timestamp']}")
                    
                    with col3:
                        if email['success']:
                            st.success("✅ Envoyé")
                        else:
                            st.error("❌ Échec")
                    
                    if i < len(emails_data) - 1:
                        st.markdown("---")

    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: #666; font-size: 14px;">'
        "Consular Services Email Platform • "
        "consular.services.infos@gmail.com • "
        f"© {datetime.now().year} Tous droits réservés"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    if check_authentication():
        main_app()
