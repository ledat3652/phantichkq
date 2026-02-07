import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from collections import Counter
from itertools import permutations, combinations
import re

# --- CẤU HÌNH TRANG WEB (Mobile Friendly) ---
st.set_page_config(layout="centered", page_title="XOSO MOBILE")

# CSS Tinh chỉnh: Font chữ to, nút bấm to
st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    h1 { font-size: 1.5rem !important; text-align: center; color: #c0392b; }
    h3 { font-size: 1.1rem !important; margin-top: 10px; margin-bottom: 5px; }
    .stButton button { width: 100%; border-radius: 8px; font-weight: bold; }
    
    /* Chỉnh font trong khung code to rõ hơn cho điện thoại */
    .stCode { font-size: 14px !important; font-family: 'Courier New', monospace !important; }
</style>
""", unsafe_allow_html=True)

st.title("📱 XSMB MOBILE PRO")

# --- SESSION STATE ---
if 'lotos' not in st.session_state: st.session_state.lotos = ""
if 'prizes' not in st.session_state: st.session_state.prizes = ""
if 'status' not in st.session_state: st.session_state.status = ""

# ==============================================================================
# 1. CRAWL DỮ LIỆU (Gọn gàng)
# ==============================================================================
with st.container():
    col1, col2 = st.columns([2, 1])
    with col1:
        date_input = st.date_input("Ngày", datetime.now(), label_visibility="collapsed")
    with col2:
        if st.button("📥 TẢI"):
            try:
                d_str = date_input.strftime('%d-%m-%Y')
                url = f"https://www.minhngoc.net.vn/ket-qua-xo-so/mien-bac/{d_str}.html"
                headers = {'User-Agent': 'Mozilla/5.0'}
                resp = requests.get(url, headers=headers, timeout=5)
                soup = BeautifulSoup(resp.content, 'html.parser')
                box = soup.find('div', class_='box_kqxs')
                if box:
                    prizes = []
                    for col in ['giaidb', 'giai1', 'giai2', 'giai3', 'giai4', 'giai5', 'giai6', 'giai7']:
                        cell = box.find('td', class_=col)
                        if cell: 
                            raw = cell.get_text(separator=" ")
                            nums = [n.strip() for n in raw.split() if n.strip().isdigit()]
                            prizes.extend(nums)
                    if len(prizes) >= 27:
                        lotos = sorted([p[-2:] for p in prizes])
                        st.session_state.lotos = " ".join(lotos)
                        st.session_state.prizes = " ".join(prizes)
                        st.session_state.status = f"✅ Xong: {d_str}"
                    else: st.error("Thiếu số!")
                else: st.error("Lỗi Web!")
            except Exception as e: st.error("Lỗi mạng!")

if st.session_state.status:
    st.caption(st.session_state.status)

# ==============================================================================
# 2. DỮ LIỆU ĐẦU VÀO (Ẩn gọn)
# ==============================================================================
with st.expander("📂 Xem dữ liệu thô"):
    st.text_area("Loto", value=st.session_state.lotos, height=80)
    st.text_area("Full Giải", value=st.session_state.prizes, height=80)

# ==============================================================================
# 3. BIỂU ĐỒ (LUÔN NẰM NGANG - FIXED LAYOUT)
# ==============================================================================
st.markdown("### 📊 THỐNG KÊ (Đầu/Đuôi)")

if st.session_state.lotos:
    # Xử lý text
    clean_text = re.sub(r'(\d+)\s*\(\s*(\d+)\s*\)', lambda m: (m.group(1) + " ") * int(m.group(2)), st.session_state.lotos)
    nums = [n for n in re.findall(r'\d+', clean_text) if len(n) >= 2]
    
    if nums:
        tails = Counter([n[-1] for n in nums])
        heads = Counter([n[-2] for n in nums])
        
        # --- TẠO BẢNG TEXT ĐỂ ÉP NẰM NGANG ---
        # Tính toán để in ra từng dòng
        chart_text = f"{'ĐUÔI (SUFFIX)':<18} | {'ĐẦU (PREFIX)'}\n"
        chart_text += "-" * 38 + "\n"
        
        # Sắp xếp theo số lượng (nhiều nhất lên đầu)
        sorted_tails = tails.most_common()
        
        for t_num, t_freq in sorted_tails:
            h_freq = heads.get(t_num, 0)
            
            # Vẽ thanh bar ngắn gọn lại chút cho vừa màn hình điện thoại
            # Dùng ký tự block ngắn hơn nếu cần, nhưng ở đây giữ nguyên
            bar_t = "█" * t_freq
            bar_h = "█" * h_freq
            
            # Format dòng: Đuôi bên trái | Đầu bên phải
            # Cắt ngắn khoảng cách đệm (<18) để vừa màn hình mobile dọc
            left_part = f"Đuôi {t_num}: {t_freq} {bar_t}"
            right_part = f"Đầu {t_num}: {h_freq} {bar_h}"
            
            chart_text += f"{left_part:<18} | {right_part}\n"
            
        # Hiển thị bằng st.code -> Luôn giữ format ngang
        st.code(chart_text, language="text")

# ==============================================================================
# 4. GHÉP 3 CÀNG
# ==============================================================================
st.markdown("### 🔗 GHÉP 3 CÀNG")
with st.container():
    c1, c2 = st.columns([1, 2])
    with c1: cang = st.text_input("Càng", placeholder="VD: 7")
    with c2: dan = st.text_input("Dàn ghép", placeholder="VD: 5289")
    
    if st.button("⚡ TẠO DÀN"):
        if cang and len(dan) >= 2:
            lst = list(dan)
            combs = list(combinations(lst, 2))
            res = [f"{cang}{p[0]}{p[1]}" for p in combs]
            st.success(" ".join(res))
        else:
            st.warning("Nhập đủ thông tin")

# ==============================================================================
# 5. SOI CẦU
# ==============================================================================
st.markdown("### 🔍 SOI CẦU")
query = st.text_input("Nhập số cần soi", placeholder="VD: 97 749")

if query and st.session_state.prizes:
    # Logic soi
    clean_loto = re.sub(r'(\d+)\s*\(\s*(\d+)\s*\)', lambda m: (m.group(1) + " ") * int(m.group(2)), st.session_state.lotos)
    loto_nums = [n for n in re.findall(r'\d+', clean_loto) if len(n) >= 2]
    tails = Counter([n[-1] for n in loto_nums])
    heads = Counter([n[-2] for n in loto_nums])
    
    raw_chunks = re.findall(r'\d+', query)
    check_list = set()
    for chunk in raw_chunks:
        if len(chunk) == 2: check_list.add(chunk)
        elif len(chunk) == 3: [check_list.add("".join(p)) for p in permutations(chunk, 2)]
        elif len(chunk) > 3: [check_list.add(chunk[i:i + 2]) for i in range(len(chunk) - 1)]

    full_prizes = [p for p in re.findall(r'\d+', st.session_state.prizes) if len(p) >= 2]
    results = []
    
    for pair in check_list:
        score = (tails.get(pair[1], 0) * 2) + heads.get(pair[0], 0)
        found_info = []
        is_found = False
        for prize in full_prizes:
            if pair in prize:
                idx = prize.find(pair)
                pos = "Đuôi" if idx == len(prize) - 2 else ("Đầu" if idx == 0 else "Giữa")
                if len(prize) == 2: pos = "Loto"
                found_info.append(f"{prize}({pos})")
                is_found = True
        results.append({'pair': pair, 'score': score, 'found': is_found, 'prizes': found_info})

    results.sort(key=lambda x: x['score'], reverse=True)

    for item in results:
        bg_color = "rgba(46, 204, 113, 0.2)" if item['found'] else "rgba(231, 76, 60, 0.1)"
        emoji = "✅" if item['found'] else "❌"
        
        st.markdown(f"""
        <div style="background-color: {bg_color}; padding: 10px; border-radius: 5px; margin-bottom: 5px;">
            <strong>{emoji} SỐ {item['pair']}</strong> (Điểm: {item['score']})<br>
            <span style="font-family: monospace; font-size: 0.9em;">
            {', '.join(item['prizes']) if item['found'] else 'Không có trong bảng KQ'}
            </span>
        </div>
        """, unsafe_allow_html=True)
