import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# --- [UI 디자인 세팅] ---
st.set_page_config(page_title="Yummy Baby Bites", page_icon="👶", layout="centered")

# CSS: 쿠팡 추천 박스 폰트 색상 및 버튼 스타일 최적화
st.markdown("""
    <style>
    .stButton>button { width: 100%; font-weight: bold; background-color: #ffaa00; color: white; border-radius: 8px; }
    .recipe-title { font-size: 28px; font-weight: bold; color: #ff6600; text-align: center; margin-bottom: 20px; }
    .coupang-box { background-color: #f0f2f6; color: #1e1e1e; padding: 20px; border-radius: 10px; border-left: 5px solid #00a9ff; line-height: 1.6; }
    </style>
""", unsafe_allow_html=True)

st.title("👶 Yummy Baby Bites")
st.markdown("냉장고 파먹기로 만드는 **우리 아기 맞춤형 특식 셰프**입니다. 👨‍🍳")

# --- [사이드바: 아기 정보 및 요리 설정] ---
with st.sidebar:
    st.header("🍼 아기 정보 설정")
    # 기본값을 15개월로 세팅하여 접근성 확보
    baby_age = st.number_input("아기 개월 수 (개월)", min_value=4, max_value=36, value=15)
    food_style = st.selectbox("원하는 요리 형태", ["리조또/덮밥류", "핑거푸드/구이류", "반찬/볶음류", "국/스프류", "간식/빵류"])
    allergy = st.text_input("알레르기 또는 제외할 재료 (선택)", placeholder="예: 땅콩, 밀가루")

# --- [메인 화면: 사용자 입력 폼 (UX 개선)] ---
with st.form("recipe_form"):
    st.subheader("🥦 냉장고에 어떤 재료가 있나요?")
    st.markdown("자주 쓰는 유아식 재료는 터치해서 고르고, 없는 건 직접 적어주세요!")

    # 모바일 환경을 고려한 카테고리별 다중 선택
    col1, col2, col3 = st.columns(3)
    with col1:
        proteins = st.multiselect("🥩 단백질", ["소고기 안심", "소고기 다짐육", "닭고기 안심", "닭가슴살", "돼지고기", "흰살생선", "새우", "계란", "두부"])
    with col2:
        veggies = st.multiselect("🥕 채소/과일", ["브로콜리", "단호박", "양파", "당근", "감자", "고구마", "애호박", "버섯", "시금치", "청경채", "사과", "바나나"])
    with col3:
        extras = st.multiselect("🧈 유제품/기타", ["무염 버터", "아기 치즈", "우유", "오트밀", "쌀밥", "밀가루"])

    # 엣지 케이스를 위한 텍스트 입력창
    other_ingredients = st.text_input("➕ 리스트에 없는 기타 재료 직접 입력 (선택)", placeholder="예: 전복, 아스파라거스, 가지")

    submitted = st.form_submit_button("✨ 맞춤형 레시피 & 쇼핑 팁 받기")

# --- [API 호출 및 화면 렌더링] ---
if submitted:
    # 1. 입력된 재료들 하나로 취합
    selected_list = proteins + veggies + extras
    if other_ingredients.strip():
        selected_list.append(other_ingredients.strip())
    
    ingredients_str = ", ".join(selected_list)

    # 2. 예외 처리: 아무것도 입력하지 않았을 때 방어
    if not ingredients_str:
        st.warning("재료를 하나 이상 선택하거나 입력해 주세요! 😅")
    else:
        with st.spinner('레시피를 설계하고, 마트 갈 목록을 고민 중입니다... ⏳'):
            try:
                # 3. 텍스트 생성 (GPT-4o-mini)
                allergy_prompt = f"주의사항: {allergy}는 절대 포함하지 마세요." if allergy else ""
                
                system_prompt = f"""
                당신은 {baby_age}개월 아기를 위한 최고의 영양사이자 요리 강사입니다.
                
                [임무 1: 레시피 작성]
                - 무염/저염식을 엄격히 지키되, 버터/치즈 등으로 칼로리를 높이세요.
                - {allergy_prompt}
                - 요리 형태는 반드시 '{food_style}' 스타일이어야 합니다.
                - 초보 부모를 위해 정확한 계량(g, 스푼), 불 조절, 조리 시간을 상세히 설명하세요.
                
                [임무 2: 추가 재료 추천]
                - 입력된 현재 재료들과 조합했을 때, 앞으로 더 다양한 메뉴를 만들 수 있는 '활용도 높은 식재료'를 쿠팡에서 1~2가지만 산다면 무엇이 좋을지 추천하고 이유를 간략히 적으세요.
                
                [출력 형식 준수]
                반드시 아래 형식으로 출력해야 합니다. 구분선을 지키세요.
                [요리명]
                (레시피 본문 내용...)
                ---COUPANG_SUGGESTION---
                (쿠팡 추천 재료 및 이유...)
                """

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"냉장고 재료: '{ingredients_str}'."}
                    ],
                    temperature=0.7
                )
                full_text = response.choices[0].message.content
                
                # 구분자를 기준으로 데이터 파싱
                parts = full_text.split("---COUPANG_SUGGESTION---")
                recipe_part = parts[0].strip()
                coupang_part = parts[1].strip() if len(parts) > 1 else "추천 정보를 불러오지 못했습니다."
                
                recipe_lines = recipe_part.split('\n')
                dish_name = recipe_lines[0].replace('[', '').replace(']', '').strip()
                recipe_body = '\n'.join(recipe_lines[1:]).strip()

                # 4. 이미지 생성 (DALL-E 3 - 실사화 프롬프트 초강화)
                image_prompt = f"""
                A candid, documentary-style photograph of homemade {dish_name} for a {baby_age}-month-old baby. 
                Shot using natural daylight from a side window. The food texture looks real, slightly imperfect, and messy.
                Served in a simple silicone baby bowl on a wooden table. Shallow depth of field, film grain texture. 
                NOT a studio photo, NO artificial gloss, Looks like a real photo taken by a parent at home.
                """
                
                image_response = client.images.generate(
                    model="dall-e-3",
                    prompt=image_prompt,
                    size="1024x1024",
                    n=1,
                )
                image_url = image_response.data[0].url

                # --- [결과 화면 렌더링] ---
                st.markdown("---")
                st.markdown(f"<div class='recipe-title'>🍽️ {dish_name}</div>", unsafe_allow_html=True)
                
                st.image(image_url, use_container_width=True, caption="집에서 직접 만든 것 같은 예상 사진")
                
                with st.expander("📝 상세 조리법 보기 (클릭)", expanded=True):
                    st.write(recipe_body)
                
                st.markdown("### 🚀 다음 장볼 때 이건 어때요?")
                st.markdown(f"""
                    <div class='coupang-box'>
                        <strong>💡 AI 영양사의 추천:</strong><br>
                        {coupang_part}
                    </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"오류가 발생했습니다. 잠시 후 다시 시도해주세요. ({e})")