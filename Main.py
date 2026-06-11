import streamlit as st
import datetime
import pandas as pd
import streamlit.components.v1 as components
import cv2

# ==========================================
# 1. PAGE CONFIGURATION & SESSION STATE
# ==========================================
st.set_page_config(page_title="AI Camera Control System", layout="wide")

if 'page' not in st.session_state:
    st.session_state.page = 'welcome'
if 'mode' not in st.session_state:
    st.session_state.mode = None
if 'history' not in st.session_state:
    st.session_state.history = []
if 'recent_crime' not in st.session_state:
    st.session_state.recent_crime = None
if 'invalid_activities' not in st.session_state:
    st.session_state.invalid_activities = []
if 'traffic_cases' not in st.session_state:
    st.session_state.traffic_cases = {}
if 'camera_url' not in st.session_state:
    st.session_state.camera_url = ""
if 'camera_connected' not in st.session_state:
    st.session_state.camera_connected = False

def go_to_page(page_name):
    st.session_state.page = page_name

# ==========================================
# 2. WELCOME SCREEN
# ==========================================
if st.session_state.page == 'welcome':
    st.markdown("<h1 style='text-align: center; color: #2c3e50;'>AI Camera Controlling System</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #7f8c8d;'>Created by Students of Sammilani Secondary School</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        logo_url = "https://i.postimg.cc/1X8qZ0vV/Gemini-Generated-Image-z401dnz401dnz401.png"
        try:
            st.image(logo_url, width=200)
        except:
            st.warning("লোগোর লিংকটি সঠিক নয়।")

        st.write("")
        if st.button("Start System", use_container_width=True, type="primary"):
            go_to_page('mode_selection')
            st.rerun()

# ==========================================
# 3. MODE SELECTION
# ==========================================
elif st.session_state.page == 'mode_selection':
    st.title("Select Software Mode")
    st.write("আপনি কোন মোডে সফটওয়্যারটি চালাতে চান?")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏫 Exam Hall Control", use_container_width=True):
            st.session_state.mode = 'exam'
            go_to_page('input_panel')
            st.rerun()
    with col2:
        if st.button("🚦 Traffic Control", use_container_width=True):
            st.session_state.mode = 'traffic'
            go_to_page('input_panel')
            st.rerun()

# ==========================================
# 4. INPUT PANEL (EXAM & TRAFFIC)
# ==========================================
elif st.session_state.page == 'input_panel':
    st.title(f"{'Exam Hall' if st.session_state.mode == 'exam' else 'Traffic'} Control - Input Panel")

    st.info("💡 আপনি চাইলে ম্যানুয়ালি নিয়ম না লিখে AI-এর স্বয়ংক্রিয় সিস্টেম ব্যবহার করতে পারেন।")

    if st.button("🤖 Use AI Detection (Auto)", use_container_width=True, type="secondary"):
        if st.session_state.mode == 'exam':
            st.session_state.invalid_activities = ["সন্দেহজনক নড়াচড়া", "মোবাইল ফোন ব্যবহার", "অন্যের সাথে কথা বলা", "মাথা নিচু করে থাকা"]
        elif st.session_state.mode == 'traffic':
            st.session_state.invalid_activities = ["লাল বাতি অমান্য করা", "অতিরিক্ত গতি", "হেলমেট না থাকা"]
            st.session_state.traffic_cases = {
                "লাল বাতি অমান্য করা": "৫০ টাকা জরিমানা (ধারা-৮৭)",
                "অতিরিক্ত গতি": "৩০ টাকা জরিমানা (ধারা-৮)",
                "হেলমেট না থাকা": "১০ টাকা জরিমানা (ধারা-৯০)"
            }
        st.success("AI Auto Mode চালু হয়েছে! ড্যাশবোর্ডে যাওয়া হচ্ছে...")
        go_to_page('dashboard')
        st.rerun()

    st.write("---")
    st.write("অথবা, ম্যানুয়ালি নিয়ম সেট করুন:")

    with st.form("input_form"):
        if st.session_state.mode == 'exam':
            st.subheader("অবৈধ কাজ (Invalid Activities)")
            activities = st.text_area("কী কী করলে নকল ধরা হবে? (কমা দিয়ে লিখুন)", "ডানে তাকানো, বামে তাকানো")

        elif st.session_state.mode == 'traffic':
            st.subheader("অপরাধ ও শাস্তির নিয়ম")
            activity_name = st.text_input("অপরাধের নাম (Invalid Activity):", "উইথআউট সিগন্যাল ওভারটেকিং")
            case_details = st.text_input("শাস্তি/জরিমানা (Case):", "২০০ টাকা জরিমানা")

        submitted = st.form_submit_button("Submit & Start Dashboard")

        if submitted:
            if st.session_state.mode == 'exam':
                st.session_state.invalid_activities = [x.strip() for x in activities.split(',')]
            else:
                st.session_state.invalid_activities = [activity_name]
                st.session_state.traffic_cases[activity_name] = case_details
            go_to_page('dashboard')
            st.rerun()

# ==========================================
# 5. MAIN DASHBOARD
# ==========================================
elif st.session_state.page == 'dashboard':
    st.title(f"Live Dashboard - {'Exam Hall' if st.session_state.mode == 'exam' else 'Traffic'} Monitor")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎥 Video", "🚨 Recent Crime", "📚 History", "⚙️ Invalid Activities", "🤖 AI Assistant"])

    # --- TAB 1: VIDEO ---
    with tab1:
        st.subheader("Live Camera Feed")

        # ngrok লিংক ইনপুট - শুধু কানেক্ট না হলে দেখাবে
        if not st.session_state.camera_connected:
            st.warning("📷 আগে ক্যামেরা কানেক্ট করুন")

            col1, col2 = st.columns([3, 1])
            with col1:
                camera_url_input = st.text_input(
                    "ngrok ক্যামেরা লিংক পেস্ট করো:",
                    placeholder="https://abcd1234.ngrok.io/video",
                    value=st.session_state.camera_url
                )
            with col2:
                st.write("") # spacing
                st.write("") # spacing
                if st.button("Connect Camera", type="primary", use_container_width=True):
                    if camera_url_input:
                        st.session_state.camera_url = camera_url_input
                        st.session_state.camera_connected = True
                        st.rerun()
                    else:
                        st.error("লিংক দাও আগে ভাই!")

            st.info("💡 কিভাবে লিংক পাবা? ফোনে IP Webcam অন করো → ল্যাপটপে `ngrok http 8080` চালাও → যে লিংক দিবে ওটা কপি করো")

        else:
            st.success(f"✅ ক্যামেরা কানেক্টেড: {st.session_state.camera_url}")
            if st.button("🔄 Disconnect & Change URL"):
                st.session_state.camera_connected = False
                st.rerun()

            run_camera = st.checkbox("ক্যামেরা চালু করুন 🔴")
            FRAME_WINDOW = st.image([])

            if run_camera:
                cap = cv2.VideoCapture(st.session_state.camera_url)
                if not cap.isOpened():
                    st.error("ক্যামেরা থেকে ভিডিও পাওয়া যাচ্ছে না! ngrok লিংক ঠিক আছে তো? IP Webcam অ্যাপ চালু আছে তো?")
                    st.session_state.camera_connected = False
                    st.rerun()

                while run_camera and st.session_state.camera_connected:
                    ret, frame = cap.read()
                    if not ret:
                        st.error("ভিডিও স্ট্রিম বন্ধ হয়ে গেছে! ngrok লিংক চেঞ্জ হইছে নাকি?")
                        break
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    FRAME_WINDOW.image(frame)
                cap.release()
            else:
                st.info("ক্যামেরা বর্তমানে বন্ধ আছে। চালু করতে উপরের চেকবক্সে ক্লিক করুন।")

        st.write("---")
        if st.button("⚠️ একটি অপরাধ ঘটান (Simulate Crime)"):
            now = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
            crime_name = st.session_state.invalid_activities[0] if st.session_state.invalid_activities else "Unknown"

            if st.session_state.recent_crime:
                st.session_state.history.append(st.session_state.recent_crime)

            new_crime = {
                "Time": now,
                "Crime": crime_name,
                "Case/Penalty": st.session_state.traffic_cases.get(crime_name, "কর্তৃপক্ষ ব্যবস্থা নেবে"),
                "Image": "📸 Captured_Image.jpg",
                "Total_Crimes_So_Far": len(st.session_state.history) + 1
            }
            st.session_state.recent_crime = new_crime
            st.success("অপরাধ সনাক্ত হয়েছে! Recent Crime এবং History ট্যাব চেক করুন।")

    # --- TAB 2: RECENT CRIME ---
    with tab2:
        st.subheader("তাৎক্ষণিক অপরাধ (Recent Crime)")
        if st.session_state.recent_crime:
            rc = st.session_state.recent_crime
            st.error(f"**সর্বশেষ অপরাধ:** {rc['Crime']}")
            st.write(f"**তারিখ ও সময়:** {rc['Time']}")
            if st.session_state.mode == 'traffic':
                st.write(f"**শাস্তি/জরিমানা:** {rc['Case/Penalty']}")
            st.write(f"**ছবি প্রমাণ:** {rc['Image']}")
            st.info(f"**মোট অপরাধের সংখ্যা:** {rc['Total_Crimes_So_Far']}")
        else:
            st.success("এখন পর্যন্ত কোনো অপরাধ সনাক্ত হয়নি।")

    # --- TAB 3: HISTORY ---
    with tab3:
        st.subheader("A to Z অপরাধের রেকর্ড")
        if st.session_state.history or st.session_state.recent_crime:
            all_crimes = st.session_state.history.copy()
            if st.session_state.recent_crime:
                all_crimes.append(st.session_state.recent_crime)
            df = pd.DataFrame(all_crimes)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("হিস্ট্রিতে কোনো রেকর্ড নেই।")

    # --- TAB 4: INVALID ACTIVITIES ---
    with tab4:
        st.subheader("বর্তমান নিয়মাবলি")
        updated_activities = st.text_area("নিয়মগুলো কমা (,) দিয়ে এডিট করুন:", ", ".join(st.session_state.invalid_activities))
        if st.button("Update Rules"):
            st.session_state.invalid_activities = [x.strip() for x in updated_activities.split(',')]
            st.success("নিয়মগুলো সফলভাবে আপডেট করা হয়েছে!")

    # --- TAB 5: AI CHATBOT ---
    with tab5:
        st.subheader("সহকারী AI চ্যাটবট")
        components.iframe("https://super-pithivier-64769e.netlify.app/", height=600, scrolling=True)

    st.write("---")
    if st.button("⬅️ Back to Main Menu"):
        go_to_page('mode_selection')
        st.rerun()