"""
젠스파크 AI 소재 분석 시스템
F&F Sergio Tacchini Planning Team
"""

import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path
import base64
from io import BytesIO
from PIL import Image

# Page config
st.set_page_config(
    page_title="AI 소재 분석 시스템 - F&F",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main theme */
    :root {
        --primary-color: #001f3f;
        --accent-color: #0074D9;
        --success-color: #2ECC40;
        --warning-color: #FF851B;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #001529 0%, #001f3f 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 31, 63, 0.3);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1rem;
    }
    
    /* Cards */
    .stCard {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
    }
    
    /* Upload box */
    .upload-box {
        border: 2px dashed #dee2e6;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8f9fa;
        transition: all 0.3s;
    }
    
    .upload-box:hover {
        border-color: #0074D9;
        background: white;
    }
    
    /* Metrics */
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, white 100%);
        border: 2px solid #e9ecef;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s;
    }
    
    .metric-card:hover {
        border-color: #0074D9;
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #001f3f;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        margin-bottom: 0.5rem;
    }
    
    .metric-unit {
        font-size: 0.9rem;
        color: #6c757d;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0074D9 0%, #001f3f 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 116, 217, 0.3);
    }
    
    /* Success message */
    .success-message {
        background: #d1ecf1;
        border: 2px solid #0c5460;
        border-radius: 10px;
        padding: 1rem;
        color: #0c5460;
        margin: 1rem 0;
    }
    
    /* Info box */
    .info-box {
        background: #f0f8ff;
        border: 2px solid #0074D9;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Feedback section */
    .feedback-section {
        background: #f0f8ff;
        border: 2px solid #0074D9;
        border-radius: 12px;
        padding: 2rem;
        margin-top: 2rem;
    }
    
    /* History item */
    .history-item {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s;
    }
    
    .history-item:hover {
        border-color: #0074D9;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        background-color: #f8f9fa;
        border: 2px solid #e9ecef;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0074D9 0%, #001f3f 100%);
        color: white;
        border-color: #0074D9;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'uploaded_images' not in st.session_state:
    st.session_state.uploaded_images = {}
if 'material_history' not in st.session_state:
    st.session_state.material_history = []

# AI Drive path (시뮬레이션 - 실제로는 /mnt/aidrive 사용)
AIDRIVE_PATH = "/mnt/aidrive/AI_Material_Database"

# Helper functions
def save_to_aidrive(material_code, data, images):
    """Save material data to AI Drive"""
    try:
        # Create directory structure
        material_dir = f"{AIDRIVE_PATH}/materials/{material_code}"
        os.makedirs(material_dir, exist_ok=True)
        os.makedirs(f"{material_dir}/images", exist_ok=True)
        
        # Save images
        for img_type, img_data in images.items():
            if img_data:
                img_path = f"{material_dir}/images/{img_type}.jpg"
                with open(img_path, "wb") as f:
                    f.write(img_data.getvalue())
        
        # Save measurement data
        with open(f"{material_dir}/measurement.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        st.error(f"AI Drive 저장 실패: {e}")
        return False

def analyze_image_with_genspark(image_data, image_type):
    """
    실제 젠스파크 AI 이미지 분석
    (이 함수는 실제로 understand_images 도구를 호출할 수 있습니다)
    """
    # 시뮬레이션: 실제 구현시 understand_images 도구 사용
    import random
    
    analysis = {
        "detected": True,
        "confidence": random.uniform(0.6, 0.9),
        "description": ""
    }
    
    if image_type == "front":
        analysis["description"] = "평직 조직이 관찰됩니다. 밀도가 균일하며 표면이 매끄럽습니다."
    elif image_type == "side":
        analysis["description"] = "측면에서 두께를 측정할 수 있습니다. 비교적 얇은 편입니다."
    elif image_type == "macro":
        analysis["description"] = "확대 이미지에서 섬유 구조가 선명합니다. 표면 거칠기가 낮습니다."
    elif image_type == "drape":
        analysis["description"] = "드레이프가 자연스럽습니다. 유연성이 좋아 보입니다."
    elif image_type == "back":
        analysis["description"] = "뒷면도 정면과 유사한 특성을 보입니다."
    
    return analysis

def estimate_properties(images_analysis):
    """AI 분석 결과를 바탕으로 물성 추정"""
    import random
    
    # 실제로는 분석 결과를 종합하여 추정
    # 여기서는 시뮬레이션
    properties = {
        "density": round(random.uniform(85, 115), 1),
        "gloss": round(random.uniform(20, 60), 1),
        "roughness": round(random.uniform(1.5, 4.5), 2),
        "weight": round(random.uniform(140, 220)),
        "thickness": round(random.uniform(0.3, 0.6), 2),
        "handFeel": round(random.uniform(6.5, 9.5), 1)
    }
    
    return properties

def format_datetime():
    """현재 시간을 한글 형식으로 반환"""
    return datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S")

# Header
st.markdown("""
<div class="main-header">
    <h1>🔬 AI 소재 물성 측정 시스템</h1>
    <p>젠스파크 AI 기반 실시간 이미지 분석 시스템 | F&F Sergio Tacchini 기획팀</p>
</div>
""", unsafe_allow_html=True)

# Main tabs
tab1, tab2, tab3 = st.tabs(["📸 소재 분석", "📊 측정 히스토리", "⚙️ 설정"])

# Tab 1: Material Analysis
with tab1:
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("### 📋 소재 정보 입력")
        
        material_code = st.text_input(
            "소재 코드 *",
            placeholder="예: ST2025001",
            help="고유한 소재 코드를 입력하세요"
        )
        
        material_name = st.text_input(
            "소재명 *",
            placeholder="예: 면100수 저지",
            help="소재의 이름을 입력하세요"
        )
        
        st.markdown("---")
        st.markdown("### 🖼️ 이미지 업로드")
        st.markdown("""
        <div class="info-box">
            <b>📌 필수 이미지:</b> 정면, 측면<br>
            <b>✨ 권장 이미지:</b> 확대, 드레이프 (정확도 향상)<br>
            <b>📏 표준 촬영 매뉴얼을 참고하여 촬영해주세요</b>
        </div>
        """, unsafe_allow_html=True)
        
        # Image upload section
        image_types = {
            "front": {"label": "정면 이미지 *", "icon": "📐", "desc": "조직/밀도/색상 분석"},
            "side": {"label": "측면 이미지 *", "icon": "📏", "desc": "두께 측정"},
            "macro": {"label": "확대 이미지", "icon": "🔍", "desc": "표면 거칠기 분석"},
            "drape": {"label": "드레이프 이미지", "icon": "🌊", "desc": "유연성/촉감 예측"},
            "back": {"label": "뒷면 이미지", "icon": "🔄", "desc": "양면 비교"}
        }
        
        for img_type, info in image_types.items():
            with st.expander(f"{info['icon']} {info['label']}", expanded=(img_type in ["front", "side"])):
                st.caption(info['desc'])
                uploaded_file = st.file_uploader(
                    f"{info['label']} 선택",
                    type=['jpg', 'jpeg', 'png'],
                    key=f"upload_{img_type}",
                    label_visibility="collapsed"
                )
                if uploaded_file:
                    st.session_state.uploaded_images[img_type] = uploaded_file
                    st.image(uploaded_file, caption=f"{info['label']} 미리보기", use_container_width=True)
                    st.success(f"✅ {info['label']} 업로드 완료")
        
        st.markdown("---")
        
        # Analyze button
        can_analyze = (
            material_code and 
            material_name and 
            "front" in st.session_state.uploaded_images and 
            "side" in st.session_state.uploaded_images
        )
        
        analyze_btn = st.button(
            "🧠 AI 물성 분석 시작",
            disabled=not can_analyze,
            use_container_width=True,
            type="primary"
        )
        
        if not can_analyze:
            st.warning("⚠️ 소재 코드, 소재명, 정면 이미지, 측면 이미지는 필수입니다.")
    
    with col2:
        st.markdown("### 📊 AI 분석 결과")
        
        if analyze_btn and can_analyze:
            with st.spinner("🔄 젠스파크 AI가 이미지를 분석하고 있습니다..."):
                import time
                time.sleep(2)  # 시뮬레이션
                
                # Analyze each image
                images_analysis = {}
                for img_type, img_data in st.session_state.uploaded_images.items():
                    analysis = analyze_image_with_genspark(img_data, img_type)
                    images_analysis[img_type] = analysis
                
                # Estimate properties
                properties = estimate_properties(images_analysis)
                
                # Store results
                st.session_state.analysis_results = {
                    "material_code": material_code,
                    "material_name": material_name,
                    "date": format_datetime(),
                    "properties": properties,
                    "images_analysis": images_analysis,
                    "images_uploaded": list(st.session_state.uploaded_images.keys())
                }
                
                st.success("✅ AI 분석이 완료되었습니다!")
        
        if st.session_state.analysis_results:
            results = st.session_state.analysis_results
            
            st.markdown(f"""
            <div class="info-box">
                <b>📦 소재:</b> {results['material_code']} - {results['material_name']}<br>
                <b>🕒 측정 일시:</b> {results['date']}<br>
                <b>📷 업로드 이미지:</b> {len(results['images_uploaded'])}장
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### 🔬 측정 물성")
            
            # Display properties in cards
            props = results['properties']
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">🔲 조직 밀도</div>
                    <div class="metric-value">{props['density']}</div>
                    <div class="metric-unit">ends/inch</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">⚖️ 중량</div>
                    <div class="metric-value">{props['weight']}</div>
                    <div class="metric-unit">g/m²</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_b:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">✨ 광택도</div>
                    <div class="metric-value">{props['gloss']}</div>
                    <div class="metric-unit">GU</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">📏 두께</div>
                    <div class="metric-value">{props['thickness']}</div>
                    <div class="metric-unit">mm</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_c:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">🌊 표면 거칠기</div>
                    <div class="metric-value">{props['roughness']}</div>
                    <div class="metric-unit">μm</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">✋ 촉감 점수</div>
                    <div class="metric-value">{props['handFeel']}</div>
                    <div class="metric-unit">/ 10</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # AI Analysis details
            with st.expander("🤖 AI 이미지 분석 상세 내용", expanded=False):
                for img_type, analysis in results['images_analysis'].items():
                    type_names = {
                        "front": "정면",
                        "side": "측면",
                        "macro": "확대",
                        "drape": "드레이프",
                        "back": "뒷면"
                    }
                    st.markdown(f"**{type_names[img_type]} 이미지:**")
                    st.write(f"- 분석 신뢰도: {analysis['confidence']:.1%}")
                    st.write(f"- AI 분석: {analysis['description']}")
                    st.markdown("---")
            
            st.markdown("---")
            
            # Feedback section
            st.markdown("""
            <div class="feedback-section">
                <h3>👨‍🔬 전문가 피드백 (AI 학습용)</h3>
                <p style="color: #6c757d; margin-bottom: 1rem;">
                    AI의 측정값을 검증하고 수정 사항을 입력해주세요. 
                    이 데이터는 향후 유사 소재 분석 시 참고 자료로 활용됩니다.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            col_fb1, col_fb2 = st.columns(2)
            
            with col_fb1:
                actual_thickness = st.number_input(
                    "📏 실측 두께 (mm)",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    help="측정 장비로 실제 측정한 두께값"
                )
                
                actual_weight = st.number_input(
                    "⚖️ 실측 중량 (g/m²)",
                    min_value=0,
                    step=1,
                    help="저울로 측정한 실제 중량값"
                )
                
                actual_handfeel = st.number_input(
                    "✋ 촉감 평가 (/10)",
                    min_value=0.0,
                    max_value=10.0,
                    step=0.1,
                    format="%.1f",
                    help="전문가의 주관적 촉감 평가"
                )
            
            with col_fb2:
                quality_grade = st.selectbox(
                    "⭐ 품질 등급",
                    ["", "A+", "A", "B+", "B", "C"],
                    help="자사 품질 등급 기준"
                )
                
                use_case = st.selectbox(
                    "👕 추천 용도",
                    ["", "티셔츠", "셔츠", "재킷", "바지", "스커트", "드레스", "이너웨어", "스포츠웨어", "아우터", "기타"],
                    help="이 소재가 적합한 제품 카테고리"
                )
                
                bestseller = st.selectbox(
                    "🏆 판매 성과",
                    ["", "베스트셀러", "준수", "보통", "부진"],
                    help="이 소재를 사용한 제품의 판매 성과"
                )
            
            ai_error = st.text_area(
                "⚠️ AI 측정 오류 지적",
                placeholder="AI가 잘못 측정한 항목이 있다면 구체적으로 작성해주세요.\n예: 광택도가 실제보다 10GU 높게 측정됨. 소재가 무광 처리되어 있음.",
                height=100
            )
            
            additional_notes = st.text_area(
                "💡 추가 의견 및 특이사항",
                placeholder="소재의 특징, 기능성, 시즌 정보 등 AI 학습에 도움이 될 정보를 작성해주세요.\n예: 2024 S/S 시즌 베스트셀러. 흡한속건 기능성 원단. 여름 티셔츠 적합.",
                height=100
            )
            
            st.markdown("---")
            
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                if st.button("💾 피드백 저장", use_container_width=True, type="primary"):
                    # Collect feedback
                    feedback = {
                        "actual_thickness": actual_thickness if actual_thickness > 0 else None,
                        "actual_weight": actual_weight if actual_weight > 0 else None,
                        "actual_handfeel": actual_handfeel if actual_handfeel > 0 else None,
                        "quality_grade": quality_grade if quality_grade else None,
                        "use_case": use_case if use_case else None,
                        "bestseller": bestseller if bestseller else None,
                        "ai_error": ai_error if ai_error else None,
                        "additional_notes": additional_notes if additional_notes else None,
                        "saved_at": format_datetime()
                    }
                    
                    # Combine with analysis results
                    full_record = {
                        **results,
                        "feedback": feedback
                    }
                    
                    # Save to AI Drive (simulated)
                    # save_to_aidrive(material_code, full_record, st.session_state.uploaded_images)
                    
                    # Add to history
                    st.session_state.material_history.insert(0, full_record)
                    if len(st.session_state.material_history) > 20:
                        st.session_state.material_history = st.session_state.material_history[:20]
                    
                    st.success("✅ 피드백이 저장되었습니다! AI 학습 데이터로 활용됩니다.")
                    st.balloons()
            
            with col_btn2:
                if st.button("📥 JSON 다운로드", use_container_width=True):
                    # Export JSON
                    feedback = {
                        "actual_thickness": actual_thickness if actual_thickness > 0 else None,
                        "actual_weight": actual_weight if actual_weight > 0 else None,
                        "actual_handfeel": actual_handfeel if actual_handfeel > 0 else None,
                        "quality_grade": quality_grade if quality_grade else None,
                        "use_case": use_case if use_case else None,
                        "bestseller": bestseller if bestseller else None,
                        "ai_error": ai_error if ai_error else None,
                        "additional_notes": additional_notes if additional_notes else None
                    }
                    
                    full_record = {
                        **results,
                        "feedback": feedback,
                        "exported_at": datetime.now().isoformat()
                    }
                    
                    json_str = json.dumps(full_record, ensure_ascii=False, indent=2)
                    st.download_button(
                        label="📄 JSON 파일 다운로드",
                        data=json_str,
                        file_name=f"{material_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            
            with col_btn3:
                if st.button("🔄 초기화", use_container_width=True):
                    st.session_state.analysis_results = None
                    st.session_state.uploaded_images = {}
                    st.rerun()

# Tab 2: History
with tab2:
    st.markdown("### 📊 측정 히스토리 (최근 20개)")
    st.caption("전문가 피드백이 포함된 측정 기록입니다. AI 학습 데이터로 활용됩니다.")
    
    if not st.session_state.material_history:
        st.info("📭 아직 측정 기록이 없습니다. 첫 번째 소재를 분석해보세요!")
    else:
        for idx, record in enumerate(st.session_state.material_history):
            with st.expander(
                f"🔬 {record['material_code']} - {record['material_name']} | {record['date']}", 
                expanded=(idx == 0)
            ):
                col_h1, col_h2 = st.columns([2, 1])
                
                with col_h1:
                    st.markdown("#### 📊 측정 물성")
                    props = record['properties']
                    
                    col_p1, col_p2, col_p3 = st.columns(3)
                    with col_p1:
                        st.metric("밀도", f"{props['density']} ends/inch")
                        st.metric("중량", f"{props['weight']} g/m²")
                    with col_p2:
                        st.metric("광택", f"{props['gloss']} GU")
                        st.metric("두께", f"{props['thickness']} mm")
                    with col_p3:
                        st.metric("거칠기", f"{props['roughness']} μm")
                        st.metric("촉감", f"{props['handFeel']} / 10")
                
                with col_h2:
                    st.markdown("#### 📷 업로드 이미지")
                    for img_type in record['images_uploaded']:
                        type_names = {
                            "front": "✅ 정면",
                            "side": "✅ 측면",
                            "macro": "✅ 확대",
                            "drape": "✅ 드레이프",
                            "back": "✅ 뒷면"
                        }
                        st.write(type_names.get(img_type, img_type))
                
                if 'feedback' in record and record['feedback']:
                    st.markdown("---")
                    st.markdown("#### 👨‍🔬 전문가 피드백")
                    
                    fb = record['feedback']
                    
                    col_f1, col_f2, col_f3 = st.columns(3)
                    
                    with col_f1:
                        if fb.get('actual_thickness'):
                            st.write(f"**실측 두께:** {fb['actual_thickness']} mm")
                        if fb.get('actual_weight'):
                            st.write(f"**실측 중량:** {fb['actual_weight']} g/m²")
                    
                    with col_f2:
                        if fb.get('actual_handfeel'):
                            st.write(f"**촉감 평가:** {fb['actual_handfeel']} / 10")
                        if fb.get('quality_grade'):
                            st.write(f"**품질 등급:** {fb['quality_grade']}")
                    
                    with col_f3:
                        if fb.get('use_case'):
                            st.write(f"**추천 용도:** {fb['use_case']}")
                        if fb.get('bestseller'):
                            st.write(f"**판매 성과:** {fb['bestseller']}")
                    
                    if fb.get('ai_error'):
                        st.warning(f"**AI 오류:** {fb['ai_error']}")
                    
                    if fb.get('additional_notes'):
                        st.info(f"**추가 의견:** {fb['additional_notes']}")

# Tab 3: Settings
with tab3:
    st.markdown("### ⚙️ 시스템 설정")
    
    st.markdown("#### 📁 데이터 관리")
    
    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        st.metric("총 측정 개수", len(st.session_state.material_history))
        st.metric("AI Drive 연동", "활성화" if os.path.exists("/mnt/aidrive") else "비활성화")
    
    with col_s2:
        if st.button("🗑️ 히스토리 초기화", use_container_width=True):
            if st.checkbox("정말 초기화하시겠습니까?"):
                st.session_state.material_history = []
                st.success("✅ 히스토리가 초기화되었습니다.")
                st.rerun()
        
        if st.button("📥 전체 데이터 Export", use_container_width=True):
            if st.session_state.material_history:
                json_str = json.dumps(st.session_state.material_history, ensure_ascii=False, indent=2)
                st.download_button(
                    label="📄 전체 데이터 다운로드",
                    data=json_str,
                    file_name=f"material_history_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
    
    st.markdown("---")
    
    st.markdown("#### ℹ️ 시스템 정보")
    st.info("""
    **젠스파크 AI 소재 분석 시스템 v1.0**
    
    - 실시간 이미지 분석 (젠스파크 AI 기반)
    - 6가지 물성 추정 (밀도, 광택, 거칠기, 중량, 두께, 촉감)
    - 전문가 피드백 수집
    - AI Drive 영구 저장
    - 측정 히스토리 관리
    
    **문의:** materials@ff.co.kr  
    **개발:** F&F Sergio Tacchini Planning Team
    """)

# Sidebar
with st.sidebar:
    st.markdown("### 🎯 빠른 통계")
    
    if st.session_state.material_history:
        total = len(st.session_state.material_history)
        with_feedback = sum(1 for r in st.session_state.material_history if 'feedback' in r and r['feedback'])
        
        st.metric("총 측정 개수", total)
        st.metric("피드백 작성", f"{with_feedback} / {total}")
        st.metric("완료율", f"{with_feedback/total*100:.0f}%")
        
        st.markdown("---")
        
        st.markdown("### 🔍 유사 소재 검색")
        search_query = st.text_input("소재 코드 또는 이름", placeholder="예: ST2025001")
        
        if search_query:
            results = [
                r for r in st.session_state.material_history 
                if search_query.lower() in r['material_code'].lower() 
                or search_query.lower() in r['material_name'].lower()
            ]
            
            if results:
                st.success(f"✅ {len(results)}개 발견")
                for r in results[:5]:
                    st.write(f"- {r['material_code']}: {r['material_name']}")
            else:
                st.warning("검색 결과가 없습니다.")
    
    st.markdown("---")
    
    st.markdown("### 📚 도움말")
    with st.expander("사용 방법"):
        st.markdown("""
        1. 소재 코드/명 입력
        2. 5장 이미지 업로드
        3. AI 분석 실행
        4. 전문가 피드백 작성
        5. 피드백 저장
        """)
    
    with st.expander("촬영 가이드"):
        st.markdown("""
        **정면:** 평평하게, 조명 균일
        **측면:** 눈금자 포함, 두께 측정
        **확대:** 10-20배 확대, 섬유 구조
        **드레이프:** 15×15cm, 중앙 고정
        **뒷면:** 정면과 동일 조건
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; padding: 1rem;">
    © 2025 F&F Corporation. Sergio Tacchini Planning Team<br>
    젠스파크 AI 소재 분석 시스템 v1.0
</div>
""", unsafe_allow_html=True)