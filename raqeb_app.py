import os
import time
import requests
import streamlit as st

st.set_page_config(page_title="رقيب", layout="centered")

# -------- STATE --------
if "page" not in st.session_state:
    st.session_state.page = "splash"

if "history" not in st.session_state:
    st.session_state.history = []

# -------- API --------
API_KEY = "sk-xxxxxxxx"

CHAT_URL = "http://elmodels.ngrok.app/v1/chat/completions"
TTS_URL  = "http://elmodels.ngrok.app/v1/audio/speech"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer sk-xxxxxxxx"
}

# -------- STYLE --------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {background:#F6F1E8;}
.block-container {max-width:420px;margin:auto;}

.title {text-align:center;font-size:32px;font-weight:bold;color:#7E6AA2;}

.card {
    background:white;
    padding:18px;
    border-radius:20px;
    margin-top:10px;
    font-size:18px;
    text-align:center;
}

button {
    width:100%;
    height:45px;
    border-radius:12px;
    background:#7E6AA2;
    color:white;
}
</style>
""", unsafe_allow_html=True)

# -------- تحليل حقيقي (المهم) --------
def real_status(heart, spo2, temp):

    if spo2 < 90 or heart > 130 or temp > 39:
        return "danger"

    elif spo2 < 95 or heart > 100 or temp > 37.5:
        return "warning"

    else:
        return "good"

# -------- LLM (نُهى) --------
def ai_analysis(heart, spo2, temp):

    prompt = f"""
    أنتِ نُهى 👩‍⚕️ مساعد صحي.

    اشرحي الحالة بشكل بسيط ولطيف لمستخدم من ذوي التوحد.

    نبض: {heart}
    أكسجين: {spo2}
    حرارة: {temp}
    """

    try:
        res = requests.post(CHAT_URL, headers=HEADERS, json={
            "model":"nuha-2.0",
            "messages":[{"role":"user","content":prompt}]
        }).json()

        if "choices" in res:
            return res["choices"][0]["message"]["content"]
    except:
        pass

    return "أنا نُهى، خلينا نتابع الحالة بهدوء"

# -------- صوت --------
def speak(status):

    if status == "good":
        return

    if status == "danger":
        text = "أنا نُهى، الحالة خطرة، لازم نتصرف الآن"
    else:
        text = "أنا نُهى، خلينا نتابع الحالة بهدوء"

    try:
        res = requests.post(TTS_URL, headers=HEADERS, json={
            "model":"elm-tts",
            "input": text,
            "voice":"ar"
        })
        st.audio(res.content)
    except:
        pass

# -------- SPLASH --------
if st.session_state.page == "splash":

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if os.path.exists("raqeb.jpeg"):
            st.image("raqeb.jpeg", width=150)

    st.markdown("<div class='title'>رقيب 🧠</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'> مساعد ذكي</p>", unsafe_allow_html=True)

    time.sleep(2)

    st.session_state.page = "login"
    st.rerun()

# -------- LOGIN --------
elif st.session_state.page == "login":

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if os.path.exists("raqeb.jpeg"):
            st.image("raqeb.jpeg", width=120)

    st.markdown("<div class='title'>رقيب 🧠</div>", unsafe_allow_html=True)

    st.text_input("البريد الإلكتروني")
    st.text_input("كلمة المرور", type="password")

    if st.button("تسجيل الدخول"):
        st.session_state.page = "form"
        st.rerun()

# -------- FORM --------
elif st.session_state.page == "form":

    st.markdown("## بيانات المستخدم")

    st.text_input("الاسم")
    st.number_input("العمر", 1, 100)
    st.radio("الجنس", ["ذكر","أنثى"])
    st.multiselect("الأمراض", ["سكر","ضغط","قلب","لا يوجد"])

    if st.button("التالي"):
        st.session_state.page = "home"
        st.rerun()

# -------- HOME --------
elif st.session_state.page == "home":

    st.markdown("## 🧠 مؤشراتك الحيويه مع نُهى")

    heart = st.slider("❤️ نبض القلب", 40, 180, 80)
    spo2  = st.slider("🫁 الأكسجين", 50, 100, 98)
    temp  = st.slider("🌡️ الحرارة", 34.0, 41.0, 36.5)

    if st.button("تحليل الحالة"):

        # ✅ التحليل الحقيقي
        cls = real_status(heart, spo2, temp)

        # 🧠 شرح LLM
        result = ai_analysis(heart, spo2, temp)

        st.session_state.history.append(result)

        # تنبيه
        if cls == "danger":
            st.error("🚨 حالة خطرة")
        elif cls == "warning":
            st.warning("⚠️ تحتاج مراقبة")
        else:
            st.success("✅ طبيعي")

        # 💥 بصري
        if cls == "danger":
            st.markdown("<h1 style='text-align:center;'>🔴 😰</h1>", unsafe_allow_html=True)
        elif cls == "warning":
            st.markdown("<h1 style='text-align:center;'>🟡 😟</h1>", unsafe_allow_html=True)
        else:
            st.markdown("<h1 style='text-align:center;'>🟢 🙂</h1>", unsafe_allow_html=True)

        st.markdown(f"<div class='card'>🧠 {result}</div>", unsafe_allow_html=True)

        speak(cls)

    if st.button("💬 الشات"):
        st.session_state.page = "chat"
        st.rerun()

    if st.button("📊 السجل"):
        st.session_state.page = "history"
        st.rerun()

# -------- CHAT --------
elif st.session_state.page == "chat":

    msg = st.text_input("اكتب لنُهى")

    if st.button("إرسال"):
        try:
            res = requests.post(CHAT_URL, headers=HEADERS, json={
                "model":"nuha-2.0",
                "messages":[{"role":"user","content":msg}]
            }).json()

            reply = res["choices"][0]["message"]["content"]
        except:
            reply = "في مشكلة"

        st.markdown(f"<div class='card'>🧠 {reply}</div>", unsafe_allow_html=True)

    if st.button("رجوع"):
        st.session_state.page = "home"
        st.rerun()

# -------- HISTORY --------
elif st.session_state.page == "history":

    st.markdown("## 🧠 السجل")

    if len(st.session_state.history) == 0:
        st.info("لا يوجد بيانات")
    else:
        for h in st.session_state.history[::-1]:
            st.markdown(f"<div class='card'>{h}</div>", unsafe_allow_html=True)

    if st.button("رجوع"):
        st.session_state.page = "home"
        st.rerun()
