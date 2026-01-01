import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, time
import pytz
import math

# ---------------------------------------------------------
# [설정] 앱 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="YieldMax Pro - Group 1",
    page_icon="💎",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# [핵심] HTML 공백 제거 함수 (렌더링 오류 방지)
# ---------------------------------------------------------
def render_html(raw_html):
    cleaned = " ".join([line.strip() for line in raw_html.splitlines() if line.strip()])
    st.markdown(cleaned, unsafe_allow_html=True)

# ---------------------------------------------------------
# [스타일] CSS (모바일 최적화 & 초고퀄리티 UI)
# ---------------------------------------------------------
render_html("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    /* 1. 글로벌 스타일 */
    html, body, [class*="css"] {
        font-family: 'Pretendard', sans-serif;
        background-color: #f2f4f6; /* 토스/카카오 스타일의 연한 회색 배경 */
        color: #191f28;
    }
    
    /* 2. 헤더 카드 (Deep Night Gradient) */
    .header-card {
        background: linear-gradient(135deg, #1a2980 0%, #26d0ce 100%);
        padding: 32px 24px;
        border-radius: 24px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px rgba(26, 41, 128, 0.25);
        position: relative;
        overflow: hidden;
    }
    /* 배경 빛 반사 효과 */
    .header-card::before {
        content: ''; position: absolute; top: -60px; right: -60px;
        width: 180px; height: 180px;
        background: rgba(255,255,255,0.1); border-radius: 50%; z-index: 0;
    }
    .header-content { position: relative; z-index: 1; }

    /* 3. 뱃지 스타일 */
    .market-badge {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 6px 12px; border-radius: 20px;
        font-size: 0.8rem; font-weight: 700;
        margin-bottom: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }
    .status-open { background: #00e676; color: #003300; animation: pulse 2s infinite; }
    .status-pre { background: #ffea00; color: #3e2723; }
    .status-after { background: #d1c4e9; color: #4527a0; }
    .status-closed { background: #eceff1; color: #455a64; border: 1px solid #cfd8dc; }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(0, 230, 118, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(0, 230, 118, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 230, 118, 0); }
    }

    .fx-badge {
        background: rgba(255,255,255,0.2);
        padding: 6px 12px; border-radius: 12px;
        font-size: 0.8rem; font-weight: 600;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255,255,255,0.2);
    }

    /* 4. 타임라인 (유리 질감) */
    .timeline-container { display: flex; gap: 8px; margin-top: 24px; }
    .glass-box {
        flex: 1; text-align: center;
        background: rgba(255,255,255,0.1);
        padding: 10px; border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.15);
        backdrop-filter: blur(4px);
    }
    .t-label { font-size: 0.7rem; color: rgba(255,255,255,0.8); margin-bottom: 4px; }
    .t-val { font-size: 0.9rem; font-weight: 700; color: #fff; white-space: nowrap; }
    .accent-gold { color: #ffd700; }
    .accent-green { color: #69f0ae; }

    /* 5. 메인 정보 카드 (그림자 & 라운드) */
    .info-card {
        background: white; border-radius: 24px; padding: 24px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.03);
        border: 1px solid #ffffff; margin-bottom: 20px;
    }
    .metric-grid { display: flex; gap: 8px; margin-top: 20px; }
    .metric-box {
        flex: 1; background: #f9f9fb; border-radius: 14px;
        padding: 12px 6px; text-align: center;
        border: 1px solid #f0f0f5;
    }
    .m-title { font-size: 0.7rem; color: #8b95a1; font-weight: 600; margin-bottom: 4px; white-space: nowrap; }
    .m-data { font-size: 0.95rem; font-weight: 800; color: #333; }

    /* 6. 계산기 카드 공통 스타일 */
    .calc-card-bg { background: white; border-radius: 24px; padding: 20px; border: 1px solid #e0e0e0; margin-top: 10px; }
    .calc-row { display: flex; justify-content: space-between; margin-bottom: 10px; align-items: center; }
    .calc-label { font-size: 0.9rem; color: #666; }
    .calc-val { font-weight: 700; color: #333; }
    .calc-divider { border-top: 1px dashed #ddd; margin: 12px 0; }
    .calc-total-label { font-size: 1rem; font-weight: 700; color: #3182f6; }
    .calc-total-val { font-size: 1.4rem; font-weight: 800; color: #3182f6; }

    /* 주의사항 박스 */
    .caution-box {
        margin-top: 16px; padding: 14px;
        background: #fafafa; border-radius: 12px;
        border: 1px solid #eee;
        font-size: 0.8rem; color: #767676; line-height: 1.5;
    }
    .caution-header { font-weight: 700; color: #555; margin-bottom: 4px; display: block; }

    /* 뱃지류 */
    .badge-roc { background: #fff0f2; color: #f04452; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }
    .badge-safe { background: #e8fdf3; color: #02cba5; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }
    .ticker-tag { background: #e8f3ff; color: #3182f6; padding: 4px 10px; border-radius: 8px; font-weight: 800; font-size: 0.9rem; }

    /* Streamlit 위젯 커스텀 */
    div.stButton > button {
        width: 100%; border-radius: 12px; font-weight: 700;
        background: #fff; border: 1px solid #e5e8eb; color: #6b7684;
        height: 48px; transition: all 0.2s;
    }
    div.stButton > button:hover { background: #f2f4f6; color: #333; border-color: #ccc; }

    /* 탭 메뉴 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px; overflow-x: auto; white-space: nowrap; 
        padding-bottom: 4px; -webkit-overflow-scrolling: touch;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px; background-color: #fff; 
        border-radius: 20px; border: 1px solid #e5e8eb;
        padding: 0 16px; font-size: 0.85rem; font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3182f6; color: white; border-color: #3182f6;
    }
    </style>
""")

# ---------------------------------------------------------
# [데이터] Group 1 (2025-12-31 기준)
# ---------------------------------------------------------
# 배당락일: 2025-12-31 (수) / 지급일: 2026-01-02 (금)
# 매수마감: 12/30(화) 미국장 마감 -> 한국시간 12/31(수) 06:00
SCHEDULE_KST = {
    "buy_limit": "12/31(수) 06:00", 
    "ex_date": "12/31(수)",
    "pay_date": "1/2(금)"
}

DATA_MAP = {
    'CHPY': {'div': 0.4401, 'rate': 40.59, 'sec': 0.00, 'roc': 99.47, 'name': 'Semiconductor Portfolio'},
    'FEAT': {'div': 0.3415, 'rate': 69.07, 'sec': 69.57, 'roc': 60.49, 'name': 'Dorsey Wright Featured 5'},
    'FIVY': {'div': 0.2507, 'rate': 41.55, 'sec': 37.98, 'roc': 60.37, 'name': 'Dorsey Wright Hybrid 5'},
    'GPTY': {'div': 0.2565, 'rate': 30.99, 'sec': 0.00, 'roc': 0.00, 'name': 'AI & Tech Portfolio'},
    'LFGY': {'div': 0.2481, 'rate': 50.04, 'sec': 0.00, 'roc': 0.00, 'name': 'Crypto Industry & Tech'},
    'QDTY': {'div': 0.1494, 'rate': 17.70, 'sec': 0.20, 'roc': 0.00, 'name': 'Nasdaq 100 0DTE'},
    'RDTY': {'div': 0.2049, 'rate': 26.63, 'sec': 1.15, 'roc': 0.00, 'name': 'R2000 0DTE'},
    'SDTY': {'div': 0.1240, 'rate': 14.37, 'sec': 0.13, 'roc': 0.00, 'name': 'S&P 500 0DTE'},
    'SLTY': {'div': 0.3947, 'rate': 60.13, 'sec': 2.05, 'roc': 95.76, 'name': 'Ultra Short Option'},
    'ULTY': {'div': 0.4866, 'rate': 65.97, 'sec': 0.00, 'roc': 0.00, 'name': 'Ultra Option Strategy'},
    'YMAG': {'div': 0.0992, 'rate': 35.86, 'sec': 59.29, 'roc': 59.48, 'name': 'Magnificent 7 Fund'},
    'YMAX': {'div': 0.1060, 'rate': 53.95, 'sec': 85.99, 'roc': 59.11, 'name': 'Universe Fund'},
}

# -----------------------------
# [함수] 마켓 상태 체크 (실시간)
# -----------------------------
def get_us_market_status():
    ny_tz = pytz.timezone('America/New_York')
    now_ny = datetime.now(ny_tz)

    # 1. 주말 체크
    if now_ny.weekday() >= 5: 
        return "⛔ 휴장 (주말)", "status-closed"

    # 2. 공휴일 체크 (2025/2026 주요 휴장일)
    holidays = [
        "2025-12-25", "2026-01-01", "2026-01-19", "2026-02-16"
    ]
    if now_ny.strftime("%Y-%m-%d") in holidays:
        return "⛔ 휴장 (공휴일)", "status-closed"

    # 3. 시간대 체크 (분 단위 환산)
    minutes = now_ny.hour * 60 + now_ny.minute
    
    if 240 <= minutes < 570:   # 04:00 ~ 09:30
        return "🌅 프리마켓", "status-pre"
    elif 570 <= minutes < 960: # 09:30 ~ 16:00
        return "🔥 정규장 오픈", "status-open"
    elif 960 <= minutes < 1200: # 16:00 ~ 20:00
        return "🌙 애프터마켓", "status-after"
    else:
        return "💤 장 마감", "status-closed"

# -----------------------------
# [함수] 데이터 연결 (15초 갱신)
# -----------------------------
@st.cache_data(ttl=15, show_spinner=False)
def get_market_info(ticker_keys):
    try:
        fx = yf.Ticker("USDKRW=X").history(period="1d")["Close"].iloc[-1]
    except:
        fx = 1435.0 # Fallback

    prices = {}
    try:
        # 한번에 조회해서 속도 최적화
        t_str = " ".join(ticker_keys)
        data = yf.download(t_str, period="1d", progress=False)['Close']
        for t in ticker_keys:
            try:
                # 데이터 형태에 따른 처리
                val = data[t].iloc[-1] if isinstance(data, pd.DataFrame) else data[t]
                prices[t] = float(val)
            except:
                prices[t] = 0.0
    except:
        pass

    now_time = datetime.now(pytz.timezone('Asia/Seoul')).strftime("%H:%M:%S")
    return fx, prices, now_time

# -----------------------------
# [UI] 실행 및 레이아웃
# -----------------------------
if st.button("🔄 실시간 시세 새로고침"):
    st.cache_data.clear()

with st.spinner("미국 현지 데이터 수신 중..."):
    t_list = sorted(list(DATA_MAP.keys()))
    usd_krw, price_map, update_time = get_market_info(t_list)
    market_text, market_class = get_us_market_status()

tax_rate = 0.154

# 1. 헤더 영역
render_html(f"""
    <div class="header-card">
        <div class="header-content" style="display:flex; justify-content:space-between; align-items:start;">
            <div>
                <div class="market-badge {market_class}">{market_text}</div>
                <h2 style="margin:0; font-size:1.5rem; font-weight:800; letter-spacing:-0.5px;">
                    YieldMax Group 1<br>최신 배당 내역
                </h2>
            </div>
            <div style="text-align:right;">
                <div class="fx-badge">🇺🇸 1$ = {usd_krw:,.0f}원</div>
                <div style="font-size:0.7rem; margin-top:4px; opacity:0.8;">{update_time} 기준</div>
            </div>
        </div>
        <div class="header-content timeline-container">
            <div class="glass-box">
                <div class="t-label">🚨 매수마감</div>
                <div class="t-val accent-gold">{SCHEDULE_KST['buy_limit']}</div>
            </div>
            <div class="glass-box">
                <div class="t-label">📉 배당락일</div>
                <div class="t-val">{SCHEDULE_KST['ex_date']}</div>
            </div>
            <div class="glass-box">
                <div class="t-label">💰 지급일</div>
                <div class="t-val accent-green">{SCHEDULE_KST['pay_date']}</div>
            </div>
        </div>
    </div>
""")

# 2. 종목 선택 및 상세 정보
st.markdown("### 💎 종목별 상세 분석")

col_sel, _ = st.columns([1, 0.01])
with col_sel:
    # 기본값 ULTY로 설정 (Group 1의 인기 종목)
    def_idx = t_list.index("ULTY") if "ULTY" in t_list else 0
    sel_ticker = st.selectbox("분석할 ETF 선택", t_list, index=def_idx)

# 데이터 계산
d = DATA_MAP[sel_ticker]
curr_p = price_map.get(sel_ticker, 0.0)
div_krw = d['div'] * usd_krw
div_krw_net = div_krw * (1 - tax_rate)

# 성향 뱃지
if d['roc'] > 50:
    risk_badge = "<span class='badge-roc'>🔥 공격형 (High Risk)</span>"
elif d['roc'] > 0:
    risk_badge = "<span class='badge-roc'>⚠️ 고수익형</span>"
else:
    risk_badge = "<span class='badge-safe'>🛡️ 건전 배당형</span>"

render_html(f"""
    <div class="info-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <span class="ticker-tag">{sel_ticker}</span>
                {risk_badge}
            </div>
            <span style="font-size:0.75rem; color:#888;">{d['name']}</span>
        </div>
        
        <div style="text-align:center; padding: 10px 0;">
            <div style="font-size:0.85rem; color:#8b95a1; margin-bottom:6px;">1주당 확정 배당금</div>
            <div style="font-size:2.4rem; font-weight:900; color:#191f28; letter-spacing:-1px; line-height:1;">
                ${d['div']:.4f}
            </div>
            <div style="font-size:1.1rem; font-weight:700; margin-top:8px;">
                <span style="color:#adb5bd;">(세전)</span> {div_krw:,.0f}원 
                <span style="margin:0 6px; color:#ddd;">|</span> 
                <span style="color:#3182f6;">{div_krw_net:,.0f}원 <span style="font-size:0.8rem; font-weight:500;">(세후)</span></span>
            </div>
        </div>

        <div class="metric-grid">
            <div class="metric-box">
                <div class="m-title">📊 분배율(Rate)</div>
                <div class="m-data" style="color:#3182f6;">{d['rate']}%</div>
            </div>
            <div class="metric-box">
                <div class="m-title">🏦 실질수익(SEC)</div>
                <div class="m-data">{d['sec']}%</div>
            </div>
            <div class="metric-box">
                <div class="m-title">↩️ 원금반환(ROC)</div>
                <div class="m-data" style="color: {'#e92c2c' if d['roc'] > 0 else '#00bfa5'};">{d['roc']}%</div>
            </div>
        </div>
        
        <div style="text-align:right; font-size:0.75rem; color:#adb5bd; margin-top:16px;">
            현재 주가 ${curr_p:.2f} 기준
        </div>
    </div>
""")

# 3. 통합 계산기 탭
st.write("")
tabs = st.tabs(["🧮 배당금", "💧 물타기", "🧪 스트레스", "📉 원금회수", "🔥 FIRE", "⛄ 스노우볼"])

# [탭1] 배당금 계산기
with tabs[0]:
    c1, c2 = st.columns([1, 1.5])
    with c1:
        st.write("") # Spacer
        shares = st.number_input("보유 수량", min_value=1, value=1000, step=10, key="cal_shares")
    with c2:
        val_pre = shares * div_krw
        val_tax = val_pre * tax_rate
        val_post = val_pre - val_tax
        render_html(f"""
            <div class="calc-card-bg">
                <div class="calc-row">
                    <span class="calc-label">세전 배당금</span>
                    <span class="calc-val">{val_pre:,.0f}원</span>
                </div>
                <div class="calc-row">
                    <span class="calc-label">세금 (15.4%)</span>
                    <span class="calc-val" style="color:#e92c2c;">-{val_tax:,.0f}원</span>
                </div>
                <div class="calc-divider"></div>
                <div class="calc-row">
                    <span class="calc-total-label">실제 입금액</span>
                    <span class="calc-total-val">{val_post:,.0f}원</span>
                </div>
            </div>
            <div class="caution-box">
                <span class="caution-header">📌 계산 기준</span>
                • 환율: <b>{usd_krw:,.2f}원</b> (실시간) / 세율: 15.4%<br>
                • 이번 주 배당금 <b>${d['div']:.4f}</b>가 기준입니다.
            </div>
        """)

# [탭2] 물타기 계산기
with tabs[1]:
    c1, c2 = st.columns(2)
    with c1:
        my_avg = st.number_input("내 평단가($)", min_value=0.1, value=curr_p*1.1, step=0.1, format="%.2f")
    with c2:
        my_qty = st.number_input("보유 수량", min_value=1, value=100, step=10, key="mul_qty")
    add_qty = st.number_input("추가 매수(주)", min_value=1, value=50, step=10)
    
    # 계산
    old_total = my_avg * my_qty
    new_total = old_total + (curr_p * add_qty)
    new_avg = new_total / (my_qty + add_qty)
    
    # 탈출 기간 단축
    m_div = d['div']
    if m_div > 0:
        old_w = my_avg / m_div
        new_w = new_avg / m_div
        saved = old_w - new_w
    else:
        old_w, new_w, saved = 0, 0, 0
        
    render_html(f"""
        <div class="calc-card-bg">
            <div style="font-size:0.9rem; color:#666; margin-bottom:8px;">평단가 변화</div>
            <div style="font-size:1.3rem; font-weight:700; display:flex; align-items:center; gap:8px;">
                ${my_avg:.2f} <span style="color:#ccc;">➔</span> <span style="color:#3182f6;">${new_avg:.2f}</span>
            </div>
            <div style="background:#f0f8ff; border-radius:12px; padding:12px; margin-top:16px;">
                <div style="font-size:0.85rem; color:#3182f6; font-weight:600;">🚀 탈출 기간 단축</div>
                <div style="font-size:1rem; font-weight:700; color:#1a2980; margin-top:4px;">
                    {old_w:.1f}주 ➔ {new_w:.1f}주 <span style="color:#00c853;">(-{saved:.1f}주 단축)</span>
                </div>
            </div>
        </div>
        <div class="caution-box">
            <span class="caution-header">📌 계산 기준</span>
            • 추가 매수는 현재가 <b>${curr_p:.2f}</b> 체결 가정<br>
            • 배당금 <b>${m_div:.4f}</b> 유지 시 단순 시뮬레이션입니다.
        </div>
    """)

# [탭3] 스트레스 테스트
with tabs[2]:
    s_qty = st.number_input("보유 수량", min_value=100, value=1000, step=100, key="str_qty")
    base_pay = s_qty * div_krw_net
    
    render_html(f"""
        <div class="calc-card-bg">
            <div class="calc-row" style="background:#f8f9fa; padding:8px; border-radius:8px;">
                <span class="calc-label">⚡ 현재 유지</span>
                <span class="calc-val" style="color:#3182f6;">{base_pay:,.0f}원</span>
            </div>
            <div class="calc-row">
                <span class="calc-label">📉 -10% 삭감</span>
                <span class="calc-val">{base_pay*0.9:,.0f}원</span>
            </div>
            <div class="calc-row">
                <span class="calc-label">📉 -30% 삭감</span>
                <span class="calc-val">{base_pay*0.7:,.0f}원</span>
            </div>
            <div class="calc-row">
                <span class="calc-label" style="color:#e92c2c;">📉 -50% 삭감</span>
                <span class="calc-val" style="color:#e92c2c;">{base_pay*0.5:,.0f}원</span>
            </div>
        </div>
        <div class="caution-box">
            <span class="caution-header">📌 계산 기준</span>
            • <b>세후(15.4% 공제)</b> 금액 기준입니다.<br>
            • 배당 삭감 시나리오를 미리 확인하여 리스크를 관리하세요.
        </div>
    """)

# [탭4] 원금회수 (BEP)
with tabs[3]:
    bep_price = st.number_input("내 평단가($)", min_value=0.1, value=curr_p, step=0.1, format="%.2f", key="bep_p")
    if d['div'] > 0:
        w_need = bep_price / d['div']
        m_need = w_need / 4.3
    else:
        w_need, m_need = 0, 0
        
    render_html(f"""
        <div class="calc-card-bg" style="text-align:center;">
            <div style="font-size:0.9rem; color:#666; margin-bottom:8px;">원금 회수(Free Ride)까지</div>
            <div style="font-size:2rem; font-weight:900; color:#e92c2c; letter-spacing:-1px;">
                {w_need:.1f}주 <span style="font-size:1rem; color:#999; font-weight:500;">(약 {m_need:.1f}개월)</span>
            </div>
            <div style="margin-top:12px; font-size:0.85rem; color:#d32f2f; background:#fff0f2; padding:8px; border-radius:8px;">
                💡 <b>{w_need:.0f}번</b>만 배당 받으면 본전입니다!
            </div>
        </div>
        <div class="caution-box">
            <span class="caution-header">📌 계산 기준</span>
            • 현재 배당금 <b>${d['div']:.4f}</b>가 앞으로도 동일하게 지급된다는 가정입니다.<br>
            • 실제 회수 기간은 배당금 변동에 따라 달라질 수 있습니다.
        </div>
    """)

# [탭5] FIRE (주간 목표)
with tabs[4]:
    target = st.number_input("목표 '주간' 배당금 (만원)", min_value=10, value=50, step=10)
    if div_krw_net > 0:
        req_shares = math.ceil((target*10000) / div_krw_net)
        req_money = req_shares * curr_p * usd_krw
    else:
        req_shares, req_money = 0, 0
        
    render_html(f"""
        <div class="calc-card-bg">
            <div style="text-align:center; margin-bottom:16px;">
                <div style="font-size:0.9rem; color:#666;">매주 <b style="color:#3182f6;">{target}만원</b> 받으려면?</div>
            </div>
            <div style="display:flex; justify-content:space-around; align-items:center;">
                <div style="text-align:center;">
                    <div style="font-size:0.8rem; color:#888;">필요 주식</div>
                    <div style="font-size:1.2rem; font-weight:800; color:#333;">{req_shares:,}주</div>
                </div>
                <div style="width:1px; height:30px; background:#eee;"></div>
                <div style="text-align:center;">
                    <div style="font-size:0.8rem; color:#888;">예상 투자금</div>
                    <div style="font-size:1.2rem; font-weight:800; color:#3182f6;">{req_money/10000:,.0f}만원</div>
                </div>
            </div>
        </div>
        <div class="caution-box">
            <span class="caution-header">📌 계산 기준</span>
            • 환율 {usd_krw:,.0f}원 / 현재가 ${curr_p:.2f} 기준<br>
            • 세후 배당금을 기준으로 역산한 결과입니다.
        </div>
    """)

# [탭6] 스노우볼
with tabs[5]:
    snow_shares = st.number_input("현재 보유 수량", min_value=1, value=1000, step=10, key="snow_s")
    
    # 1. 이번주 받을 돈 (세후)
    this_pay = snow_shares * div_krw_net
    # 2. 재투자 가능 수량
    re_price = curr_p * usd_krw
    if re_price > 0:
        add_cnt = math.floor(this_pay / re_price)
        rem_cash = this_pay - (add_cnt * re_price)
        next_inc = add_cnt * div_krw_net
    else:
        add_cnt, rem_cash, next_inc = 0, 0, 0
        
    render_html(f"""
        <div class="calc-card-bg" style="background:linear-gradient(135deg, #e3f2fd 0%, #fff 100%);">
            <div style="text-align:center; margin-bottom:10px;">
                <span style="font-size:0.9rem; color:#555;">이번 배당금으로</span><br>
                <span style="font-size:1.5rem; font-weight:900; color:#1565c0;">+{add_cnt}주</span>
                <span style="font-size:1rem; font-weight:700;"> 추가 매수!</span>
            </div>
            <div style="background:white; border-radius:12px; padding:12px; text-align:center; border:1px solid #bbdefb;">
                <div style="font-size:0.8rem; color:#888;">다음 주 늘어나는 배당금</div>
                <div style="font-size:1.1rem; font-weight:800; color:#1565c0;">+{next_inc:,.0f}원 🆙</div>
            </div>
            <div style="text-align:center; font-size:0.75rem; color:#999; margin-top:8px;">
                (남는 돈 {rem_cash:,.0f}원은 간식비 ☕)
            </div>
        </div>
        <div class="caution-box">
            <span class="caution-header">📌 계산 기준</span>
            • 재투자 단가: <b>${curr_p:.2f}</b> (현재가)<br>
            • 배당금이 유지된다고 가정했을 때의 복리 효과입니다.
        </div>
    """)

# 4. 용어 설명
st.write("")
with st.expander("🎓 주린이 용어 가이드"):
    render_html("""
    <div style="padding:10px; font-size:0.85rem; line-height:1.6; color:#555;">
        <p><b>1️⃣ Distribution Rate (분배율)</b><br>
        이번 배당금을 1년 내내 똑같이 준다고 가정했을 때의 연 수익률입니다.</p>
        <p><b>2️⃣ 30-Day SEC Yield</b><br>
        최근 30일간 펀드가 실제로 벌어들인 이자 수익(펀더멘털)입니다.</p>
        <p><b>3️⃣ ROC (Return of Capital)</b><br>
        <span style="color:#e92c2c;">⚠️ 중요!</span> 펀드가 번 돈이 아니라, <b>투자 원금을 깎아서</b> 배당으로 준 비율입니다.</p>
    </div>
    """)
