import streamlit as st
import folium
from streamlit_folium import st_folium
import sqlite3
from rules import evaluate_hazard_rules

# Page Setup
st.set_page_config(page_title="HAZARD ASSISTANT", page_icon="🚨", layout="wide")

# SQLite Setup
def init_db():
    conn = sqlite3.connect('hazard_system.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY, password TEXT, name TEXT,
                    age INTEGER, mobility TEXT, language TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Session State Defaults
defaults = {
    'logged_in': False, 'username': '', 'name': 'Ramesh Kumar',
    'age': 70, 'mobility': 'Limited Mobility', 'language': 'Telugu',
    'hazard_type': 'Flood 🌊', 'severity': 'High',
    'battery_level': 100, 'offline_mode': False, 'chat_history': []
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Multilingual Alerts
TRANSLATIONS = {
    'English': {'alert': '🚨 EMERGENCY ALERT — HIGH RISK', 'warning': 'Follow specific disaster protocols below immediately.'},
    'Telugu': {'alert': '🚨 అత్యవసర హెచ్చరిక — అధిక ప్రమాదం', 'warning': 'వెంటనే సురక్షిత ప్రాంతానికి వెళ్ళండి.'},
    'Hindi': {'alert': '🚨 आपातकालीन चेतावनी — उच्च जोखिम', 'warning': 'नीचे दिए गए आपदा दिशानिर्देशों का पालन करें।'},
    'Tamil': {'alert': '🚨 அவசர எச்சரிக்கை — அதிக ஆபத்து', 'warning': 'பாதுகாப்பான இடத்திற்கு உடனடியாக செல்லவும்.'},
    'Kannada': {'alert': '🚨 ತುರ್ತು ಎಚ್ಚರಿಕೆ — ಹೆಚ್ಚಿನ ಅಪಾಯ', 'warning': 'ಸುರಕ್ಷಿತ ಪ್ರದೇಶಕ್ಕೆ ತಕ್ಷಣ ತೆರಳಿ.'}
}

def speak_text(text):
    lang_map = {'English': 'en-US', 'Telugu': 'te-IN', 'Hindi': 'hi-IN', 'Tamil': 'ta-IN', 'Kannada': 'kn-IN'}
    code = lang_map.get(st.session_state['language'], 'en-US')
    clean_text = text.replace("'", "\\'").replace("\n", " ")
    js_code = f"""
        <script>
            var msg = new SpeechSynthesisUtterance('{clean_text}');
            msg.lang = '{code}';
            msg.rate = 0.9;
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(msg);
        </script>
    """
    st.components.v1.html(js_code, height=0, width=0)

# Sidebar & Navigation
st.sidebar.title("🚨 HAZARD ASSISTANT")

if not st.session_state['logged_in']:
    st.sidebar.subheader("🔒 User Login")
    login_tab, signup_tab = st.sidebar.tabs(["Login", "Sign Up"])
    with login_tab:
        user = st.text_input("Username", key="l_user")
        pwd = st.text_input("Password", type="password", key="l_pwd")
        if st.button("Log In"):
            conn = sqlite3.connect('hazard_system.db')
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
            row = c.fetchone()
            conn.close()
            if row:
                st.session_state['logged_in'] = True
                st.session_state['username'], st.session_state['name'], st.session_state['age'], st.session_state['mobility'], st.session_state['language'] = row[0], row[2], row[3], row[4], row[5]
                st.rerun()
            else:
                st.error("Invalid credentials.")
    with signup_tab:
        new_user = st.text_input("New Username", key="s_user")
        new_pwd = st.text_input("New Password", type="password", key="s_pwd")
        new_name = st.text_input("Full Name", value="New User")
        new_age = st.number_input("Age", value=30, min_value=1, max_value=110)
        new_mob = st.selectbox("Mobility", ["Normal", "Limited Mobility", "Wheelchair"])
        new_lang = st.selectbox("Preferred Language", ["English", "Telugu", "Hindi", "Tamil", "Kannada"])
        if st.button("Create Account"):
            conn = sqlite3.connect('hazard_system.db')
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", (new_user, new_pwd, new_name, new_age, new_mob, new_lang))
                conn.commit()
                st.success("Account created! Please log in.")
            except sqlite3.IntegrityError:
                st.error("Username already exists.")
            conn.close()
else:
    st.sidebar.write(f"Logged in: **{st.session_state['name']}**")
    if st.sidebar.button("Log Out"):
        st.session_state['logged_in'] = False
        st.rerun()

st.sidebar.markdown("---")

# 🚨 HAZARD SELECTOR IN SIDEBAR (CHOOSE ANY OF THE 7 OPTIONS)
st.sidebar.subheader("🚨 Disaster Selection")
hazards_list = [
    "Flood 🌊", 
    "Fire 🔥", 
    "Gas Leak 💨", 
    "Building Collapse 🏚️", 
    "Road Accident 🚗", 
    "Cyclone 🌪️", 
    "Earthquake 🌎"
]
st.session_state['hazard_type'] = st.sidebar.selectbox("Active Disaster", hazards_list, index=hazards_list.index(st.session_state['hazard_type']))
st.session_state['severity'] = st.sidebar.select_slider("Severity Level", ["Low", "Medium", "High", "Critical"], value=st.session_state['severity'])

st.sidebar.markdown("---")
nav = st.sidebar.radio("Navigation", [
    "1. Dashboard",
    "2. User Profile",
    "3. Emergency Guidance & Voice",
    "4. Emergency Chat Assistant",
    "5. Wearable Assistant"
])

# Global Controls
st.session_state['language'] = st.sidebar.selectbox("🌐 System Language", ["English", "Telugu", "Hindi", "Tamil", "Kannada"], index=["English", "Telugu", "Hindi", "Tamil", "Kannada"].index(st.session_state['language']))
st.session_state['battery_level'] = st.sidebar.slider("🔋 Battery Level", 5, 100, st.session_state['battery_level'])
st.session_state['offline_mode'] = st.sidebar.toggle("📶 Offline Mode", st.session_state['offline_mode'])

lang_dict = TRANSLATIONS.get(st.session_state['language'], TRANSLATIONS['English'])

# PAGE 1: DASHBOARD
if nav == "1. Dashboard":
    st.title("హజార్డ్ అసిస్టెంట్" if st.session_state['language'] == 'Telugu' else "HAZARD ASSISTANT")
    st.caption("Personalized Multi-Hazard Emergency System")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Hazard", st.session_state['hazard_type'])
    col2.metric("Severity Level", st.session_state['severity'])
    col3.metric("Network", "📶 Offline" if st.session_state['offline_mode'] else "🌐 Online")
    col4.metric("Battery Level", f"{st.session_state['battery_level']}%")
    
    st.error(f"### {lang_dict['alert']} — {st.session_state['hazard_type'].upper()}")
    st.write(f"**Warning:** {lang_dict['warning']}")

# PAGE 2: USER PROFILE
elif nav == "2. User Profile":
    st.title("👤 User Profile Settings")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state['name'] = st.text_input("Name", st.session_state['name'])
        st.session_state['age'] = st.number_input("Age", 1, 100, st.session_state['age'])
    with col2:
        st.session_state['mobility'] = st.selectbox("Mobility Condition", ["Normal", "Limited Mobility", "Wheelchair"], index=["Normal", "Limited Mobility", "Wheelchair"].index(st.session_state['mobility']))
        st.session_state['language'] = st.selectbox("Language Profile", ["English", "Telugu", "Hindi", "Tamil", "Kannada"], index=["English", "Telugu", "Hindi", "Tamil", "Kannada"].index(st.session_state['language']))

# PAGE 3: GUIDANCE & VOICE
elif nav == "3. Emergency Guidance & Voice":
    st.title(f"🚨 Guidance: {st.session_state['hazard_type']}")
    st.error(f"### {lang_dict['alert']}")
    
    steps, warnings = evaluate_hazard_rules(
        st.session_state['hazard_type'], st.session_state['age'], st.session_state['mobility'],
        st.session_state['battery_level'], st.session_state['offline_mode'], st.session_state['language']
    )

    if st.button("🔊 Play Voice Guidance", type="primary"):
        speak_text(f"Alert for {st.session_state['hazard_type']}. " + " ".join(steps[:2]))
        
    st.markdown("---")
    st.subheader(f"📋 Personalized Guidance for {st.session_state['name']}")
    for idx, step in enumerate(steps, 1):
        st.write(f"**{idx}.** {step}")
    for w in warnings:
        st.warning(f"⚠️ {w}")

    st.markdown("---")
    st.subheader("🏫 Shelter & Safe Route")
    if st.session_state['offline_mode'] or st.session_state['battery_level'] <= 20:
        st.warning("📶 Offline/Low Battery: Directional cached view.")
        st.write("📍 **Safe Area 1** — 800m North")
    else:
        m = folium.Map(location=[16.3067, 80.4365], zoom_start=14)
        folium.Marker([16.3067, 80.4365], popup="You", icon=folium.Icon(color="red")).add_to(m)
        folium.Marker([16.3150, 80.4420], popup="Safe Zone", icon=folium.Icon(color="green")).add_to(m)
        st_folium(m, height=260, use_container_width=True)

# PAGE 4: CHATBOT
# ==========================================
# PAGE 4: EMERGENCY CHAT ASSISTANT (UPDATED)
# ==========================================
elif nav == "4. Emergency Chat Assistant":
    st.title("💬 Emergency & Evacuation Chatbot")
    st.caption(f"Currently monitoring: **{st.session_state['hazard_type']}**")

    # Display Chat History
    for msg in st.session_state['chat_history']:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_query = st.chat_input("Ask about disasters, packing items, or evacuation...")

    if user_query:
        # Save & Display User Question
        st.session_state['chat_history'].append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.write(user_query)

        q = user_query.lower()
        hazard = st.session_state['hazard_type']

        # RULE 1: Standard Emergency Bag / Carrying Checklist
        if any(w in q for w in ["carry", "pack", "bag", "items", "bring", "kit", "checklist"]):
            reply = """
🎒 **UNIVERSAL EMERGENCY GO-BAG CHECKLIST:**
* **Documents:** Government IDs, insurance papers, cash in a waterproof bag.
* **Medical:** 7-day essential medicines, first-aid kit, extra glasses/wheelchair accessories.
* **Survival:** Sealed bottled water (2L per person), high-calorie non-perishable food.
* **Tech:** Fully charged power bank, flashlight, emergency whistle, battery radio.
* **Personal:** Warm extra clothes, N95 masks, sturdy shoes, hygiene wipes.
            """

        # RULE 2: Specific Disaster Advice (Floods)
        elif "flood" in q or "Flood" in hazard:
            if any(w in q for w in ["water", "drink"]):
                reply = "⚠️ **Flood Water Warning:** Never drink tap or flood water. Use bottled water only to avoid waterborne diseases."
            else:
                reply = "🌊 **Flood Action:** Pack your Go-Bag, turn off main electricity/gas lines, and move immediately to high ground or Shelter A."

        # RULE 3: Specific Disaster Advice (Fire)
        elif "fire" in q or "Fire" in hazard:
            reply = "🔥 **Fire Action:** Leave everything behind except vital meds/IDs if immediately accessible. Crawl low under smoke and never use elevators."

        # RULE 4: Specific Disaster Advice (Gas Leak)
        elif "gas" in q or "Gas" in hazard:
            reply = "💨 **Gas Leak Action:** Cover your mouth, do NOT touch light switches or smartphones indoors, and evacuate into fresh outdoor air immediately."

        # RULE 5: Specific Disaster Advice (Earthquake / Collapse)
        elif "earthquake" in q or "collapse" in q or "Earthquake" in hazard or "Collapse" in hazard:
            reply = "🛡️ **Earthquake Action:** Drop, Cover, and Hold On. If trapped, tap periodically on metal pipes so rescue teams can locate you."

        # RULE 6: Shelter Location Queries
        elif any(w in q for w in ["shelter", "where", "route", "location"]):
            reply = "📍 **Nearest Safe Zone:** Safe Shelter A is located **800m North**. Wheelchair ramps and medical teams are available."

        # Default Response
        else:
            reply = f"For **{hazard}**, focus on personal safety first. Type **'what to carry'** to see your emergency checklist or **'shelter'** for route guidance."

        # Save & Display Assistant Response
        st.session_state['chat_history'].append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.write(reply)

# PAGE 5: WEARABLE
elif nav == "5. Wearable Assistant":
    st.title("⌚ Wearable Display")
    steps, _ = evaluate_hazard_rules(
        st.session_state['hazard_type'], st.session_state['age'], st.session_state['mobility'],
        st.session_state['battery_level'], st.session_state['offline_mode'], st.session_state['language']
    )
    short_step = steps[0] if steps else "EVACUATE"

    st.markdown(f"""
        <div style="width:260px; height:320px; background:#000; border:8px solid #333; border-radius:35px; padding:15px; margin:auto; text-align:center; color:#fff; font-family:monospace;">
            <div style="font-size:0.75rem; color:#888;">14:32 | 🔋 {st.session_state['battery_level']}%</div>
            <hr style="border-color:#333; margin:8px 0;">
            <div style="color:#ff4b4b; font-weight:bold; font-size:1rem;">{st.session_state['hazard_type']}</div>
            <div style="font-size:0.7rem; color:#ffaa00;">SEVERITY: {st.session_state['severity']}</div>
            <div style="background:#222; padding:8px; border-radius:6px; font-size:0.75rem; margin:10px 0; height:80px; overflow:hidden;">
                {short_step}
            </div>
            <div>
                <span style="background:#333; padding:4px 8px; border-radius:4px; font-size:0.7rem;">🔊 LISTEN</span>
                <span style="background:#f00; padding:4px 8px; border-radius:4px; font-size:0.7rem; font-weight:bold;">🆘 SOS</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
