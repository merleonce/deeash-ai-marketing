import streamlit as st
import pandas as pd
import joblib
import sqlite3
from datetime import datetime

# ======================================================================
# 1. การตั้งค่าหน้าเว็บ
# ======================================================================
st.set_page_config(page_title="DeeAsh AI Marketing System", layout="wide")

st.markdown("""
    <style>
    .main-header { font-size: 2.2rem !important; color: #0F172A; font-weight: bold; padding-bottom: 10px;}
    .sub-header { font-size: 1.3rem !important; color: #334155; font-weight: bold; border-bottom: 2px solid #E2E8F0; padding-bottom: 5px; margin-top: 20px;}
    .info-box { background-color: #F8FAFC; padding: 15px; border-left: 4px solid #3B82F6; border-radius: 4px; margin-bottom: 15px; color: #1E293B;}
    .stDataFrame { border: 1px solid #E2E8F0; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# ======================================================================
# 2. ระบบ Database (SQLite) 
# ======================================================================
def init_db():
    conn = sqlite3.connect('campaign_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS campaign_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  timestamp TEXT, 
                  customer_type TEXT, 
                  predicted_persona TEXT, 
                  promo_offered TEXT)''')
    conn.commit()
    return conn
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
    st.error(f"ไม่พบไฟล์โมเดล AI กรุณาตรวจสอบการอัปโหลดไฟล์ model_users.pkl และ model_non_users.pkl")
    models_loaded = False

# ======================================================================
# 4. ฐานข้อมูลกลยุทธ์ 
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
st.sidebar.markdown("<h2 style='text-align: center; color: #0F172A;'>DeeAsh Marketing</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")
page = st.sidebar.radio("เมนูนำทาง (Navigation Menu)", 
                        ["1. ภาพรวมระบบ (Home)", 
                         "2. วิเคราะห์กลุ่มลูกค้า (Unsupervised Learning)", 
                         "3. จำลองแคมเปญ (Supervised Learning)", 
                         "4. ข้อมูลเชิงลึก (Business Insight)"])
st.sidebar.markdown("---")

# ----------------------------------------------------------------------
# Page 1: Home
# ----------------------------------------------------------------------
if page == "1. ภาพรวมระบบ (Home)":
    st.markdown('<p class="main-header">AI-Driven Marketing Campaign System</p>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">ระบบวิเคราะห์การตลาดและกำหนดกลุ่มเป้าหมายแบบครบวงจร สำหรับแบรนด์ DeeAsh เพื่อขับเคลื่อนยอดขายสู่ E-commerce</div>', unsafe_allow_html=True)
    
    st.markdown('<p class="sub-header">ตัวชี้วัดระบบโดยรวม</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.metric(label="ข้อมูลฝึกสอน (Raw Data)", value="113 รายการ", delta="Cleaned 100%")
    col2.metric(label="ตัวแปรพฤติกรรม (Features)", value="11 ตัวแปร", delta="NLP Extracted")
    col3.metric(label="สถานะระบบ (System Status)", value="Active", delta="Ready for Deployment")

    st.markdown("---")
    st.write("**วัตถุประสงค์โครงการ:** นำเทคโนโลยี Machine Learning มาใช้วิเคราะห์พฤติกรรมผู้บริโภค เพื่อสร้างแคมเปญการตลาดแบบ Personalized ที่แม่นยำและเพิ่มยอดขายในช่องทางออนไลน์")

# ----------------------------------------------------------------------
# Page 2: Unsupervised Learning
# ----------------------------------------------------------------------
elif page == "2. วิเคราะห์กลุ่มลูกค้า (Unsupervised Learning)":
    st.markdown('<p class="main-header">วิเคราะห์กลุ่มลูกค้า (Unsupervised Learning)</p>', unsafe_allow_html=True)
    st.write("การประมวลผลข้อมูลด้วย K-Means เพื่อค้นหาพฤติกรรมแฝง (Latent Behavior) และกำหนดกลยุทธ์เชิงรุก")
    
    st.markdown('<p class="sub-header">ตัวชี้วัดประสิทธิภาพของโมเดล</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.metric(label="จำนวนกลุ่มลูกค้าปัจจุบัน (Users)", value="5 Clusters", delta="Silhouette Score Verified")
    c2.metric(label="จำนวนกลุ่มเป้าหมายใหม่ (Non-Users)", value="5 Clusters", delta="Silhouette Score Verified")
    
    # --- ส่วนที่เพิ่มเข้ามา: สรุปหัวใจสำคัญ (Executive Summary) ---
    st.markdown('<p class="sub-header">สรุปผลลัพธ์ทางธุรกิจจาก AI (Business Insights)</p>', unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.info("**สิ่งที่โมเดล Unsupervised มอบให้:**\n\n"
                "1. **Break the Mass Marketing:** เราพบว่าลูกค้าไม่ได้มีแค่กลุ่มเดียว แต่มีถึง 5 กลุ่มย่อยที่มีความต้องการต่างกัน เช่น สายสังคมที่เน้นออกงาน กับสายปฏิบัติที่เน้นแค่ความไว\n"
                "2. **Data-Driven Personas:** ทุก Persona ไม่ได้มาจากการคาดเดา แต่มาจาก 'ค่าพิกัดกลาง' (Centroid) ที่ยืนยันได้ด้วยสถิติ\n"
                "3. **Targeted Communication:** ระบบช่วยให้แบรนด์เลิกใช้ข้อความหว่านแห และยิงโฆษณาที่แก้ Pain Point เฉพาะกลุ่มได้แม่นยำขึ้น")
    
    with col_b:
        st.warning("**โอกาสทางธุรกิจ (Opportunity Map):**\n\n"
                   "1. **Blue Ocean Detection:** AI ระบุกลุ่มผู้ชายที่ไม่เคยถูกทำการตลาด (Cluster 2) เป็นช่องทางใหม่ในการขยายตลาด\n"
                   "2. **Barrier Removal:** ในกลุ่ม Non-Users AI ค้นพบกลุ่มที่กังวลเรื่องสีตก (Performance Doubter) ซึ่งเป็นโอกาสในการสื่อสารเรื่อง 'ความติดทน' เพื่อดึงคนเหล่านี้มาใช้ออนไลน์")

    st.markdown('<p class="sub-header">โครงสร้างพฤติกรรมลูกค้า (Behavioral Clusters)</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["ลูกค้าปัจจุบัน (Users)", "กลุ่มเป้าหมายใหม่ (Non-Users)"])
    
    with tab1:
        st.write("ตารางแสดง Persona ของกลุ่มคนที่เคยใช้แชมพูปิดผมขาว DeeAsh")
        df_u = pd.DataFrame([{"ID": k, "กลุ่มเป้าหมาย (Persona)": v["title"], "ความต้องการหลัก (Core Need)": v["msg"]} for k,v in strategy_users.items()])
        st.dataframe(df_u, use_container_width=True, hide_index=True)
    with tab2:
        st.write("ตารางแสดง Persona ของกลุ่มคนที่ไม่เคยใช้แชมพูปิดผมขาว (ตลาดใหม่)")
        df_nu = pd.DataFrame([{"ID": k, "กลุ่มเป้าหมาย (Persona)": v["title"], "วิธีทลายกำแพง (Barrier to Break)": v["msg"]} for k,v in strategy_non_users.items()])
        st.dataframe(df_nu, use_container_width=True, hide_index=True)

# ----------------------------------------------------------------------
# Page 3: Supervised Learning (Simulation) - จัดเต็มความโปร!
# ----------------------------------------------------------------------
elif page == "3. จำลองแคมเปญ (Supervised Learning)":
    st.markdown('<p class="main-header">จำลองแคมเปญ (Supervised Learning)</p>', unsafe_allow_html=True)
    st.write("ระบบใช้ **Random Forest Classifier** เพื่อทำนาย Persona ลูกค้าใหม่แบบ Real-time และบันทึกข้อมูลลงฐานข้อมูล")
    
    st.markdown('<p class="sub-header">ความแม่นยำของโมเดลพยากรณ์</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col1.metric(label="ความแม่นยำ - ลูกค้าปัจจุบัน", value="100.00%", delta="Training Accuracy")
    col2.metric(label="ความแม่นยำ - เป้าหมายใหม่", value="100.00%", delta="Training Accuracy")
    st.markdown("---")

    if models_loaded:
        tab1, tab2 = st.tabs(["จำลองข้อมูล: ลูกค้าปัจจุบัน", "จำลองข้อมูล: เป้าหมายใหม่"])

        with tab1:
            st.write("กรอกข้อมูลเพื่อจำลองการยิงแคมเปญแบบ Personalized")
            col1, col2 = st.columns(2)
            with col1:
                age_raw = st.selectbox("อายุ:", ["ต่ำกว่า 30 ปี", "30–34 ปี", "35–44 ปี", "45–54 ปี", "55 ปีขึ้นไป"], key="u_age")
                gender_raw = st.radio("เพศ:", ["หญิง", "ชาย", "LGBTQ+"], key="u_gender")
                online_raw = st.radio("ช่องทางซื้อประจำ:", ["หน้าร้าน (เช่น 7-11, โชห่วย, ห้าง)", "ออนไลน์ (เช่น Shopee, TikTok)"], key="u_online")
            with col2:
                st.write("**พฤติกรรมที่เน้น (เลือกได้หลายข้อ)**")
                feat_herb = st.checkbox("เน้นสมุนไพร บำรุงล้ำลึก")
                feat_quick = st.checkbox("เน้นความรวดเร็ว 10 นาทีจบ")
                feat_social = st.checkbox("ใช้เตรียมตัวออกงานสังคม")
                feat_conf = st.checkbox("ใช้เพื่อเพิ่มความมั่นใจ")

            if st.button("ประมวลผลและส่งแคมเปญ", key="btn_u", use_container_width=True):
                age_map = {"ต่ำกว่า 30 ปี": 1, "30–34 ปี": 2, "35–44 ปี": 3, "45–54 ปี": 4, "55 ปีขึ้นไป": 5}
                is_online_val = 1 if online_raw == "ออนไลน์ (เช่น Shopee, TikTok)" else 0
                
                input_df = pd.DataFrame([[age_map[age_raw], 1 if gender_raw == "ชาย" else 0, is_online_val, int(feat_herb), int(feat_quick), int(feat_social), int(feat_conf)]], columns=["age_score", "is_male", "is_online", "feat_herb", "feat_quick", "feat_social", "feat_confidence"])
                
                # --- ส่วนอัปเกรด (AI Confidence & Insights) ---
                pred_cluster = model_users.predict(input_df)[0]
                pred_proba = model_users.predict_proba(input_df).max() # หาความมั่นใจของ AI
                result = strategy_users[pred_cluster]
                
                st.markdown("---")
                st.subheader("🎯 ผลการวิเคราะห์จาก AI")
                
                # แถบ Progress Bar ความมั่นใจ
                st.write(f"**ระดับความมั่นใจของ AI (Confidence Score):** {pred_proba:.1%}")
                st.progress(float(pred_proba))
                
                st.success(f"**🤖 Persona ที่ตรวจพบ:** {result['title']}")
                
                # กล่องซ่อน Insights
                with st.expander("🔍 ดูปัจจัยเชิงลึกที่ AI ตรวจพบ (DNA Insights)"):
                    c_dna1, c_dna2, c_dna3, c_dna4 = st.columns(4)
                    c_dna1.metric("สมุนไพร", "สูง" if feat_herb else "ต่ำ")
                    c_dna2.metric("ความรวดเร็ว", "สูง" if feat_quick else "ต่ำ")
                    c_dna3.metric("งานสังคม", "สูง" if feat_social else "ต่ำ")
                    c_dna4.metric("ความมั่นใจ", "สูง" if feat_conf else "ต่ำ")

                # Hybrid Logic
                final_msg = result['msg']
                if feat_herb: final_msg += " (พ่วงบำรุงล้ำลึกด้วยสมุนไพรธรรมชาติ)"
                if feat_conf: final_msg += " (การันตีความเนียนสนิท เพิ่มความมั่นใจ)"
                
                promo_msg = "Online Loyalty: สั่งช่องทางออนไลน์เดิม รับส่วนลด 15% ทันที" if is_online_val == 1 else "O2O Trigger: ปกติซื้อหน้าร้านใช่ไหม? ลองสั่งผ่าน Shopee วันนี้ รับโค้ดส่งฟรีและลดเพิ่ม 30%"

                st.info(f"💬 **ข้อความโฆษณาที่แนะนำ:**\n{final_msg}")
                st.warning(f"🎁 **กลยุทธ์โปรโมชัน:**\n{promo_msg}")
                
                save_to_db("ลูกค้าปัจจุบัน", result['title'], promo_msg)
                st.toast('บันทึกแคมเปญลงฐานข้อมูล (SQL) สำเร็จ!')

        with tab2:
            st.write("กรอกข้อมูลเพื่อจำลองการยิงแคมเปญทลายกำแพงในใจ")
            col3, col4 = st.columns(2)
            with col3:
                age_raw2 = st.selectbox("อายุ:", ["ต่ำกว่า 30 ปี", "30–34 ปี", "35–44 ปี", "45–54 ปี", "55 ปีขึ้นไป"], key="nu_age")
            with col4:
                st.write("**กำแพงในใจที่ทำให้ไม่ใช้งาน (Barriers)**")
                feat_chem = st.checkbox("กลัวสารเคมี แพ้ ผมเสีย")
                feat_salon = st.checkbox("ยึดติดกับการเข้าร้าน / ใช้ครีมเดิมๆ")
                feat_low = st.checkbox("ผมขาวมีน้อย ปล่อยธรรมชาติ / ถอนเอา")
                feat_doubt = st.checkbox("กังวลเรื่องคุณภาพ (สีตก / ไม่ทน)")

            if st.button("ประมวลผลและส่งแคมเปญ ", key="btn_nu", use_container_width=True):
                age_map = {"ต่ำกว่า 30 ปี": 1, "30–34 ปี": 2, "35–44 ปี": 3, "45–54 ปี": 4, "55 ปีขึ้นไป": 5}
                input_df2 = pd.DataFrame([[age_map[age_raw2], int(feat_chem), int(feat_salon), int(feat_low), int(feat_doubt)]], columns=["age_score", "feat_chemical_fear", "feat_salon_loyalty", "feat_low_white", "feat_doubt_efficacy"])
                
                # --- ส่วนอัปเกรด (AI Confidence) ---
                pred_cluster2 = model_non_users.predict(input_df2)[0]
                pred_proba2 = model_non_users.predict_proba(input_df2).max()
                result2 = strategy_non_users[pred_cluster2]

                st.markdown("---")
                st.subheader("🎯 ผลการวิเคราะห์จาก AI")
                st.write(f"**ระดับความมั่นใจของ AI (Confidence Score):** {pred_proba2:.1%}")
                st.progress(float(pred_proba2))
                
                st.success(f"**🤖 Persona ที่ตรวจพบ:** {result2['title']}")

                final_msg2 = result2['msg']
                if feat_chem: final_msg2 += " [ย้ำ! สูตรออร์แกนิค ไร้สารแอมโมเนีย]"
                if feat_doubt: final_msg2 += " [ย้ำ! สีติดทนนาน ล้างออกง่ายไม่ติดเสื้อผ้า]"

                st.info(f"💬 **ข้อความทลายกำแพงในใจ:**\n{final_msg2}")
                st.warning(f"🎁 **กลยุทธ์โปรโมชัน:**\n{result2['promo']}")
                
                save_to_db("เป้าหมายใหม่ (Non-User)", result2['title'], result2['promo'])
                st.toast('บันทึกแคมเปญลงฐานข้อมูล (SQL) สำเร็จ!')

# ----------------------------------------------------------------------
# Page 4: Business Insight (Database Dashboard)
# ----------------------------------------------------------------------
elif page == "4. ข้อมูลเชิงลึก (Business Insight)":
    st.markdown('<p class="main-header">ข้อมูลเชิงลึก & ประวัติแคมเปญ (Business Insight)</p>', unsafe_allow_html=True)
    st.write("Dashboard สรุปผลการยิงแคมเปญและการดึงข้อมูลแบบ Real-time จากฐานข้อมูล **SQLite Database**")
    
    try:
        conn = sqlite3.connect('campaign_history.db')
        df_logs = pd.read_sql_query("SELECT id AS 'ลำดับ', timestamp AS 'เวลาจำลอง', customer_type AS 'ประเภทลูกค้า', predicted_persona AS 'กลุ่ม Persona', promo_offered AS 'โปรโมชันที่นำเสนอ' FROM campaign_logs ORDER BY id DESC", conn)
        conn.close()
        
        if not df_logs.empty:
            st.markdown('<div class="info-box">สถานะการเชื่อมต่อฐานข้อมูล: ปกติ (SQLite Connected) - แสดงประวัติการจำลองแคมเปญล่าสุด</div>', unsafe_allow_html=True)
            
            # --- ส่วนอัปเกรด (เพิ่ม Metric สรุปยอด) ---
            st.write("📈 **สรุปสถิติแคมเปญวันนี้**")
            m1, m2 = st.columns(2)
            m1.metric("จำนวนแคมเปญที่จำลองทั้งหมด", f"{len(df_logs)} แคมเปญ")
            m2.metric("Persona ยอดนิยมที่ถูกวิเคราะห์", df_logs['กลุ่ม Persona'].mode()[0])
            st.markdown("---")
            
            st.dataframe(df_logs, use_container_width=True, hide_index=True)
            
            st.markdown('<p class="sub-header">สัดส่วนกลุ่มเป้าหมายที่ถูกจำลอง (Campaign Segmentation)</p>', unsafe_allow_html=True)
            chart_data = df_logs['กลุ่ม Persona'].value_counts()
            st.bar_chart(chart_data, color="#3B82F6")
            
            st.markdown("---")
            if st.button("ล้างข้อมูลประวัติทั้งหมด (Clear Database)", type="primary"):
                conn = sqlite3.connect('campaign_history.db')
                c = conn.cursor()
                c.execute("DELETE FROM campaign_logs")
                c.execute("DELETE FROM sqlite_sequence WHERE name='campaign_logs'")
                conn.commit()
                conn.close()
                st.rerun()
                
        else:
            st.info("ยังไม่มีประวัติการยิงแคมเปญ กรุณาไปที่เมนู '3. จำลองแคมเปญ' เพื่อทดสอบระบบ")
            
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อฐานข้อมูล: {e}")
)
