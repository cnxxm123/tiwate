"""
提瓦特放置游戏 - 塔防战斗引擎
处理：地图、塔部署、敌人路径移动、攻击、元素反应、波次管理
"""
import time
import math
import random
from .data import (
    ELEMENTS, CHARACTERS, TD_TOWER_STATS, TD_MAPS, TD_ENEMY_STATS,
    TD_REACTIONS, TD_REACTION_WINDOW
)


class Tower:
    """塔防中的塔（角色）"""

    def __init__(self, char_id, level, grid_x, grid_y, cell_size):
        self.char_id = char_id
        char_data = CHARACTERS[char_id]
        td_stats = TD_TOWER_STATS[char_id]

        self.name = char_data["name"]
        self.element = char_data["element"]
        self.stars = char_data["stars"]
        self.level = level

        # 塔属性（等级加成）
        lv_bonus = 1 + (level - 1) * 0.05
        self.cost = td_stats["cost"]
        self.range = td_stats["range"]
        self.atk_speed = td_stats["atk_speed"] * lv_bonus
        self.damage = int(td_stats["td_dmg"] * lv_bonus)
        self.max_hp = 100 + level * 20
        self.hp = self.max_hp
        self.shield = 0

        # 位置（格坐标和像素坐标）
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.px = grid_x * cell_size + cell_size / 2
        self.py = grid_y * cell_size + cell_size / 2
        self.cell_size = cell_size

        # 攻击状态
        self.attack_cooldown = 0  # 距下次攻击剩余时间
        self.target = None

        # 技能
        self.ability = td_stats["td_ability"]
        self.ability_cd = td_stats["td_ability_cd"]
        self.ability_cd_remaining = 0
        self.ability_desc = td_stats["td_ability_desc"]
        self.ability_active = False
        self.ability_timer = 0

        # 增益
        self.dmg_bonus = 0  # 伤害加成百分比
        self.speed_bonus = 0

        # 特殊状态
        self.oz_tower = None  # 菲谢尔的奥兹（独立攻击塔）
        self.coordinated = False  # 行秋的协同攻击状态

    def get_effective_damage(self):
        return int(self.damage * (1 + self.dmg_bonus))

    def get_effective_atk_speed(self):
        return self.atk_speed * (1 + self.speed_bonus)

    def can_attack(self):
        return self.attack_cooldown <= 0

    def reset_cooldown(self):
        speed = self.get_effective_atk_speed()
        self.attack_cooldown = 1.0 / max(speed, 0.1)

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

    def heal(self, amount):
        self.hp = min(self.hp + amount, self.max_hp)

    def update(self, dt):
        """更新塔状态"""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if self.ability_cd_remaining > 0:
            self.ability_cd_remaining -= dt
        if self.ability_active:
            self.ability_timer -= dt
            if self.ability_timer <= 0:
                self.ability_active = False
                if self.coordinated:
                    self.coordinated = False
                    self.speed_bonus = 0

    def use_ability(self):
        """使用技能"""
        if self.ability_cd_remaining > 0:
            return False
        self.ability_cd_remaining = self.ability_cd
        self.ability_active = True

        if self.ability == "coordinated_atk":
            self.coordinated = True
            self.speed_bonus = 1.0
            self.ability_timer = 5.0
        elif self.ability == "atk_buff":
            self.ability_timer = 6.0
        elif self.ability == "summon_oz":
            self.ability_timer = 8.0
        elif self.ability == "shield_slow":
            self.ability_timer = 4.0
        elif self.ability == "dmg_debuff":
            self.ability_timer = 5.0
        else:
            self.ability_timer = 0.5
        return True

    def find_target(self, enemies):
        """在射程内优先攻击进度最高且非冻结的敌人"""
        best = None
        best_priority = -1
        for enemy in enemies:
            if enemy.dead or enemy.reached_end:
                continue
            dist = math.hypot(enemy.px - self.px, enemy.py - self.py)
            cell_dist = dist / self.cell_size
            if cell_dist <= self.range:
                # 优先攻击非冻结的、进度高的敌人
                priority = enemy.path_index * 10 + (0 if enemy.frozen else 1000)
                if priority > best_priority:
                    best = enemy
                    best_priority = priority
                elif priority == best_priority and best is not None:
                    # 同级优先最近的
                    if dist < math.hypot(best.px - self.px, best.py - self.py):
                        best = enemy
        return best


class Enemy:
    """塔防敌人"""

    def __init__(self, enemy_id, path, cell_size, wave_level=1):
        stats = TD_ENEMY_STATS[enemy_id]
        self.id = enemy_id
        self.name = stats["name"]
        self.element = stats.get("element")
        self.color = stats["color"]

        # 属性随波次成长
        wscale = 1 + (wave_level - 1) * 0.3
        self.max_hp = int(stats["hp"] * wscale)
        self.hp = self.max_hp
        self.base_speed = stats["speed"] * cell_size  # 转换为像素/秒
        self.speed = self.base_speed
        self.gold_reward = stats["gold"]

        # 路径
        self.path = path
        self.cell_size = cell_size
        self.path_index = 0
        self.px, self.py = self._path_pos(0)
        self.dead = False
        self.reached_end = False

        # 状态效果
        self.frozen = False
        self.frozen_timer = 0
        self.slowed = False
        self.slow_timer = 0
        self.slow_amount = 0
        self.def_down = 0
        self.def_down_timer = 0
        self.dot_damage = 0
        self.dot_timer = 0

        # 元素反应追踪
        self.element_hits = []  # [(element, timestamp), ...]

    def _path_pos(self, idx):
        """获取路径上某点的像素坐标"""
        if idx >= len(self.path):
            idx = len(self.path) - 1
        gx, gy = self.path[idx]
        return gx * self.cell_size + self.cell_size / 2, gy * self.cell_size + self.cell_size / 2

    def update(self, dt):
        """更新敌人状态"""
        # 处理冻结
        if self.frozen:
            self.frozen_timer -= dt
            if self.frozen_timer <= 0:
                self.frozen = False
            return  # 冻结时不动

        # 处理减速
        effective_speed = self.speed
        if self.slowed:
            self.slow_timer -= dt
            effective_speed *= (1 - self.slow_amount)
            if self.slow_timer <= 0:
                self.slowed = False

        # 处理减防
        if self.def_down > 0:
            self.def_down_timer -= dt
            if self.def_down_timer <= 0:
                self.def_down = 0

        # 处理DOT
        if self.dot_damage > 0:
            self.dot_timer -= dt
            self.hp -= int(self.dot_damage * dt)
            if self.dot_timer <= 0:
                self.dot_damage = 0

        # 移动
        self.path_index += (effective_speed * dt) / self.cell_size
        idx = int(self.path_index)
        if idx >= len(self.path) - 1:
            self.reached_end = True
            self.px, self.py = self._path_pos(len(self.path) - 1)
        else:
            # 插值位置
            frac = self.path_index - idx
            x1, y1 = self._path_pos(idx)
            x2, y2 = self._path_pos(idx + 1)
            self.px = x1 + (x2 - x1) * frac
            self.py = y1 + (y2 - y1) * frac

        # 检查死亡
        if self.hp <= 0:
            self.hp = 0
            self.dead = True

    def take_damage(self, dmg, element=None):
        """受到伤害，记录元素"""
        if self.dead:
            return 0

        # 减防影响
        if self.def_down > 0:
            dmg = int(dmg * (1 + self.def_down))

        actual = min(self.hp, dmg)
        self.hp -= actual

        # 记录元素命中
        if element:
            now = time.time()
            self.element_hits.append((element, now))
            # 清理过期记录
            self.element_hits = [(e, t) for e, t in self.element_hits
                                 if now - t < TD_REACTION_WINDOW]

        if self.hp <= 0:
            self.dead = True

        return actual

    def check_reaction(self, new_element):
        """检查是否触发元素反应"""
        now = time.time()
        # 找最近的另一个元素
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


class TDEngine:
    """塔防游戏引擎"""

    def __init__(self, map_data, available_chars):
        """
        map_data: TD_MAPS 中的地图配置
        available_chars: {char_id: level} 玩家拥有的可部署角色
        """
        self.map = map_data
        self.width = map_data["width"]
        self.height = map_data["height"]
        self.cell_size = map_data["cell_size"]
        self.path = map_data["path"]
        self.waves = map_data["waves"]
        self.gold = map_data["starting_gold"]
        self.max_lives = map_data["lives"]
        self.lives = self.max_lives

        # 塔
        self.towers = []
        self.available_chars = available_chars

        # 敌人
        self.enemies = []
        self.enemies_to_spawn = []  # 待生成的敌人队列
        self.wave_index = -1
        self.wave_active = False
        self.wave_enemy_count = 0
        self.wave_spawn_interval = 1.0
        self.wave_spawn_timer = 0
        self.wave_spawn_queue = []

        # 游戏状态
        self.running = False
        self.paused = False
        self.game_over = False
        self.victory = False
        self.game_time = 0

        # 反应特效日志
        self.effects = []  # [{type, px, py, timer, text, color}]
        self.kill_count = 0
        self.gold_earned = 0

        # 路径集合（不可建造）
        self.path_set = set(self.path)
        # 可建造格子（不在路径上的所有格子）
        self.buildable = []
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in self.path_set:
                    self.buildable.append((x, y))

    def can_place_tower(self, grid_x, grid_y):
        """检查是否可以在该位置建塔"""
        if (grid_x, grid_y) in self.path_set:
            return False
        if not (0 <= grid_x < self.width and 0 <= grid_y < self.height):
            return False
        # 检查是否已有塔
        for t in self.towers:
            if t.grid_x == grid_x and t.grid_y == grid_y:
                return False
        return True

    def place_tower(self, char_id, grid_x, grid_y):
        """放置塔，返回 Tower 或 None"""
        if not self.can_place_tower(grid_x, grid_y):
            return None
        td_s = TD_TOWER_STATS.get(char_id)
        if not td_s:
            return None
        if self.gold < td_s["cost"]:
            return None

        level = self.available_chars.get(char_id, 1)
        tower = Tower(char_id, level, grid_x, grid_y, self.cell_size)
        self.gold -= tower.cost
        self.towers.append(tower)
        return tower

    def upgrade_tower(self, tower):
        """升级塔（+3级，消耗金币）"""
        cost = tower.cost // 2
        if self.gold < cost:
            return False
        self.gold -= cost
        tower.level += 3
        lv_bonus = 1 + (tower.level - 1) * 0.05
        tower.damage = int(TD_TOWER_STATS[tower.char_id]["td_dmg"] * lv_bonus)
        tower.max_hp = max(tower.max_hp, 100 + tower.level * 20)
        tower.hp = tower.max_hp
        return True

    def sell_tower(self, tower):
        """出售塔，返还50%金币"""
        refund = tower.cost // 2
        self.gold += refund
        if tower in self.towers:
            self.towers.remove(tower)

    def use_tower_ability(self, tower):
        """使用塔技能"""
        if tower.ability_cd_remaining > 0:
            return None

        result = {"tower": tower, "type": tower.ability}

        if tower.ability == "flame_slash":
            tower.use_ability()
            # 对前方扇形敌人造成伤害
            hit_enemies = []
            for e in self.enemies:
                if e.dead:
                    continue
                dx = e.px - tower.px
                dy = e.py - tower.py
                dist = math.hypot(dx, dy) / self.cell_size
                if dist <= tower.range * 1.2:
                    dmg = int(tower.get_effective_damage() * 2.0)
                    actual = e.take_damage(dmg, tower.element)
                    self._check_enemy_reaction(e, tower.element)
                    hit_enemies.append(e)
                    if actual > 0:
                        self._add_effect("damage", e.px, e.py, f"-{actual}", "#e44")
            result["hit_count"] = len(hit_enemies)

        elif tower.ability == "atk_buff":
            tower.use_ability()
            count = 0
            for t in self.towers:
                if t is tower:
                    continue
                dist = math.hypot(t.px - tower.px, t.py - tower.py) / self.cell_size
                if dist <= 2:
                    t.dmg_bonus = 0.4
                    count += 1
            result["buff_count"] = count

        elif tower.ability == "dmg_debuff":
            tower.use_ability()
            count = 0
            for e in self.enemies:
                if e.dead:
                    continue
                dist = math.hypot(e.px - tower.px, e.py - tower.py) / self.cell_size
                if dist <= tower.range:
                    e.apply_def_down(0.5, 5.0)
                    count += 1
            result["debuff_count"] = count

        elif tower.ability == "coordinated_atk":
            tower.use_ability()
            result["active"] = True

        elif tower.ability == "summon_oz":
            tower.use_ability()
            # 在塔旁边创建奥兹
            oz = Tower("fischl", tower.level, tower.grid_x, tower.grid_y, self.cell_size)
            oz.name = "奥兹"
            oz.damage = int(tower.damage * 0.7)
            oz.atk_speed = 1.2
            oz.ability = "none"
            oz.ability_cd = 999
            oz.oz_tower = None
            tower.oz_tower = oz
            self.towers.append(oz)
            result["oz_created"] = True

        elif tower.ability == "teleport_strike":
            tower.use_ability()
            best = None
            best_hp = 0
            for e in self.enemies:
                if e.dead:
                    continue
                dist = math.hypot(e.px - tower.px, e.py - tower.py) / self.cell_size
                if dist <= tower.range and e.hp > best_hp:
                    best = e
                    best_hp = e.hp
            if best:
                dmg = int(tower.get_effective_damage() * 3.4)
                actual = best.take_damage(dmg, tower.element)
                self._check_enemy_reaction(best, tower.element)
                self._add_effect("damage", best.px, best.py, f"-{actual}", "#a0f")
                result["strike_dmg"] = actual

        elif tower.ability == "party_heal":
            tower.use_ability()
            count = 0
            for t in self.towers:
                heal = int(t.max_hp * 0.4)
                t.heal(heal)
                count += 1
            result["heal_count"] = count

        elif tower.ability == "shield_slow":
            tower.use_ability()
            # 给周围塔加护盾 + 减速周围敌人
            shield_count = 0
            for t in self.towers:
                dist = math.hypot(t.px - tower.px, t.py - tower.py) / self.cell_size
                if dist <= 2:
                    t.shield = int(t.max_hp * 0.3)
                    shield_count += 1
            slow_count = 0
            for e in self.enemies:
                if e.dead:
                    continue
                dist = math.hypot(e.px - tower.px, e.py - tower.py) / self.cell_size
                if dist <= tower.range:
                    e.apply_slow(0.5, 4.0)
                    slow_count += 1
            result["shield_count"] = shield_count
            result["slow_count"] = slow_count

        return result

    def _check_enemy_reaction(self, enemy, new_element):
        """检查并触发元素反应"""
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
            # AOE伤害基于触发反应的敌人血量比例
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

    def start(self):
        """开始游戏"""
        self.running = True
        self._start_next_wave()

    def _start_next_wave(self):
        """开始下一波"""
        self.wave_index += 1
        if self.wave_index >= len(self.waves):
            return

        wave = self.waves[self.wave_index]
        self.wave_active = True
        self.wave_spawn_interval = wave["interval"]
        self.wave_spawn_timer = 0

        # 构建出怪队列（随机打乱）
        queue = []
        for enemy_id, count in wave["enemies"]:
            for _ in range(count):
                queue.append(enemy_id)
        random.shuffle(queue)
        self.wave_spawn_queue = queue
        self.wave_enemy_count = len(queue)

    def _spawn_enemy(self):
        """生成一个敌人"""
        if not self.wave_spawn_queue:
            return
        eid = self.wave_spawn_queue.pop(0)
        enemy = Enemy(eid, self.path, self.cell_size, self.wave_index + 1)
        self.enemies.append(enemy)

    def update(self, dt):
        """主更新循环"""
        if not self.running or self.game_over:
            return

        self.game_time += dt

        # 波次管理
        if self.wave_active:
            self.wave_spawn_timer -= dt
            if self.wave_spawn_timer <= 0 and self.wave_spawn_queue:
                self._spawn_enemy()
                self.wave_spawn_timer = self.wave_spawn_interval

            # 检查波次是否结束
            if not self.wave_spawn_queue:
                alive = [e for e in self.enemies if not e.dead and not e.reached_end]
                if not alive:
                    self.wave_active = False
                    # 波次奖励
                    wave_bonus = 50 + self.wave_index * 30
                    self.gold += wave_bonus
                    self._add_effect("wave", self.width * self.cell_size / 2,
                                     self.height * self.cell_size / 2,
                                     f"第{self.wave_index + 1}波完成! +{wave_bonus}💰", "#ff0")
                    # 检查所有波次
                    if self.wave_index >= len(self.waves) - 1:
                        self.game_over = True
                        self.victory = True
                    else:
                        self._start_next_wave()

        # 更新塔
        for tower in self.towers:
            tower.update(dt)
            # 清理奥兹
            if tower.oz_tower and tower.ability_timer <= 0:
                if tower.oz_tower in self.towers:
                    self.towers.remove(tower.oz_tower)
                tower.oz_tower = None

            # 攻击
            if tower.ability != "none" or tower.name == "奥兹":
                if tower.can_attack():
                    target = tower.find_target(self.enemies)
                    if target:
                        dmg = tower.get_effective_damage()
                        reaction = TD_REACTIONS.get(f"{tower.element}+{target.element}"
                                                    if target.element else None)
                        if reaction and reaction.get("dmg_mult"):
                            dmg = int(dmg * reaction["dmg_mult"])
                        actual = target.take_damage(dmg, tower.element)
                        self._check_enemy_reaction(target, tower.element)
                        tower.reset_cooldown()
                        if actual > 0:
                            self._add_effect("damage", target.px, target.py,
                                             f"-{actual}", ELEMENTS[tower.element]["color"])

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

        # 清理死亡/到达终点的敌人
        self.enemies = [e for e in self.enemies if not e.dead and not e.reached_end]

        # 更新特效计时器
        self.effects = [ef for ef in self.effects if ef["timer"] > 0]
        for ef in self.effects:
            ef["timer"] -= dt

        # 检查塔是否被破坏
        self.towers = [t for t in self.towers if not t.is_destroyed()]

    def get_state(self):
        """获取当前状态（供UI渲染）"""
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
            "towers": [{
                "name": t.name, "element": ELEMENTS[t.element],
                "px": t.px, "py": t.py, "range": t.range * self.cell_size,
                "hp": t.hp, "max_hp": t.max_hp, "shield": t.shield,
                "level": t.level, "stars": t.stars,
                "ability_cd_remaining": t.ability_cd_remaining,
            } for t in self.towers],
            "enemies": [{
                "name": e.name, "px": e.px, "py": e.py,
                "hp": e.hp, "max_hp": e.max_hp,
                "color": e.color, "frozen": e.frozen,
                "slowed": e.slowed, "element": e.element,
            } for e in self.enemies],
            "effects": self.effects[:],
            "path": self.path,
            "buildable": self.buildable,
        }