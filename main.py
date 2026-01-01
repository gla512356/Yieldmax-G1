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
# [핵심] HTML 공백 제거 함수
# ---------------------------------------------------------
def render_html(raw_html):
    cleaned = " ".join([line.strip() for line in raw_html.splitlines() if line.strip()])
    st.markdown(cleaned, unsafe_allow_html=True)

# ---------------------------------------------------------
# [스타일] CSS (프리미엄 UI/UX + 탭 최적화)
# ---------------------------------------------------------
render_html("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    /* 1. 기본 세팅 */
    html, body, [class*="css"] {
        font-family: 'Pretendard', sans-serif;
        background-color: #f4f6f8;
        color: #1b1e26;
    }

    /* 2. 헤더 카드 */
    .header-card {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        padding: 32px 24px;
        border-radius: 28px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 15px 35px rgba(15, 32, 39, 0.25);
        position: relative;
        overflow: hidden;
    }
    .header-card::after {
        content: ''; position: absolute; top: -50%; right: -20%;
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    /* 환율 배지 */
    .fx-badge {
        background: rgba(255, 255, 255, 0.1);
        padding: 6px 12px;
        border-radius: 12px;
        font-size: 0.8rem; font-weight: 500;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.15);
        display: inline-flex; align-items: center; gap: 6px;
        margin-bottom: 8px;
    }

    /* 마켓 상태 배지 */
    .market-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-bottom: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }

    .status-open { background-color: #00e676; color: #003300; animation: pulse 2s infinite; }
    .status-pre { background-color: #ffea00; color: #3e2723; }
    .status-after { background-color: #d1c4e9; color: #4527a0; }
    .status-closed { background-color: #cfd8dc; color: #455a64; }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(0, 230, 118, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(0, 230, 118, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 230, 118, 0); }
    }

    /* 3. 타임라인 */
    .timeline-container { display: flex; gap: 10px; margin-top: 28px; }
    .glass-box {
        flex: 1; text-align: center;
        background: rgba(255,255,255,0.08);
        padding: 12px; border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(5px);
    }
    .t-label { font-size: 0.75rem; color: rgba(255,255,255,0.7); margin-bottom: 4px; }
    .t-val { font-size: 0.95rem; font-weight: 700; color: #fff; }
    .accent-gold { color: #ffd700; }

    /* 4. 정보 카드 */
    .info-card { background: white; border-radius: 24px; padding: 28px 24px; box-shadow: 0 8px 20px rgba(0,0,0,0.04); border: 1px solid #ffffff; margin-bottom: 20px; }

    /* 5. 메트릭 그리드 */
    .metric-container { display: flex; gap: 12px; margin-top: 24px; }
    .metric-box { flex: 1; background: #f9fafb; border-radius: 16px; padding: 16px 8px; text-align: center; border: 1px solid #edf0f5; transition: all 0.2s; }
    .metric-box:hover { background: #f0f4ff; border-color: #dbe4ff; transform: translateY(-2px); }
    .m-title { font-size: 0.7rem; color: #8b95a1; font-weight: 600; margin-bottom: 6px; }
    .m-data { font-size: 1rem; font-weight: 800; color: #333; }

    /* 6. 각종 카드 스타일 */
    .calc-box { background: #f8f9fa; border-radius: 20px; padding: 24px; margin-top: 10px; border: 1px solid #edf0f5; }
    .fire-card { background: linear-gradient(135deg, #fff 0%, #f3f6ff 100%); border: 1px solid #dcebfb; border-radius: 24px; padding: 24px; margin-top: 10px; box-shadow: 0 4px 12px rgba(49, 130, 246, 0.08); text-align: center; }
    .bep-card { background: linear-gradient(135deg, #fff 0%, #fff8f8 100%); border: 1px solid #ffebee; border-radius: 24px; padding: 24px; margin-top: 10px; box-shadow: 0 4px 12px rgba(233, 44, 44, 0.05); text-align: center; }
    .snow-card { background: linear-gradient(135deg, #e3f2fd 0%, #f1f8ff 100%); border: 1px solid #bbdefb; border-radius: 24px; padding: 24px; margin-top: 10px; box-shadow: 0 4px 12px rgba(33, 150, 243, 0.1); text-align: center; }
    .stress-card { background: #fff; border: 1px solid #eee; border-radius: 20px; padding: 20px; margin-top: 10px; }
    .mul-card { background: #fff; border: 1px solid #e0e0e0; border-radius: 20px; padding: 20px; margin-top: 10px; }

    /* 유틸리티 */
    .result-row { display: flex; justify-content: space-between; margin-bottom: 12px; align-items: center; }
    .result-label { font-size: 0.9rem; color: #6b7684; }
    .result-val { font-weight: 700; color: #333; }
    .result-total { font-size: 1.5rem; font-weight: 800; color: #3182f6; }
    .mul-arrow { font-size: 1.2rem; color: #bbb; margin: 0 8px; }
    .mul-highlight { color: #3182f6; font-weight: 800; }
    .stress-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #f5f5f5; }
    .stress-row:last-child { border-bottom: none; }
    .stress-label { font-size: 0.9rem; color: #666; font-weight: 600; }
    .stress-val { font-size: 1rem; font-weight: 700; color: #333; }
    .stress-badge { font-size: 0.75rem; padding: 3px 8px; border-radius: 6px; background: #eee; color: #666; margin-right: 8px; }

    .caution-box { margin-top: 15px; padding: 14px; background: #fafafa; border-radius: 12px; border: 1px dashed #d1d6db; text-align: left; font-size: 0.8rem; color: #666; line-height: 1.6; }
    .caution-title { font-weight: 700; color: #4e5968; margin-bottom: 4px; display: block; }

    /* 뱃지 */
    .ticker-tag { background: #e8f3ff; color: #3182f6; padding: 4px 10px; border-radius: 8px; font-weight: 800; font-size: 0.9rem; }
    .risk-badge-high { background: #fff0f2; color: #e92c2c; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }
    .risk-badge-low { background: #e3fcf2; color: #00bfa5; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }

    /* 버튼 & 탭 */
    div.stButton > button { width: 100%; border-radius: 12px; font-weight: 700; background-color: #ffffff; border: 1px solid #e5e8eb; color: #4e5968; padding: 0.5rem 1rem; transition: all 0.2s; }
    div.stButton > button:hover { background-color: #f2f4f6; color: #191f28; border-color: #c5cdd6; }

    /* 탭 메뉴 스크롤 가능하게 (모바일 대응) */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; overflow-x: auto; white-space: nowrap; -webkit-overflow-scrolling: touch; padding-bottom: 4px; }
    .stTabs [data-baseweb="tab"] { height: 46px; background-color: #fff; border-radius: 10px; border: 1px solid #eee; gap: 0; padding: 0 14px; font-size: 0.85rem; flex-shrink: 0; }
    .stTabs [aria-selected="true"] { background-color: #eef4ff; border-color: #3182f6; color: #3182f6; font-weight: 700; }
    </style>
""")

# ---------------------------------------------------------
# [데이터]
# ---------------------------------------------------------
SCHEDULE_KST = {
    "buy_limit": "12/31(수) 06:00",
    "ex_date": "12/31(수)",
    "pay_date": "1/2(금) 밤"
}

DATA_MAP = {
    'CHPY': {'div': 0.4401, 'rate': 40.59, 'sec': 0.00, 'roc': 99.47, 'name': 'Semiconductor Income'},
    'FEAT': {'div': 0.3415, 'rate': 69.07, 'sec': 69.57,'roc': 60.49, 'name': 'Dorsey Wright Featured 5'},
    'FIVY': {'div': 0.2507, 'rate': 41.55, 'sec': 37.98,'roc': 60.37, 'name': 'Dorsey Wright Hybrid 5'},
    'GPTY': {'div': 0.2565, 'rate': 30.99, 'sec': 0.00, 'roc': 0.00,  'name': 'AI & Tech Portfolio'},
    'LFGY': {'div': 0.2481, 'rate': 50.04, 'sec': 0.00, 'roc': 0.00,  'name': 'Crypto Industry & Tech'},
    'QDTY': {'div': 0.1494, 'rate': 17.70, 'sec': 0.20, 'roc': 0.00,  'name': 'Nasdaq 100 0DTE'},
    'RDTY': {'div': 0.2049, 'rate': 26.63, 'sec': 1.15, 'roc': 0.00,  'name': 'R2000 0DTE'},
    'SDTY': {'div': 0.1240, 'rate': 14.37, 'sec': 0.13, 'roc': 0.00,  'name': 'S&P 500 0DTE'},
    'SLTY': {'div': 0.3947, 'rate': 60.13, 'sec': 2.05, 'roc': 95.76, 'name': 'Ultra Short Option'},
    'ULTY': {'div': 0.4866, 'rate': 65.97, 'sec': 0.00, 'roc': 0.00,  'name': 'Ultra Option Strategy'},
    'YMAG': {'div': 0.0992, 'rate': 35.86, 'sec': 59.29,'roc': 59.48, 'name': 'Magnificent 7 Fund'},
    'YMAX': {'div': 0.1060, 'rate': 53.95, 'sec': 85.99,'roc': 59.11, 'name': 'Universe Fund'},
}

# -----------------------------
# [함수] 마켓 상태 체크
# -----------------------------
def get_us_market_status():
    ny_tz = pytz.timezone('America/New_York')
    now_ny = datetime.now(ny_tz)

    if now_ny.weekday() >= 5: 
        return "⛔ 휴장 (주말)", "status-closed"

    holidays_2025 = [
        "2025-01-01", "2025-01-20", "2025-02-17", "2025-04-18", 
        "2025-05-26", "2025-06-19", "2025-07-04", "2025-09-01", 
        "2025-11-27", "2025-12-25"
    ]
    if now_ny.strftime("%Y-%m-%d") in holidays_2025:
        return "⛔ 휴장 (공휴일)", "status-closed"

    minutes = now_ny.hour * 60 + now_ny.minute
    if 240 <= minutes < 570:
        return "🌅 프리마켓 진행 중", "status-pre"
    elif 570 <= minutes < 960:
        return "🔥 정규장 오픈 (실시간)", "status-open"
    elif 960 <= minutes < 1200:
        return "🌙 애프터마켓 진행 중", "status-after"
    else:
        return "💤 장 마감 (휴장)", "status-closed"

# -----------------------------
# [함수] 데이터 연결 (15초 갱신)
# -----------------------------
@st.cache_data(ttl=15, show_spinner=False)
def get_market_info(ticker_keys):
    try:
        fx = yf.Ticker("USDKRW=X").history(period="1d")["Close"].iloc[-1]
    except:
        fx = 1430.0

    prices = {}
    try:
        t_str = " ".join(ticker_keys)
        data = yf.download(t_str, period="1d", progress=False)['Close']
        for t in ticker_keys:
            try:
                val = data[t].iloc[-1] if isinstance(data, pd.DataFrame) else data[t]
                prices[t] = float(val)
            except:
                prices[t] = 0.0
    except:
        pass

    now_time = datetime.now(pytz.timezone('Asia/Seoul')).strftime("%H:%M:%S")
    return fx, prices, now_time

# -----------------------------
# [로직] 데이터 로딩
# -----------------------------
if st.button("🔄 실시간 시세 새로고침"):
    st.cache_data.clear()

with st.spinner("미국 현지 데이터 수신 중..."):
    t_list = sorted(list(DATA_MAP.keys()))
    usd_krw, price_map, update_time = get_market_info(t_list)
    market_text, market_class = get_us_market_status()

tax_rate = 0.154

# -----------------------------
# [UI] 1. 메인 헤더
# -----------------------------
render_html(f"""
    <div class="header-card">
        <div style="display:flex; justify-content:space-between; align-items:start;">
            <div>
                <span class="market-badge {market_class}">{market_text}</span>
                <h2 style="margin:0; font-size:1.6rem; font-weight:800; letter-spacing:-0.5px;">
                    YieldMax 그룹 1<br>최신 배당 내역
                </h2>
            </div>
            <div style="text-align:right;">
                <div class="fx-badge">
                    1 USD = {usd_krw:,.2f}원
                </div>
                <div style="font-size:0.75rem; margin-top:4px; opacity:0.8;">
                    기준: {update_time} (KST)
                </div>
            </div>
        </div>

        <div class="timeline-container">
            <div class="glass-box">
                <div class="t-label">🚨 매수마감(한국)</div>
                <div class="t-val accent-gold">{SCHEDULE_KST['buy_limit']}</div>
            </div>
            <div class="glass-box">
                <div class="t-label">📉 배당락일</div>
                <div class="t-val">{SCHEDULE_KST['ex_date']}</div>
            </div>
            <div class="glass-box">
                <div class="t-label">💰 지급일(예정)</div>
                <div class="t-val" style="color:#69f0ae;">{SCHEDULE_KST['pay_date']}</div>
            </div>
        </div>
    </div>
""")

# -----------------------------
# [UI] 2. 상세 정보
# -----------------------------
st.markdown("### 💎 종목별 상세 분석")

col_sel, _ = st.columns([1, 0.01])
with col_sel:
    def_idx = t_list.index("ULTY") if "ULTY" in t_list else 0
    sel_ticker = st.selectbox("분석할 ETF 선택", t_list, index=def_idx)

# 데이터
d = DATA_MAP[sel_ticker]
curr_p = price_map.get(sel_ticker, 0.0)
div_krw = d['div'] * usd_krw
div_krw_net = div_krw * (1 - tax_rate)

if d['roc'] > 50:
    analysis_badge = "<span class='risk-badge-high'>🔥 초고위험 공격형</span>"
elif d['roc'] > 0:
    analysis_badge = "<span class='risk-badge-high'>⚠️ 고수익 추구형</span>"
else:
    analysis_badge = "<span class='risk-badge-low'>🛡️ 건전 배당형</span>"

render_html(f"""
    <div class="info-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
            <div style="display:flex; align-items:center; gap:12px;">
                <span class="ticker-tag">{sel_ticker}</span>
                {analysis_badge}
            </div>
            <span style="font-size:0.8rem; color:#888;">{d['name']}</span>
        </div>

        <div style="text-align:center; padding: 10px 0 20px 0;">
            <div style="font-size:0.9rem; color:#8b95a1; margin-bottom:6px;">1주당 확정 배당금</div>
            <div style="font-size:2.6rem; font-weight:900; color:#191f28; letter-spacing:-1px; line-height:1;">
                ${d['div']:.4f}
            </div>
            <div style="font-size:1.1rem; font-weight:700; color:#3182f6; margin-top:10px;">
                ≈ {div_krw:,.0f}원 <span style="font-size:0.9rem; font-weight:500; color:#adb5bd;">(세전)</span>
                <span style="margin:0 8px; color:#e0e0e0;">|</span>
                <span style="color:#2196f3;">{div_krw_net:,.0f}원 <span style="font-size:0.8rem; font-weight:500; color:#888;">(세후)</span></span>
            </div>
        </div>

        <div class="metric-container">
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

        <div style="text-align:right; font-size:0.8rem; color:#adb5bd; margin-top:16px;">
            현재 주가 ${curr_p:.2f} 기준
        </div>
    </div>
""")

# -----------------------------
# [UI] 3. 멀티 탭 기능 (6개 통합)
# -----------------------------
st.write("")
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🧮 배당금", "💧 물타기", "🧪 스트레스", "📉 원금회수", "🔥 FIRE", "⛄ 스노우볼"
])

# --- 탭1: 계산기 ---
with tab1:
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.write("") 
        shares = st.number_input("보유 수량(주)", min_value=1, value=1000, step=10, key="shares_cal")
    with col2:
        total_krw_before = shares * div_krw
        total_krw_after = total_krw_before * (1 - tax_rate)
        render_html(f"""
            <div class="calc-box">
                <div class="result-row">
                    <span class="result-label">총 배당금(세전)</span>
                    <span class="result-val">{total_krw_before:,.0f}원</span>
                </div>
                <div class="result-row">
                    <span class="result-label">세금(15.4%)</span>
                    <span class="result-val" style="color:#e92c2c;">-{total_krw_before*tax_rate:,.0f}원</span>
                </div>
                <div style="border-top:1px dashed #c5cdd6; margin: 12px 0;"></div>
                <div class="result-row">
                    <span class="result-label" style="font-weight:700; color:#3182f6;">실제 입금액</span>
                    <span class="result-total">{total_krw_after:,.0f}원</span>
                </div>
            </div>
            <div class="caution-box">
                <span class="caution-title">📌 계산 기준</span>
                • 환율: <b>{usd_krw:,.2f}원</b> (실시간) / 세율: <b>15.4%</b> (배당소득세)<br>
                • 이번 주 배당금 <b>${d['div']:.4f}</b> 기준으로 계산되었습니다.
            </div>
        """)

# --- 탭2: 물타기 계산기 ---
with tab2:
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        my_avg = st.number_input("내 평단가 ($)", min_value=0.1, value=curr_p*1.1, step=0.1, format="%.2f")
    with col_m2:
        my_qty = st.number_input("현재 보유 수량", min_value=1, value=100, step=10)
    add_qty = st.number_input("추가 매수 수량 (주)", min_value=1, value=50, step=10)

    total_cost_old = my_avg * my_qty
    total_cost_new = total_cost_old + (curr_p * add_qty)
    total_qty_new = my_qty + add_qty
    new_avg = total_cost_new / total_qty_new

    monthly_div = d['div'] 
    if monthly_div > 0:
        old_weeks = my_avg / monthly_div
        new_weeks = new_avg / monthly_div
        saved_weeks = old_weeks - new_weeks
    else:
        old_weeks = 0
        new_weeks = 0
        saved_weeks = 0

    render_html(f"""
        <div class="mul-card">
            <div style="font-size:0.9rem; color:#666; margin-bottom:8px;">평단가 변화</div>
            <div style="font-size:1.4rem; font-weight:700; color:#333; display:flex; align-items:center;">
                ${my_avg:.2f} <span class="mul-arrow">➔</span> <span class="mul-highlight">${new_avg:.2f}</span>
            </div>
            <div style="margin-top:15px; padding:12px; background:#e3f2fd; border-radius:12px;">
                <div style="font-size:0.9rem; color:#1565c0;">🚀 탈출(원금회수) 기간 단축 효과</div>
                <div style="font-size:1.1rem; font-weight:700; color:#0d47a1; margin-top:4px;">
                    {old_weeks:.1f}주 ➔ {new_weeks:.1f}주 <span style="color:#2e7d32;">(-{saved_weeks:.1f}주 단축!)</span>
                </div>
            </div>
        </div>
        <div class="caution-box">
            <span class="caution-title">📌 계산 기준</span>
            • 추가 매수는 <b>현재가 ${curr_p:.2f}</b>에 체결된다고 가정했습니다.<br>
            • 배당금 <b>${monthly_div:.4f}</b>가 유지될 경우의 단순 시뮬레이션입니다.
        </div>
    """)

# --- 탭3: 스트레스 테스트 ---
with tab3:
    stress_shares = st.number_input("내 보유 수량", min_value=1, value=1000, step=10, key="stress_shares")
    base_div = d['div'] * usd_krw * (1 - tax_rate) # 세후
    current_pay = stress_shares * base_div
    cut_10 = current_pay * 0.9
    cut_30 = current_pay * 0.7
    cut_50 = current_pay * 0.5

    render_html(f"""
        <div class="stress-card">
            <div class="stress-row" style="background:#f9f9f9; border-radius:8px; padding:10px;">
                <span class="stress-label">⚡ 현재 유지 시</span>
                <span class="stress-val" style="color:#3182f6;">{current_pay:,.0f}원</span>
            </div>
            <div class="stress-row">
                <span class="stress-label"><span class="stress-badge">📉 -10% 삭감</span></span>
                <span class="stress-val">{cut_10:,.0f}원</span>
            </div>
            <div class="stress-row">
                <span class="stress-label"><span class="stress-badge">📉 -30% 삭감</span></span>
                <span class="stress-val">{cut_30:,.0f}원</span>
            </div>
            <div class="stress-row">
                <span class="stress-label"><span class="stress-badge" style="background:#ffebee; color:#c62828;">📉 -50% 삭감</span></span>
                <span class="stress-val" style="color:#c62828;">{cut_50:,.0f}원</span>
            </div>
        </div>
        <div class="caution-box">
            <span class="caution-title">📌 계산 기준</span>
            • <b>세후(15.4% 공제)</b> 금액 기준입니다.<br>
            • 실제 지급액은 환율 및 배당금 변동에 따라 차이가 있을 수 있습니다.
        </div>
    """)

# --- 탭4: BEP ---
with tab4:
    my_price = st.number_input(f"내 평단가 ($)", min_value=0.1, value=curr_p, step=0.1, format="%.2f", key="bep_price")
    monthly_div = d['div'] 

    if monthly_div > 0:
        weeks_needed = my_price / monthly_div
        months_needed = weeks_needed / 4.3
        render_html(f"""
            <div class="bep-card">
                <div style="color:#555; font-size:0.9rem; margin-bottom:8px;">원금 회수(Free Ride)까지</div>
                <div style="font-size:2rem; font-weight:900; color:#e92c2c; margin-bottom:8px;">
                    {weeks_needed:.1f}주 <span style="font-size:1rem; color:#888; font-weight:500;">(약 {months_needed:.1f}개월)</span>
                </div>
                <div style="background:#fff0f2; padding:10px; border-radius:12px; font-size:0.85rem; color:#d63031;">
                    💡 <b>{weeks_needed:.0f}번</b>만 배당을 더 받으면 원금 회수 완료!
                </div>
            </div>
            <div class="caution-box">
                <span class="caution-title">📌 계산 기준</span>
                • 현재 {sel_ticker} 배당금 <b>${monthly_div:.4f}</b> 기준으로 계산되었습니다.<br>
                • <b>"다음 주에도 배당금이 똑같이 나온다면"</b>을 가정한 결과입니다.
            </div>
        """)

# --- 탭5: 주간 FIRE ---
with tab5:
    weekly_div_net = div_krw * (1 - tax_rate)
    target_money = st.number_input("목표 '주간' 배당금 (만원)", min_value=10, value=50, step=10, key="fire_target")
    target_krw = target_money * 10000

    if weekly_div_net > 0:
        needed_shares = math.ceil(target_krw / weekly_div_net)
        needed_capital = needed_shares * curr_p * usd_krw
    else:
        needed_shares = 0
        needed_capital = 0

    render_html(f"""
        <div class="fire-card">
            <div style="font-size:1.1rem; font-weight:700; color:#191f28; margin-bottom:15px;">
                매주 <span style="color:#3182f6; font-size:1.4rem;">{target_money:,}만원</span> 받기
            </div>
            <div style="display:flex; justify-content:center; align-items:center; gap:20px; margin-top:20px;">
                <div>
                    <div style="font-size:0.85rem; color:#888; margin-bottom:4px;">필요 주식 수</div>
                    <div style="font-size:1.4rem; font-weight:900; color:#333;">{needed_shares:,}주</div>
                </div>
                <div style="width:1px; height:40px; background:#e5e8eb;"></div>
                <div>
                    <div style="font-size:0.85rem; color:#888; margin-bottom:4px;">예상 투자금</div>
                    <div style="font-size:1.4rem; font-weight:900; color:#3182f6;">{needed_capital/10000:,.0f}만원</div>
                </div>
            </div>
        </div>
        <div class="caution-box">
            <span class="caution-title">📌 계산 기준</span>
            • 환율: <b>{usd_krw:,.2f}원</b> / 현재 주가: <b>${curr_p:.2f}</b><br>
            • 이번 주 배당금 <b>${d['div']:.4f}</b>가 매주 지속된다고 가정한 결과입니다.
        </div>
    """)

# --- 탭6: 스노우볼 (통합됨) ---
with tab6:
    my_shares = st.number_input("현재 보유 주식 수", min_value=1, value=1000, step=10, key="snow_shares_tab")
    weekly_div_net = div_krw * (1 - tax_rate)
    current_weekly_pay = my_shares * weekly_div_net
    share_price_krw = curr_p * usd_krw

    if share_price_krw > 0:
        reinvest_shares = math.floor(current_weekly_pay / share_price_krw)
        leftover_cash = current_weekly_pay - (reinvest_shares * share_price_krw)
        next_week_increase = reinvest_shares * weekly_div_net

        render_html(f"""
            <div class="snow-card">
                <div style="margin-bottom:15px;">
                    <span style="font-size:0.9rem; color:#555;">이번 주 배당금으로</span><br>
                    <span style="font-size:1.6rem; font-weight:900; color:#2196f3;">+{reinvest_shares}주</span>
                    <span style="font-size:1.1rem; font-weight:700; color:#333;"> 추가 매수 가능!</span>
                </div>
                <div style="background:white; border-radius:12px; padding:15px; border:1px solid #e3f2fd;">
                    <div style="font-size:0.9rem; color:#888;">그럼 다음 주 내 배당금은?</div>
                    <div style="font-size:1.3rem; font-weight:800; color:#191f28; margin-top:4px;">
                        {current_weekly_pay:,.0f}원 <span style="color:#2196f3;">(+{next_week_increase:,.0f}원)</span>
                    </div>
                </div>
            </div>
            <div class="caution-box">
                <span class="caution-title">📌 계산 기준</span>
                • 재투자 주가: <b>${curr_p:.2f}</b> / 배당금 유지 가정<br>
                • 남는 차액 {leftover_cash:,.0f}원은 제외하고 계산되었습니다.
            </div>
        """)

# -----------------------------
# [UI] 5. 용어 설명
# -----------------------------
st.write("")
with st.expander("🎓 주린이를 위한 용어 가이드"):
    render_html("""
    <div style="background:#f2f4f6; padding:16px; border-radius:12px; font-size:0.9rem; line-height:1.6; color:#4e5968;">
        <div style="margin-bottom:12px;">
            <strong style="color:#191f28;">1️⃣ Distribution Rate (분배율)</strong><br>
            이번 배당금을 1년 내내 똑같이 준다고 가정했을 때의 단순 연 수익률입니다.
        </div>
        <div style="margin-bottom:12px;">
            <strong style="color:#191f28;">2️⃣ 30-Day SEC Yield (실질 수익률)</strong><br>
            최근 30일간 펀드가 <b>실제로 번 이자 수익</b>입니다. 이 수치가 높을수록 펀드 자체가 돈을 잘 벌고 있다는 뜻입니다.
        </div>
        <div>
            <strong style="color:#191f28;">3️⃣ ROC (Return of Capital, 원금 반환)</strong><br>
            <span style="color:#e92c2c;">⚠️ 주의!</span> 펀드가 번 돈이 아니라, <b>내 원금을 깎아서 배당으로 돌려주는 비율</b>입니다.
        </div>
    </div>
    """)
