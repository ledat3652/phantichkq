import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from collections import Counter
from itertools import permutations, combinations
import re

# --- CẤU HÌNH ---
st.set_page_config(layout="centered", page_title="XOSO V46")

# CSS: TẠO GIAO DIỆN KIỂU "Ô VUÔNG" (CARD)
st.markdown("""
<style>
    /* Thu gọn lề trên dưới */
    .block-container { padding-top: 1rem; padding-bottom: 5rem; max-width: 600px; }
    
    /* Style cho các nút bấm và ô nhập */
    .stButton button { width: 100%; border-radius: 5px; font-weight: bold; }
    .stTextInput input { text-align: center; font-weight: bold; }
    
    /* Tạo khung viền cho các khu vực (Card Style) */
    .css-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    h3 { margin-top: 0px; font-size: 1rem; color: #444; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: #d35400;'>📱 TOOL SOI CẦU PRO</h2>", unsafe_allow_html=True)

# --- SESSION ---
if 'lotos' not in st.session_state: st.session_state.lotos = ""
if 'prizes' not in st.session_state: st.session_state.prizes = ""
if 'status' not in st.session_state: st.session_state.status = ""
if 'ghep_res' not in st.session_state: st.session_state.ghep_res = ""

# ==============================================================================
# 1. KHUNG TẢI DỮ LIỆU (Đóng khung lại)
# ==============================================================================
with st.container(border=True):
    c1, c2 = st.columns([2, 1])
    with c1:
        date_input = st.date_input("Ngày", datetime.now(), label_visibility="collapsed")
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
                        st.session_state.status = f"✅ Đã tải: {d_str}"
                    else: st.error("Thiếu số")
                else: st.error("Lỗi Web")
            except: st.error("Lỗi mạng")
    
    if st.session_state.status:
        st.caption(st.session_state.status)
    
    with st.expander("👁️ Xem dữ liệu"):
        st.text_area("Loto", st.session_state.lotos, height=60)
        st.text_area("Full", st.session_state.prizes, height=60)

# ==============================================================================
# 2. GHÉP 3 CÀNG (KIỂU Ô VUÔNG COMPACT)
# ==============================================================================
# Thay vì trải dài, ta đóng nó vào 1 cái hộp (Container Border)
with st.container(border=True):
    st.markdown("### 🔗 GHÉP 3 CÀNG")
    
    # Hàng 1: Càng (Nhỏ) - Dàn (Lớn)
    c1, c2 = st.columns([1, 2.5])
    with c1:
        cang = st.text_input("C", placeholder="Càng", label_visibility="collapsed")
    with c2:
        dan = st.text_input("D", placeholder="Nhập dàn ghép...", label_visibility="collapsed")
    
    # Hàng 2: Nút bấm (To, Dài hết khổ)
    if st.button("⚡ BẤM ĐỂ GHÉP", type="primary"):
        if cang and len(dan) >= 2:
            res = [f"{cang}{p[0]}{p[1]}" for p in combinations(list(dan), 2)]
            st.session_state.ghep_res = " ".join(res)
        else:
            st.session_state.ghep_res = "⚠️ Nhập Càng & Dàn (2 số+)"
            
    # Hàng 3: Kết quả (Nổi bật)
    if st.session_state.ghep_res:
        st.success(f"**KQ:** {st.session_state.ghep_res}")

# ==============================================================================
# 3. THỐNG KÊ (KIỂU BẢNG)
# ==============================================================================
with st.container(border=True):
    st.markdown("### 📊 THỐNG KÊ")
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
    else:
        st.info("Chưa có dữ liệu")

# ==============================================================================
# 4. SOI CẦU (KIỂU Ô VUÔNG)
# ==============================================================================
with st.container(border=True):
    st.markdown("### 🔍 SOI CẦU")
    # Hàng 1: Ô nhập + Nút (Nằm cùng dòng cho gọn)
    c_soi, c_btn = st.columns([3, 1])
    with c_soi:
        q = st.text_input("S", placeholder="Số cần soi...", label_visibility="collapsed")
    with c_btn:
        run_soi = st.button("GO")

    if run_soi and q and st.session_state.prizes:
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
        
        st.write("---")
        for r in res:
            icon = "✅" if r['ok'] else "❌"
            color = "green" if r['ok'] else "red"
            st.markdown(f":{color}[**{icon} {r['p']}**] (Đ:{r['s']})  \n`{', '.join(r['f']) if r['ok'] else ''}`")
