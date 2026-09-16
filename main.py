"""
提瓦特放置游戏 - 塔防桌面版 (陷阱+塔版本)
"""
import time
import customtkinter as ctk
from tkinter import messagebox, Canvas

from game.data import (
    ELEMENTS, BUILDING_DEFS, TD_MAPS
)
from game.save import SaveManager, create_new_game
from game.battle_screen import BattleScreen

# ==================== 主题配置 ====================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg": "#0a0a14",
    "panel": "#141428",
    "card": "#1a1a35",
    "gold": "#d4a843",
    "gold_light": "#f0d68a",
    "text": "#e0d8c8",
    "text_secondary": "#8a8a9a",
    "border": "#2a2a45",
    "accent_blue": "#3b82f6",
    "fire": "#ef4444",
    "water": "#3b82f6",
    "thunder": "#a855f7",
    "ice": "#7dd3fc",
    "wind": "#4ade80",
    "rock": "#fbbf24",
    "grass": "#22c55e",
    "hp_green": "#4ade80",
    "hp_yellow": "#fbbf24",
    "hp_red": "#ef4444",
}


def format_num(n):
    if n >= 10000:
        return f"{n / 10000:.1f}万"
    if n >= 1000:
        return f"{n / 1000:.1f}k"
    return str(n)


# ==================== 主应用 ====================
class TiwateGame(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("提瓦特放置 - 塔防")
        self.geometry("1080x720")
        self.minsize(1000, 700)
        self.configure(fg_color="#0d0d1a")

        self.save_mgr = SaveManager()
        self.gs = None
        self.battle = None
        self.battle_stage_id = 1
        self.play_start = time.time()
        self.td_game_loop_id = None
        self.td_last_time = 0
        self.td_paused = False
        self.td_cell_size = 60

        self._load_state()
        self.battle_screen = BattleScreen(self)
        self._build_top_bar()
        self._build_content_frame()
        self._build_bottom_bar()

        self._show_battle_page()
        self._refresh_all()

        self.after(500, self._check_offline)
        self._update_timers()

    # ==================== 状态管理 ====================

    def _load_state(self):
        saved = self.save_mgr.load()
        if saved:
            self.gs = saved
        else:
            self.gs = create_new_game()
            self.save_mgr.save(self.gs)

    def _save_state(self):
        self.gs["last_online"] = time.time()
        self.save_mgr.save(self.gs)

    def _update_resin(self):
        now = time.time()
        last = self.gs["resources"].get("resin_last_update", now)
        elapsed = now - last
        gain = int(elapsed / 480)
        if gain > 0:
            self.gs["resources"]["resin"] = min(160, self.gs["resources"].get("resin", 0) + gain)
            self.gs["resources"]["resin_last_update"] = now

    def _apply_rewards(self, rewards):
        r = self.gs["resources"]
        r["mora"] = r.get("mora", 0) + rewards.get("mora", 0)
        r["exp_books"] = r.get("exp_books", 0) + rewards.get("exp_books", 0)
        r["primogems"] = r.get("primogems", 0) + rewards.get("primogems", 0)
        self.gs["adventure_exp"] = self.gs.get("adventure_exp", 0) + rewards.get("adventure_exp", 0)
        while self.gs["adventure_exp"] >= self.gs["adventure_rank"] * 100:
            self.gs["adventure_exp"] -= self.gs["adventure_rank"] * 100
            self.gs["adventure_rank"] += 1
            r["resin"] = min(160, r.get("resin", 0) + 60)
            r["mora"] = r.get("mora", 0) + 500

    def _update_timers(self):
        self._update_resin()
        self._update_resource_bar()
        elapsed = int(time.time() - self.play_start)
        mins = elapsed // 60
        hrs = mins // 60
        time_str = f"游玩: {hrs}时{mins % 60}分" if hrs > 0 else f"游玩: {mins}分"
        self.lbl_play_time.configure(text=time_str)
        self.after(10000, self._update_timers)

    # ==================== 顶部资源栏 ====================

    def _build_top_bar(self):
        self.top_bar = ctk.CTkFrame(self, fg_color="#141428", height=48, corner_radius=0)
        self.top_bar.pack(fill="x", side="top")
        self.top_bar.pack_propagate(False)

        ctk.CTkLabel(self.top_bar, text="✦ 提瓦特放置 - 塔防", font=("Microsoft YaHei", 16, "bold"),
                     text_color=COLORS["gold_light"]).pack(side="left", padx=20)

        res_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        res_frame.pack(side="right", padx=16)

        self.lbl_mora = self._make_res_label(res_frame, "🪙")
        self.lbl_mora.pack(side="left", padx=8)
        self.lbl_gems = self._make_res_label(res_frame, "💎")
        self.lbl_gems.pack(side="left", padx=8)
        self.lbl_books = self._make_res_label(res_frame, "📘")
        self.lbl_books.pack(side="left", padx=8)
        self.lbl_resin = self._make_res_label(res_frame, "⚗️")
        self.lbl_resin.pack(side="left", padx=8)
        self.lbl_ar = self._make_res_label(res_frame, "⭐")
        self.lbl_ar.pack(side="left", padx=8)

    def _make_res_label(self, parent, icon):
        return ctk.CTkLabel(parent, text=f"{icon} 0", font=("Microsoft YaHei", 12),
                            text_color=COLORS["text_secondary"])

    def _update_resource_bar(self):
        r = self.gs["resources"]
        self.lbl_mora.configure(text=f"🪙 {format_num(r.get('mora', 0))}")
        self.lbl_gems.configure(text=f"💎 {format_num(r.get('primogems', 0))}")
        self.lbl_books.configure(text=f"📘 {r.get('exp_books', 0)}")
        self.lbl_resin.configure(text=f"⚗️ {r.get('resin', 0)}/160")
        self.lbl_ar.configure(text=f"⭐ Lv.{self.gs.get('adventure_rank', 1)}")

    # ==================== 内容区 ====================

    def _build_content_frame(self):
        self.content_frame = ctk.CTkFrame(self, fg_color="#141428", corner_radius=10)
        self._build_battle_page()

    # ==================== 底部栏 ====================

    def _build_bottom_bar(self):
        self.bottom_bar = ctk.CTkFrame(self, fg_color="#141428", height=40, corner_radius=0)
        self.bottom_bar.pack(fill="x", side="bottom")
        self.bottom_bar.pack_propagate(False)

        ctk.CTkButton(self.bottom_bar, text="📋 每日委托 (+20000🪙)", font=("Microsoft YaHei", 12),
                      fg_color="transparent", text_color=COLORS["text_secondary"],
                      hover_color="#1a1a35", command=self._claim_daily).pack(side="left", padx=16)

        ctk.CTkButton(self.bottom_bar, text="💾 保存游戏", font=("Microsoft YaHei", 12),
                      fg_color="transparent", text_color=COLORS["text_secondary"],
                      hover_color="#1a1a35", command=self._save_game).pack(side="left", padx=8)

        self.lbl_play_time = ctk.CTkLabel(self.bottom_bar, text="游玩: 0分",
                                          font=("Microsoft YaHei", 11), text_color=COLORS["text_secondary"])
        self.lbl_play_time.pack(side="right", padx=20)

    # ============================================================
    #  战斗页面（UI 构建）
    # ============================================================

    def _build_battle_page(self):
        parent = self.content_frame

        # --- 关卡选择面板 ---
        self.stage_panel = ctk.CTkFrame(parent, fg_color="transparent")
        self._build_stage_select(self.stage_panel)

        # --- TD战斗面板 ---
        self.battle_panel = ctk.CTkFrame(parent, fg_color="transparent")

        self.td_top = ctk.CTkFrame(self.battle_panel, fg_color="#1a1a35", height=40, corner_radius=6)
        self.td_top.pack(fill="x", pady=(0, 6))
        self.td_top.pack_propagate(False)

        self.lbl_td_gold = ctk.CTkLabel(self.td_top, text="💰 0", font=("Microsoft YaHei", 13, "bold"),
                                        text_color=COLORS["gold"])
        self.lbl_td_gold.pack(side="left", padx=12)

        self.lbl_td_wave = ctk.CTkLabel(self.td_top, text="波次: 0/0", font=("Microsoft YaHei", 12),
                                        text_color=COLORS["text"])
        self.lbl_td_wave.pack(side="left", padx=12)

        self.lbl_td_lives = ctk.CTkLabel(self.td_top, text="❤️ 20", font=("Microsoft YaHei", 13, "bold"),
                                         text_color=COLORS["hp_red"])
        self.lbl_td_lives.pack(side="left", padx=12)

        self.lbl_td_info = ctk.CTkLabel(self.td_top, text="", font=("Microsoft YaHei", 11),
                                        text_color=COLORS["text_secondary"])
        self.lbl_td_info.pack(side="right", padx=12)

        self.btn_td_start = ctk.CTkButton(self.td_top, text="▶ 开始出怪",
                                          font=("Microsoft YaHei", 13),
                                          fg_color="#8a6520", hover_color="#a08030",
                                          text_color="#fff", width=120,
                                          command=self.battle_screen.start_wave)
        self.btn_td_start.pack(side="right", padx=4, pady=4)

        self.btn_td_back = ctk.CTkButton(self.td_top, text="返回选关",
                                         font=("Microsoft YaHei", 12),
                                         fg_color="transparent", text_color=COLORS["text_secondary"],
                                         border_width=1, border_color=COLORS["border"],
                                         hover_color="#1a1a35", width=100,
                                         command=self.battle_screen.return_to_stage_select)
        self.btn_td_back.pack(side="right", padx=4, pady=4)

        # Canvas
        self.td_mid_frame = ctk.CTkFrame(self.battle_panel, fg_color="transparent")
        self.td_mid_frame.pack(fill="both", expand=True)

        self.td_canvas_frame = ctk.CTkFrame(self.td_mid_frame, fg_color="#0a0a14", corner_radius=0)
        self.td_canvas_frame.pack(fill="both", expand=True)

        self.td_canvas = Canvas(self.td_canvas_frame, bg="#0a0a14", highlightthickness=0, bd=0)
        self.td_canvas.pack(expand=True)
        self.td_canvas.bind("<Button-1>", self.battle_screen.on_click_canvas)

        self.battle_active = False

    def _show_battle_page(self):
        self.content_frame.pack(fill="both", expand=True, padx=12, pady=(8, 0))
        self._show_stage_select()

    def _build_stage_select(self, parent):
        for w in parent.winfo_children():
            w.destroy()

        ctk.CTkLabel(parent, text="选择关卡", font=("Microsoft YaHei", 15, "bold"),
                     text_color=COLORS["gold_light"]).pack(anchor="w", pady=(0, 8))

        grid_frame = ctk.CTkFrame(parent, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True)

        self.stage_cards = {}
        progress = self.gs["stage_progress"]
        unlocked = progress.get("highest_stage_unlocked", 1)
        completed = progress.get("completed_stages", [])

        cols = 3
        for i, tdm in enumerate(TD_MAPS):
            sid = tdm["id"]
            is_locked = sid > unlocked
            is_done = sid in completed

            card = ctk.CTkFrame(grid_frame, fg_color="#1a1a35", border_width=2, corner_radius=8)
            if not is_locked and not is_done:
                card.configure(border_color=COLORS["gold"])
            elif is_locked:
                card.configure(fg_color="#121224")
            card.grid(row=i // cols, column=i % cols, padx=4, pady=4, sticky="nsew")

            name_text = f"{tdm['name']} {'✓' if is_done else '🔒' if is_locked else ''}"
            lbl = ctk.CTkLabel(card, text=name_text, font=("Microsoft YaHei", 12, "bold"),
                              text_color=COLORS["text"] if not is_locked else "#555")
            lbl.pack(pady=(8, 2))

            ctk.CTkLabel(card, text=f"🗺️ {tdm['width']}×{tdm['height']} | {len(tdm['waves'])}波",
                         font=("Microsoft YaHei", 10), text_color=COLORS["text_secondary"]).pack()
            ctk.CTkLabel(card, text=f"初始 💰{tdm['starting_gold']} | ❤️{tdm['lives']}",
                         font=("Microsoft YaHei", 10), text_color=COLORS["gold"]).pack(pady=(0, 8))

            if not is_locked:
                lbl.bind("<Button-1>", lambda e, s=sid: self._select_stage(s))
                for child in card.winfo_children():
                    child.bind("<Button-1>", lambda e, s=sid: self._select_stage(s))
                card.bind("<Button-1>", lambda e, s=sid: self._select_stage(s))
            self.stage_cards[sid] = card

        for c in range(cols):
            grid_frame.grid_columnconfigure(c, weight=1, uniform="stage")
        for r in range((len(TD_MAPS) + cols - 1) // cols):
            grid_frame.grid_rowconfigure(r, weight=1, uniform="stage")

        self.btn_start = ctk.CTkButton(parent, text="🗺️ 进入地图", font=("Microsoft YaHei", 14, "bold"),
                                       fg_color="#8a6520", hover_color="#a08030", text_color="#fff",
                                       height=36, command=self.battle_screen.enter_map)
        self.btn_start.pack(pady=(12, 4))

    def _select_stage(self, stage_id):
        self.battle_stage_id = stage_id
        for sid, card in self.stage_cards.items():
            card.configure(border_color=COLORS["gold"] if sid == stage_id else COLORS["border"])

    def _show_stage_select(self):
        self.stage_panel.pack(fill="both", expand=True)
        self.battle_panel.pack_forget()
        self._build_stage_select(self.stage_panel)
        self.battle_active = False

    # ============================================================
    #  离线收益 & 每日委托
    # ============================================================

    def _check_offline(self):
        now = time.time()
        last = self.gs.get("last_online", now)
        offline_sec = min(max(0, now - last), 43200)
        if offline_sec < 60:
            return

        hours = offline_sec / 3600
        mora = int(100 * hours * 0.7)
        exp = max(0, int(hours * 0.7 * 2))
        ar_exp = int(hours * 0.7 * 50)

        go = messagebox.askyesno(
            "欢迎回来！",
            f"你离开了 {hours:.1f} 小时\n\n离线收益:\n🪙 摩拉: {mora}\n📘 经验书: {exp}\n⭐ 冒险阅历: {ar_exp}\n\n领取奖励？"
        )
        if go:
            self._apply_rewards({"mora": mora, "exp_books": exp, "adventure_exp": ar_exp, "primogems": 0})
            self.gs["last_online"] = now
            self._save_state()
            self._update_resource_bar()

    def _claim_daily(self):
        now = time.time()
        last = self.gs["dailies"].get("last_daily_reset", 0)
        if now - last > 86400:
            self.gs["dailies"]["commissions_done"] = 0
            self.gs["dailies"]["last_daily_reset"] = now

        done = self.gs["dailies"].get("commissions_done", 0)
        remaining = max(0, 4 - done)
        if remaining <= 0:
            messagebox.showinfo("提示", "今日委托已全部完成！")
            return

        actual = min(remaining, 4)
        self.gs["dailies"]["commissions_done"] += actual
        rewards = {"mora": actual * 5000, "exp_books": actual * 3, "adventure_exp": actual * 50}
        self._apply_rewards(rewards)
        self._save_state()
        self._update_resource_bar()
        messagebox.showinfo("每日委托", f"完成{actual}个委托！\n获得 🪙{actual * 5000}摩拉 📘{actual * 3}经验书")

    def _save_game(self):
        self._save_state()
        messagebox.showinfo("提示", "游戏已保存！")

    def _refresh_all(self):
        self._update_resource_bar()


# ==================== 启动 ====================
if __name__ == "__main__":
    app = TiwateGame()
    app.mainloop()