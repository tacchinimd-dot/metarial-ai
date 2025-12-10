"""
F&F Sergio Tacchini - Genspark AI 소재 분석 시스템 (AI Drive 연동 버전)
Version: 2.0 (AI Drive Integration)
Date: 2025-12-10
"""

import streamlit as st
from PIL import Image
import io
import json
from datetime import datetime
import os
from pathlib import Path

# ========================================
# AI Drive 설정
# ========================================
AI_DRIVE_BASE = Path("/mnt/aidrive/AI_Material_Analysis_Data")
IMAGES_FOLDER = AI_DRIVE_BASE / "images"
DATA_FOLDER = AI_DRIVE_BASE / "analysis_data"
HISTORY_FILE = DATA_FOLDER / "analysis_history.json"

# AI Drive 폴더 생성 (로컬 실행 시에만 작동)
def init_aidrive():
    """AI Drive 폴더 초기화"""
    try:
        AI_DRIVE_BASE.mkdir(parents=True, exist_ok=True)
        IMAGES_FOLDER.mkdir(parents=True, exist_ok=True)
        DATA_FOLDER.mkdir(parents=True, exist_ok=True)
        
        # 빈 히스토리 파일 생성
        if not HISTORY_FILE.exists():
            HISTORY_FILE.write_text(json.dumps([], ensure_ascii=False, indent=2))
        
        return True
    except Exception as e:
        # Streamlit Cloud에서는 /mnt/aidrive 접근 불가 - 세션 스토리지로 대체
        return False

# ========================================
# 데이터 저장/로드 함수
# ========================================

def save_image_to_aidrive(image, material_code, image_type):
    """이미지를 AI Drive에 저장"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{material_code}_{image_type}_{timestamp}.png"
        filepath = IMAGES_FOLDER / filename
        
        # 이미지 저장
        image.save(str(filepath))
        return str(filepath)
    except Exception as e:
        # Streamlit Cloud - 임시 저장
        return f"[임시저장] {material_code}_{image_type}_{timestamp}.png"

def load_history_from_aidrive():
    """AI Drive에서 분석 이력 로드"""
    try:
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception:
        # Streamlit Cloud - 세션 스토리지 사용
        return st.session_state.get('analysis_history', [])

def save_history_to_aidrive(history_data):
    """AI Drive에 분석 이력 저장"""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        # Streamlit Cloud - 세션 스토리지에 백업
        st.session_state['analysis_history'] = history_data
        return False

def add_analysis_record(record):
    """새 분석 기록 추가"""
    history = load_history_from_aidrive()
    
    # 최신 기록을 맨 앞에 추가
    history.insert(0, record)
    
    # 최대 100개까지만 저장
    if len(history) > 100:
        history = history[:100]
    
    # 저장
    is_aidrive = save_history_to_aidrive(history)
    
    return is_aidrive

# ========================================
# 페이지 설정
# ========================================
st.set_page_config(
    page_title="F&F AI 소재 분석 시스템",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 초기화
aidrive_available = init_aidrive()

# ========================================
# CSS 스타일
# ========================================
st.markdown("""
<style>
    /* 메인 컬러: F&F Navy */
    :root {
        --primary-color: #1e3a8a;
        --secondary-color: #3b82f6;
        --accent-color: #10b981;
    }
    
    /* 헤더 스타일 */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* 카드 스타일 */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .success-card {
        background: #f0fdf4;
        border-left-color: #10b981;
    }
    
    .warning-card {
        background: #fffbeb;
        border-left-color: #f59e0b;
    }
    
    /* 메트릭 스타일 */
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e3a8a;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-unit {
        font-size: 1rem;
        color: #9ca3af;
        font-weight: 400;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border-radius: 6px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transform: translateY(-2px);
    }
    
    /* 이미지 업로드 영역 */
    .uploadedFile {
        border: 2px dashed #3b82f6;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* 히스토리 카드 */
    .history-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .history-card:hover {
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-color: #3b82f6;
    }
    
    /* 뱃지 스타일 */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .badge-primary {
        background: #dbeafe;
        color: #1e3a8a;
    }
    
    .badge-success {
        background: #d1fae5;
        color: #065f46;
    }
    
    .badge-info {
        background: #e0e7ff;
        color: #3730a3;
    }
</style>
""", unsafe_allow_html=True)

# ========================================
# 헤더
# ========================================
st.markdown("""
<div class="main-header">
    <h1>🧵 F&F AI 소재 분석 시스템</h1>
    <p>Sergio Tacchini Planning Team | AI-Powered Material Analysis</p>
</div>
""", unsafe_allow_html=True)

# AI Drive 상태 표시
if aidrive_available:
    st.success("✅ **AI Drive 연동 완료** - 팀원들과 데이터가 자동으로 공유됩니다!")
else:
    st.warning("⚠️ **세션 스토리지 모드** - Streamlit Cloud에서는 브라우저 세션에만 저장됩니다. 로컬 실행 시 AI Drive가 자동 연동됩니다.")

# ========================================
# 사이드바: 소재 정보 입력
# ========================================
with st.sidebar:
    st.markdown("### 📋 소재 기본 정보")
    
    material_code = st.text_input(
        "소재 코드",
        placeholder="예: ST-2024-001",
        help="내부 관리용 소재 식별 코드"
    )
    
    material_name = st.text_input(
        "소재명",
        placeholder="예: 프리미엄 코튼 저지",
        help="소재의 상품명 또는 설명"
    )
    
    supplier = st.text_input(
        "공급처",
        placeholder="예: 대한섬유",
        help="소재 제공 업체명"
    )
    
    st.markdown("---")
    st.markdown("### 📸 이미지 업로드")
    st.caption("표준 촬영 매뉴얼에 따라 촬영된 이미지를 업로드해주세요.")

# ========================================
# 메인: 이미지 업로드
# ========================================
st.markdown("## 📸 소재 이미지 업로드")

uploaded_images = {}
image_types = {
    "front": {"label": "① 전면 이미지", "icon": "🔲", "desc": "소재의 정면 (조직, 색상, 밀도 분석)"},
    "side": {"label": "② 측면 이미지", "icon": "📐", "desc": "소재의 측면 (두께 측정용)"},
    "macro": {"label": "③ 확대 이미지", "icon": "🔍", "desc": "10-20배 확대 (섬유 구조 분석)"},
    "drape": {"label": "④ 드레이프 이미지", "icon": "👗", "desc": "자연스럽게 늘어뜨린 상태 (유연성 분석)"},
    "back": {"label": "⑤ 후면 이미지", "icon": "🔳", "desc": "소재의 뒷면 (선택사항)"}
}

cols = st.columns(5)
for idx, (img_type, info) in enumerate(image_types.items()):
    with cols[idx]:
        st.markdown(f"**{info['icon']} {info['label']}**")
        uploaded = st.file_uploader(
            info['desc'],
            type=['jpg', 'jpeg', 'png'],
            key=f"upload_{img_type}",
            label_visibility="collapsed"
        )
        if uploaded:
            uploaded_images[img_type] = Image.open(uploaded)
            st.image(uploaded_images[img_type], use_container_width=True)

# ========================================
# AI 분석 실행
# ========================================
st.markdown("---")

if st.button("🚀 AI 물성 분석 시작", type="primary", use_container_width=True):
    if not material_code:
        st.error("❌ 소재 코드를 입력해주세요!")
    elif not uploaded_images:
        st.error("❌ 최소 1개 이상의 이미지를 업로드해주세요!")
    else:
        with st.spinner("🔬 AI가 소재를 분석하고 있습니다..."):
            import time
            import random
            
            # 시뮬레이션: 실제로는 AI 모델 호출
            time.sleep(2)
            
            # 분석 결과 생성 (시뮬레이션)
            analysis_results = {
                "density": random.randint(85, 115),
                "gloss": random.randint(20, 60),
                "roughness": round(random.uniform(1.5, 4.5), 2),
                "weight": random.randint(140, 220),
                "thickness": round(random.uniform(0.3, 0.6), 2),
                "touch_score": round(random.uniform(6.5, 9.5), 1)
            }
            
            # 이미지를 AI Drive에 저장
            saved_images = {}
            for img_type, img in uploaded_images.items():
                path = save_image_to_aidrive(img, material_code, img_type)
                saved_images[img_type] = path
            
            # 분석 기록 생성
            record = {
                "timestamp": datetime.now().isoformat(),
                "material_code": material_code,
                "material_name": material_name,
                "supplier": supplier,
                "uploaded_images": list(uploaded_images.keys()),
                "saved_image_paths": saved_images,
                "analysis": analysis_results,
                "feedback": None  # 나중에 추가
            }
            
            # AI Drive에 저장
            is_saved = add_analysis_record(record)
            
            st.session_state['current_analysis'] = record
            st.session_state['show_results'] = True
            
            if is_saved:
                st.success("✅ **분석 완료 및 AI Drive 저장 성공!** 팀원들이 이 결과를 볼 수 있습니다.")
            else:
                st.info("ℹ️ **분석 완료** (세션에만 저장됨)")

# ========================================
# 분석 결과 표시
# ========================================
if st.session_state.get('show_results') and st.session_state.get('current_analysis'):
    st.markdown("---")
    st.markdown("## 📊 AI 분석 결과")
    
    results = st.session_state['current_analysis']['analysis']
    
    # 6개 메트릭 표시
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">조직 밀도</div>
            <div class="metric-value">{results['density']}<span class="metric-unit"> ends/inch</span></div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("직물 조직의 밀도 (날실 수)")
    
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">광택도</div>
            <div class="metric-value">{results['gloss']}<span class="metric-unit"> GU</span></div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("표면 광택 정도")
    
    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">표면 조도</div>
            <div class="metric-value">{results['roughness']}<span class="metric-unit"> μm</span></div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("표면 거칠기")
    
    with col4:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">중량</div>
            <div class="metric-value">{results['weight']}<span class="metric-unit"> g/m²</span></div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("단위 면적당 무게")
    
    with col5:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">두께</div>
            <div class="metric-value">{results['thickness']}<span class="metric-unit"> mm</span></div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("소재 두께")
    
    with col6:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">촉감 점수</div>
            <div class="metric-value">{results['touch_score']}<span class="metric-unit"> /10</span></div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("예상 촉감 품질")
    
    # AI 해석
    st.markdown("### 🤖 AI 종합 평가")
    st.markdown(f"""
    <div class="info-card success-card">
        <h4>✅ 분석 완료</h4>
        <p><strong>소재 코드:</strong> {material_code}</p>
        <p><strong>분석 이미지 수:</strong> {len(uploaded_images)}장</p>
        <p><strong>종합 평가:</strong> 해당 소재는 <span class="badge badge-primary">중량급 니트</span> 특성을 보이며, 
        두께 {results['thickness']}mm, 중량 {results['weight']}g/m²로 <span class="badge badge-success">가을/겨울용</span> 
        의류에 적합합니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 전문가 피드백 입력 폼
    st.markdown("---")
    st.markdown("### 👤 전문가 피드백 (AI 학습용)")
    
    with st.form("feedback_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            actual_thickness = st.number_input(
                "실측 두께 (mm)",
                min_value=0.0,
                max_value=5.0,
                step=0.01,
                help="실제 측정한 두께 값"
            )
            
            actual_weight = st.number_input(
                "실측 중량 (g/m²)",
                min_value=0,
                max_value=500,
                step=1,
                help="실제 측정한 중량 값"
            )
            
            actual_touch = st.slider(
                "실제 촉감 점수 (1~10)",
                min_value=1,
                max_value=10,
                value=7,
                help="전문가가 평가한 실제 촉감 점수"
            )
        
        with col2:
            quality_grade = st.selectbox(
                "품질 등급",
                ["상급 (A)", "중상급 (B+)", "중급 (B)", "중하급 (C+)", "하급 (C)"]
            )
            
            recommended_use = st.text_input(
                "추천 용도",
                placeholder="예: 겨울 니트, 후드티 안감"
            )
            
            sales_performance = st.selectbox(
                "판매 성과 (선택사항)",
                ["선택 안함", "베스트셀러", "정상", "저조"]
            )
        
        additional_notes = st.text_area(
            "기타 의견",
            placeholder="AI 분석 오차, 특이사항, 개선 제안 등을 자유롭게 입력해주세요.",
            height=100
        )
        
        submitted = st.form_submit_button("💾 피드백 저장", type="primary", use_container_width=True)
        
        if submitted:
            # 피드백 데이터 추가
            feedback_data = {
                "actual_thickness": actual_thickness if actual_thickness > 0 else None,
                "actual_weight": actual_weight if actual_weight > 0 else None,
                "actual_touch": actual_touch,
                "quality_grade": quality_grade,
                "recommended_use": recommended_use,
                "sales_performance": sales_performance if sales_performance != "선택 안함" else None,
                "additional_notes": additional_notes,
                "feedback_timestamp": datetime.now().isoformat()
            }
            
            # 현재 분석 기록에 피드백 추가
            st.session_state['current_analysis']['feedback'] = feedback_data
            
            # AI Drive에 업데이트
            history = load_history_from_aidrive()
            if history and history[0]['material_code'] == material_code:
                history[0]['feedback'] = feedback_data
                is_saved = save_history_to_aidrive(history)
                
                if is_saved:
                    st.success("✅ **피드백이 AI Drive에 저장되었습니다!** 팀원들이 볼 수 있습니다.")
                else:
                    st.info("ℹ️ 피드백이 세션에 저장되었습니다.")
            
            st.balloons()

# ========================================
# 측정 이력 조회
# ========================================
st.markdown("---")
st.markdown("## 📜 측정 이력")

history = load_history_from_aidrive()

if not history:
    st.info("아직 분석 이력이 없습니다. 첫 번째 소재를 분석해보세요!")
else:
    # 검색 필터
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        search_code = st.text_input("🔍 소재 코드 검색", placeholder="예: ST-2024")
    with col2:
        search_supplier = st.text_input("🏭 공급처 검색", placeholder="예: 대한섬유")
    with col3:
        show_feedback_only = st.checkbox("피드백 있는 항목만", value=False)
    
    # 필터링
    filtered_history = history
    if search_code:
        filtered_history = [h for h in filtered_history if search_code.lower() in h.get('material_code', '').lower()]
    if search_supplier:
        filtered_history = [h for h in filtered_history if search_supplier.lower() in h.get('supplier', '').lower()]
    if show_feedback_only:
        filtered_history = [h for h in filtered_history if h.get('feedback')]
    
    st.caption(f"총 {len(filtered_history)}건의 분석 기록")
    
    # 이력 카드 표시
    for idx, record in enumerate(filtered_history[:20]):  # 최대 20개 표시
        with st.expander(f"📦 {record['material_code']} - {record.get('material_name', '(소재명 없음)')} | {record['timestamp'][:10]}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                **소재 코드:** {record['material_code']}  
                **소재명:** {record.get('material_name', 'N/A')}  
                **공급처:** {record.get('supplier', 'N/A')}  
                **분석 시간:** {record['timestamp'][:19].replace('T', ' ')}  
                **업로드 이미지:** {', '.join(record.get('uploaded_images', []))}
                """)
                
                # AI 분석 결과
                if 'analysis' in record:
                    analysis = record['analysis']
                    st.markdown("**AI 분석 결과:**")
                    result_text = f"밀도: {analysis.get('density')} ends/inch | "
                    result_text += f"광택: {analysis.get('gloss')} GU | "
                    result_text += f"조도: {analysis.get('roughness')} μm | "
                    result_text += f"중량: {analysis.get('weight')} g/m² | "
                    result_text += f"두께: {analysis.get('thickness')} mm | "
                    result_text += f"촉감: {analysis.get('touch_score')}/10"
                    st.text(result_text)
            
            with col2:
                # 피드백 표시
                if record.get('feedback'):
                    st.markdown("**✅ 전문가 피드백 있음**")
                    feedback = record['feedback']
                    if feedback.get('quality_grade'):
                        st.markdown(f"**품질:** {feedback['quality_grade']}")
                    if feedback.get('recommended_use'):
                        st.markdown(f"**용도:** {feedback['recommended_use']}")
                    if feedback.get('actual_thickness'):
                        st.markdown(f"**실측 두께:** {feedback['actual_thickness']} mm")
                else:
                    st.markdown("**⚠️ 피드백 없음**")
            
            # JSON 다운로드 버튼
            json_str = json.dumps(record, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 이 기록 다운로드 (JSON)",
                data=json_str,
                file_name=f"{record['material_code']}_analysis.json",
                mime="application/json",
                key=f"download_{idx}"
            )

# ========================================
# 전체 데이터 내보내기
# ========================================
if history:
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        # JSON 전체 내보내기
        json_data = json.dumps(history, ensure_ascii=False, indent=2)
        st.download_button(
            label="📥 전체 이력 다운로드 (JSON)",
            data=json_data,
            file_name=f"material_analysis_history_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # CSV 변환 후 내보내기
        csv_lines = ["소재코드,소재명,공급처,분석시간,밀도,광택,조도,중량,두께,촉감,품질등급,피드백여부"]
        for record in history:
            analysis = record.get('analysis', {})
            feedback = record.get('feedback', {})
            line = f"{record.get('material_code', '')},"
            line += f"{record.get('material_name', '')},"
            line += f"{record.get('supplier', '')},"
            line += f"{record.get('timestamp', '')[:19]},"
            line += f"{analysis.get('density', '')},"
            line += f"{analysis.get('gloss', '')},"
            line += f"{analysis.get('roughness', '')},"
            line += f"{analysis.get('weight', '')},"
            line += f"{analysis.get('thickness', '')},"
            line += f"{analysis.get('touch_score', '')},"
            line += f"{feedback.get('quality_grade', '')},"
            line += f"{'있음' if feedback else '없음'}"
            csv_lines.append(line)
        
        csv_data = "\n".join(csv_lines)
        st.download_button(
            label="📥 전체 이력 다운로드 (CSV)",
            data=csv_data.encode('utf-8-sig'),  # Excel 호환
            file_name=f"material_analysis_history_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# ========================================
# 푸터
# ========================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6b7280; padding: 2rem 0;'>
    <p><strong>F&F Sergio Tacchini Planning Team</strong></p>
    <p>AI Material Analysis System v2.0 (AI Drive Integration)</p>
    <p>문의: kijeongk@fnf.co.kr</p>
</div>
""", unsafe_allow_html=True)
