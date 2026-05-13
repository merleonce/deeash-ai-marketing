import streamlit as st
import pandas as pd
import joblib
import sqlite3
from datetime import datetime
import re

# ======================================================================
# 1. การตั้งค่าหน้าเว็บ (Professional Dashboard UI)
# ======================================================================
st.set_page_config(page_title="DeeAsh AI Marketing System", layout="wide")
st.markdown("""
    <style>
    .main-header { font-size: 2.2rem !important; color: #0F172A; font-weight: bold; }
    .sub-header { font-size: 1.3rem !important; color: #334155; font-weight: bold; border-bottom: 2px solid #E2E8F0; padding-bottom: 5px; margin-top: 20px;}
    .info-box { background-color: #F8FAFC; padding: 15px; border-left: 4px solid #3B82F6; border-radius: 4px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# ======================================================================
# 2. ระบบฐานข้อมูล (SQLite - Backend)
# ======================================================================
def init_db():
    conn = sqlite3.connect('campaign_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS campaign_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, customer_type TEXT, predicted_persona TEXT, promo_offered TEXT)''')
    conn.commit()
    conn.close()

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
# 3. โหลดโมเดล AI (Pre-trained Models)
# ======================================================================
@st.cache_resource
def load_models():
    return joblib.load("model_users.pkl"), joblib.load("model_non_users.pkl")

try:
    model_users, model_non_users = load_models()
    models_loaded = True
except Exception as e:
    st.error(f"⚠️ ไม่พบไฟล์โมเดล AI กรุณาตรวจสอบการอัปโหลดไฟล์ (.pkl) ใน GitHub")
    models_loaded = False

# ======================================================================
# 4. ฐานข้อมูลกลยุทธ์ (Hybrid Recommendation Logic)
# ======================================================================
strategy_users = {
    0: {"title": "Traditional Socialite (สายสังคมหน้าร้าน)", "msg": "เตรียมตัวให้พร้อมสำหรับทุกงานสำคัญ! ปิดผมขาวได้แนบเนียน รวดเร็วทันใจ"},
    1: {"title": "High-Expectation Socialite (สายเป๊ะเน้นบำรุง)", "msg": "ที่สุดของการปิดผมขาวพร้อมบำรุงล้ำลึก มั่นใจและดูเด็กลงในทุกสถานการณ์สำคัญ"},
    2: {"title": "Male Blue Ocean (ผู้ชายเน้นไวและบำรุง)", "msg": "ทางเลือกใหม่ของผู้ชาย! ปิดผมขาวไวใน 10 นาที จบง่ายในห้องน้ำ ไม่เลอะเทอะ"},
    3: {"title": "Young Modern Perfectionist (รุ่นใหม่เป๊ะออนไลน์)", "msg": "ตอบโจทย์ชีวิตเร่งรีบ! ปิดผมขาวเนียนสนิท 100% ให้ลุคดูเด็กลงแบบเป็นธรรมชาติ"},
    4: {"title": "Pragmatic Routine User (สายเน้นไว ใช้ประจำวัน)", "msg": "จัดการผมขาวเองได้ง่ายๆ ทุกเดือนที่บ้าน ด้วยสูตรอ่อนโยน ประหยัดเวลาเข้าร้าน"}
}

strategy_non_users = {
    0: {"title": "Traditional Method Loyalist (สายยึดติดร้าน/ครีมย้อม)", "msg": "ผลลัพธ์ระดับซาลอนที่คุณทำเองได้! สีติดชัด กลิ่นไม่ฉุน ตัวช่วยกู้ชีพคิวช่างเต็ม", "promo": "Online Starter Kit: สั่งเซ็ตซาลอนผ่าน TikTok วันนี้ รับฟรี! อุปกรณ์คลุมไหล่"},
    1: {"title": "Natural Acceptor (สายหงอกน้อย/ปล่อยธรรมชาติ)", "msg": "เลิกถอนให้รากผมอักเสบ! จัดการผมขาวเฉพาะจุด คืนความอ่อนโยนไม่ทำร้ายผมเดิม", "promo": "Shopee Choice: เริ่มเพียง 59.- กดใส่ตะกร้าไว้เผื่อวันไหนอยากดูเด็กลง!"},
    2: {"title": "Health-Conscious Skeptic (สายกลัวสารเคมี/แพ้)", "msg": "สบายใจทุกครั้งที่สระ! ปราศจากแอมโมเนีย อ่อนโยน ไม่แสบ ไม่คัน", "promo": "LazMall Risk-Free: ซื้อผ่าน Lazada หากแพ้ ยินดีคืนเงิน 100% ทันที!"},
    3: {"title": "Performance Doubter (สายกังวลคุณภาพ กลัวสีตก)", "msg": "ทลายทุกความเชื่อเดิมๆ! แชมพูล็อกสีติดทนนาน สระกี่ครั้งสีก็ไม่ตก", "promo": "Review & Earn: ซื้อบน Shopee รีวิวว่าสีไม่หลุด รับ Coins คืน 50%"},
    4: {"title": "Indifferent Potential (สายเฉยชา รอจุดเปลี่ยน)", "msg": "เปลี่ยนเรื่องย้อมผมที่ยุ่งยากให้เป็นเรื่องง่าย! แค่ฉีก เท สระ ไม่เลอะมือ", "promo": "TikTok Viral Offer: แลกซื้อไซส์ทดลอง 19 บาท ส่งฟรี!"}
}

# ======================================================================
# 5. ฟังก์ชันการแนะนำแบบ Hybrid (Personalization Engine)
# ======================================================================
def hybrid_recommendation(row, target_type):
    c_id = row['cluster_id']
    base = strategy_users.get(c_id) if target_type == "Users" else strategy_non_users.get(c_id)
    
    # Logic ผสมข้อความเสริม
    final_msg = base['msg']
    if target_type == "Users":
        if row.get('feat_herb', 0) == 1: final_msg += " (พ่วงบำรุงล้ำลึกด้วยสมุนไพรธรรมชาติ)"
        if row.get('feat_confidence', 0) == 1: final_msg += " (การันตีความเนียนสนิท เพิ่มความมั่นใจ)"
    else:
        if row.get('feat_chemical_fear', 0) == 1: final_msg += " [สูตรออร์แกนิค ไร้สารแอมโมเนีย]"
        if row.get('feat_doubt_efficacy', 0) == 1: final_msg += " [สีติดทนนาน ล้างออกง่ายไม่ติดเสื้อผ้า]"
    
    promo = base.get('promo', "ข้อเสนอพิเศษรอคุณอยู่")
    return base['title'], final_msg, promo

# ======================================================================
# 6. ส่วนประกอบหน้าเว็บ (Sidebar & Pages)
# ======================================================================
st.sidebar.title("DeeAsh AI Marketing")
page = st.sidebar.radio("Navigation", ["1. ภาพรวมระบบ (Home)", "2. วิเคราะห์กลุ่มลูกค้า (Unsupervised)", "3. จำลองแคมเปญ (Supervised)", "4. ข้อมูลเชิงลึก (Business Insight)"])

if page == "1. ภาพรวมระบบ (Home)":
    st.markdown('<p class="main-header">AI-Driven Marketing Campaign System</p>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">ระบบวิเคราะห์การตลาดและกำหนดกลุ่มเป้าหมาย (Customer Targeting) แบบครบวงจร (End-to-End Pipeline) สำหรับแบรนด์ DeeAsh เพื่อขับเคลื่อนยอดขายสู่ E-commerce</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("ข้อมูล (Raw Data)", "113 รายการ", "Cleaned 100%")
    c2.metric("โมเดล AI", "2 ชุด", "Clustering & Classification")
    c3.metric("สถานะระบบ", "Active", "Ready")
    st.markdown("---")
    st.write("ระบบนี้ใช้เทคนิค Machine Learning ทั้ง Unsupervised Learning เพื่อหา Persona และ Supervised Learning เพื่อทำนายพฤติกรรมลูกค้าแบบ Real-time พร้อมผสานกลยุทธ์ O2O เพื่อเปลี่ยนลูกค้าหน้าร้านสู่ช่องทางออนไลน์")

elif page == "2. วิเคราะห์กลุ่มลูกค้า (Unsupervised)":
    st.markdown('<p class="main-header">วิเคราะห์กลุ่มลูกค้า (Unsupervised Learning)</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">สรุปผลการแบ่งกลุ่ม (Cluster Analysis)</p>', unsafe_allow_html=True)
    st.write("เราใช้เทคนิค **K-Means Clustering** ร่วมกับ **Silhouette Score** เพื่อหาจำนวนกลุ่มลูกค้าที่เหมาะสมที่สุด (Optimal K=5)")
    st.dataframe(pd.DataFrame([{"ID": k, "Persona": v["title"], "Need/Barrier": v["msg"]} for k,v in {**strategy_users, **strategy_non_users}.items()]), use_container_width=True)

elif page == "3. จำลองแคมเปญ (Supervised)":
    st.markdown('<p class="main-header">จำลองแคมเปญ (Supervised Learning)</p>', unsafe_allow_html=True)
    st.write("โมเดล **Random Forest Classifier** จะทำนาย Persona ของลูกค้าและดึงกลยุทธ์การตลาดมาแสดงผลให้ทันที")
    
    tab1, tab2 = st.tabs(["ลูกค้าปัจจุบัน (Users)", "เป้าหมายใหม่ (Non-Users)"])
    with tab1:
        age_u = st.selectbox("อายุ:", ["ต่ำกว่า 30 ปี", "30–34 ปี", "35–44 ปี", "45–54 ปี", "55 ปีขึ้นไป"])
        gen_u = st.radio("เพศ:", ["หญิง", "ชาย", "LGBTQ+"])
        on_u = st.radio("ช่องทางซื้อ:", ["หน้าร้าน", "ออนไลน์"])
        h, q, s, c = st.columns(4)
        herb = h.checkbox("เน้นสมุนไพร")
        quick = q.checkbox("เน้นรวดเร็ว")
        soc = s.checkbox("ออกงานสังคม")
        conf = c.checkbox("เน้นมั่นใจ")
        
        if st.button("ประมวลผล (Users)"):
            age_map = {"ต่ำกว่า 30 ปี": 1, "30–34 ปี": 2, "35–44 ปี": 3, "45–54 ปี": 4, "55 ปีขึ้นไป": 5}
            data = pd.DataFrame([[age_map[age_u], 1 if gen_u=="ชาย" else 0, 1 if on_u=="ออนไลน์" else 0, int(herb), int(quick), int(soc), int(conf)]], columns=['age_score', 'is_male', 'is_online', 'feat_herb', 'feat_quick', 'feat_social', 'feat_confidence'])
            pred = model_users.predict(data)[0]
            proba = model_users.predict_proba(data).max()
            
            # Hybrid Recommendation
            title, msg, promo = hybrid_recommendation(pd.Series({'cluster_id': pred, 'feat_herb': int(herb), 'feat_confidence': int(conf)}), "Users")
            
            st.success(f"Persona: {title}")
            st.progress(float(proba))
            st.info(f"ข้อความ: {msg}")
            
            # O2O Logic
            if on_u == "หน้าร้าน":
                st.warning("O2O Trigger: ลูกค้าหน้าร้าน! แนะนำโปรโมชันเปลี่ยนใจสู่ Shopee/TikTok ลด 30%")
            save_to_db("User", title, msg)

    with tab2:
        age_nu = st.selectbox("อายุ:", ["ต่ำกว่า 30 ปี", "30–34 ปี", "35–44 ปี", "45–54 ปี", "55 ปีขึ้นไป"])
        chem = st.checkbox("กลัวสารเคมี"); salon = st.checkbox("ติดซาลอน"); low = st.checkbox("หงอกน้อย"); doubt = st.checkbox("กังวลคุณภาพ")
        
        if st.button("ประมวลผล (Non-Users)"):
            age_map = {"ต่ำกว่า 30 ปี": 1, "30–34 ปี": 2, "35–44 ปี": 3, "45–54 ปี": 4, "55 ปีขึ้นไป": 5}
            data = pd.DataFrame([[age_map[age_nu], int(chem), int(salon), int(low), int(doubt)]], columns=['age_score', 'feat_chemical_fear', 'feat_salon_loyalty', 'feat_low_white', 'feat_doubt_efficacy'])
            pred = model_non_users.predict(data)[0]
            
            title, msg, promo = hybrid_recommendation(pd.Series({'cluster_id': pred, 'feat_chemical_fear': int(chem), 'feat_doubt_efficacy': int(doubt)}), "Non-Users")
            st.success(f"Persona: {title}")
            st.info(f"ข้อความ: {msg}")
            st.warning(f"โปรโมชัน: {promo}")
            save_to_db("Non-User", title, promo)

elif page == "4. ข้อมูลเชิงลึก (Business Insight)":
    st.markdown('<p class="main-header">Business Insight & Campaign Logs</p>', unsafe_allow_html=True)
    conn = sqlite3.connect('campaign_history.db')
    df_logs = pd.read_sql_query("SELECT * FROM campaign_logs", conn)
    conn.close()
    st.dataframe(df_logs, use_container_width=True)
    if st.button("ล้างข้อมูลทั้งหมด"):
        conn = sqlite3.connect('campaign_history.db')
        conn.execute("DELETE FROM campaign_logs"); conn.commit(); conn.close(); st.rerun()
