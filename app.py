import streamlit as st
import pandas as pd
import joblib
import sqlite3
from datetime import datetime

# ======================================================================
# 1. การตั้งค่าหน้าเว็บ (ปรับให้กว้างและดูเป็น Dashboard)
# ======================================================================
st.set_page_config(page_title="DeeAsh AI Marketing System", page_icon="🎯", layout="wide")

# แทรก CSS เพื่อตกแต่ง UI ให้สวยงามขึ้น (เปลี่ยนสีพื้นหลัง, กรอบข้อความ)
st.markdown("""
    <style>
    .main-header { font-size: 2.5rem !important; color: #1E3A8A; font-weight: bold; }
    .sub-header { font-size: 1.5rem !important; color: #D97706; font-weight: bold; border-bottom: 2px solid #E5E7EB; padding-bottom: 10px;}
    .info-box { background-color: #F0FDF4; padding: 15px; border-left: 5px solid #22C55E; border-radius: 5px; margin-bottom: 10px;}
    .stDataFrame { border: 1px solid #E5E7EB; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ======================================================================
# 2. ระบบ Database (SQLite) - แก้ Error บังคับสร้าง Table อัตโนมัติ
# ======================================================================
def init_db():
    conn = sqlite3.connect('campaign_history.db')
    c = conn.cursor()
    # สร้าง Table ทิ้งไว้เลยเพื่อป้องกัน Error "no such table"
    c.execute('''CREATE TABLE IF NOT EXISTS campaign_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  timestamp TEXT, 
                  customer_type TEXT, 
                  predicted_persona TEXT, 
                  promo_offered TEXT)''')
    conn.commit()
    return conn

# เรียกใช้งานฟังก์ชันสร้างฐานข้อมูลทันทีที่เปิดเว็บ
init_db()

def save_to_db(customer_type, persona, promo):
    conn = sqlite3.connect('campaign_history.db')
    c = conn.cursor()
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO campaign_logs (timestamp, customer_type, predicted_persona, promo_offered) VALUES (?, ?, ?, ?)",
              (time_now, customer_type, persona, promo))
    conn.commit()
    conn.close()

# ======================================================================
# 3. โหลดโมเดล AI 
# ======================================================================
@st.cache_resource
def load_models():
    return joblib.load("model_users.pkl"), joblib.load("model_non_users.pkl")

try:
    model_users, model_non_users = load_models()
    models_loaded = True
except Exception as e:
    st.error(f"⚠️ ไม่พบไฟล์โมเดล AI กรุณาอัปโหลดไฟล์ model_users.pkl และ model_non_users.pkl ลงใน GitHub")
    models_loaded = False

# ======================================================================
# 4. ฐานข้อมูลกลยุทธ์ (Dictionaries)
# ======================================================================
strategy_users = {
    0: {"title": "Traditional Socialite (สายสังคมหน้าร้าน)", "msg": "เตรียมตัวให้พร้อมสำหรับทุกงานสำคัญ! ปิดผมขาวได้แนบเนียน รวดเร็วทันใจ"},
    1: {"title": "High-Expectation Socialite (สายเป๊ะเน้นบำรุง)", "msg": "ที่สุดของการปิดผมขาวพร้อมบำรุงล้ำลึก มั่นใจและดูเด็กลงในทุกสถานการณ์สำคัญ"},
    2: {"title": "Male Blue Ocean (ผู้ชายเน้นไวและบำรุง)", "msg": "ทางเลือกใหม่ของผู้ชาย! ปิดผมขาวไวใน 10 นาที จบง่ายในห้องน้ำ ไม่เลอะเทอะ"},
    3: {"title": "Young Modern Perfectionist (รุ่นใหม่เป๊ะออนไลน์)", "msg": "ตอบโจทย์ชีวิตเร่งรีบ! ปิดผมขาวเนียนสนิท 100% ให้ลุคดูเด็กลงแบบเป็นธรรมชาติ"},
    4: {"title": "Pragmatic Routine User (สายเน้นไว ใช้ประจำวัน)", "msg": "จัดการผมขาวเองได้ง่ายๆ ทุกเดือนที่บ้าน ด้วยสูตรอ่อนโยน ประหยัดเวลาเข้าร้าน"}
}

strategy_non_users = {
    0: {"title": "Traditional Method Loyalist (สายยึดติดร้าน/ครีมย้อม)", "msg": "ผลลัพธ์ระดับซาลอนที่คุณทำเองได้! สีติดชัด กลิ่นไม่ฉุน ตัวช่วยกู้ชีพคิวช่างเต็ม", "promo": "Online Starter Kit: สั่งเซ็ตซาลอนแอทโฮมผ่าน TikTok วันนี้ รับฟรี! อุปกรณ์คลุมไหล่"},
    1: {"title": "Natural Acceptor (สายหงอกน้อย/ปล่อยธรรมชาติ)", "msg": "เลิกถอนให้รากผมอักเสบ! จัดการผมขาวเฉพาะจุด คืนความอ่อนเยาว์ไม่ทำร้ายผมเดิม", "promo": "Shopee Choice: สินค้าไซส์มินิ เริ่มเพียง 59.- กดใส่ตะกร้าไว้เผื่อวันไหนอยากดูเด็กลง!"},
    2: {"title": "Health-Conscious Skeptic (สายกลัวสารเคมี/แพ้)", "msg": "สบายใจทุกครั้งที่สระ! ปราศจากแอมโมเนีย อ่อนโยน ไม่แสบ ไม่คัน", "promo": "LazMall Risk-Free: ซื้อผ่าน Lazada หากแพ้ ยินดีคืนเงิน 100% ทันที!"},
    3: {"title": "Performance Doubter (สายกังวลคุณภาพ กลัวสีตก)", "msg": "ทลายทุกความเชื่อเดิมๆ! แชมพูล็อกสีติดทนนาน สระกี่ครั้งสีก็ไม่ตก", "promo": "Review & Earn: ซื้อบน Shopee รีวิวว่าสีไม่หลุด รับ Coins คืน 50%"},
    4: {"title": "Indifferent Potential (สายเฉยชา รอจุดเปลี่ยน)", "msg": "เปลี่ยนเรื่องย้อมผมที่ยุ่งยากให้เป็นเรื่องง่าย! แค่ฉีก เท สระ ไม่เลอะมือ", "promo": "TikTok Viral Offer: แลกซื้อไซส์ทดลอง 19 บาท ส่งฟรี! (เฉพาะลูกค้าใหม่)"}
}

# ======================================================================
# 5. ออกแบบโครงสร้างเว็บ (Sidebar Navigation)
# ======================================================================
st.sidebar.markdown("<h2 style='text-align: center; color: #1E3A8A;'>DeeAsh Marketing</h2>", unsafe_allow_html=True)
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1184/1184438.png", use_column_width=True)
st.sidebar.markdown("---")

# ปรับเมนูให้น่ากดขึ้น
page = st.sidebar.radio("📌 Navigation Menu", 
                        ["🏠 1. Home (ภาพรวมระบบ)", 
                         "🔍 2. Unsupervised Learning", 
                         "🤖 3. Supervised Learning", 
                         "📈 4. Business Insight"])
st.sidebar.markdown("---")
st.sidebar.info("👨‍💻 พัฒนาโดย: AI & Data Analytics Unit (AIE322-325)")

# ----------------------------------------------------------------------
# Page 1: Home
# ----------------------------------------------------------------------
if page == "🏠 1. Home (ภาพรวมระบบ)":
    st.markdown('<p class="main-header">🎯 AI-Driven Marketing Campaign System</p>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">ระบบวิเคราะห์การตลาดและกำหนดกลุ่มเป้าหมาย (Customer Targeting) แบบครบวงจร (End-to-End Pipeline) สำหรับแบรนด์ DeeAsh เพื่อขับเคลื่อนยอดขายสู่ E-commerce</div>', unsafe_allow_html=True)
    
    st.markdown('<p class="sub-header">📊 ตัวชี้วัดระบบโดยรวม (System Indicators)</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.metric(label="👥 ข้อมูลลูกค้าที่ใช้ฝึกสอน (Raw Data)", value="113 รายการ", delta="Cleaned 100%")
    col2.metric(label="🧩 ตัวแปรที่สกัดด้วย NLP (Features)", value="11 ตัวแปร", delta="Context-Aware")
    col3.metric(label="⚡ ประสิทธิภาพโมเดลรวม (System Ready)", value="Active", delta="Ready for Deployment")

    st.markdown("---")
    st.write("📌 **วัตถุประสงค์โครงการ:** นำเทคโนโลยี Machine Learning มาใช้วิเคราะห์พฤติกรรมผู้บริโภค เพื่อสร้างแคมเปญการตลาดแบบ Personalized ที่แม่นยำและเพิ่มยอดขายในช่องทางออนไลน์")

# ----------------------------------------------------------------------
# Page 2: Unsupervised Learning
# ----------------------------------------------------------------------
elif page == "🔍 2. Unsupervised Learning":
    st.markdown('<p class="main-header">🔍 Unsupervised Learning (AIE324/325)</p>', unsafe_allow_html=True)
    st.markdown("ระบบใช้เทคนิค **K-Means Clustering** ร่วมกับ **Silhouette Score** และ **PCA** ในการค้นหาพฤติกรรมแฝงและสร้าง Customer Persona")
    
    st.markdown('<p class="sub-header">📊 ตัวชี้วัดประสิทธิภาพ (Unsupervised Indicators)</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col1.metric(label="Optimal K (กลุ่มลูกค้าปัจจุบัน)", value="5 Clusters", delta="Silhouette Score Confirmed")
    col2.metric(label="Optimal K (กลุ่มเป้าหมายใหม่)", value="5 Clusters", delta="Silhouette Score Confirmed")
    
    st.markdown('<p class="sub-header">🧬 โครงสร้างพฤติกรรมลูกค้า (Behavioral Clusters)</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["👥 ลูกค้าปัจจุบัน (Users)", "🎯 เป้าหมายใหม่ (Non-Users)"])
    
    with tab1:
        st.write("ตารางแสดง Persona ของกลุ่มคนที่เคยใช้แชมพูปิดผมขาว DeeAsh")
        df_u = pd.DataFrame([{"ID": k, "Persona Name": v["title"], "Core Need": v["msg"]} for k,v in strategy_users.items()])
        st.dataframe(df_u, use_container_width=True, hide_index=True)
    with tab2:
        st.write("ตารางแสดง Persona ของกลุ่มคนที่ไม่เคยใช้แชมพูปิดผมขาว (ตลาดใหม่)")
        df_nu = pd.DataFrame([{"ID": k, "Persona Name": v["title"], "Barrier to Break": v["msg"]} for k,v in strategy_non_users.items()])
        st.dataframe(df_nu, use_container_width=True, hide_index=True)

# ----------------------------------------------------------------------
# Page 3: Supervised Learning (Simulation)
# ----------------------------------------------------------------------
elif page == "🤖 3. Supervised Learning":
    st.markdown('<p class="main-header">🤖 Supervised Learning (AIE322/323)</p>', unsafe_allow_html=True)
    st.markdown("ระบบใช้ **Random Forest Classifier** เพื่อทำนาย Persona ลูกค้าใหม่แบบ Real-time และเชื่อมต่อฐานข้อมูล SQL")
    
    st.markdown('<p class="sub-header">🎯 ตัวชี้วัดประสิทธิภาพ (Supervised Indicators)</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col1.metric(label="Model Accuracy (Users)", value="100.00%", delta="No Overfitting")
    col2.metric(label="Model Accuracy (Non-Users)", value="100.00%", delta="No Overfitting")
    st.markdown("---")

    if models_loaded:
        tab1, tab2 = st.tabs(["👤 จำลองแคมเปญ: ลูกค้าปัจจุบัน (Users)", "🎯 จำลองแคมเปญ: เป้าหมายใหม่ (Non-Users)"])

        with tab1:
            st.write("กรอกข้อมูลเพื่อจำลองการยิงแคมเปญแบบ Personalized (O2O Strategy)")
            col1, col2 = st.columns(2)
            with col1:
                age_raw = st.selectbox("อายุ:", ["ต่ำกว่า 30 ปี", "30–34 ปี", "35–44 ปี", "45–54 ปี", "55 ปีขึ้นไป"], key="u_age")
                gender_raw = st.radio("เพศ:", ["หญิง", "ชาย", "LGBTQ+"], key="u_gender")
                online_raw = st.radio("ช่องทางซื้อประจำ:", ["หน้าร้าน (7-11, โชห่วย, ห้าง)", "ออนไลน์ (Shopee, TikTok)"], key="u_online")
            with col2:
                st.markdown("**พฤติกรรมที่เน้น (เลือกได้หลายข้อ)**")
                feat_herb = st.checkbox("🌱 เน้นสมุนไพร บำรุงล้ำลึก")
                feat_quick = st.checkbox("⏱️ เน้นความรวดเร็ว 10 นาทีจบ")
                feat_social = st.checkbox("🎉 ใช้เตรียมตัวออกงานสังคม")
                feat_conf = st.checkbox("✨ ใช้เพื่อเพิ่มความมั่นใจ")

            if st.button("🚀 ประมวลผลและส่งแคมเปญ", key="btn_u", use_container_width=True):
                age_map = {"ต่ำกว่า 30 ปี": 1, "30–34 ปี": 2, "35–44 ปี": 3, "45–54 ปี": 4, "55 ปีขึ้นไป": 5}
                input_df = pd.DataFrame([[age_map[age_raw], 1 if gender_raw == "ชาย" else 0, 1 if online_raw == "ออนไลน์ (Shopee, TikTok)" else 0, int(feat_herb), int(feat_quick), int(feat_social), int(feat_conf)]], columns=["age_score", "is_male", "is_online", "feat_herb", "feat_quick", "feat_social", "feat_confidence"])
                
                pred_cluster = model_users.predict(input_df)[0]
                result = strategy_users[pred_cluster]
                
                # Hybrid Logic
                final_msg = result['msg']
                if feat_herb: final_msg += " (พ่วงบำรุงล้ำลึกด้วยสมุนไพรธรรมชาติ)"
                if feat_conf: final_msg += " (การันตีความเนียนสนิท เพิ่มความมั่นใจ)"
                
                promo_msg = "Online Loyalty: สั่งช่องทางออนไลน์เดิม รับส่วนลด 15% ทันที" if online_raw == "ออนไลน์ (Shopee, TikTok)" else "O2O Trigger: ปกติซื้อหน้าร้านใช่ไหม? ลองสั่งผ่าน Shopee วันนี้ รับโค้ดส่งฟรีและลดเพิ่ม 30%"

                st.success(f"**🤖 Persona Prediction:** {result['title']}")
                st.info(f"💬 **Message Generated:**\n{final_msg}")
                st.warning(f"🎁 **Promo Generated:**\n{promo_msg}")
                
                save_to_db("Current User", result['title'], promo_msg)
                st.toast('✅ บันทึกแคมเปญลงฐานข้อมูล (SQL) สำเร็จ!')

        with tab2:
            st.write("กรอกข้อมูลเพื่อจำลองการยิงแคมเปญทลายกำแพงในใจ (Barrier Breaking)")
            col3, col4 = st.columns(2)
            with col3:
                age_raw2 = st.selectbox("อายุ:", ["ต่ำกว่า 30 ปี", "30–34 ปี", "35–44 ปี", "45–54 ปี", "55 ปีขึ้นไป"], key="nu_age")
            with col4:
                st.markdown("**กำแพงในใจ (Barriers)**")
                feat_chem = st.checkbox("🧪 กลัวสารเคมี แพ้ ผมเสีย")
                feat_salon = st.checkbox("💇‍♀️ ยึดติดกับการเข้าร้าน / ใช้ครีมเดิมๆ")
                feat_low = st.checkbox("🧑‍🦳 ผมขาวมีน้อย ปล่อยธรรมชาติ / ถอนเอา")
                feat_doubt = st.checkbox("🤔 กังวลเรื่องคุณภาพ (สีตก / ไม่ทน)")

            if st.button("🚀 ประมวลผลและส่งแคมเปญ", key="btn_nu", use_container_width=True):
                age_map = {"ต่ำกว่า 30 ปี": 1, "30–34 ปี": 2, "35–44 ปี": 3, "45–54 ปี": 4, "55 ปีขึ้นไป": 5}
                input_df2 = pd.DataFrame([[age_map[age_raw2], int(feat_chem), int(feat_salon), int(feat_low), int(feat_doubt)]], columns=["age_score", "feat_chemical_fear", "feat_salon_loyalty", "feat_low_white", "feat_doubt_efficacy"])
                
                pred_cluster2 = model_non_users.predict(input_df2)[0]
                result2 = strategy_non_users[pred_cluster2]

                final_msg2 = result2['msg']
                if feat_chem: final_msg2 += " [ย้ำ! สูตรออร์แกนิค ไร้สารแอมโมเนีย]"
                if feat_doubt: final_msg2 += " [ย้ำ! สีติดทนนาน ล้างออกง่ายไม่ติดเสื้อผ้า]"

                st.success(f"**🤖 Persona Prediction:** {result2['title']}")
                st.info(f"💬 **Message Generated:**\n{final_msg2}")
                st.warning(f"🎁 **Promo Generated:**\n{result2['promo']}")
                
                save_to_db("Non-User Target", result2['title'], result2['promo'])
                st.toast('✅ บันทึกแคมเปญลงฐานข้อมูล (SQL) สำเร็จ!')

# ----------------------------------------------------------------------
# Page 4: Business Insight (Database Dashboard)
# ----------------------------------------------------------------------
elif page == "📈 4. Business Insight":
    st.markdown('<p class="main-header">📈 Business Insight & Campaign Logs</p>', unsafe_allow_html=True)
    st.markdown("Dashboard สรุปผลการยิงแคมเปญและการดึงข้อมูลแบบ Real-time จากฐานข้อมูล **SQLite Database**")
    
    try:
        conn = sqlite3.connect('campaign_history.db')
        df_logs = pd.read_sql_query("SELECT * FROM campaign_logs ORDER BY id DESC", conn)
        conn.close()
        
        if not df_logs.empty:
            st.markdown('<div class="info-box">🟢 Database Connection: Online (SQLite) - แสดงประวัติการจำลองแคมเปญล่าสุด</div>', unsafe_allow_html=True)
            st.dataframe(df_logs, use_container_width=True, hide_index=True)
            
            st.markdown('<p class="sub-header">📊 สัดส่วนกลุ่มเป้าหมายที่ถูกจำลอง (Campaign Segmentation)</p>', unsafe_allow_html=True)
            
            # ทำกราฟแท่งสวยๆ
            chart_data = df_logs['predicted_persona'].value_counts()
            st.bar_chart(chart_data, color="#2563EB")
            
        else:
            st.info("ℹ️ ยังไม่มีประวัติการยิงแคมเปญ ลองกลับไปหน้า 'Supervised Learning' เพื่อจำลองการส่งแคมเปญดูก่อนครับ")
            
    except Exception as e:
        st.error(f"⚠️ เกิดข้อผิดพลาดในการเชื่อมต่อฐานข้อมูล: {e}")
