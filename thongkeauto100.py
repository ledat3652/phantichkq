import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from collections import Counter
from itertools import permutations, combinations
import re

# --- CẤU HÌNH ---
st.set_page_config(layout="centered", page_title="XOSO MOBILE V43-MOD")

# CSS: Tinh chỉnh khoảng cách cho siêu gọn (Giữ nguyên bản cũ)
st.markdown("""
<style>
    .block-container { padding-top: 0.5rem; padding-bottom: 2rem; }
    h1 { font-size: 1.2rem !important; text-align: center; color: #c0392b; margin-bottom: 0px; }
    h3 { font-size: 1rem !important; margin-top: 10px; margin-bottom: 5px; color: #2980b9; }
    .stButton button { width: 100%; padding: 0px 5px; min-height: 0px; height: 38px; }
    .stTextInput input { padding: 5px; font-size: 14px; }
    div[data-testid="stExpander"] div[role="button"] p { font-size: 14px; font-weight: bold; }
    .css-1544g2n { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

st.title("📱 XSMB MOBILE PRO")

# --- SESSION ---
if 'lotos' not in st.session_state: st.session_state.lotos = ""
if 'prizes' not in st.session_state: st.session_state.prizes = ""
if 'status' not in st.session_state: st.session_state.status = ""
if 'ghep_res' not in st.session_state: st.session_state.ghep_res = ""

# ==============================================================================
# 1. TẢI DỮ LIỆU (DÒNG 1)
# ==============================================================================
c_date, c_btn = st.columns([2, 1])
with c_date:
    date_input = st.date_input("D", datetime.now(), label_visibility="collapsed")
with c_btn:
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
                    st.session_state.status = f"✅ OK: {d_str}"
                else: st.error("Thiếu số")
            else: st.error("Lỗi Web")
        except: st.error("Lỗi mạng")

if st.session_state.status: st.caption(st.session_state.status)

with st.expander("📂 Dữ liệu thô"):
    st.text_area("Loto", st.session_state.lotos)
    st.text_area("Full", st.session_state.prizes)

# ==============================================================================
# 2. THỐNG KÊ NGANG (DÒNG 2)
# ==============================================================================
if st.session_state.lotos:
    clean = re.sub(r'(\d+)\s*\(\s*(\d+)\s*\)', lambda m: (m.group(1)+" ")*int(m.group(2)), st.session_state.lotos)
    nums = [n for n in re.findall(r'\d+', clean) if len(n)>=2]
    if nums:
        tails = Counter([n[-1] for n in nums])
        heads = Counter([n[-2] for n in nums])
        txt = f"{'ĐUÔI':<15}| {'ĐẦU'}\n" + "-"*30 + "\n"
        for t, f in tails.most_common():
            h_f = heads.get(t, 0)
            txt += f"Đuôi {t}: {f:<5}| Đầu {t}: {h_f}\n" # Bỏ thanh bar cho gọn dòng
        st.code(txt, language="text")

# ==============================================================================
# 3. SOI CẦU (CHUYỂN LÊN TRÊN GHÉP SỐ)
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
        <div style="background:{bg};padding:5px;border-radius:5px;margin-bottom:5px;font-size:14px;">
        <b>{icon} {r['p']}</b> (Điểm: {r['s']})<br>
        <span style="font-family:monospace;font-size:12px;">{', '.join(r['f']) if r['ok'] else ''}</span>
        </div>""", unsafe_allow_html=True)

# ==============================================================================
# 4. GHÉP 3 CÀNG (ĐÃ CHUYỂN XUỐNG DƯỚI CÙNG)
# ==============================================================================
st.markdown("### 🔗 GHÉP 3 CÀNG")

# DÒNG 1: INPUT CÀNG | INPUT DÀN | NÚT BẤM
c1, c2, c3 = st.columns([1, 2, 1], gap="small")
with c1:
    cang = st.text_input("C", placeholder="Càng", label_visibility="collapsed")
with c2:
    dan = st.text_input("D", placeholder="Dàn ghép", label_visibility="collapsed")
with c3:
    if st.button("GHÉP"):
        if cang and len(dan) >= 2:
            res = [f"{cang}{p[0]}{p[1]}" for p in combinations(list(dan), 2)]
            st.session_state.ghep_res = " ".join(res)
        else: st.session_state.ghep_res = "Thiếu số!"

# DÒNG 2: KẾT QUẢ
if st.session_state.ghep_res:
    st.info(st.session_state.ghep_res)
