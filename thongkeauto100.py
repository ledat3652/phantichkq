import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from collections import Counter
from itertools import permutations, combinations
import re

# --- CẤU HÌNH ---
st.set_page_config(layout="centered", page_title="XOSO V45")

# CSS: CƯỠNG ÉP NẰM NGANG TRÊN MOBILE
st.markdown("""
<style>
    /* 1. Ép tất cả các cột (st.columns) phải nằm trên 1 hàng, không được xuống dòng */
    div[data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 5px !important;
        overflow-x: auto !important; /* Nếu bé quá thì cho trượt ngang chứ ko xuống dòng */
        align-items: center !important; /* Căn giữa theo chiều dọc */
    }
    
    /* 2. Cho phép các cột co nhỏ tối đa */
    div[data-testid="column"] {
        width: auto !important;
        flex: 1 1 auto !important;
        min-width: 10px !important;
    }

    /* 3. Tinh chỉnh ô nhập liệu và nút bấm bé lại để vừa màn hình */
    .stTextInput input { 
        font-size: 12px; 
        padding: 2px 5px; 
        height: 36px; 
        min-height: 36px; 
    }
    .stButton button { 
        font-size: 11px; 
        padding: 0px; 
        height: 36px; 
        min-height: 36px;
        width: 100%;
        line-height: 1;
    }
    
    /* 4. Giảm khoảng cách thừa thãi */
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    h1 { margin-bottom: 0px; font-size: 1.2rem; text-align: center; color: #c0392b; }
    p { margin-bottom: 0px; }
</style>
""", unsafe_allow_html=True)

st.title("📱 XSMB V45")

# --- SESSION ---
if 'lotos' not in st.session_state: st.session_state.lotos = ""
if 'prizes' not in st.session_state: st.session_state.prizes = ""
if 'status' not in st.session_state: st.session_state.status = ""
if 'ghep_res' not in st.session_state: st.session_state.ghep_res = ""

# ==============================================================================
# 1. TẢI DỮ LIỆU (1 Dòng ngang)
# ==============================================================================
c1, c2 = st.columns([2, 1]) # Tỷ lệ 2:1
with c1:
    date_input = st.date_input("D", datetime.now(), label_visibility="collapsed")
with c2:
    if st.button("📥 TẢI"):
        try:
            d_str = date_input.strftime('%d-%m-%Y')
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
                else: st.error("Thiếu số")
            else: st.error("Lỗi Web")
        except: st.error("Lỗi mạng")

if st.session_state.status: st.caption(st.session_state.status)

with st.expander("📂 Dữ liệu thô"):
    st.text_area("Loto", st.session_state.lotos)
    st.text_area("Full", st.session_state.prizes)

# ==============================================================================
# 2. THỐNG KÊ (Bắt buộc ngang)
# ==============================================================================
if st.session_state.lotos:
    clean = re.sub(r'(\d+)\s*\(\s*(\d+)\s*\)', lambda m: (m.group(1)+" ")*int(m.group(2)), st.session_state.lotos)
    nums = [n for n in re.findall(r'\d+', clean) if len(n)>=2]
    if nums:
        tails = Counter([n[-1] for n in nums])
        heads = Counter([n[-2] for n in nums])
        # Dùng markdown table cho gọn
        txt = f"```text\n{'ĐUÔI':<12}| {'ĐẦU'}\n" + "-"*25 + "\n"
        for t, f in tails.most_common():
            h_f = heads.get(t, 0)
            txt += f"Đuôi {t}: {f:<4}| Đầu {t}: {h_f}\n" 
        txt += "```"
        st.markdown(txt)

# ==============================================================================
# 3. GHÉP 3 CÀNG (ÉP 1 DÒNG: CÀNG - DÀN - NÚT - KQ)
# ==============================================================================
st.markdown("### 🔗 GHÉP 3 CÀNG")

# Chia 4 cột với tỷ lệ cực nhỏ để nhét vừa 1 dòng điện thoại
# C1: Càng (15%) | C2: Dàn (30%) | C3: Nút (15%) | C4: KQ (40%)
c1, c2, c3, c4 = st.columns([1.5, 3, 1.5, 4], gap="small")

with c1:
    cang = st.text_input("C", placeholder="C", label_visibility="collapsed")
with c2:
    dan = st.text_input("D", placeholder="Dàn", label_visibility="collapsed")
with c3:
    if st.button("GO"):
        if cang and len(dan) >= 2:
            res = [f"{cang}{p[0]}{p[1]}" for p in combinations(list(dan), 2)]
            st.session_state.ghep_res = " ".join(res)
        else:
            st.session_state.ghep_res = "Lỗi"
with c4:
    st.text_input("K", value=st.session_state.ghep_res, placeholder="KQ", label_visibility="collapsed", disabled=True)

# ==============================================================================
# 4. SOI CẦU
# ==============================================================================
st.markdown("### 🔍 SOI CẦU")
q = st.text_input("Soi", placeholder="Nhập số...", label_visibility="collapsed")

if q and st.session_state.prizes:
    clean = re.sub(r'(\d+)\s*\(\s*(\d+)\s*\)', lambda m: (m.group(1)+" ")*int(m.group(2)), st.session_state.lotos)
    nums = [n for n in re.findall(r'\d+', clean) if len(n)>=2]
    T = Counter([n[-1] for n in nums])
    H = Counter([n[-2] for n in nums])
    
    check = set()
    for c in re.findall(r'\d+', q):
        if len(c)==2: check.add(c)
        elif len(c)==3: [check.add("".join(p)) for p in permutations(c,2)]
        elif len(c)>3: [check.add(c[i:i+2]) for i in range(len(c)-1)]
    
    full = [p for p in re.findall(r'\d+', st.session_state.prizes) if len(p)>=2]
    res = []
    for pair in check:
        sc = (T.get(pair[1],0)*2) + H.get(pair[0],0)
        fnd = []
        ok = False
        for p in full:
            if pair in p:
                idx = p.find(pair)
                pos = "Đuôi" if idx==len(p)-2 else ("Đầu" if idx==0 else "Giữa")
                if len(p)==2: pos="Loto"
                fnd.append(f"{p}({pos})")
                ok = True
        res.append({'p': pair, 's': sc, 'ok': ok, 'f': fnd})
    
    res.sort(key=lambda x: x['s'], reverse=True)
    
    for r in res:
        icon = "✅" if r['ok'] else "❌"
        bg = "#d4edda" if r['ok'] else "#f8d7da"
        st.markdown(f"""
        <div style="background:{bg};padding:5px;border-radius:5px;margin-bottom:5px;font-size:13px;">
        <b>{icon} {r['p']}</b> (Đ:{r['s']})<br>
        <span style="font-family:monospace;font-size:11px;">{', '.join(r['f']) if r['ok'] else ''}</span>
        </div>""", unsafe_allow_html=True)
