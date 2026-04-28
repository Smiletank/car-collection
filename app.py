import streamlit as st
import os
from datetime import datetime
from PIL import Image
import pandas as pd
import database as db
import ai_recognition as ai

st.set_page_config(
    page_title="小车收藏管理",
    page_icon="🚗",
    layout="wide"
)

if 'recognition_result' not in st.session_state:
    st.session_state.recognition_result = None
if 'uploaded_image_path' not in st.session_state:
    st.session_state.uploaded_image_path = None

with st.sidebar:
    st.header("⚙️ 配置")
    api_key = st.text_input("智谱API Key", type="password", 
                            help="在 open.bigmodel.cn 获取")
    auto_enrich = st.checkbox("智能补全信息", value=True,
                              help="自动搜索补全系列、编号等信息")
    st.divider()
    st.header("📊 统计")
    all_cars = db.get_all_cars()
    st.metric("总收藏", len(all_cars))
    if all_cars:
        df = pd.DataFrame(all_cars, columns=['ID', '品牌', '车型', '颜色', '系列', '编号', '备注', '图片', '入库时间'])
        brand_counts = df['品牌'].value_counts()
        st.write("品牌分布：")
        st.bar_chart(brand_counts)

st.title("🚗 小车收藏管理")
st.write("上传照片，AI自动识别，批量入库")

tab1, tab2, tab3 = st.tabs(["📸 入库", "🔍 查重", "📚 收藏库"])

with tab1:
    st.header("上传照片识别")
    uploaded_file = st.file_uploader(
        "上传小车照片（支持一张多车）", 
        type=['jpg', 'jpeg', 'png'],
        key="uploader"
    )
    
    if uploaded_file:
        os.makedirs(db.IMAGE_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = f"{db.IMAGE_DIR}/{timestamp}_{uploaded_file.name}"
        
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.session_state.uploaded_image_path = image_path
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(image_path, caption="上传的图片")
        
        if st.button("🔍 开始识别", type="primary"):
            if not api_key:
                st.error("请先在侧边栏输入智谱API Key")
            else:
                with st.spinner("AI正在识别中..." + ("（正在智能补全信息...）" if auto_enrich else "")):
                    try:
                        if auto_enrich:
                            result = ai.recognize_and_enrich(image_path, api_key)
                        else:
                            result = ai.recognize_cars(image_path, api_key)
                        st.session_state.recognition_result = result
                        st.success(f"识别完成！发现 {len(result)} 辆小车")
                    except Exception as e:
                        st.error(f"识别失败：{str(e)}")
    
    if st.session_state.recognition_result:
        st.divider()
        st.header("识别结果（可编辑）")
        result = st.session_state.recognition_result
        df = pd.DataFrame(result)
        for col in ['brand', 'model', 'color', 'series', 'code', 'no
