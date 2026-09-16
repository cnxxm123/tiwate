"""
提瓦特放置游戏 - 塔防战斗引擎（陷阱+塔版本）
处理：地图、塔部署、陷阱放置、敌人路径移动、攻击、元素反应、波次管理
"""
import time
import math
import random
from .data import (
    ELEMENTS, BUILDING_DEFS, TD_MAPS, TD_ENEMY_STATS,
    TD_REACTIONS, TD_REACTION_WINDOW
)


class Trap:
    """陷阱（放在路径上，敌人经过时触发元素附着）"""

    def __init__(self, bid, bdef, grid_x, grid_y, cell_size):
        self.bid = bid
        self.name = bdef["name"]
        self.element = bdef["element"]
        self.cost = bdef["cost"]
        self.icon = bdef.get("icon", "?")
        self.color = bdef.get("color", "#fff")
        self.cooldown = bdef.get("cooldown", 2.0)
        self.cooldown_remaining = 0
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.px = grid_x * cell_size + cell_size / 2
        self.py = grid_y * cell_size + cell_size / 2
        self.cell_size = cell_size
        self.trigger_count = 0  # 触发次数统计

    def can_trigger(self):
        return self.cooldown_remaining <= 0

    def trigger(self):
        self.cooldown_remaining = self.cooldown
        self.trigger_count += 1

    def update(self, dt):
        if self.cooldown_remaining > 0:
            self.cooldown_remaining -= dt


class Tower:
    """塔（放在空地上，自动攻击射程内的敌人）"""

    def __init__(self, bid, bdef, grid_x, grid_y, cell_size):
        self.bid = bid
        self.name = bdef["name"]
        self.element = bdef["element"]
        self.cost = bdef["cost"]
        self.range = bdef["range"]
        self.atk_speed = bdef["atk_speed"]
        self.damage = bdef["damage"]
        self.icon = bdef.get("icon", "?")
        self.color = bdef.get("color", "#fff")
        self.max_hp = 300
        self.hp = self.max_hp
        self.shield = 0
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.px = grid_x * cell_size + cell_size / 2
        self.py = grid_y * cell_size + cell_size / 2
        self.cell_size = cell_size
        self.attack_cooldown = 0
        self.target = None
        self.dmg_bonus = 0

    def get_effective_damage(self):
        return int(self.damage * (1 + self.dmg_bonus))

    def can_attack(self):
        return self.attack_cooldown <= 0

    def reset_cooldown(self):
        self.attack_cooldown = 1.0 / max(self.atk_speed, 0.1)

    def find_target(self, enemies):
        """在射程内优先攻击进度最高的敌人"""
        best = None
        best_progress = -1
        for enemy in enemies:
            if enemy.dead or enemy.reached_end:
                continue
            dist = math.hypot(enemy.px - self.px, enemy.py - self.py)
            cell_dist = dist / self.cell_size
            if cell_dist <= self.range:
                if enemy.path_index > best_progress:
                    best = enemy
                    best_progress = enemy.path_index
                elif enemy.path_index == best_progress and best is not None:
                    if dist < math.hypot(best.px - self.px, best.py - self.py):
                        best = enemy
        return best

    def take_damage(self, dmg):
        if self.shield > 0:
            if self.shield >= dmg:
                self.shield -= dmg
                return 0
            dmg -= self.shield
            self.shield = 0
        actual = min(self.hp, dmg)
        self.hp -= actual
        return actual

    def is_destroyed(self):
        return self.hp <= 0

    def update(self, dt):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt


class Enemy:
    """塔防敌人"""

    def __init__(self, enemy_id, path, cell_size, wave_level=1):
        stats = TD_ENEMY_STATS[enemy_id]
        self.id = enemy_id
        self.name = stats["name"]
        self.element = stats.get("element")
        self.color = stats["color"]
        self.max_hp = int(stats["hp"] * (1 + (wave_level - 1) * 0.3))
        self.hp = self.max_hp
        self.base_speed = stats["speed"] * cell_size
        self.speed = self.base_speed
        self.gold_reward = stats["gold"]
        self.path = path
        self.cell_size = cell_size
        self.path_index = 0
        self.px, self.py = self._path_pos(0)
        self.dead = False
        self.reached_end = False
        self.frozen = False
        self.frozen_timer = 0
        self.slowed = False
        self.slow_timer = 0
        self.slow_amount = 0
        self.def_down = 0
        self.def_down_timer = 0
        self.dot_damage = 0
        self.dot_timer = 0
        self.last_trap_trigger = {}  # {trap_bid: timestamp} 每个陷阱的独立冷却
        self.element_hits = []

    def _path_pos(self, idx):
        if idx >= len(self.path):
            idx = len(self.path) - 1
        gx, gy = self.path[idx]
        return gx * self.cell_size + self.cell_size / 2, gy * self.cell_size + self.cell_size / 2

    def update(self, dt):
        if self.frozen:
            self.frozen_timer -= dt
            if self.frozen_timer <= 0:
                self.frozen = False
            return

        effective_speed = self.speed
        if self.slowed:
            self.slow_timer -= dt
            effective_speed *= (1 - self.slow_amount)
            if self.slow_timer <= 0:
                self.slowed = False

        if self.def_down > 0:
            self.def_down_timer -= dt
            if self.def_down_timer <= 0:
                self.def_down = 0

        if self.dot_damage > 0:
            self.dot_timer -= dt
            self.hp -= int(self.dot_damage * dt)
            if self.dot_timer <= 0:
                self.dot_damage = 0

        self.path_index += (effective_speed * dt) / self.cell_size
        idx = int(self.path_index)
        if idx >= len(self.path) - 1:
            self.reached_end = True
            self.px, self.py = self._path_pos(len(self.path) - 1)
        else:
            frac = self.path_index - idx
            x1, y1 = self._path_pos(idx)
            x2, y2 = self._path_pos(idx + 1)
            self.px = x1 + (x2 - x1) * frac
            self.py = y1 + (y2 - y1) * frac

        if self.hp <= 0:
            self.hp = 0
            self.dead = True

    def take_damage(self, dmg, element=None):
        if self.dead:
            return 0
        if self.def_down > 0:
            dmg = int(dmg * (1 + self.def_down))
        actual = min(self.hp, dmg)
        self.hp -= actual
        if element:
            now = time.time()
            self.element_hits.append((element, now))
            self.element_hits = [(e, t) for e, t in self.element_hits
                                 if now - t < TD_REACTION_WINDOW]
        if self.hp <= 0:
            self.dead = True
        return actual

    def apply_element(self, element):
        """直接附着元素（陷阱触发时调用）"""
        now = time.time()
        self.element_hits.append((element, now))
        self.element_hits = [(e, t) for e, t in self.element_hits
                              if now - t < TD_REACTION_WINDOW]

    def get_active_element(self):
        """返回敌人当前活跃的元素：优先 element_hits 中最近附着的，其次固有元素"""
        now = time.time()
        # 清理过期记录
        self.element_hits = [(e, t) for e, t in self.element_hits
                             if now - t < TD_REACTION_WINDOW]
        if self.element_hits:
            return self.element_hits[-1][0]  # 最近附着的元素
        return self.element

    def check_reaction(self, new_element):
        now = time.time()
        other = None
        for elem, ts in self.element_hits:
            if elem != new_element and now - ts < TD_REACTION_WINDOW:
                other = elem
                break
        if not other:
            return None
        key = f"{new_element}+{other}"
        return TD_REACTIONS.get(key)

    def apply_freeze(self, duration):
        self.frozen = True
        self.frozen_timer = duration

    def apply_slow(self, amount, duration):
        self.slowed = True
        self.slow_amount = max(self.slow_amount, amount)
        self.slow_timer = max(self.slow_timer, duration)

    def apply_dot(self, dps, duration):
        self.dot_damage = dps
        self.dot_timer = duration

    def apply_def_down(self, amount, duration):
        self.def_down = amount
        self.def_down_timer = duration


class Projectile:
    """箭矢/弹道：从塔飞向目标的飞行物"""

    def __init__(self, start_x, start_y, target_x, target_y, color="#fff"):
        self.x = start_x
        self.y = start_y
        self.start_x = start_x
        self.start_y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.color = color
        self.progress = 0  # 0→1，1 表示到达
        self.speed = 8  # 每秒前进的比例

    def update(self, dt):
        self.progress += self.speed * dt
        self.x = self.start_x + (self.target_x - self.start_x) * min(self.progress, 1)
        self.y = self.start_y + (self.target_y - self.start_y) * min(self.progress, 1)
        return self.progress >= 1  # 返回是否到达


class TDEngine:
    """塔防游戏引擎（陷阱+塔版本）"""

    def __init__(self, map_data):
        self.map = map_data
        self.width = map_data["width"]
        self.height = map_data["height"]
        self.cell_size = map_data["cell_size"]
        self.path = map_data["path"]
        self.waves = map_data["waves"]
        self.gold = map_data["starting_gold"]
        self.max_lives = map_data["lives"]
        self.lives = self.max_lives

        self.towers = []
        self.traps = []
        self.enemies = []
        self.wave_index = -1
        self.wave_active = False
        self.wave_spawn_interval = 1.0
        self.wave_spawn_timer = 0
        self.wave_spawn_queue = []

        self.running = False
        self.paused = False
        self.game_over = False
        self.victory = False
        self.game_time = 0

        self.effects = []
        self.projectiles = []
        self.kill_count = 0
        self.gold_earned = 0

        self.path_set = set(self.path)
        self.buildable = []
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in self.path_set:
                    self.buildable.append((x, y))

    def can_place_tower(self, grid_x, grid_y):
        """塔只能放在空地（非路径）"""
        if (grid_x, grid_y) in self.path_set:
            return False
        if not (0 <= grid_x < self.width and 0 <= grid_y < self.height):
            return False
        for t in self.towers:
            if t.grid_x == grid_x and t.grid_y == grid_y:
                return False
        return True

    def can_place_trap(self, grid_x, grid_y):
        """陷阱必须放在路径上，且该格子上没有其他陷阱"""
        if (grid_x, grid_y) not in self.path_set:
            return False
        if not (0 <= grid_x < self.width and 0 <= grid_y < self.height):
            return False
        for tr in self.traps:
            if tr.grid_x == grid_x and tr.grid_y == grid_y:
                return False
        return True

    def place_tower(self, bid, grid_x, grid_y):
        bdef = BUILDING_DEFS.get(bid)
        if not bdef or bdef["type"] != "tower":
            return None
        if not self.can_place_tower(grid_x, grid_y):
            return None
        if self.gold < bdef["cost"]:
            return None
        tower = Tower(bid, bdef, grid_x, grid_y, self.cell_size)
        self.gold -= tower.cost
        self.towers.append(tower)
        return tower

    def place_trap(self, bid, grid_x, grid_y):
        bdef = BUILDING_DEFS.get(bid)
        if not bdef or bdef["type"] != "trap":
            return None
        if not self.can_place_trap(grid_x, grid_y):
            return None
        if self.gold < bdef["cost"]:
            return None
        trap = Trap(bid, bdef, grid_x, grid_y, self.cell_size)
        self.gold -= trap.cost
        self.traps.append(trap)
        return trap

    def sell_trap_or_tower(self, grid_x, grid_y):
        """出售指定位置的建筑"""
        for t in self.towers:
            if t.grid_x == grid_x and t.grid_y == grid_y:
                refund = t.cost // 2
                self.gold += refund
                self.towers.remove(t)
                return True
        for tr in self.traps:
            if tr.grid_x == grid_x and tr.grid_y == grid_y:
                refund = tr.cost // 2
                self.gold += refund
                self.traps.remove(tr)
                return True
        return False

    def start(self):
        self.running = True
        self._start_next_wave()

    def _start_next_wave(self):
        self.wave_index += 1
        if self.wave_index >= len(self.waves):
            return
        wave = self.waves[self.wave_index]
        self.wave_active = True
        self.wave_spawn_interval = wave["interval"]
        self.wave_spawn_timer = 0
        queue = []
        for enemy_id, count in wave["enemies"]:
            for _ in range(count):
                queue.append(enemy_id)
        random.shuffle(queue)
        self.wave_spawn_queue = queue

    def _spawn_enemy(self):
        if not self.wave_spawn_queue:
            return
        eid = self.wave_spawn_queue.pop(0)
        enemy = Enemy(eid, self.path, self.cell_size, self.wave_index + 1)
        self.enemies.append(enemy)

    def _check_enemy_reaction(self, enemy, new_element):
        reaction = enemy.check_reaction(new_element)
        if not reaction:
            return
        pos_x, pos_y = enemy.px, enemy.py
        if reaction.get("freeze"):
            enemy.apply_freeze(reaction["freeze_duration"])
            self._add_effect("reaction", pos_x, pos_y, f"❄️冻结", "#7df")
        elif reaction.get("dot"):
            enemy.apply_dot(reaction["dot_dmg"], reaction["dot_duration"])
            self._add_effect("reaction", pos_x, pos_y, f"⚡感电", "#a0f")
        elif reaction.get("aoe"):
            radius = reaction["aoe_radius"] * self.cell_size
            aoe_dmg = int(enemy.max_hp * 0.1 * reaction["aoe_dmg_ratio"])
            aoe_dmg = max(aoe_dmg, 20)
            for other in self.enemies:
                if other is enemy or other.dead:
                    continue
                dist = math.hypot(other.px - pos_x, other.py - pos_y)
                if dist <= radius:
                    other.take_damage(aoe_dmg, enemy.element)
            if reaction.get("def_down"):
                enemy.apply_def_down(reaction["def_down"], reaction.get("def_down_dur", 4.0))
            self._add_effect("reaction", pos_x, pos_y, f"💥{reaction['name']}", "#f80")
        elif reaction.get("dmg_mult"):
            self._add_effect("reaction", pos_x, pos_y, f"✨{reaction['name']}", "#ff0")

    def _add_effect(self, etype, px, py, text, color):
        self.effects.append({"type": etype, "px": px, "py": py, "timer": 1.2,
                             "text": text, "color": color})

    def update(self, dt):
        if not self.running or self.game_over:
            return

        self.game_time += dt

        # 波次管理
        if self.wave_active:
            self.wave_spawn_timer -= dt
            if self.wave_spawn_timer <= 0 and self.wave_spawn_queue:
                self._spawn_enemy()
                self.wave_spawn_timer = self.wave_spawn_interval

            if not self.wave_spawn_queue:
                alive = [e for e in self.enemies if not e.dead and not e.reached_end]
                if not alive:
                    self.wave_active = False
                    wave_bonus = 50 + self.wave_index * 30
                    self.gold += wave_bonus
                    self._add_effect("wave", self.width * self.cell_size / 2,
                                     self.height * self.cell_size / 2,
                                     f"第{self.wave_index + 1}波完成! +{wave_bonus}💰", "#ff0")
                    if self.wave_index >= len(self.waves) - 1:
                        self.game_over = True
                        self.victory = True
                    else:
                        self._start_next_wave()

        # 更新塔 + 攻击
        for tower in self.towers:
            tower.update(dt)
            if tower.can_attack():
                target = tower.find_target(self.enemies)
                if target:
                    dmg = tower.get_effective_damage()
                    # 检查反应加成
                    target_element = target.get_active_element()
                    reaction = TD_REACTIONS.get(
                        f"{tower.element}+{target_element}" if target_element else None)
                    if reaction and reaction.get("dmg_mult"):
                        dmg = int(dmg * reaction["dmg_mult"])
                    actual = target.take_damage(dmg, tower.element)
                    self._check_enemy_reaction(target, tower.element)
                    tower.reset_cooldown()
                    # 生成箭矢弹道
                    self.projectiles.append(Projectile(
                        tower.px, tower.py, target.px, target.py,
                        color=ELEMENTS[tower.element]["color"]
                    ))
                    if actual > 0:
                        self._add_effect("damage", target.px, target.py,
                                         f"-{actual}", ELEMENTS[tower.element]["color"])

        # 更新陷阱
        for trap in self.traps:
            trap.update(dt)
            if trap.can_trigger():
                for enemy in self.enemies:
                    if enemy.dead or enemy.reached_end:
                        continue
                    # 检查敌人是否经过该陷阱格子
                    egx = int(enemy.px // self.cell_size)
                    egy = int(enemy.py // self.cell_size)
                    if egx == trap.grid_x and egy == trap.grid_y:
                        # 检查该敌人对该陷阱的独立冷却
                        last_t = enemy.last_trap_trigger.get(trap.bid, 0)
                        if time.time() - last_t >= trap.cooldown:
                            enemy.apply_element(trap.element)
                            trap.trigger()
                            enemy.last_trap_trigger[trap.bid] = time.time()
                            self._add_effect("trap", enemy.px, enemy.py,
                                             f"💧附着", ELEMENTS[trap.element]["color"])

        # 更新敌人
        for enemy in self.enemies:
            if enemy.dead or enemy.reached_end:
                continue
            enemy.update(dt)
            if enemy.reached_end:
                self.lives -= 1
                self._add_effect("leak", enemy.px, enemy.py, "漏怪! ❤️-1", "#f44")
                if self.lives <= 0:
                    self.game_over = True
                    self.victory = False
            elif enemy.dead:
                self.gold += enemy.gold_reward
                self.gold_earned += enemy.gold_reward
                self.kill_count += 1
                self._add_effect("gold", enemy.px, enemy.py, f"+{enemy.gold_reward}💰", "#ff0")

        self.enemies = [e for e in self.enemies if not e.dead and not e.reached_end]
        self.effects = [ef for ef in self.effects if ef["timer"] > 0]
        for ef in self.effects:
            ef["timer"] -= dt
        # 更新弹道，移除已到达的
        self.projectiles = [p for p in self.projectiles if not p.update(dt)]
        self.towers = [t for t in self.towers if not t.is_destroyed()]

    def resize(self, new_cell_size):
        """窗口大小变化时重新计算所有实体坐标"""
        if new_cell_size == self.cell_size:
            return
        ratio = new_cell_size / self.cell_size
        self.cell_size = new_cell_size

        for t in self.towers:
            t.cell_size = new_cell_size
            t.px = t.grid_x * new_cell_size + new_cell_size / 2
            t.py = t.grid_y * new_cell_size + new_cell_size / 2

        for tr in self.traps:
            tr.cell_size = new_cell_size
            tr.px = tr.grid_x * new_cell_size + new_cell_size / 2
            tr.py = tr.grid_y * new_cell_size + new_cell_size / 2

        for e in self.enemies:
            if e.dead or e.reached_end:
                continue
            e.speed = e.speed * ratio
            e.base_speed = e.base_speed * ratio
            e.cell_size = new_cell_size
            idx_i = int(e.path_index)
            if idx_i >= len(e.path) - 1:
                gx, gy = e.path[-1]
                e.px = gx * new_cell_size + new_cell_size / 2
                e.py = gy * new_cell_size + new_cell_size / 2
            else:
                frac = e.path_index - idx_i
                x1 = e.path[idx_i][0] * new_cell_size + new_cell_size / 2
                y1 = e.path[idx_i][1] * new_cell_size + new_cell_size / 2
                x2 = e.path[idx_i + 1][0] * new_cell_size + new_cell_size / 2
                y2 = e.path[idx_i + 1][1] * new_cell_size + new_cell_size / 2
                e.px = x1 + (x2 - x1) * frac
                e.py = y1 + (y2 - y1) * frac

        for ef in self.effects:
            ef["px"] *= ratio
            ef["py"] *= ratio

        for p in self.projectiles:
            p.x *= ratio
            p.y *= ratio
            p.start_x *= ratio
            p.start_y *= ratio
            p.target_x *= ratio
            p.target_y *= ratio

    def get_state(self):
        return {
            "running": self.running,
            "game_over": self.game_over,
            "victory": self.victory,
            "gold": self.gold,
            "lives": self.lives,
            "max_lives": self.max_lives,
            "wave": self.wave_index + 1,
            "total_waves": len(self.waves),
            "game_time": self.game_time,
            "kill_count": self.kill_count,
        }