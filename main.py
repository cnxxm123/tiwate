"""
提瓦特放置游戏 - 塔防桌面版 (CustomTkinter GUI)
"""
import time
import random
import math
import threading
import copy
import customtkinter as ctk
from tkinter import messagebox, Canvas

# 游戏逻辑模块
from game.data import (
    CHARACTERS, ELEMENTS, RESONANCES, STAGES, MAX_LEVEL, get_exp_books_for_level,
    TD_TOWER_STATS, TD_MAPS, TD_ENEMY_STATS, TD_REACTIONS
)
from game.engine import BattleEngine  # 保留兼容
from game.td_engine import TDEngine
from game.save import SaveManager, create_new_game

# ==================== 主题配置 ====================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# 颜色常量
COLORS = {
    "bg": "#0a0a14",
    "panel": "#141428",
    "card": "#1a1a35",
    "gold": "#d4a843",
    "gold_light": "#f0d68a",
    "text": "#e0d8c8",
    "text_secondary": "#8a8a9a",
    "border": "#2a2a45",
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
    """格式化数字显示"""
    if n >= 10000:
        return f"{n / 10000:.1f}万"
    if n >= 1000:
        return f"{n / 1000:.1f}k"
    return str(n)


# ==================== 主应用 ====================
class TiwateGame(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 窗口设置
        self.title("提瓦特放置")
        self.geometry("1280x900")
        self.minsize(1000, 700)
        self.configure(fg_color="#0d0d1a")

        # 游戏状态
        self.save_mgr = SaveManager()
        self.gs = None
        self.battle = None      # TD引擎实例
        self.battle_stage_id = 1
        self.play_start = time.time()
        self.td_game_loop_id = None  # 游戏循环ID
        self.td_last_time = 0
        self.td_selected_char = None  # 选中的待部署角色
        self.td_paused = False

        # 加载存档
        self._load_state()

        # 构建界面
        self._build_top_bar()
        self._build_tab_nav()
        self._build_content_frames()
        self._build_bottom_bar()

        # 显示初始页面
        self._switch_tab("battle")
        self._refresh_all()

        # 检查离线收益
        self.after(500, self._check_offline)

        # 定时刷新(树脂、游玩时间)
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
        # 冒险等级提升
        while self.gs["adventure_exp"] >= self.gs["adventure_rank"] * 100:
            self.gs["adventure_exp"] -= self.gs["adventure_rank"] * 100
            self.gs["adventure_rank"] += 1
            r["resin"] = min(160, r.get("resin", 0) + 60)
            r["mora"] = r.get("mora", 0) + 500

    def _update_timers(self):
        """定时刷新资源栏和游玩时间"""
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

        # 标题
        ctk.CTkLabel(self.top_bar, text="✦ 提瓦特放置", font=("Microsoft YaHei", 16, "bold"),
                     text_color=COLORS["gold_light"]).pack(side="left", padx=20)

        # 资源
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
        lbl = ctk.CTkLabel(parent, text=f"{icon} 0", font=("Microsoft YaHei", 12),
                           text_color=COLORS["text_secondary"])
        return lbl

    def _update_resource_bar(self):
        r = self.gs["resources"]
        self.lbl_mora.configure(text=f"🪙 {format_num(r.get('mora', 0))}")
        self.lbl_gems.configure(text=f"💎 {format_num(r.get('primogems', 0))}")
        self.lbl_books.configure(text=f"📘 {r.get('exp_books', 0)}")
        self.lbl_resin.configure(text=f"⚗️ {r.get('resin', 0)}/160")
        self.lbl_ar.configure(text=f"⭐ Lv.{self.gs.get('adventure_rank', 1)}")

    # ==================== 标签导航 ====================

    def _build_tab_nav(self):
        self.tab_frame = ctk.CTkFrame(self, fg_color="#0a0a14", height=36, corner_radius=0)
        self.tab_frame.pack(fill="x", side="top")
        self.tab_frame.pack_propagate(False)

        self.tab_btns = {}
        tabs = [("battle", "⚔️ 战斗"), ("shop", "🛒 商店"), ("team", "👥 编队"), ("chars", "📋 角色")]
        for key, label in tabs:
            btn = ctk.CTkButton(self.tab_frame, text=label, font=("Microsoft YaHei", 13),
                                fg_color="transparent", text_color=COLORS["text_secondary"],
                                hover_color="#1a1a35", width=100, height=30, corner_radius=6,
                                command=lambda k=key: self._switch_tab(k))
            btn.pack(side="left", padx=2, pady=2)
            self.tab_btns[key] = btn

    def _switch_tab(self, tab_name):
        for key, btn in self.tab_btns.items():
            if key == tab_name:
                btn.configure(fg_color="#141428", text_color=COLORS["gold_light"])
            else:
                btn.configure(fg_color="transparent", text_color=COLORS["text_secondary"])

        for frame in self.content_frames.values():
            frame.pack_forget()

        self.content_frames[tab_name].pack(fill="both", expand=True, padx=12, pady=(8, 0))

        if tab_name == "battle":
            self._show_stage_select() if not self.battle else None
        elif tab_name == "shop":
            self._refresh_shop()
        elif tab_name == "team":
            self._refresh_team()
        elif tab_name == "chars":
            self._refresh_chars()

    # ==================== 内容区框架 ====================

    def _build_content_frames(self):
        self.content_frames = {}
        # 战斗页面用普通Frame（不需要滚动，地图铺满）
        self.content_frames["battle"] = ctk.CTkFrame(self, fg_color="#141428", corner_radius=10)
        for key in ["shop", "team", "chars"]:
            frame = ctk.CTkScrollableFrame(self, fg_color="#141428", corner_radius=10)
            self.content_frames[key] = frame

        self._build_battle_page()
        self._build_shop_page()
        self._build_team_page()
        self._build_chars_page()

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
    #  战斗页面（塔防）
    # ============================================================

    def _build_battle_page(self):
        parent = self.content_frames["battle"]

        # --- 关卡选择面板 ---
        self.stage_panel = ctk.CTkFrame(parent, fg_color="transparent")
        self._build_stage_select(self.stage_panel)

        # --- TD战斗面板 ---
        self.battle_panel = ctk.CTkFrame(parent, fg_color="transparent")

        # 战斗头部（资源条）
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

        # Canvas画布（塔防地图）- 中间行左侧
        self.td_mid_frame = ctk.CTkFrame(self.battle_panel, fg_color="transparent")
        self.td_mid_frame.pack(fill="both", expand=True, pady=4)

        self.td_canvas_frame = ctk.CTkFrame(self.td_mid_frame, fg_color="#0a0a14", corner_radius=8)
        self.td_canvas_frame.pack(side="left", fill="both", expand=True)

        self.td_canvas = Canvas(self.td_canvas_frame, bg="#0a0a14", highlightthickness=0, bd=0)
        self.td_canvas.pack(fill="both", expand=True)
        self.td_canvas.bind("<Button-1>", self._td_click_canvas)

        # 待部署角色选择面板 - 中间行右侧
        self.td_char_bar = ctk.CTkFrame(self.td_mid_frame, fg_color="#141428", width=130, corner_radius=6)
        self.td_char_bar.pack(side="right", fill="y", padx=(6, 0))
        self.td_char_bar.pack_propagate(False)

        self.td_char_buttons = {}

        # 控制按钮
        ctrl = ctk.CTkFrame(self.battle_panel, fg_color="transparent")
        ctrl.pack(fill="x", pady=(6, 0))

        self.btn_td_start = ctk.CTkButton(ctrl, text="▶ 开始出怪", font=("Microsoft YaHei", 13),
                                          fg_color="#8a6520", hover_color="#a08030", text_color="#fff",
                                          width=120, command=self._td_start_wave)
        self.btn_td_start.pack(side="left", padx=4)

        self.btn_td_back = ctk.CTkButton(ctrl, text="返回选关", font=("Microsoft YaHei", 12),
                                         fg_color="transparent", text_color=COLORS["text_secondary"],
                                         border_width=1, border_color=COLORS["border"],
                                         hover_color="#1a1a35", width=100, command=self._td_return)
        self.btn_td_back.pack(side="right", padx=4)

        self.battle_active = False

    def _build_stage_select(self, parent):
        for w in parent.winfo_children():
            w.destroy()

        ctk.CTkLabel(parent, text="选择关卡（塔防地图）", font=("Microsoft YaHei", 15, "bold"),
                     text_color=COLORS["gold_light"]).pack(anchor="w", pady=(0, 8))

        self.stage_cards = {}
        progress = self.gs["stage_progress"]
        unlocked = progress.get("highest_stage_unlocked", 1)
        completed = progress.get("completed_stages", [])

        for tdm in TD_MAPS:
            sid = tdm["id"]
            is_locked = sid > unlocked
            is_done = sid in completed

            card = ctk.CTkFrame(parent, fg_color="#1a1a35", border_width=2, corner_radius=8)
            if not is_locked and not is_done:
                card.configure(border_color=COLORS["gold"])
            elif is_locked:
                card.configure(fg_color="#121224")
            card.pack(side="left", padx=4, pady=2, fill="x", expand=True)

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

        self.btn_start = ctk.CTkButton(parent, text="🗺️ 进入地图", font=("Microsoft YaHei", 14, "bold"),
                                       fg_color="#8a6520", hover_color="#a08030", text_color="#fff",
                                       height=36, command=self._td_enter_map)
        self.btn_start.pack(pady=(12, 4))

    def _select_stage(self, stage_id):
        self.battle_stage_id = stage_id
        for sid, card in self.stage_cards.items():
            card.configure(border_color=COLORS["gold"] if sid == stage_id else COLORS["border"])

    def _show_stage_select(self):
        self.stage_panel.pack(fill="x")
        self.battle_panel.pack_forget()
        self._build_stage_select(self.stage_panel)
        self.battle_active = False

    # --- 塔防逻辑 ---

    def _td_enter_map(self):
        """进入TD地图（部署阶段）"""
        tdm = next((m for m in TD_MAPS if m["id"] == self.battle_stage_id), None)
        if not tdm:
            return

        # 检查队伍
        team = self.gs.get("team", [])
        if not team:
            messagebox.showwarning("提示", "请先到编队页面设置队伍！")
            return

        # 构建可用角色列表
        avail = {}
        for cid in team:
            if cid in self.gs["characters"] and cid in TD_TOWER_STATS:
                avail[cid] = self.gs["characters"][cid]["level"]

        if not avail:
            messagebox.showwarning("提示", "队伍中没有可用于塔防的角色！")
            return

        # 隐藏外围UI，让战斗占满全屏
        self.top_bar.pack_forget()
        self.tab_frame.pack_forget()
        self.bottom_bar.pack_forget()

        self.stage_panel.pack_forget()
        self.battle_panel.pack(fill="both", expand=True)
        self.update_idletasks()

        # 全屏地图：窗口尺寸减去战斗内固定UI，加安全边距
        win_w = self.winfo_width()
        win_h = self.winfo_height()
        # 右侧角色栏 ~140px + padding + 安全边距
        avail_w = win_w - 170
        # td_top(46) + ctrl(42) + CTkScrollableFrame内部padding + 安全边距
        avail_h = max(200, win_h - 126)

        tdm_copy = copy.deepcopy(tdm)
        cs_w = avail_w // tdm["width"]
        cs_h = avail_h // tdm["height"]
        cell_size = max(50, min(cs_w, cs_h, 90))  # 上限90避免过大
        self.td_cell_size = cell_size
        tdm_copy["cell_size"] = cell_size

        # 创建TD引擎（使用动态格子尺寸）
        self.battle = TDEngine(tdm_copy, avail)
        self.td_selected_char = None
        self.battle_active = True

        # 更新资源显示
        self._td_update_top_bar()

        # Canvas尺寸设为刚好填满容器（不触发滚动条）
        canvas_w = tdm_copy["width"] * cell_size
        canvas_h = tdm_copy["height"] * cell_size
        self.td_canvas.configure(width=canvas_w, height=canvas_h)
        # 限制Canvas框架不超出
        self.td_canvas_frame.configure(width=canvas_w + 4, height=canvas_h + 4)
        self.td_canvas.delete("all")

        # 渲染地图
        self._td_render_map()

        # 渲染角色栏
        self._td_render_char_bar(avail)

        # 按钮状态
        self.btn_td_start.configure(state="normal", text="▶ 开始出怪")

    def _td_render_char_bar(self, avail):
        """渲染可部署角色栏（竖向排列在右侧）"""
        children = list(self.td_char_bar.winfo_children())
        for w in children:
            w.destroy()
        self.td_char_buttons.clear()

        ctk.CTkLabel(self.td_char_bar, text="部署角色",
                     font=("Microsoft YaHei", 11, "bold"), text_color=COLORS["gold_light"]).pack(pady=(8, 2))
        ctk.CTkLabel(self.td_char_bar, text="点击后部署",
                     font=("Microsoft YaHei", 8), text_color=COLORS["text_secondary"]).pack(pady=(0, 6))

        for i, (cid, level) in enumerate(avail.items()):
            td_s = TD_TOWER_STATS[cid]
            cd = CHARACTERS[cid]
            btn = ctk.CTkButton(self.td_char_bar,
                                text=f"{ELEMENTS[cd['element']]['icon']} {cd['name']}\n💰{td_s['cost']}",
                                font=("Microsoft YaHei", 9), fg_color="#1a1a35",
                                hover_color="#2a2a55", text_color=COLORS["text"],
                                border_width=1, border_color=COLORS["border"],
                                height=40, width=110,
                                command=lambda c=cid: self._td_select_char(c))
            btn.pack(padx=6, pady=3)
            self.td_char_buttons[cid] = btn

    def _td_select_char(self, char_id):
        """选中一个角色准备部署"""
        self.td_selected_char = char_id
        for cid, btn in self.td_char_buttons.items():
            if cid == char_id:
                btn.configure(border_color=COLORS["gold"], fg_color="#2a2a45")
            else:
                btn.configure(border_color=COLORS["border"], fg_color="#1a1a35")

    def _td_click_canvas(self, event):
        """Canvas点击事件"""
        if not self.battle:
            return

        # 计算格子坐标
        tdm = next((m for m in TD_MAPS if m["id"] == self.battle_stage_id), None)
        if not tdm:
            return
        gx = event.x // self.td_cell_size
        gy = event.y // self.td_cell_size

        # 部署阶段和战斗阶段都可以部署塔
        if self.td_selected_char:
            tower = self.battle.place_tower(self.td_selected_char, gx, gy)
            if tower:
                self.td_selected_char = None
                for btn in self.td_char_buttons.values():
                    btn.configure(border_color=COLORS["border"], fg_color="#1a1a35")
                self._td_render_map()
                self._td_update_top_bar()
            return

        # 检查是否点击了已有的塔（使用技能）——仅战斗中
        if self.battle.running:
            for t in self.battle.towers:
                if t.grid_x == gx and t.grid_y == gy:
                    result = self.battle.use_tower_ability(t)
                    if result:
                        self._td_update_top_bar()
                        self._td_render_map()
                    return

    def _td_start_wave(self):
        """开始出怪"""
        if not self.battle:
            return
        self.battle.start()
        self.btn_td_start.configure(state="disabled", text="出怪中...")
        # 启动游戏循环
        self.td_last_time = time.time()
        self._td_game_loop()

    def _td_game_loop(self):
        """游戏主循环（60fps）"""
        if not self.battle or self.battle.game_over:
            self._td_handle_end()
            return
        if not self.battle_active:
            return

        now = time.time()
        dt = min(now - self.td_last_time, 0.1)  # 最大0.1秒步长
        self.td_last_time = now

        self.battle.update(dt)
        self._td_render_map()
        self._td_update_top_bar()

        if not self.battle.game_over:
            self.td_game_loop_id = self.after(16, self._td_game_loop)

    def _td_update_top_bar(self):
        """更新资源栏"""
        if not self.battle:
            return
        self.lbl_td_gold.configure(text=f"💰 {self.battle.gold}")
        self.lbl_td_wave.configure(text=f"波次: {self.battle.wave_index + 1}/{len(self.battle.waves)}")
        self.lbl_td_lives.configure(text=f"❤️ {self.battle.lives}/{self.battle.max_lives}")
        t = self.battle.game_time
        self.lbl_td_info.configure(text=f"⏱ {int(t // 60)}:{int(t % 60):02d}  击杀:{self.battle.kill_count}")

    def _td_render_map(self):
        """渲染TD地图"""
        canvas = self.td_canvas
        canvas.delete("all")
        if not self.battle:
            return

        tdm = next((m for m in TD_MAPS if m["id"] == self.battle_stage_id), None)
        if not tdm:
            return
        cs = self.td_cell_size

        # 画网格
        for y in range(tdm["height"]):
            for x in range(tdm["width"]):
                x1, y1 = x * cs, y * cs
                x2, y2 = x1 + cs, y1 + cs
                if (x, y) in self.battle.path_set:
                    canvas.create_rectangle(x1, y1, x2, y2, fill="#2a2a18", outline="#3a3a20", width=1)
                else:
                    canvas.create_rectangle(x1, y1, x2, y2, fill="#111122", outline="#1a1a30", width=1)

        # 画路径标记
        path = self.battle.path
        for i, (px, py) in enumerate(path):
            x1, y1 = px * cs + 2, py * cs + 2
            x2, y2 = px * cs + cs - 2, py * cs + cs - 2
            if i == 0:
                canvas.create_rectangle(x1, y1, x2, y2, fill="#2a5a2a", outline="#4a8a4a", width=1)
                canvas.create_text(px * cs + cs / 2, py * cs + cs / 2, text="S", fill="#0f0",
                                   font=("Microsoft YaHei", 10, "bold"))
            elif i == len(path) - 1:
                canvas.create_rectangle(x1, y1, x2, y2, fill="#5a2a2a", outline="#8a4a4a", width=1)
                canvas.create_text(px * cs + cs / 2, py * cs + cs / 2, text="E", fill="#f44",
                                   font=("Microsoft YaHei", 10, "bold"))
            else:
                canvas.create_rectangle(x1, y1, x2, y2, fill="#2a2a18", outline="#3a3a20", width=1)
                # 路径方向箭头
                if i < len(path) - 1:
                    nx, ny = path[i + 1]
                    cx, cy = px * cs + cs / 2, py * cs + cs / 2
                    dx, dy = (nx - px) * cs * 0.3, (ny - py) * cs * 0.3
                    canvas.create_line(cx, cy, cx + dx, cy + dy, fill="#559", width=2, arrow="last")

        # 画塔
        for t in self.battle.towers:
            x, y = t.px, t.py
            r = 16
            elem_color = ELEMENTS[t.element]["color"]
            # 塔底盘
            canvas.create_oval(x - r - 2, y - r - 2, x + r + 2, y + r + 2,
                               fill="#1a1a35", outline=elem_color, width=2)
            # 范围圈
            tr = t.range * cs
            canvas.create_oval(x - tr, y - tr, x + tr, y + tr,
                               outline=elem_color, width=1, dash=(3, 3))
            # HP条
            hp_ratio = t.hp / t.max_hp if t.max_hp > 0 else 0
            bar_w = 30
            bar_h = 3
            canvas.create_rectangle(x - bar_w / 2, y - r - 10, x + bar_w / 2, y - r - 7,
                                    fill="#333", outline="")
            hp_color = "#4f4" if hp_ratio > 0.6 else ("#ff0" if hp_ratio > 0.3 else "#f44")
            canvas.create_rectangle(x - bar_w / 2, y - r - 10,
                                    x - bar_w / 2 + bar_w * hp_ratio, y - r - 7,
                                    fill=hp_color, outline="")
            # 图标
            canvas.create_text(x, y, text=ELEMENTS[t.element]["icon"],
                               font=("Microsoft YaHei", 12))
            # 名字
            canvas.create_text(x, y + r + 8, text=t.name, font=("Microsoft YaHei", 8),
                               fill="#ccc")

        # 画敌人
        for e in self.battle.enemies:
            if e.dead or e.reached_end:
                continue
            x, y = e.px, e.py
            r = 10
            color = e.color
            if e.frozen:
                color = "#88ccff"
            elif e.slowed:
                color = "#aaaaaa"

            canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="#fff", width=1)
            # HP条
            hp_ratio = e.hp / e.max_hp if e.max_hp > 0 else 0
            bar_w = 22
            canvas.create_rectangle(x - bar_w / 2, y - r - 6, x + bar_w / 2, y - r - 3,
                                    fill="#333", outline="")
            canvas.create_rectangle(x - bar_w / 2, y - r - 6,
                                    x - bar_w / 2 + bar_w * hp_ratio, y - r - 3,
                                    fill="#4f4" if hp_ratio > 0.5 else "#f44", outline="")
            # 状态图标
            if e.frozen:
                canvas.create_text(x, y - r - 12, text="❄️", font=("Microsoft YaHei", 8))
            if e.element:
                canvas.create_text(x + r, y - r, text=ELEMENTS[e.element]["icon"],
                                   font=("Microsoft YaHei", 7))

        # 画特效
        for ef in self.battle.effects:
            alpha = min(1, ef["timer"] / 1.2)
            font_size = int(10 + (1 - alpha) * 8)
            canvas.create_text(ef["px"], ef["py"] - 20 * (1 - alpha), text=ef["text"],
                               font=("Microsoft YaHei", max(8, font_size)),
                               fill=ef["color"],
                               stipple="" if alpha > 0.5 else "gray50")

    def _td_handle_end(self):
        """战斗结束处理"""
        # 停止游戏循环
        if self.td_game_loop_id:
            self.after_cancel(self.td_game_loop_id)
            self.td_game_loop_id = None

        self.btn_td_start.configure(state="disabled")

        if self.battle.victory:
            rewards = {
                "mora": self.battle.gold_earned + random.randint(200, 500) * self.battle_stage_id,
                "exp_books": random.randint(1, max(2, self.battle_stage_id)),
                "adventure_exp": self.battle_stage_id * 15,
            }
            self._apply_rewards(rewards)
            self._update_resource_bar()

            if self.battle_stage_id not in self.gs["stage_progress"].get("completed_stages", []):
                self.gs["stage_progress"]["completed_stages"] = \
                    self.gs["stage_progress"].get("completed_stages", []) + [self.battle_stage_id]
            next_id = self.battle_stage_id + 1
            if next_id > self.gs["stage_progress"]["highest_stage_unlocked"]:
                if any(m["id"] == next_id for m in TD_MAPS):
                    self.gs["stage_progress"]["highest_stage_unlocked"] = next_id
            self._save_state()

            messagebox.showinfo("胜利！", f"✨ 关卡完成！\n摩拉:{rewards['mora']} 书:{rewards['exp_books']}")
            self._td_return()
        else:
            messagebox.showinfo("失败", "X 生命值归零，请重新挑战！")
            self._td_return()

    def _td_return(self):
        """返回关卡选择"""
        if self.td_game_loop_id:
            self.after_cancel(self.td_game_loop_id)
            self.td_game_loop_id = None
        # 恢复外围UI
        self.top_bar.pack(fill="x", side="top")
        self.tab_frame.pack(fill="x", side="top")
        self.bottom_bar.pack(fill="x", side="bottom")
        self._show_stage_select()
        self._save_state()

    # ============================================================
    #  商店页面（金币购买角色）
    # ============================================================

    # 角色商店价格
    CHAR_PRICES = {
        # 5★ 15000 (T0)
        "raiden": 15000, "nahida": 15000, "furina": 15000, "zhongli": 15000,
        "mavuika": 15000, "kazuha": 15000, "neuvillette": 15000,
        "arlecchino": 15000, "xilonen": 15000,
        # 5★ 12000 (T1)
        "yelan": 12000, "alhaitham": 12000, "navia": 12000, "ayaka": 12000,
        "hutao": 12000, "nilou": 12000, "kokomi": 12000, "clorinde": 12000,
        "chasca": 12000, "kinich": 12000, "citlali": 12000, "xianyun": 12000,
        # 5★ 10000 (T2)
        "tartaglia": 10000, "xiao": 10000, "wanderer": 10000, "itto": 10000,
        "cyno": 10000, "yae_miko": 10000, "lyney": 10000, "wriothesley": 10000,
        "baizhu": 10000, "shenhe": 10000, "yoimiya": 10000, "eula": 10000,
        "emilie": 10000, "venti": 10000, "ganyu": 10000, "chiori": 10000,
        "ayato": 10000, "mualani": 10000, "varesa": 10000,
        # 5★ 8000 (T3 常驻/较弱)
        "diluc": 8000, "mona": 8000, "keqing": 8000, "qiqi": 8000,
        "jean": 8000, "tighnari": 8000, "dehya": 8000, "klee": 8000,
        "albedo": 8000, "sigewinne": 8000,
        # 4★ 6000 (T0/T1)
        "bennett": 6000, "xiangling": 6000, "xingqiu": 6000, "fischl": 6000,
        "sucrose": 6000, "kuki": 6000, "chevreuse": 6000, "faruzan": 6000,
        "gorou": 6000, "sara": 6000,
        # 4★ 4000 (T2)
        "beidou": 4000, "rosaria": 4000, "yaoyao": 4000, "gaming": 4000,
        "lanyan": 4000, "lynette": 4000, "thoma": 4000, "yunjin": 4000,
        "kirara": 4000, "diona": 4000, "layla": 4000, "collei": 4000,
        "ororon": 4000, "charlotte": 4000, "kachina": 4000, "sethos": 4000,
        "kaeya": 4000, "yanfei": 4000, "ningguang": 4000,
        # 4★ 2500 (T3)
        "lisa": 2500, "candace": 2500, "heizou": 2500, "chongyun": 2500,
        "freminet": 2500, "mika": 2500, "noelle": 2500, "barbara": 2500,
        "razor": 2500, "amber": 2500, "xinyan": 2500, "sayu": 2500,
        "dori": 2500, "kaveh": 2500,
    }

    def _build_shop_page(self):
        self.shop_parent = self.content_frames["shop"]

    def _refresh_shop(self):
        parent = self.shop_parent
        for w in parent.winfo_children():
            w.destroy()

        ctk.CTkLabel(parent, text="角色商店", font=("Microsoft YaHei", 15, "bold"),
                     text_color=COLORS["gold_light"]).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(parent, text="使用摩拉购买角色加入你的队伍",
                     font=("Microsoft YaHei", 10),
                     text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 8))

        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x")

        owned = self.gs.get("characters", {})
        wallet = self.gs["resources"].get("mora", 0)

        row = 0
        col = 0
        for cid, cd in CHARACTERS.items():
            card = ctk.CTkFrame(grid, fg_color="#1a1a35", corner_radius=8, border_width=1,
                                border_color=COLORS["gold"] if cid not in owned and wallet >= self.CHAR_PRICES[cid] else COLORS["border"])
            card.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")

            ctk.CTkLabel(card, text=ELEMENTS[cd["element"]]["icon"],
                         font=("Microsoft YaHei", 28)).pack(pady=(8, 0))
            ctk.CTkLabel(card, text=cd["name"],
                         font=("Microsoft YaHei", 13, "bold"), text_color=COLORS["text"]).pack()
            ctk.CTkLabel(card, text="⭐" * cd["stars"],
                         font=("Microsoft YaHei", 11), text_color=COLORS["gold"]).pack()
            ctk.CTkLabel(card, text=f"{ELEMENTS[cd['element']]['name']} · {cd['role']}",
                         font=("Microsoft YaHei", 10), text_color=COLORS["text_secondary"]).pack()
            ctk.CTkLabel(card, text=cd["description"],
                         font=("Microsoft YaHei", 9), text_color=COLORS["text_secondary"],
                         wraplength=140).pack(pady=(2, 4))

            price = self.CHAR_PRICES[cid]
            if cid in owned:
                btn = ctk.CTkButton(card, text="已拥有 ✓", font=("Microsoft YaHei", 10),
                                    fg_color="#1a3a1a", hover_color="#1a3a1a", text_color="#6a6",
                                    height=26, state="disabled")
            elif wallet >= price:
                btn = ctk.CTkButton(card, text=f"🪙 {format_num(price)} 购买", font=("Microsoft YaHei", 10),
                                    fg_color="#8a6520", hover_color="#a08030", text_color="#fff",
                                    height=26, command=lambda c=cid: self._buy_char(c))
            else:
                btn = ctk.CTkButton(card, text=f"🪙 {format_num(price)} (不足)", font=("Microsoft YaHei", 10),
                                    fg_color="#333", hover_color="#333", text_color="#555",
                                    height=26, state="disabled")
            btn.pack(pady=(0, 8))

            col += 1
            if col >= 4:
                col = 0
                row += 1

        for i in range(4):
            grid.grid_columnconfigure(i, weight=1)

    def _buy_char(self, char_id):
        price = self.CHAR_PRICES[char_id]
        if self.gs["resources"].get("mora", 0) < price:
            messagebox.showwarning("摩拉不足", f"需要{price}摩拉！")
            return
        if char_id in self.gs["characters"]:
            messagebox.showwarning("提示", "已拥有该角色！")
            return

        self.gs["resources"]["mora"] -= price
        self.gs["characters"][char_id] = {"level": 1, "constellation": 0, "exp": 0}
        cd = CHARACTERS[char_id]
        self._update_resource_bar()
        self._save_state()
        self._refresh_shop()
        messagebox.showinfo("购买成功", f"{ELEMENTS[cd['element']]['icon']} {cd['name']} 已加入队伍！")

    # ============================================================
    #  编队页面
    # ============================================================

    def _build_team_page(self):
        self.team_parent = self.content_frames["team"]

    def _refresh_team(self):
        parent = self.team_parent
        for w in parent.winfo_children():
            w.destroy()

        team = self.gs.get("team", [])

        # 上方：队伍槽位
        top = ctk.CTkFrame(parent, fg_color="transparent")
        top.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(top, text=f"当前队伍 ({len(team)}/4)",
                     font=("Microsoft YaHei", 14, "bold"),
                     text_color=COLORS["gold_light"]).pack(anchor="w")
        ctk.CTkLabel(top, text="相同元素≥2触发元素共鸣",
                     font=("Microsoft YaHei", 10),
                     text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 6))

        # 4个槽位
        slots_frame = ctk.CTkFrame(top, fg_color="transparent")
        slots_frame.pack(fill="x")

        for i in range(4):
            slot = ctk.CTkFrame(slots_frame, fg_color="#1a1a35", corner_radius=8,
                                border_width=2)
            if i < len(team):
                cid = team[i]
                cd = self.gs["characters"].get(cid)
                if cd and cid in CHARACTERS:
                    cinfo = CHARACTERS[cid]
                    slot.configure(border_color=COLORS["border"])
                    inner = ctk.CTkFrame(slot, fg_color="transparent")
                    inner.pack(fill="x", padx=10, pady=8)
                    ctk.CTkLabel(inner, text=ELEMENTS[cinfo["element"]]["icon"],
                                 font=("Microsoft YaHei", 20)).pack(side="left", padx=(0, 6))
                    ctk.CTkLabel(inner, text=cinfo["name"],
                                 font=("Microsoft YaHei", 12, "bold"),
                                 text_color=COLORS["text"]).pack(side="left")
                    ctk.CTkLabel(inner, text=f"Lv.{cd['level']}",
                                 font=("Microsoft YaHei", 10),
                                 text_color=COLORS["text_secondary"]).pack(side="left", padx=4)
                    ctk.CTkButton(inner, text="✕", width=24, height=24,
                                  fg_color="transparent", text_color=COLORS["hp_red"],
                                  hover_color="#331111",
                                  command=lambda idx=i: self._team_remove(idx)).pack(side="right")
                else:
                    slot.configure(border_color="#2a2a2a")
                    ctk.CTkLabel(slot, text="空位", font=("Microsoft YaHei", 12),
                                 text_color="#555").pack(pady=16)
            else:
                slot.configure(border_color="#2a2a2a")
                ctk.CTkLabel(slot, text="空位", font=("Microsoft YaHei", 12),
                             text_color="#555").pack(pady=16)
            slot.pack(side="left", fill="x", expand=True, padx=3)

        # 共鸣显示
        elem_counts = {}
        for cid in team:
            cd = CHARACTERS.get(cid)
            if cd:
                elem_counts[cd["element"]] = elem_counts.get(cd["element"], 0) + 1

        res_effects = {
            "fire": "全队攻击力+25%", "water": "全队受治疗+30%",
            "thunder": "充能效率+30%", "ice": "暴击率+15%",
            "wind": "冷却时间-15%", "rock": "护盾强效+15%", "grass": "全队精通+80",
        }
        res_frame = ctk.CTkFrame(top, fg_color="transparent")
        res_frame.pack(fill="x", pady=4)
        for elem, cnt in elem_counts.items():
            if cnt >= 2:
                ctk.CTkLabel(res_frame, text=f"{ELEMENTS[elem]['icon']} {elem}共鸣: {res_effects.get(elem, '')}",
                             font=("Microsoft YaHei", 11), text_color=COLORS["gold_light"],
                             fg_color="transparent").pack(side="left", padx=8)

        # 保存按钮
        if team:
            ctk.CTkButton(top, text="💾 保存编队", font=("Microsoft YaHei", 12),
                          fg_color="#8a6520", hover_color="#a08030", text_color="#fff",
                          command=self._team_save).pack(pady=(8, 0))

        # 下方：角色列表
        ctk.CTkLabel(parent, text="角色列表（点击加入/移出队伍）",
                     font=("Microsoft YaHei", 13, "bold"),
                     text_color=COLORS["gold_light"]).pack(anchor="w", pady=(12, 6))

        roster_frame = ctk.CTkFrame(parent, fg_color="transparent")
        roster_frame.pack(fill="x")

        chars = self.gs.get("characters", {})
        if not chars:
            ctk.CTkLabel(parent, text="还没有角色，去商店购买吧！",
                         font=("Microsoft YaHei", 12),
                         text_color=COLORS["text_secondary"]).pack(pady=20)
            return

        row = 0
        col = 0
        for cid, cs in chars.items():
            cd = CHARACTERS.get(cid)
            if not cd:
                continue
            in_team = cid in team
            card = ctk.CTkFrame(roster_frame, fg_color="#1a1a35", corner_radius=6,
                                border_width=1,
                                border_color=COLORS["accent_blue"] if in_team else COLORS["border"])
            card.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")

            ctk.CTkLabel(card, text=ELEMENTS[cd["element"]]["icon"],
                         font=("Microsoft YaHei", 22)).pack(pady=(6, 0))
            ctk.CTkLabel(card, text=cd["name"],
                         font=("Microsoft YaHei", 11, "bold"), text_color=COLORS["text"]).pack()
            ctk.CTkLabel(card, text=f"Lv.{cs['level']} ⭐{cd['stars']}",
                         font=("Microsoft YaHei", 10),
                         text_color=COLORS["text_secondary"]).pack(pady=(0, 6))

            # 点击
            for child in card.winfo_children():
                child.bind("<Button-1>", lambda e, cid=cid: self._team_toggle(cid))
            card.bind("<Button-1>", lambda e, cid=cid: self._team_toggle(cid))

            col += 1
            if col >= 4:
                col = 0
                row += 1

        # 配置grid列权重
        for i in range(4):
            roster_frame.grid_columnconfigure(i, weight=1)

    def _team_toggle(self, cid):
        team = list(self.gs.get("team", []))
        if cid in team:
            team.remove(cid)
        else:
            if len(team) >= 4:
                messagebox.showwarning("提示", "队伍已满（最多4人）")
                return
            team.append(cid)
        self.gs["team"] = team
        self._refresh_team()

    def _team_remove(self, index):
        team = list(self.gs.get("team", []))
        if 0 <= index < len(team):
            team.pop(index)
            self.gs["team"] = team
            self._refresh_team()

    def _team_save(self):
        self._save_state()
        self._update_resource_bar()
        messagebox.showinfo("提示", "编队已保存！")

    # ============================================================
    #  角色页面
    # ============================================================

    def _build_chars_page(self):
        self.chars_parent = self.content_frames["chars"]
        self.char_detail_frame = None

    def _refresh_chars(self):
        parent = self.chars_parent
        for w in parent.winfo_children():
            w.destroy()

        ctk.CTkLabel(parent, text="我的角色", font=("Microsoft YaHei", 15, "bold"),
                     text_color=COLORS["gold_light"]).pack(anchor="w", pady=(0, 8))

        chars = self.gs.get("characters", {})
        if not chars:
            ctk.CTkLabel(parent, text="还没有角色，去商店购买吧！",
                         font=("Microsoft YaHei", 12),
                         text_color=COLORS["text_secondary"]).pack(pady=40)
            return

        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x")

        row = 0
        col = 0
        for cid, cs in chars.items():
            cd = CHARACTERS.get(cid)
            if not cd:
                continue

            card = ctk.CTkFrame(grid, fg_color="#1a1a35", corner_radius=8, border_width=1,
                                border_color=COLORS["border"])
            card.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")

            ctk.CTkLabel(card, text=ELEMENTS[cd["element"]]["icon"],
                         font=("Microsoft YaHei", 28)).pack(pady=(8, 0))
            ctk.CTkLabel(card, text=cd["name"],
                         font=("Microsoft YaHei", 13, "bold"), text_color=COLORS["text"]).pack()
            ctk.CTkLabel(card, text="⭐" * cd["stars"],
                         font=("Microsoft YaHei", 11), text_color=COLORS["gold"]).pack()
            ctk.CTkLabel(card, text=f"Lv.{cs['level']} / {MAX_LEVEL[cd['stars']]} | 命{cs.get('constellation', 0)}",
                         font=("Microsoft YaHei", 10), text_color=COLORS["text_secondary"]).pack()
            ctk.CTkLabel(card, text=f"{ELEMENTS[cd['element']]['name']} · {cd['role']}",
                         font=("Microsoft YaHei", 10), text_color=COLORS["text_secondary"]).pack(pady=(0, 6))

            # 升级按钮
            books = get_exp_books_for_level(cs["level"])
            can_up = cs["level"] < MAX_LEVEL[cd["stars"]] and self.gs["resources"].get("exp_books", 0) >= books
            btn = ctk.CTkButton(card, text=f"📘 升级({books}书)", font=("Microsoft YaHei", 10),
                                fg_color="#8a6520" if can_up else "#333",
                                hover_color="#a08030" if can_up else "#333",
                                text_color="#fff" if can_up else "#555",
                                height=26, width=120,
                                command=lambda cid=cid: self._levelup_char(cid))
            btn.pack(pady=(0, 8))
            if not can_up and cs["level"] >= MAX_LEVEL[cd["stars"]]:
                btn.configure(text="已满级", state="disabled")

            col += 1
            if col >= 4:
                col = 0
                row += 1

        for i in range(4):
            grid.grid_columnconfigure(i, weight=1)

    def _levelup_char(self, cid):
        if cid not in self.gs["characters"]:
            return
        cs = self.gs["characters"][cid]
        cd = CHARACTERS.get(cid)
        if not cd:
            return
        max_lv = MAX_LEVEL[cd["stars"]]
        if cs["level"] >= max_lv:
            messagebox.showwarning("提示", "已满级！")
            return
        books = get_exp_books_for_level(cs["level"])
        if self.gs["resources"].get("exp_books", 0) < books:
            messagebox.showwarning("经验书不足", f"需要{books}本经验书！")
            return

        self.gs["resources"]["exp_books"] -= books
        cs["level"] += 1
        self._update_resource_bar()
        self._save_state()
        self._refresh_chars()

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
        stage = next((s for s in STAGES if s["id"] == self.gs["stage_progress"]["current_stage"]), None)
        mora_per_h = stage["mora_per_hour"] if stage else 100

        mora = int(mora_per_h * hours * 0.7)
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

    # ==================== 刷新所有 ====================

    def _refresh_all(self):
        self._update_resource_bar()


# ==================== 启动 ====================
if __name__ == "__main__":
    app = TiwateGame()
    app.mainloop()