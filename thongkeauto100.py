import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from collections import Counter
from itertools import permutations, combinations
import re

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(layout="wide", page_title="XOSO PRO WEB")

# CSS để chỉnh font chữ to như bạn thích
st.markdown("""
<style>
    .big-font { font-size:20px !important; font-weight: bold; font-family: 'Courier New', monospace; }
    .header-style { font-size:24px; font-weight: bold; color: #c0392b; text-align: center; }
    textarea { font-size: 14px !important; font-family: 'Courier New', monospace !important; }
    .stCode { font-size: 16px !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="header-style">HỆ THỐNG PHÂN TÍCH DỮ LIỆU (WEB VERSION)</p>', unsafe_allow_html=True)

# --- KHỞI TẠO SESSION STATE (Để lưu dữ liệu không bị mất khi bấm nút) ---
if 'lotos' not in st.session_state: st.session_state.lotos = ""
if 'prizes' not in st.session_state: st.session_state.prizes = ""
if 'status' not in st.session_state: st.session_state.status = ""

# ==============================================================================
# 1. KHUNG CRAWL DỮ LIỆU
# ==============================================================================
with st.container():
    c1, c2, c3 = st.columns([1, 1, 3])
    with c1:
        date_input = st.date_input("Chọn ngày", datetime.now())
    with c2:
        st.write("") # Căn lề
        st.write("") 
        if st.button("🚀 TẢI DỮ LIỆU", type="primary"):
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
                        st.session_state.status = f"✅ Đã tải xong ngày {d_str}"
                    else:
                        st.error(f"Thiếu dữ liệu ({len(prizes)} số).")
                else:
                    st.error("Lỗi: Không tìm thấy bảng kết quả.")
            except Exception as e:
                st.error(f"Lỗi kết nối: {e}")
    with c3:
        st.write("")
        st.write("")
        if st.session_state.status:
            st.success(st.session_state.status)

# ==============================================================================
# 2. KHUNG NHẬP LIỆU (NHỎ GỌN)
# ==============================================================================
col1, col2 = st.columns(2)
with col1:
    st.markdown("**1. INPUT FREQUENCY**")
    input_loto = st.text_area("Loto", value=st.session_state.lotos, height=100, label_visibility="collapsed")
with col2:
    st.markdown("**2. SOURCE DB**")
    input_db = st.text_area("Source DB", value=st.session_state.prizes, height=100, label_visibility="collapsed")

# ==============================================================================
# 3. DISTRIBUTION METRICS (FONT TO)
# ==============================================================================
st.markdown("---")
st.markdown("**DISTRIBUTION METRICS (X/Y Analysis):**")

if input_loto:
    # Xử lý text
    clean_text = re.sub(r'(\d+)\s*\(\s*(\d+)\s*\)', lambda m: (m.group(1) + " ") * int(m.group(2)), input_loto)
    nums = [n for n in re.findall(r'\d+', clean_text) if len(n) >= 2]
    
    if nums:
        tails = Counter([n[-1] for n in nums])
        heads = Counter([n[-2] for n in nums])
        
        # Vẽ biểu đồ Text
        chart = f"{'SUFFIX (ĐUÔI)':<40} | {'PREFIX (ĐẦU)'}\n" + "-" * 85 + "\n"
        for t_num, t_freq in tails.most_common():
            h_freq = heads.get(t_num, 0)
            bar_t = "█" * t_freq
            bar_h = "█" * h_freq
            chart += f"Đuôi {t_num}: {t_freq} lần {bar_t:<15} | Đầu {t_num}: {h_freq} lần {bar_h}\n"
        
        # Hiển thị font to
        st.markdown(f"```text\n{chart}\n```")

# ==============================================================================
# 4. GHÉP 3 CÀNG
# ==============================================================================
st.markdown("---")
st.markdown("**GHÉP 3 CÀNG (NHANH)**")
with st.container():
    c1, c2, c3, c4 = st.columns([1, 2, 1, 4])
    with c1:
        cang = st.text_input("Càng", max_chars=1, placeholder="VD: 7")
    with c2:
        dan = st.text_input("Ghép với", placeholder="VD: 5289")
    with c3:
        st.write("") # Spacer align button
        if st.button("CHẠY GHÉP"):
            if cang and len(dan) >= 2:
                lst = list(dan)
                combs = list(combinations(lst, 2))
                res = [f"{cang}{p[0]}{p[1]}" for p in combs]
                st.session_state.ghep_res = " ".join(res)
    with c4:
        res_val = st.session_state.get('ghep_res', '')
        st.text_input("KẾT QUẢ:", value=res_val)

# ==============================================================================
# 5. SOI CẦU (CHI TIẾT START/MID/END)
# ==============================================================================
st.markdown("---")
st.markdown("**SOI CẦU (Query ID)**")
query = st.text_input("Nhập số cần soi", placeholder="VD: 97 749", key="q_input")

if st.button("SOI NGAY") and query and input_db:
    # 1. Phân tích số nhập vào
    raw_chunks = re.findall(r'\d+', query)
    check_list = set()
    display_str = []
    
    for chunk in raw_chunks:
        if len(chunk) == 2:
            check_list.add(chunk); display_str.append(chunk)
        elif len(chunk) == 3:
            perms = ["".join(p) for p in permutations(chunk, 2)]
            for p in perms: check_list.add(p)
            display_str.append(f"{chunk}(Perm)")
        elif len(chunk) > 3:
            pairs = [chunk[i:i + 2] for i in range(len(chunk) - 1)]
            for p in pairs: check_list.add(p)
            display_str.append(f"{chunk}(Seq)")

    # 2. Tính toán
    # Lấy lại data sạch
    clean_loto = re.sub(r'(\d+)\s*\(\s*(\d+)\s*\)', lambda m: (m.group(1) + " ") * int(m.group(2)), input_loto)
    loto_nums = [n for n in re.findall(r'\d+', clean_loto) if len(n) >= 2]
    tails = Counter([n[-1] for n in loto_nums])
    heads = Counter([n[-2] for n in loto_nums])
    
    full_prizes = [p for p in re.findall(r'\d+', input_db) if len(p) >= 2]
    
    results = []
    for pair in check_list:
        score = (tails.get(pair[1], 0) * 2) + heads.get(pair[0], 0)
        
        found_info = []
        is_found = False
        for prize in full_prizes:
            if pair in prize:
                idx = prize.find(pair)
                if len(prize) == 2: pos = "Loto"
                elif idx == len(prize) - 2: pos = "End"
                elif idx == 0: pos = "Start"
                else: pos = "Mid"
                found_info.append(f"{prize} ({pos})")
                is_found = True
        
        results.append({'pair': pair, 'score': score, 'found': is_found, 'prizes': found_info})

    results.sort(key=lambda x: x['score'], reverse=True)

    # 3. Hiển thị kết quả
    st.info(f"QUERY ID: {', '.join(display_str)}")
    
    final_out = ""
    for item in results:
        status = f"MATCHED: {', '.join(item['prizes'])}" if item['found'] else "NO MATCH"
        final_out += f"ID {item['pair']} | {status:<55} | Score: {item['score']}\n"
    
    st.markdown(f"```text\n{final_out}\n```")
