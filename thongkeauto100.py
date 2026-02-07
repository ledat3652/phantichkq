import tkinter as tk
from tkinter import messagebox
import re
import os
import datetime
from collections import Counter
from itertools import permutations, combinations
import threading

# --- KIỂM TRA THƯ VIỆN CRAWL ---
try:
    import requests
    from bs4 import BeautifulSoup

    has_crawl_lib = True
except ImportError:
    has_crawl_lib = False

# --- CẤU HÌNH WORD ---
try:
    from docx import Document
    from docx.shared import Pt

    has_word_lib = True
except ImportError:
    has_word_lib = False


class ToolXoSoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DATA ANALYTICS PRO - SYSTEM V41.0 (RESTORED QUERY FORMAT)")
        self.root.geometry("1300x980")

        # Font cấu hình chung
        self.font_label = ("Arial", 10, "bold")
        self.font_input = ("Arial", 11)

        # --- TIÊU ĐỀ ---
        tk.Label(root, text="HỆ THỐNG PHÂN TÍCH DỮ LIỆU", font=("Arial", 18, "bold"), fg="#c0392b").pack(pady=5)

        # =========================================================================
        # 1. KHUNG AUTO CRAWL
        # =========================================================================
        top_frame = tk.Frame(root)
        top_frame.pack(fill="x", padx=10, pady=5)

        crawl_frame = tk.Frame(top_frame)
        crawl_frame.pack(side="left")

        tk.Label(crawl_frame, text="Ngày (dd/mm/yyyy):", font=self.font_input).pack(side="left", padx=(0, 5))

        self.entry_date = tk.Entry(crawl_frame, font=self.font_input, width=12)
        self.entry_date.insert(0, datetime.datetime.now().strftime("%d/%m/%Y"))
        self.entry_date.pack(side="left", padx=5)

        if has_crawl_lib:
            tk.Button(crawl_frame, text="TẢI DỮ LIỆU", command=self.run_crawl_thread,
                      bg="#27ae60", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=5)

        self.lbl_status = tk.Label(crawl_frame, text="Ready", fg="blue", font=("Arial", 9, "italic"))
        self.lbl_status.pack(side="left", padx=5)

        # =========================================================================
        # 2. KHUNG NHẬP LIỆU (NHỎ GỌN - 4 DÒNG)
        # =========================================================================
        raw_frame = tk.Frame(root)
        raw_frame.pack(pady=5, padx=10, fill="both")

        # --- CỘT TRÁI: INPUT FREQUENCY ---
        frame_col1 = tk.LabelFrame(raw_frame, text="1. INPUT FREQUENCY", font=("Arial", 10, "bold"), fg="#2c3e50")
        frame_col1.pack(side="left", fill="both", expand=True, padx=5)

        toolbar1 = tk.Frame(frame_col1)
        toolbar1.pack(fill="x", padx=2, pady=2)
        tk.Button(toolbar1, text="DÁN", command=lambda: self.paste_text(self.raw_text_1), bg="#34495e", fg="white",
                  width=6, font=("Arial", 8, "bold")).pack(side="left")
        tk.Button(toolbar1, text="XÓA", command=lambda: self.raw_text_1.delete(1.0, tk.END), bg="#e74c3c", fg="white",
                  width=6, font=("Arial", 8, "bold")).pack(side="right")

        self.raw_text_1 = tk.Text(frame_col1, height=4, width=45, font=("Courier New", 11))
        self.raw_text_1.pack(fill="both", expand=True, padx=2, pady=2)

        # --- CỘT GIỮA: NÚT UPDATE ---
        btn_frame = tk.Frame(raw_frame, bg="#e67e22")
        btn_frame.pack(side="left", fill="y", padx=5)
        tk.Button(btn_frame, text=">>>\n\nCẬP\nNHẬT\n\n<<<", command=self.manual_update_stats,
                  bg="#e67e22", fg="white", font=("Arial", 10, "bold"), width=6, relief="flat").pack(fill="both",
                                                                                                     expand=True)

        # --- CỘT PHẢI: SOURCE DB ---
        frame_col2 = tk.LabelFrame(raw_frame, text="2. SOURCE DB", font=("Arial", 10, "bold"), fg="#2c3e50")
        frame_col2.pack(side="left", fill="both", expand=True, padx=5)

        toolbar2 = tk.Frame(frame_col2)
        toolbar2.pack(fill="x", padx=2, pady=2)
        tk.Button(toolbar2, text="DÁN", command=lambda: self.paste_text(self.raw_text_2), bg="#34495e", fg="white",
                  width=6, font=("Arial", 8, "bold")).pack(side="left")
        tk.Button(toolbar2, text="XÓA", command=lambda: self.raw_text_2.delete(1.0, tk.END), bg="#e74c3c", fg="white",
                  width=6, font=("Arial", 8, "bold")).pack(side="right")

        self.raw_text_2 = tk.Text(frame_col2, height=4, width=45, font=("Courier New", 11))
        self.raw_text_2.pack(fill="both", expand=True, padx=2, pady=2)

        # =========================================================================
        # 3. DISTRIBUTION METRICS (FONT SIZE 20)
        # =========================================================================
        tk.Label(root, text="DISTRIBUTION METRICS (X/Y Analysis):", font=("Arial", 10, "bold"), anchor="w",
                 fg="#2980b9").pack(fill="x", padx=10, pady=(5, 0))

        self.text_stats_display = tk.Text(root, height=12, font=("Courier New", 20, "bold"), bg="#fdfefe")
        self.text_stats_display.pack(padx=10, pady=2, fill='x')

        # =========================================================================
        # 4. GHÉP 3 CÀNG
        # =========================================================================
        ghep_frame = tk.LabelFrame(root, text="Merge", font=("Arial", 10, "bold"), fg="#8e44ad")
        ghep_frame.pack(fill="x", padx=10, pady=5)

        inner_ghep = tk.Frame(ghep_frame)
        inner_ghep.pack(fill="x", padx=5, pady=5)

        tk.Label(inner_ghep, text="Càng:", font=self.font_label).pack(side="left")
        self.entry_cang = tk.Entry(inner_ghep, font=self.font_input, width=5, justify="center")
        self.entry_cang.pack(side="left", padx=5)

        tk.Label(inner_ghep, text="Ghép:", font=self.font_label).pack(side="left", padx=(10, 0))
        self.entry_dan = tk.Entry(inner_ghep, font=self.font_input, width=15)
        self.entry_dan.pack(side="left", padx=5)

        tk.Button(inner_ghep, text="GHÉP", command=self.thuc_hien_ghep_so,
                  bg="#8e44ad", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=10)

        tk.Label(inner_ghep, text="KẾT QUẢ:", font=self.font_label).pack(side="left", padx=(10, 0))
        self.entry_ket_qua_ghep = tk.Entry(inner_ghep, font=("Arial", 11, "bold"), fg="black")
        self.entry_ket_qua_ghep.pack(side="left", padx=5, fill="x", expand=True)

        # =========================================================================
        # 5. SOI CẦU (ĐÃ SỬA LẠI FORMAT TIẾNG ANH & CHI TIẾT)
        # =========================================================================
        soi_frame = tk.LabelFrame(root, text="Nhập 3 số cần xem", font=("Arial", 10, "bold"), fg="#27ae60")
        soi_frame.pack(fill="x", padx=10, pady=5)

        inner_soi = tk.Frame(soi_frame)
        inner_soi.pack(fill="x", padx=5, pady=5)

        self.entry_user_nums = tk.Entry(inner_soi, font=("Arial", 14))
        self.entry_user_nums.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_user_nums.bind("<Return>", lambda event: self.check_manual())

        tk.Button(inner_soi, text="SOI NGAY", command=self.check_manual,
                  bg="#27ae60", fg="white", font=("Arial", 10, "bold"), width=12).pack(side="right")

        self.text_result = tk.Text(root, height=8, font=("Courier New", 12))
        self.text_result.pack(padx=10, pady=5, fill='both', expand=True)

        # BIẾN DỮ LIỆU
        self.stats_heads = Counter()
        self.stats_tails = Counter()
        self.full_prizes = []
        self.has_data_1 = False
        self.has_data_2 = False

    # =========================================================================
    # HÀM LOGIC
    # =========================================================================
    def thuc_hien_ghep_so(self):
        cang = self.entry_cang.get().strip()
        dan = self.entry_dan.get().strip()
        if not cang or len(dan) < 2: return
        list_dan = list(dan)
        to_hop = list(combinations(list_dan, 2))
        ket_qua = [f"{cang}{p[0]}{p[1]}" for p in to_hop]
        result_str = " ".join(ket_qua)
        self.entry_ket_qua_ghep.delete(0, tk.END)
        self.entry_ket_qua_ghep.insert(0, result_str)
        self.root.clipboard_clear()
        self.root.clipboard_append(result_str)

    def run_crawl_thread(self):
        date_str = self.entry_date.get().strip()
        if not date_str: return
        self.lbl_status.config(text="Đang tải...", fg="orange")
        t = threading.Thread(target=self.crawl_data, args=(date_str,))
        t.daemon = True;
        t.start()

    def crawl_data(self, date_str):
        try:
            d_obj = datetime.datetime.strptime(date_str, '%d/%m/%Y')
            url = f"https://www.minhngoc.net.vn/ket-qua-xo-so/mien-bac/{d_obj.strftime('%d-%m-%Y')}.html"
            resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            if resp.status_code != 200: self.lbl_status.config(text="Lỗi HTTP", fg="red"); return
            soup = BeautifulSoup(resp.content, 'html.parser')
            box = soup.find('div', class_='box_kqxs')
            if not box: self.lbl_status.config(text="Lỗi Web/Ngày", fg="red"); return
            prizes = []
            for col in ['giaidb', 'giai1', 'giai2', 'giai3', 'giai4', 'giai5', 'giai6', 'giai7']:
                cell = box.find('td', class_=col)
                if cell: prizes.extend([n.strip() for n in cell.get_text(separator=" ").split() if n.strip().isdigit()])
            lotos = sorted([p[-2:] for p in prizes])

            def update_gui():
                self.raw_text_1.delete(1.0, tk.END);
                self.raw_text_1.insert(tk.END, " ".join(lotos))
                self.raw_text_2.delete(1.0, tk.END);
                self.raw_text_2.insert(tk.END, " ".join(prizes))
                self.manual_update_stats()
                self.lbl_status.config(text="Đã tải xong!", fg="green")

            self.root.after(0, update_gui)
        except:
            self.lbl_status.config(text="Lỗi", fg="red")

    def paste_text(self, widget):
        try:
            widget.insert(tk.END, self.root.clipboard_get())
        except:
            pass

    def manual_update_stats(self):
        text1 = self.raw_text_1.get("1.0", tk.END)
        clean_text1 = re.sub(r'(\d+)\s*\(\s*(\d+)\s*\)', lambda m: (m.group(1) + " ") * int(m.group(2)), text1)
        loto_nums = [n for n in re.findall(r'\d+', clean_text1) if len(n) >= 2]
        if loto_nums:
            self.stats_tails = Counter([n[-1] for n in loto_nums])
            self.stats_heads = Counter([n[-2] for n in loto_nums])
            self.has_data_1 = True;
            self.show_statistics_table()
        else:
            self.has_data_1 = False
            self.text_stats_display.delete(1.0, tk.END);
            self.text_stats_display.insert(tk.END, ">>> Trống")
        text2 = self.raw_text_2.get("1.0", tk.END)
        self.full_prizes = [p for p in re.findall(r'\d+', text2) if len(p) >= 2]
        self.has_data_2 = bool(self.full_prizes)

    def show_statistics_table(self):
        output = f"{'SUFFIX (ĐUÔI)':<40} | {'PREFIX (ĐẦU)'}\n" + "-" * 80 + "\n"
        for t_num, t_freq in self.stats_tails.most_common():
            h_freq = self.stats_heads.get(t_num, 0)
            output += f"Đuôi {t_num}: {t_freq} lần {'█' * t_freq:<15} | Đầu {t_num}: {h_freq} lần {'█' * h_freq}\n"
        self.text_stats_display.delete(1.0, tk.END);
        self.text_stats_display.insert(tk.END, output)

    # --- HÀM SOI CẦU ĐÃ CHỈNH SỬA (QUAN TRỌNG) ---
    def check_manual(self):
        if not self.has_data_1 and not self.has_data_2: self.manual_update_stats()
        user_input = self.entry_user_nums.get()
        if not user_input: return

        # 1. Phân tích chuỗi nhập (Xử lý Permutation/Sequence để hiển thị Header)
        raw_chunks = re.findall(r'\d+', user_input)
        check_list = set()
        display_str = []
        for chunk in raw_chunks:
            if len(chunk) == 2:
                check_list.add(chunk);
                display_str.append(chunk)
            elif len(chunk) == 3:
                perms = ["".join(p) for p in permutations(chunk, 2)]
                for p in perms: check_list.add(p)
                display_str.append(f"{chunk}(Perm:{','.join(perms)})")
            elif len(chunk) > 3:
                pairs = [chunk[i:i + 2] for i in range(len(chunk) - 1)]
                for p in pairs: check_list.add(p)
                display_str.append(f"{chunk}(Seq:{','.join(pairs)})")

        results = []
        for pair in check_list:
            score = (self.stats_tails.get(pair[1], 0) * 2) + self.stats_heads.get(pair[0], 0) if self.has_data_1 else 0

            # Logic tìm kiếm chi tiết (Start/Mid/End)
            found_info = []
            is_found = False
            if self.has_data_2:
                for prize in self.full_prizes:
                    if pair in prize:
                        idx = prize.find(pair)
                        if len(prize) == 2:
                            pos = "Loto"
                        elif idx == len(prize) - 2:
                            pos = "End"
                        elif idx == 0:
                            pos = "Start"
                        else:
                            pos = "Mid"
                        found_info.append(f"{prize} ({pos})")
                        is_found = True

            results.append({'pair': pair, 'score': score, 'found': is_found, 'prizes': found_info})

        results.sort(key=lambda x: x['score'], reverse=True)

        # 2. Xuất kết quả theo Format Tiếng Anh cũ
        screen_output = f"QUERY ID: {', '.join(display_str)}\n" + "=" * 80 + "\n"
        for item in results:
            if item['found']:
                status = f"MATCHED: {', '.join(item['prizes'])}"
            else:
                status = "NO MATCH"

            score_str = f"Score: {item['score']}"
            screen_output += f"ID {item['pair']} | {status:<60} | {score_str}\n"

        self.text_result.delete(1.0, tk.END)
        self.text_result.insert(tk.END, screen_output)


if __name__ == "__main__":
    root = tk.Tk()
    app = ToolXoSoApp(root)
    root.mainloop()
