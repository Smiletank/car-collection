import streamlit as st
import os
from datetime import datetime
from PIL import Image
import pandas as pd
import database as db
import ai_recognition as ai

# 页面配置
st.set_page_config(
    page_title="小车收藏管理",
    page_icon="🚗",
    layout="wide"
)

# 初始化session state
if 'recognition_result' not in st.session_state:
    st.session_state.recognition_result = None
if 'uploaded_image_path' not in st.session_state:
    st.session_state.uploaded_image_path = None

# 侧边栏 - API配置
with st.sidebar:
    st.header("⚙️ 配置")
    api_key = st.text_input("智谱API Key", type="password", 
                            help="在 open.bigmodel.cn 获取")
    
    # 智能补全开关
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

# 主页面
st.title("🚗 小车收藏管理")
st.write("上传照片，AI自动识别，批量入库")

tab1, tab2, tab3 = st.tabs(["📸 入库", "🔍 查重", "📚 收藏库"])

# ============ 入库功能 ============
with tab1:
    st.header("上传照片识别")
    
    uploaded_file = st.file_uploader(
        "上传小车照片（支持一张多车）", 
        type=['jpg', 'jpeg', 'png'],
        key="uploader"
    )
    
    if uploaded_file:
        # 保存图片
        os.makedirs("data/images", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = f"data/images/{timestamp}_{uploaded_file.name}"
        
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.session_state.uploaded_image_path = image_path
        
        # 显示图片
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(image_path, caption="上传的图片")
        
        # 识别按钮
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
    
    # 显示识别结果
    if st.session_state.recognition_result:
        st.divider()
        st.header("识别结果（可编辑）")
        
        result = st.session_state.recognition_result
        df = pd.DataFrame(result)
        
        # 确保所有列都存在
        for col in ['brand', 'model', 'color', 'series', 'code', 'note']:
            if col not in df.columns:
                df[col] = ''
        
        # 使用data_editor让用户可以编辑
        edited_df = st.data_editor(
            df[['brand', 'model', 'color', 'series', 'code', 'note']],
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "brand": st.column_config.TextColumn("品牌", required=True),
                "model": st.column_config.TextColumn("车型", required=True),
                "color": st.column_config.TextColumn("颜色"),
                "series": st.column_config.TextColumn("系列"),
                "code": st.column_config.TextColumn("编号"),
                "note": st.column_config.TextColumn("备注")
            }
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("✅ 确认入库", type="primary"):
                # 保存编辑后的数据
                count = 0
                for _, row in edited_df.iterrows():
                    if pd.notna(row['brand']) and pd.notna(row['model']):
                        db.add_car(
                            brand=str(row['brand']),
                            model=str(row['model']),
                            color=str(row['color']) if pd.notna(row['color']) else "",
                            series=str(row['series']) if pd.notna(row['series']) else "",
                            code=str(row['code']) if pd.notna(row['code']) else "",
                            note=str(row['note']) if pd.notna(row['note']) else "",
                            image_path=st.session_state.uploaded_image_path or ""
                        )
                        count += 1
                
                st.success(f"成功入库 {count} 辆小车！")
                st.session_state.recognition_result = None
                st.session_state.uploaded_image_path = None
                st.rerun()
        
        with col2:
            if st.button("❌ 取消"):
                st.session_state.recognition_result = None
                st.session_state.uploaded_image_path = None
                st.rerun()

# ============ 查重功能 ============
with tab2:
    st.header("查重检测")
    st.write("上传照片，检查是否已有相同或相似的小车")
    
    check_file = st.file_uploader(
        "上传要检查的照片", 
        type=['jpg', 'jpeg', 'png'],
        key="check_uploader"
    )
    
    if check_file:
        # 临时保存
        temp_path = f"data/images/temp_{check_file.name}"
        with open(temp_path, "wb") as f:
            f.write(check_file.getbuffer())
        
        st.image(temp_path, caption="要检查的图片")
        
        if st.button("🔍 开始查重", type="primary"):
            if not api_key:
                st.error("请先在侧边栏输入智谱API Key")
            else:
                with st.spinner("AI识别并查重中..."):
                    try:
                        # 识别图片中的车
                        result = ai.recognize_cars(temp_path, api_key)
                        
                        st.subheader("识别结果：")
                        for i, car in enumerate(result, 1):
                            info = f"**第{i}辆：** {car['brand']} - {car['model']} ({car['color']})"
                            if car.get('series'):
                                info += f" [{car['series']}]"
                            st.write(info)
                            
                            # 在数据库中查找相似车型
                            similar = db.search_cars(model=car['model'])
                            
                            if similar:
                                st.warning(f"⚠️ 发现 {len(similar)} 辆相似车型：")
                                for s in similar:
                                    # s的顺序：id, brand, model, color, series, code, note, image_path, created_at
                                    car_id, brand, model, color, series, code, note, img_path, created_at = s[:9]
                                    
                                    col1, col2 = st.columns([2, 1])
                                    with col1:
                                        st.write(f"**{brand} - {model}**")
                                        st.write(f"颜色：{color} | 系列：{series} | 编号：{code}")
                                        st.write(f"入库时间：{created_at}")
                                    with col2:
                                        # 显示已入库的图片
                                        if img_path and os.path.exists(img_path):
                                            st.image(img_path, caption="已入库的图", width=150)
                                        else:
                                            st.write("_暂无图片_")
                                    st.write("---")
                            else:
                                st.success("✅ 没有找到相似车型，可以放心购买！")
                            
                            st.divider()
                        
                    except Exception as e:
                        st.error(f"识别失败：{str(e)}")
        
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)

# ============ 收藏库浏览 ============
with tab3:
    st.header("我的收藏库")
    
    # 搜索和筛选
    col1, col2 = st.columns([3, 1])
    with col1:
        search_model = st.text_input("搜索车型")
    with col2:
        filter_brand = st.selectbox("筛选品牌", ["全部", "风火轮", "火柴盒", "TLV", "多美卡", "其他"])
    
    # 获取数据
    all_cars = db.get_all_cars()
    
    if all_cars:
        df = pd.DataFrame(all_cars, columns=['ID', '品牌', '车型', '颜色', '系列', '编号', '备注', '图片', '入库时间'])
        
        # 筛选
        if search_model:
            df = df[df['车型'].str.contains(search_model, case=False, na=False)]
        if filter_brand != "全部":
            df = df[df['品牌'].str.contains(filter_brand, case=False, na=False)]
        
        # 显示为表格
        st.dataframe(
            df[['品牌', '车型', '颜色', '系列', '编号', '备注', '入库时间']],
            use_container_width=True,
            hide_index=True
        )
        
        # 删除功能
        with st.expander("🗑️ 管理收藏（删除）"):
            car_to_delete = st.selectbox(
                "选择要删除的收藏",
                options=df['ID'].tolist(),
                format_func=lambda x: f"{df[df['ID']==x]['车型'].values[0]} ({df[df['ID']==x]['颜色'].values[0]})"
            )
            if st.button("删除"):
                db.delete_car(car_to_delete)
                st.success("删除成功！")
                st.rerun()
    else:
        st.info("收藏库是空的，快去入库一些小车吧！🚗")

# 运行说明
st.divider()
st.caption("""
💡 **使用说明：**
1. 在侧边栏输入你的智谱API Key（在 open.bigmodel.cn 获取）
2. 开启"智能补全"可自动搜索系列、编号等信息
3. 在"入库"页面上传照片，AI自动识别
4. 编辑识别结果后确认入库
5. 在"查重"页面检查是否已有相似车型
""")
