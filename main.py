import streamlit as st

# 페이지 설정
st.set_page_config(page_title="💖 MBTI 여행지 추천!", page_icon="✈️")

# 귀여운 스타일링 (CSS)
st.markdown(
    """
    <style>
    .main {
        background-color: #FFF5F7;
    }
    .stSelectbox label {
        color: #FF6B81 !important;
        font-size: 1.2rem !important;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #FF8EAE;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 10px 24px;
        font-size: 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #FF6B81;
        color: white;
    }
    .title-text {
        color: #FF477E;
        text-align: center;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 데이터 베이스 (MBTI별 추천)
mbti_data = {
    "ISTJ": {
        "place": "🇯🇵 일본 교토",
        "desc": "조용하고 차분한 고풍스러운 거리! 계획대로 완벽하게 다녀올 수 있는 정갈한 여행지예요 ⛩️",
    },
    "ISFJ": {
        "place": "🇨🇭 스위스 인터라켄",
        "desc": "동화 같은 알프스 마을에서 마음까지 포근해지는 힐링 여행! 다정한 당신에게 딱이에요 🏔️",
    },
    "INFJ": {
        "place": "🇨🇿 체코 프라하",
        "desc": "낭만 가득한 골목길을 거닐며 깊은 생각과 감성을 충전할 수 있는 신비로운 도시예요 🏰",
    },
    "INTJ": {
        "place": "🇬🇧 영국 런던",
        "desc": "풍부한 역사와 스마트한 박물관, 미술관이 가득! 알찬 탐방을 즐겨보세요 🏛️",
    },
    "ISTP": {
        "place": "🇳🇿 뉴질랜드 퀸스타운",
        "desc": "스릴 넘치는 액티비티의 천국! 답답함을 날려버릴 라이딩과 익스트림을 즐겨봐요 🪂",
    },
    "ISFP": {
        "place": "🇮🇩 인도네시아 발리",
        "desc": "여유로운 힐링과 예쁜 카페, 감성적인 석양이 가득한 자연 속 리조트 🌴",
    },
    "INFP": {
        "place": "🇮🇸 아이슬란드 레이캬비크",
        "desc": "몽환적인 오로라와 신비로운 대자연! 상상력이 풍부한 당신을 위한 감성 공간 🌌",
    },
    "INTP": {
        "place": "🇪🇬 이집트 카이로",
        "desc": "호기심을 자극하는 피라미드와 수수께끼 같은 역사속으로 지적 탐험을 떠나봐요 🗿",
    },
    "ESTP": {
        "place": "🇺🇸 미국 라스베이거스",
        "desc": "화려한 조명과 화끈한 밤문화, 끊이지 않는 즐길 거리가 가득한 액티브한 도시 🎰",
    },
    "ESFP": {
        "place": "🇪🇸 스페인 바르셀로나",
        "desc": "열정적인 사람들과 정열적인 플라멩코! 언제나 축제 같은 에너지를 느껴보세요 💃",
    },
    "ENFP": {
        "place": "🇹🇭 태국 방콕",
        "desc": "통통 튀는 화려한 야시장과 맛있는 길거리 음식! 자유롭고 활기찬 최적의 여행지 툭툭 🛺",
    },
    "ENTP": {
        "place": "🇧🇷 브라질 리우데자네이루",
        "desc": "예측 불가한 즐거움과 다채로운 모험이 기다리는 열정의 도시 🎭",
    },
    "ESTJ": {
        "place": "🇸🇬 싱가포르",
        "desc": "깔끔하고 완벽한 도시 인프라! 동선과 계획에 맞춰 깔끔하게 즐길 수 있는 미식의 천국 🏙️",
    },
    "ESFJ": {
        "place": "🇮🇹 이탈리아 피렌체",
        "desc": "따뜻한 햇살 아래 친구, 연인과 함께 맛있는 음식을 나누며 추억을 쌓기 좋은 로맨틱한 곳 🍕",
    },
    "ENFJ": {
        "place": "🇬🇷 그리스 산토리니",
        "desc": "하얀 건물의 아름다운 풍경과 따뜻하고 정겨운 분위기가 모두를 행복하게 만들어요 🌊",
    },
    "ENTJ": {
        "place": "🇺🇸 미국 뉴욕",
        "desc": "세상의 중심에서 느끼는 트렌디함과 웅장함! 목표 의식을 자극하는 눈부신 야경 🗽",
    },
}

# UI 구성
st.markdown(
    "<h1 class='title-text'>🎀 MBTI별 떠나기 좋은 찰떡 여행지 🎀</h1>",
    unsafe_allow_html=True,
)
st.write("")
st.write("당신의 MBTI를 선택하면 어울리는 찰떡 여행지를 추천해드려요! ✨")

# MBTI 선택 박스
selected_mbti = st.selectbox(
    "💖 당신의 MBTI는 무엇인가요?", list(mbti_data.keys())
)

st.write("")

# 결과 출력 버튼
if st.button("✈️ 추천 여행지 확인하기!"):
    result = mbti_data[selected_mbti]

    st.balloons()  # 귀여운 풍선 애니메이션 효과!

    st.success(f"### 🎉 {selected_mbti}에게 딱 맞는 여행지")
    st.header(f"✨ {result['place']}")
    st.write(f"👉 **왜 이 여행지일까요?** {result['desc']}")

    st.write("---")
    st.write("💕 설레는 여행을 준비해보세요!")
