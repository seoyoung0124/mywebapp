import pandas as pd
import requests
import streamlit as st
import plotly.express as px

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="전국 연도별 인구 지표 지도",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ 전국 시군구별 인구 지표 지도")
st.caption("연도별·지역별 고령인구 및 유소년인구 비율을 확인할 수 있는 지도입니다.")

# 2. 데이터 불러오기 (캐싱 적용)
@st.cache_data
def load_data():
    # 인구 데이터 불러오기 ('코드' 열은 문자열로 읽기)
    pop_url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/population_yearly.csv.gz"
    df = pd.read_csv(pop_url, dtype={'코드': str})
    
    # 지도 경계 GeoJSON 데이터 불러오기
    geo_url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/boundaries/sigungu_kr.geojson"
    geojson = requests.get(geo_url).json()
    
    return df, geojson

df, geojson = load_data()

# GeoJSON 내의 유효한 시군구 코드 집합 추출
geojson_codes = set(feat['properties']['코드'] for feat in geojson['features'])

# 시도별 경계 중심점(위도, 경도) 및 확대(Zoom) 레벨 정의
SIDO_CENTERS = {
    '전국': {'lat': 35.8, 'lon': 127.8, 'zoom': 6.2},
    '서울특별시': {'lat': 37.5665, 'lon': 126.9780, 'zoom': 9.5},
    '부산광역시': {'lat': 35.1796, 'lon': 129.0756, 'zoom': 9.5},
    '대구광역시': {'lat': 35.8714, 'lon': 128.6014, 'zoom': 9.0},
    '인천광역시': {'lat': 37.4563, 'lon': 126.7052, 'zoom': 9.0},
    '광주광역시': {'lat': 35.1595, 'lon': 126.8526, 'zoom': 10.0},
    '대전광역시': {'lat': 36.3504, 'lon': 127.3845, 'zoom': 10.0},
    '울산광역시': {'lat': 35.5384, 'lon': 129.3114, 'zoom': 10.0},
    '세종특별자치시': {'lat': 36.4800, 'lon': 127.2890, 'zoom': 10.5},
    '경기도': {'lat': 37.4138, 'lon': 127.5183, 'zoom': 8.3},
    '강원특별자치도': {'lat': 37.8228, 'lon': 128.1555, 'zoom': 8.0},
    '충청북도': {'lat': 36.6357, 'lon': 127.4912, 'zoom': 8.3},
    '충청남도': {'lat': 36.5184, 'lon': 126.8000, 'zoom': 8.3},
    '전라북도': {'lat': 35.7175, 'lon': 127.1530, 'zoom': 8.3},
    '전북특별자치도': {'lat': 35.7175, 'lon': 127.1530, 'zoom': 8.3},
    '전라남도': {'lat': 34.8679, 'lon': 126.9910, 'zoom': 8.0},
    '경상북도': {'lat': 36.4919, 'lon': 128.8889, 'zoom': 8.0},
    '경상남도': {'lat': 35.4606, 'lon': 128.2132, 'zoom': 8.3},
    '제주특별자치도': {'lat': 33.4890, 'lon': 126.4983, 'zoom': 9.2}
}

# 3. 사이드바 컨트롤러 (연도, 지표, 시도 선택)
st.sidebar.header("⚙️ 지도 설정")

# (1) 연도 선택 슬라이더
min_year = int(df['연도'].min())
max_year = int(df['연도'].max())
selected_year = st.sidebar.slider("연도 선택", min_value=min_year, max_value=max_year, value=max_year)

# (2) 지표 선택
metric_option = st.sidebar.selectbox(
    "인구 지표 선택",
    ["고령인구 비율 (65세 이상)", "유소년인구 비율 (0~14세)"]
)

# (3) 시도 선택
sido_list = ["전국"] + sorted([s for s in df['시도'].unique() if pd.notna(s)])
selected_sido = st.sidebar.selectbox("시도 선택 (지역 확대)", sido_list)


# 4. 선택된 연도 데이터 전처리
df_year = df[df['연도'] == selected_year].copy()

# 행정동 코드(10자리)에서 앞 5자리 잘라 시군구코드 생성
df_year['시군구코드'] = df_year['코드'].str[:5]

# 행정구역 개편 코드 보정 함수
def fix_sigungu_code(code):
    if pd.isna(code):
        return code
    # 군위군: 경북(47720) -> 대구(27720)
    if code == '47720':
        return '27720'
    # 강원: 42 -> 51
    if code.startswith('42'):
        return '51' + code[2:]
    # 전북: 45 -> 52
    if code.startswith('45'):
        return '52' + code[2:]
    return code

df_year['시군구코드'] = df_year['시군구코드'].apply(fix_sigungu_code)

# 나이별 인구 열 구분
total_pop_cols = [col for col in df_year.columns if col.startswith('계_')]

elderly_cols = []  # 65세 이상
youth_cols = []    # 0~14세

for col in total_pop_cols:
    age_str = col.replace('계_', '').replace('세 이상', '').replace('세', '')
    if age_str.isdigit():
        age = int(age_str)
        if age >= 65:
            elderly_cols.append(col)
        elif age <= 14:
            youth_cols.append(col)

# 시군구 단위 인구 합산
df_year['총인구'] = df_year[total_pop_cols].sum(axis=1)
df_year['고령인구'] = df_year[elderly_cols].sum(axis=1)
df_year['유소년인구'] = df_year[youth_cols].sum(axis=1)

# 시군구별 그룹화
df_sigungu = df_year.groupby(['시도', '시군구', '시군구코드'], as_index=False)[['총인구', '고령인구', '유소년인구']].sum()

# 비율(%) 계산
df_sigungu['고령화율'] = (df_sigungu['고령인구'] / df_sigungu['총인구']) * 100
df_sigungu['유소년비율'] = (df_sigungu['유소년인구'] / df_sigungu['총인구']) * 100

# GeoJSON과 매칭 여부 체크
df_sigungu['매칭여부'] = df_sigungu['시군구코드'].isin(geojson_codes)
unmatched_regions = df_sigungu[~df_sigungu['매칭여부']]


# 5. 지표별 구간 및 색상 설정
if metric_option == "고령인구 비율 (65세 이상)":
    target_col = '고령화율'
    metric_name = "고령화율"
    bins = [-1, 19, 23, 28, 38, 100]
    labels = ['19% 미만', '19% 이상 ~ 23% 미만', '23% 이상 ~ 28% 미만', '28% 이상 ~ 38% 미만', '38% 이상']
    color_discrete_map = {
        '19% 미만': '#edf8e9',
        '19% 이상 ~ 23% 미만': '#bae4b3',
        '23% 이상 ~ 28% 미만': '#74c476',
        '28% 이상 ~ 38% 미만': '#31a354',
        '38% 이상': '#006d2c'
    }
else:
    target_col = '유소년비율'
    metric_name = "유소년 비율"
    bins = [-1, 6, 8, 10, 12, 100]
    labels = ['6% 미만', '6% 이상 ~ 8% 미만', '8% 이상 ~ 10% 미만', '10% 이상 ~ 12% 미만', '12% 이상']
    color_discrete_map = {
        '6% 미만': '#f7fbff',
        '6% 이상 ~ 8% 미만': '#c6dbef',
        '8% 이상 ~ 10% 미만': '#6baed6',
        '10% 이상 ~ 12% 미만': '#2171b5',
        '12% 이상': '#08306b'
    }

df_sigungu['지표_구간'] = pd.cut(
    df_sigungu[target_col], 
    bins=bins, 
    labels=labels, 
    right=False
)

df_sigungu[target_col] = df_sigungu[target_col].round(1)


# 6. 상단 지표 카드 세 장 (Metric)
national_total_pop = df_sigungu['총인구'].sum()
if metric_option == "고령인구 비율 (65세 이상)":
    national_target_pop = df_sigungu['고령인구'].sum()
else:
    national_target_pop = df_sigungu['유소년인구'].sum()

national_rate = (national_target_pop / national_total_pop * 100) if national_total_pop > 0 else 0

max_row = df_sigungu.loc[df_sigungu[target_col].idxmax()]
min_row = df_sigungu.loc[df_sigungu[target_col].idxmin()]

col1, col2, col3 = st.columns(3)
col1.metric("전국 평균 " + metric_name, f"{national_rate:.1f}%")
col2.metric("가장 높은 시군구", f"{max_row['시도']} {max_row['시군구']}", f"{max_row[target_col]:.1f}%")
col3.metric("가장 낮은 시군구", f"{min_row['시도']} {min_row['시군구']}", f"{min_row[target_col]:.1f}%")

st.divider()


# 7. Plotly 단계구분도 생성 (choropleth_map 사용 및 호환성 처리)
center_info = SIDO_CENTERS.get(selected_sido, SIDO_CENTERS['전국'])

# Plotly 버전에 따라 px.choropleth_map 또는 px.choropleth_mapbox 호출
if hasattr(px, "choropleth_map"):
    fig = px.choropleth_map(
        df_sigungu,
        geojson=geojson,
        locations='시군구코드',
        featureidkey='properties.코드',
        color='지표_구간',
        color_discrete_map=color_discrete_map,
        category_orders={'지표_구간': labels},
        hover_name='시군구',
        hover_data={
            '시도': True,
            target_col: ':.1f%',
            '시군구코드': False,
            '지표_구간': False
        },
        center={"lat": center_info['lat'], "lon": center_info['lon']},
        zoom=center_info['zoom'],
        map_style="white-bg"
    )
else:
    fig = px.choropleth_mapbox(
        df_sigungu,
        geojson=geojson,
        locations='시군구코드',
        featureidkey='properties.코드',
        color='지표_구간',
        color_discrete_map=color_discrete_map,
        category_orders={'지표_구간': labels},
        hover_name='시군구',
        hover_data={
            '시도': True,
            target_col: ':.1f%',
            '시군구코드': False,
            '지표_구간': False
        },
        center={"lat": center_info['lat'], "lon": center_info['lon']},
        zoom=center_info['zoom'],
        mapbox_style="white-bg"
    )

fig.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    legend_title_text=f'{metric_name} 구간',
    legend=dict(
        yanchor="top",
        y=0.98,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(255, 255, 255, 0.8)"
    )
)

st.subheader(f"📊 {selected_year}년 {selected_sido} {metric_name} 지도")
st.plotly_chart(fig, use_container_width=True)

# 경계 데이터 미매칭 지역 안내 문구 표시
if not unmatched_regions.empty:
    unmatched_list = [f"{r['시도']} {r['시군구']}" for _, r in unmatched_regions.iterrows()]
    st.caption(
        f"⚠️ **행정구역 미매칭 안내 ({selected_year}년 기준):** "
        f"지도 경계(GeoJSON)에 코드가 맞지 않는 {len(unmatched_list)}개 지역은 지도에 표현되지 않거나 회색으로 나타납니다. "
        f"({', '.join(unmatched_list)})"
    )

st.divider()


# 8. 하단 데이터 표 (상위 10개 및 하위 10개)
t_col1, t_col2 = st.columns(2)

df_display = df_sigungu[['시도', '시군구', target_col]].copy()

with t_col1:
    st.subheader(f"🔴 {metric_name} 높은 지역 Top 10")
    top10 = df_display.sort_values(by=target_col, ascending=False).head(10).reset_index(drop=True)
    top10.index = top10.index + 1
    st.dataframe(top10, use_container_width=True)

with t_col2:
    st.subheader(f"🔵 {metric_name} 낮은 지역 Top 10")
    bottom10 = df_display.sort_values(by=target_col, ascending=True).head(10).reset_index(drop=True)
    bottom10.index = bottom10.index + 1
    st.dataframe(bottom10, use_container_width=True)
