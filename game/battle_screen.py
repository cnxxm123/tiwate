"""
战斗界面模块：地图渲染、战斗流程、交互处理
"""
import time
import random
import math
import copy
from tkinter import Menu, messagebox

from game.data import TD_MAPS, BUILDING_DEFS, ELEMENTS
from game.td_engine import TDEngine

GRASS_COLORS = ["#2d5a2d", "#356c35", "#2a4a2a"]
FLOWER_COLORS = ["#ffd700", "#ff9a9e", "#a0c4ff", "#fdffb6"]
GRID_GREEN = ["#1a3320", "#1f3a24", "#1c3522"]


class BattleScreen:
    """管理战斗界面的所有逻辑：进入地图、渲染、交互、战斗循环"""

    def __init__(self, app):
        self.app = app  # TiwateGame instance

    # ── 属性代理：简化 app.xxx 的访问 ──
    @property
    def battle(self):
        return self.app.battle

    @battle.setter
    def battle(self, v):
        self.app.battle = v

    @property
    def battle_stage_id(self):
        return self.app.battle_stage_id

    @property
    def td_cell_size(self):
        return self.app.td_cell_size

    @td_cell_size.setter
    def td_cell_size(self, v):
        self.app.td_cell_size = v

    @property
    def td_game_loop_id(self):
        return self.app.td_game_loop_id

    @td_game_loop_id.setter
    def td_game_loop_id(self, v):
        self.app.td_game_loop_id = v

    @property
    def td_last_time(self):
        return self.app.td_last_time

    @td_last_time.setter
    def td_last_time(self, v):
        self.app.td_last_time = v

    # ============================================================
    #  进入 / 退出地图
    # ============================================================

    def enter_map(self):
        app = self.app
        tdm = next((m for m in TD_MAPS if m["id"] == app.battle_stage_id), None)
        if not tdm:
            return

        app.top_bar.pack_forget()
        app.bottom_bar.pack_forget()
        app.stage_panel.pack_forget()
        app.content_frame.pack(fill="both", expand=True, padx=0, pady=0)
        app.battle_panel.pack(fill="both", expand=True)

        app.update_idletasks()
        app.update()

        mid_w = app.td_mid_frame.winfo_width()
        mid_h = app.td_mid_frame.winfo_height()
        if mid_w < 100:
            mid_w = app.winfo_width()
        if mid_h < 100:
            mid_h = app.winfo_height() - 50

        cs_w = mid_w // tdm["width"]
        cs_h = mid_h // tdm["height"]
        cell_size = max(50, min(cs_w, cs_h, 90))
        self.td_cell_size = cell_size

        tdm_copy = copy.deepcopy(tdm)
        tdm_copy["cell_size"] = cell_size
        self.battle = TDEngine(tdm_copy)
        app.battle_active = True

        self.update_top_bar()

        canvas_w = tdm_copy["width"] * cell_size
        canvas_h = tdm_copy["height"] * cell_size
        app.td_canvas.configure(width=canvas_w, height=canvas_h)
        app.td_canvas.delete("all")
        self.render_map()

        app.btn_td_start.configure(state="normal", text="▶ 开始出怪")
        app.td_canvas_frame.bind("<Configure>", self.on_canvas_resize)

    def return_to_stage_select(self):
        app = self.app
        if self.td_game_loop_id:
            app.after_cancel(self.td_game_loop_id)
            self.td_game_loop_id = None
        app.td_canvas_frame.unbind("<Configure>")
        app.content_frame.pack(fill="both", expand=True, padx=12, pady=(8, 0))
        app.top_bar.pack(fill="x", side="top")
        app.bottom_bar.pack(fill="x", side="bottom")
        app._show_stage_select()
        app._save_state()

    def on_canvas_resize(self, event=None):
        app = self.app
        if not self.battle or not app.battle_active:
            return
        tdm = next((m for m in TD_MAPS if m["id"] == app.battle_stage_id), None)
        if not tdm:
            return
        mid_w = app.td_mid_frame.winfo_width()
        mid_h = app.td_mid_frame.winfo_height()
        if mid_w < 100 or mid_h < 100:
            return
        cs_w = mid_w // tdm["width"]
        cs_h = mid_h // tdm["height"]
        new_cs = max(40, min(cs_w, cs_h))
        if abs(new_cs - self.td_cell_size) < 3:
            return

        self.td_cell_size = new_cs
        self.battle.resize(new_cs)
        app.td_canvas.configure(width=tdm["width"] * new_cs, height=tdm["height"] * new_cs)
        self.render_map()

    # ============================================================
    #  点击交互
    # ============================================================

    def on_click_canvas(self, event):
        app = self.app
        if not self.battle:
            return

        gx = event.x // self.td_cell_size
        gy = event.y // self.td_cell_size

        tdm = next((m for m in TD_MAPS if m["id"] == app.battle_stage_id), None)
        if not tdm:
            return
        if not (0 <= gx < tdm["width"] and 0 <= gy < tdm["height"]):
            return

        is_path = (gx, gy) in self.battle.path_set

        existing = None
        for t in self.battle.towers:
            if t.grid_x == gx and t.grid_y == gy:
                existing = t
                break
        for tr in self.battle.traps:
            if tr.grid_x == gx and tr.grid_y == gy:
                existing = tr
                break

        popup = Menu(app, tearoff=0, bg="#141428", fg="#e0d8c8",
                     activebackground="#2a2a45", activeforeground="#f0d68a",
                     font=("Microsoft YaHei", 11))

        if existing:
            popup.add_command(
                label=f"🏚 出售 {existing.name} (返还{existing.cost // 2}💰)",
                command=lambda: self.do_sell(gx, gy))
        else:
            for bid, bdef in BUILDING_DEFS.items():
                if bdef["type"] == "trap" and is_path:
                    popup.add_command(
                        label=f"{bdef['icon']} {bdef['name']}  [{bdef['cost']}💰]",
                        command=lambda b=bid: self.do_place(b, gx, gy))
                elif bdef["type"] == "tower" and not is_path:
                    popup.add_command(
                        label=f"{bdef['icon']} {bdef['name']}  [{bdef['cost']}💰]",
                        command=lambda b=bid: self.do_place(b, gx, gy))

        if popup.index("end") is not None:
            popup.tk_popup(event.x_root, event.y_root)

    def do_place(self, bid, gx, gy):
        bdef = BUILDING_DEFS[bid]
        if bdef["type"] == "tower":
            result = self.battle.place_tower(bid, gx, gy)
        else:
            result = self.battle.place_trap(bid, gx, gy)
        if result:
            self.render_map()
            self.update_top_bar()

    def do_sell(self, gx, gy):
        self.battle.sell_trap_or_tower(gx, gy)
        self.render_map()
        self.update_top_bar()

    # ============================================================
    #  战斗循环
    # ============================================================

    def start_wave(self):
        if not self.battle:
            return
        self.battle.start()
        self.app.btn_td_start.configure(state="disabled", text="出怪中...")
        self.td_last_time = time.time()
        self.game_loop()

    def game_loop(self):
        app = self.app
        if not self.battle or self.battle.game_over:
            self.handle_end()
            return
        if not app.battle_active:
            return

        now = time.time()
        dt = min(now - self.td_last_time, 0.1)
        self.td_last_time = now

        self.battle.update(dt)
        self.render_map()
        self.update_top_bar()

        if not self.battle.game_over:
            self.td_game_loop_id = app.after(16, self.game_loop)

    def update_top_bar(self):
        app = self.app
        if not self.battle:
            return
        app.lbl_td_gold.configure(text=f"💰 {self.battle.gold}")
        app.lbl_td_wave.configure(text=f"波次: {self.battle.wave_index + 1}/{len(self.battle.waves)}")
        app.lbl_td_lives.configure(text=f"❤️ {self.battle.lives}/{self.battle.max_lives}")
        t = self.battle.game_time
        app.lbl_td_info.configure(text=f"⏱ {int(t // 60)}:{int(t % 60):02d}  击杀:{self.battle.kill_count}")

    # ============================================================
    #  地图渲染
    # ============================================================

    def render_map(self):
        app = self.app
        canvas = app.td_canvas
        canvas.delete("all")
        if not self.battle:
            return

        tdm = next((m for m in TD_MAPS if m["id"] == app.battle_stage_id), None)
        if not tdm:
            return
        cs = self.td_cell_size
        path_set = self.battle.path_set

        self._draw_grid(canvas, tdm, cs, path_set)
        self._draw_decorations(canvas, tdm, cs, path_set)
        self._draw_path(canvas, tdm, cs, path_set)
        self._draw_entities(canvas, cs)

    def _draw_grid(self, canvas, tdm, cs, path_set):
        for y in range(tdm["height"]):
            for x in range(tdm["width"]):
                x1, y1 = x * cs, y * cs
                x2, y2 = x1 + cs, y1 + cs
                if (x, y) in path_set:
                    canvas.create_rectangle(x1, y1, x2, y2,
                                            fill="#4a3728", outline="#5a4738", width=0)
                else:
                    shade = (x + y) % 3
                    canvas.create_rectangle(x1, y1, x2, y2,
                                            fill=GRID_GREEN[shade], outline="#25402a", width=0)

    def _draw_decorations(self, canvas, tdm, cs, path_set):
        for y in range(tdm["height"]):
            for x in range(tdm["width"]):
                if (x, y) in path_set:
                    continue
                seed = x * 1000 + y
                random.seed(seed)
                cx, cy = x * cs + cs / 2, y * cs + cs / 2
                s = cs * 0.08
                for _ in range(random.randint(1, 3)):
                    dx = random.uniform(-cs * 0.35, cs * 0.35)
                    dy = random.uniform(-cs * 0.35, cs * 0.35)
                    kind = random.randint(0, 4)
                    if kind == 0:  # 草丛
                        canvas.create_polygon(
                            cx + dx - s * 1.5, cy + dy + s,
                            cx + dx, cy + dy - s * 1.5,
                            cx + dx + s * 1.5, cy + dy + s,
                            fill=random.choice(GRASS_COLORS), outline="")
                    elif kind == 1:  # 小花
                        if cs >= 45:
                            canvas.create_oval(
                                cx + dx - s, cy + dy - s,
                                cx + dx + s, cy + dy + s,
                                fill=random.choice(FLOWER_COLORS), outline="")
                    elif kind == 2:  # 小石子
                        canvas.create_oval(
                            cx + dx - s * 1.2, cy + dy - s * 0.7,
                            cx + dx + s * 0.8, cy + dy + s * 0.9,
                            fill="#3a3a40", outline="")
        random.seed()

    def _draw_path(self, canvas, tdm, cs, path_set):
        path = self.battle.path
        for i, (px, py) in enumerate(path):
            x1, y1 = px * cs + 1, py * cs + 1
            x2, y2 = px * cs + cs - 1, py * cs + cs - 1

            if i == 0:  # 起点
                canvas.create_rectangle(x1, y1, x2, y2,
                                        fill="#1a4a2a", outline="#4aff8a", width=2)
                canvas.create_rectangle(px * cs + cs * 0.2, py * cs + cs * 0.15,
                                        px * cs + cs * 0.8, py * cs + cs * 0.85,
                                        fill="#0d2818", outline="#6affaa", width=2)
                canvas.create_text(px * cs + cs / 2, py * cs + cs / 2,
                                   text="🚪", font=("Segoe UI Emoji", int(cs * 0.35)))
            elif i == len(path) - 1:  # 终点
                canvas.create_rectangle(x1, y1, x2, y2,
                                        fill="#3a1a1a", outline="#ff4a4a", width=2)
                canvas.create_oval(px * cs + cs * 0.2, py * cs + cs * 0.2,
                                   px * cs + cs * 0.8, py * cs + cs * 0.8,
                                   fill="#2a0000", outline="#ff6666", width=2)
                canvas.create_oval(px * cs + cs * 0.3, py * cs + cs * 0.3,
                                   px * cs + cs * 0.7, py * cs + cs * 0.7,
                                   fill="#200808", outline="#ff4444", width=2)
                canvas.create_text(px * cs + cs / 2, py * cs + cs / 2,
                                   text="🎯", font=("Segoe UI Emoji", int(cs * 0.35)))
            else:  # 路径中间
                canvas.create_rectangle(x1, y1, x2, y2,
                                        fill="#4a3728", outline="#5a4738", width=0)
                # 方向箭头
                if i % 2 == 0 and cs >= 40:
                    prev_x, prev_y = path[i - 1]
                    next_x, next_y = path[i + 1] if i + 1 < len(path) else (px, py)
                    dx = (next_x - prev_x) * cs * 0.35
                    dy = (next_y - prev_y) * cs * 0.35
                    mid_x = px * cs + cs / 2
                    mid_y = py * cs + cs / 2
                    canvas.create_line(mid_x - dx, mid_y - dy, mid_x + dx, mid_y + dy,
                                       arrow="last", arrowshape=(cs * 0.2, cs * 0.3, cs * 0.12),
                                       fill="#7a5a3a", width=2)

    def _draw_entities(self, canvas, cs):
        battle = self.battle

        # ── 陷阱 ──
        for tr in battle.traps:
            x, y = tr.grid_x * cs + cs / 2, tr.grid_y * cs + cs / 2
            r = cs * 0.4
            canvas.create_oval(x - r, y - r, x + r, y + r,
                               fill="#154060", outline="#4a9ad4", width=2)
            canvas.create_text(x, y, text="💧",
                               font=("Segoe UI Emoji", int(cs * 0.3)))

        # ── 塔 ──
        for tw in battle.towers:
            x, y = tw.grid_x * cs + cs / 2, tw.grid_y * cs + cs / 2
            r = cs * 0.38
            # 塔基阴影
            canvas.create_oval(x - r + 2, y - r + 2, x + r + 2, y + r + 2,
                               fill="#0a0a0a", outline="")
            canvas.create_oval(x - r, y - r, x + r, y + r,
                               fill="#2a2040", outline="#8b6baa", width=2)
            canvas.create_text(x, y, text="🏹",
                               font=("Segoe UI Emoji", int(cs * 0.3)))

        # ── 敌人 ──
        for e in battle.enemies:
            if e.dead:
                continue
            x, y = e.px, e.py
            r = cs * 0.3
            # 阴影
            canvas.create_oval(x - r + 2, y - r + 2, x + r + 2, y + r - 1,
                               fill="#0a0a0a", outline="")
            # 身体
            body_color = "#c84040"
            if e.id == "enemy_2":
                body_color = "#c86020"
            elif e.id == "enemy_3":
                body_color = "#9050a0"
            elif e.id == "enemy_4":
                body_color = "#6070a0"
            elif e.id == "enemy_5":
                body_color = "#a0a0a0"
            canvas.create_oval(x - r, y - r, x + r, y + r,
                               fill=body_color, outline="#222", width=1)
            # 生命条
            hp_ratio = e.hp / e.max_hp
            bar_w = cs * 0.6
            if hp_ratio > 0.5:
                hp_color = "#4aff4a"
            elif hp_ratio > 0.2:
                hp_color = "#ffaa00"
            else:
                hp_color = "#ff3333"
            canvas.create_rectangle(x - bar_w / 2, y - r - 5,
                                    x - bar_w / 2 + bar_w * hp_ratio, y - r - 2,
                                    fill=hp_color, outline="")
            if e.frozen:
                canvas.create_text(x, y - r - 10, text="❄️",
                                   font=("Segoe UI Emoji", int(cs * 0.1)))
            if e.element_hits:
                last_el = e.element_hits[-1][0]
                canvas.create_text(x + r + 4, y - r,
                                   text=ELEMENTS[last_el]["icon"],
                                   font=("Segoe UI Emoji", int(cs * 0.1)))

        # ── 特效 ──
        for ef in battle.effects:
            alpha = min(1, ef["timer"] / 1.2)
            font_size = int(10 + (1 - alpha) * 8)
            canvas.create_text(ef["px"], ef["py"] - 20 * (1 - alpha),
                               text=ef["text"],
                               font=("Microsoft YaHei", max(8, font_size)),
                               fill=ef["color"])

        # ── 弹道（箭矢）──
        for p in battle.projectiles:
            # 箭杆：从起点到当前位置画一条线
            dx = p.x - p.start_x
            dy = p.y - p.start_y
            length = math.hypot(dx, dy)
            if length > 0:
                # 箭矢角度
                angle = math.atan2(dy, dx)
                arrow_len = cs * 0.25
                # 箭杆
                canvas.create_line(p.start_x, p.start_y, p.x, p.y,
                                   fill=p.color, width=2)
                # 箭头（三角形）
                tip_x = p.x
                tip_y = p.y
                canvas.create_polygon(
                    tip_x, tip_y,
                    tip_x - arrow_len * math.cos(angle - 0.5),
                    tip_y - arrow_len * math.sin(angle - 0.5),
                    tip_x - arrow_len * math.cos(angle + 0.5),
                    tip_y - arrow_len * math.sin(angle + 0.5),
                    fill=p.color, outline="")

    # ============================================================
    #  结算
    # ============================================================

    def handle_end(self):
        app = self.app
        if self.td_game_loop_id:
            app.after_cancel(self.td_game_loop_id)
            self.td_game_loop_id = None

        app.btn_td_start.configure(state="disabled")

        if self.battle.victory:
            rewards = {
                "mora": self.battle.gold_earned + random.randint(200, 500),
                "exp_books": random.randint(1, 3),
                "adventure_exp": 15,
            }
            app._apply_rewards(rewards)
            app._update_resource_bar()

            if app.battle_stage_id not in app.gs["stage_progress"].get("completed_stages", []):
                app.gs["stage_progress"]["completed_stages"] = \
                    app.gs["stage_progress"].get("completed_stages", []) + [app.battle_stage_id]
            next_id = app.battle_stage_id + 1
            if next_id > app.gs["stage_progress"]["highest_stage_unlocked"]:
                if any(m["id"] == next_id for m in TD_MAPS):
                    app.gs["stage_progress"]["highest_stage_unlocked"] = next_id
            app._save_state()

            messagebox.showinfo("胜利！",
                                f"✨ 关卡完成！\n摩拉:{rewards['mora']} 书:{rewards['exp_books']}")
            self.return_to_stage_select()
        else:
            messagebox.showinfo("失败", "X 生命值归零，请重新挑战！")
            self.return_to_stage_select()