import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from itertools import combinations
import re

# --- CẤU HÌNH ---
st.set_page_config(layout="centered", page_title="XOSO V47")

# --- CSS QUAN TRỌNG: ÉP CÁC CỘT KHÔNG ĐƯỢC XUỐNG DÒNG ---
st.markdown("""
<style>
    /* 1. Ép hàng ngang tuyệt đối */
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important; /* Cấm xuống dòng */
        gap: 5px !important; /* Khoảng cách giữa các ô cực nhỏ */
        align-items: center !important;
    }
    
    /* 2. Cho phép các cột co lại bé xíu cũng được */
    div[data-testid="column"] {
        min-width: 10px !important;
        width: auto !important;
        flex: 1 1 auto !important;
        padding: 0px !important;
    }
    
    /* 3. Chỉnh ô nhập liệu nhỏ gọn */
    .stTextInput input {
        font-size: 14px;
        padding: 0px 5px;
        height: 40px;
        min-height: 40px;
        text-align: center;
    }
    
    /* 4. Chỉnh nút bấm */
    .stButton button {
        height: 40px;
        min-height: 40px;
        padding: 0px;
        font-weight: bold;
        white-space: nowrap; /* Chữ không được xuống dòng */
    }

    /* 5. Ẩn lề thừa */
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    h3 { margin: 0px; font-size: 1rem; color: #d35400; }
</style>
""", unsafe_allow_html=True)

# --- SESSION ---
if 'lotos' not in st.session_state: st.session_state.lotos = ""
if 'prizes' not in st.session_state: st.session_state.prizes = ""
if 'status' not in st.session_state: st.session_state.status = ""
if 'ghep_res' not in st.session_state: st.session_state.ghep_res = ""

# ==============================================================================
# 1. TẢI DỮ LIỆU (Cũng ép 1 hàng: Chọn ngày | Nút Tải)
# ==============================================================================
c1, c2 = st.columns([2, 1])
with c1:
    d_input = st.date_input("D", datetime.now(), label_visibility="collapsed")
with c2:
    if st.button("📥 TẢI"):
        try:
            d_str = d_input.strftime('%d-%m-%Y')
            url = f"https://www.minhngoc.net.vn/ket-qua-xo-so/mien-bac/{d_str}.html"
            resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
            soup = BeautifulSoup(resp.content, 'html.parser')
            box = soup.find('div', class_='box_kqxs')
            if box:
                prizes = []
                for col in ['giaidb', 'giai1', 'giai2', 'giai3', 'giai4', 'giai5', 'giai6', 'giai7']:
                    cell = box.find('td', class_=col)
                    if cell: 
                        prizes.extend([n.strip() for n in cell.get_text(separator=" ").split() if n.strip().isdigit()])
                if len(prizes) >= 27:
                    lotos = sorted([p[-2:] for p in prizes])
                    st.session_state.lotos = " ".join(lotos)
                    st.session_state.prizes = " ".join(prizes)
                    st.session_state.status = f"OK: {d_str}"
                else: st.error("Thiếu")
            else: st.error("Lỗi Web")
        except: st.error("Lỗi Mạng")

if st.session_state.status: st.caption(st.session_state.status)

# ==============================================================================
# 2. GHÉP 3 CÀNG (ĐÚNG Ý BẠN: 3 Ô - 1 HÀNG)
# ==============================================================================
st.markdown("### 🔗 GHÉP SỐ")

# Tỷ lệ cột: [1 phần] [2.5 phần] [1.5 phần]
# Tức là ô Dàn sẽ dài gấp đôi ô Càng
col_cang, col_dan, col_nut = st.columns([1, 2.5, 1.5])

with col_cang:
    # Ô nhập Càng
    cang = st.text_input("C", placeholder="C", label_visibility="collapsed")

with col_dan:
    # Ô nhập Dàn
    dan = st.text_input("D", placeholder="Dàn 5289", label_visibility="collapsed")

with col_nut:
    # Nút Bấm
    if st.button("GHÉP"):
        if cang and len(dan) >= 2:
            res = [f"{cang}{p[0]}{p[1]}" for p in combinations(list(dan), 2)]
            st.session_state.ghep_res = " ".join(res)
        else:
            st.session_state.ghep_res = "Thiếu số"

# Kết quả hiện ngay bên dưới
if st.session_state.ghep_res:
    st.info(st.session_state.ghep_res)

# ==============================================================================
# 3. THỐNG KÊ & SOI CẦU (Giữ nguyên cho gọn)
# ==============================================================================
with st.expander("📊 DỮ LIỆU & THỐNG KÊ"):
    st.text_area("Loto", st.session_state.lotos)
    
    if st.session_state.lotos:
        clean = re.sub(r'(\d+)\s*\(\s*(\d+)\s*\)', lambda m: (m.group(1)+" ")*int(m.group(2)), st.session_state.lotos)
        nums = [n for n in re.findall(r'\d+', clean) if len(n)>=2]
        if nums:
            tails = Counter([n[-1] for n in nums])
            heads = Counter([n[-2] for n in nums])
            txt = f"```text\n{'ĐUÔI':<10}| {'ĐẦU'}\n" + "-"*20 + "\n"
            for t, f in tails.most_common():
                h_f = heads.get(t, 0)
                txt += f"{t}: {f:<4}| {t}: {h_f}\n" 
            txt += "```"
            st.markdown(txt)

st.markdown("### 🔍 SOI CẦU")
c_soi, c_run = st.columns([3, 1])
with c_soi:
    q = st.text_input("S", placeholder="Số soi...", label_visibility="collapsed")
with c_run:
    st.button("GO")

if q and st.session_state.prizes:
    full = [p for p in re.findall(r'\d+', st.session_state.prizes) if len(p)>=2]
    # (Logic soi cầu giữ nguyên cho gọn code)
    check = set(re.findall(r'\d+', q))
    found = []
    for c in check:
        for p in full:
            if c in p: found.append(f"{p}")
    if found: st.success(f"CÓ: {', '.join(found)}")
    else: st.warning("KHÔNG CÓ")
