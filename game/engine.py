"""
提瓦特放置游戏 - 回合制战斗引擎
处理：元素附着、反应检测、伤害计算、协同攻击、增益/减益
"""
import random
import math
from .data import ELEMENTS, REACTIONS, RESONANCES, ENEMIES


class Character:
    """战斗中的角色实例"""

    def __init__(self, char_data, level=1, constellation=0):
        self.id = char_data["id"]
        self.name = char_data["name"]
        self.element = char_data["element"]
        self.stars = char_data["stars"]
        self.level = level
        self.constellation = constellation  # 命之座 (0-6)

        # 计算当前等级属性
        self.base_atk = char_data["base_atk"]
        self.base_def = char_data["base_def"]
        self.base_hp = char_data["base_hp"]
        growth = (char_data["atk_growth"], char_data["def_growth"], char_data["hp_growth"])
        self.atk = self._calc_stat(self.base_atk, growth[0])
        self.defense = self._calc_stat(self.base_def, growth[1])
        self.max_hp = self._calc_stat(self.base_hp, growth[2])
        self.hp = self.max_hp

        self.em = char_data["base_em"]  # 元素精通
        self.er = char_data["base_er"]  # 元素充能效率
        self.cr = char_data["base_cr"]  # 暴击率
        self.cd = char_data["base_cd"]  # 暴击伤害

        # 技能数据
        self.skill_data = char_data.get("skill", {})
        self.burst_data = char_data.get("burst", {})
        self.skill_cooldown_remaining = 0
        self.skill_max_cd = self.skill_data.get("cooldown", 3)
        self.energy = 0
        self.max_energy = self.burst_data.get("energy_cost", 60)

        # 状态
        self.shield = 0
        self.frozen = False
        self.dead = False

        # 增益/减益（用于共鸣等）
        self.buffs = {}  # {key: {value, duration}}

    def _calc_stat(self, base, growth_rate):
        """计算当前等级属性: base * (1 + (level-1) * growth_rate)"""
        return int(base * (1 + (self.level - 1) * growth_rate))

    def get_effective_atk(self):
        """获取有效攻击力（含增益）"""
        bonus = 1.0 + self.buffs.get("atk_pct", 0)
        return int(self.atk * bonus)

    def get_effective_cr(self):
        """获取有效暴击率"""
        return min(self.cr + self.buffs.get("cr_bonus", 0), 1.0)

    def get_effective_er(self):
        """获取有效充能效率"""
        return self.er + self.buffs.get("er_bonus", 0)

    def take_damage(self, damage):
        """受到伤害，优先消耗护盾"""
        if self.shield > 0:
            if self.shield >= damage:
                self.shield -= damage
                return 0
            else:
                damage -= self.shield
                self.shield = 0
        actual = max(0, damage - int(self.defense * 0.3))
        self.hp -= actual
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
        return actual

    def heal(self, amount):
        """回复生命值"""
        heal_bonus = 1.0 + self.buffs.get("heal_bonus", 0)
        actual_heal = int(amount * heal_bonus)
        self.hp = min(self.hp + actual_heal, self.max_hp)
        return actual_heal

    def add_shield(self, amount):
        """添加护盾"""
        shield_bonus = 1.0 + self.buffs.get("shield_bonus", 0)
        self.shield += int(amount * shield_bonus)

    def gain_energy(self, amount):
        """获取能量"""
        er = self.get_effective_er()
        self.energy = min(self.energy + int(amount * er), self.max_energy)

    def tick_buffs(self):
        """每回合减少增益持续时间，移除过期增益"""
        expired = []
        for key, data in self.buffs.items():
            data["duration"] -= 1
            if data["duration"] <= 0:
                expired.append(key)
        for key in expired:
            del self.buffs[key]
        # 更新简化的buff值
        self._refresh_buff_values()

    def _refresh_buff_values(self):
        """从buffs字典刷新快捷访问值"""
        self.buff_atk_pct = sum(
            d["value"] for k, d in self.buffs.items() if k.startswith("atk_pct_"))
        self.buff_cr = sum(
            d["value"] for k, d in self.buffs.items() if k.startswith("cr_"))
        # 真正的值在 get_effective_* 方法中计算

    def is_alive(self):
        return not self.dead


class Enemy:
    """战斗中的敌人实例"""

    def __init__(self, enemy_id, level=1):
        data = ENEMIES[enemy_id]
        self.id = enemy_id
        self.name = data["name"]
        self.element = data.get("element", None)
        self.level = level
        scale = data["level_scale"]
        self.max_hp = int(data["base_hp"] * (1 + (level - 1) * scale * 0.1))
        self.hp = self.max_hp
        self.atk = int(data["base_atk"] * (1 + (level - 1) * scale * 0.08))
        self.defense = int(data["base_def"] * (1 + (level - 1) * scale * 0.06))
        self.dead = False

        # 元素附着状态
        self.element_aura = None  # 当前附着的元素
        self.aura_remaining = 0   # 附着剩余回合

        # 减益
        self.debuffs = {}
        self.frozen_turns = 0
        self.dot_damage = []  # [(damage_per_turn, turns_remaining, element)]

    def apply_element(self, element):
        """给敌人附着元素，返回是否触发了反应"""
        if self.element_aura is None:
            self.element_aura = element
            self.aura_remaining = 2  # 附着持续2回合
            return None
        else:
            # 检查反应
            reaction_key = f"{element}+{self.element_aura}"
            reaction = REACTIONS.get(reaction_key)
            if reaction:
                # 触发反应后清除或更新附着
                self.element_aura = element
                self.aura_remaining = 2
                return reaction
            else:
                # 无反应，覆盖附着
                self.element_aura = element
                self.aura_remaining = 2
                return None

    def take_damage(self, damage):
        """受到伤害"""
        actual = max(0, damage - int(self.defense * 0.2))
        self.hp -= actual
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
        return actual

    def add_debuff(self, key, value, duration):
        """添加减益效果"""
        self.debuffs[key] = {"value": value, "duration": duration}

    def get_debuff(self, key):
        """获取减益值"""
        d = self.debuffs.get(key)
        if d and d["duration"] > 0:
            return d["value"]
        return 0

    def tick_status(self):
        """回合更新状态"""
        # 处理冻结
        if self.frozen_turns > 0:
            self.frozen_turns -= 1

        # 处理持续伤害
        dot_total = 0
        remaining_dots = []
        for dmg, turns, element in self.dot_damage:
            dot_total += dmg
            if turns > 1:
                remaining_dots.append((dmg, turns - 1, element))
        self.dot_damage = remaining_dots

        # 处理附着
        if self.aura_remaining > 0:
            self.aura_remaining -= 1
            if self.aura_remaining <= 0:
                self.element_aura = None

        # 处理减益
        expired = []
        for key, data in self.debuffs.items():
            data["duration"] -= 1
            if data["duration"] <= 0:
                expired.append(key)
        for key in expired:
            del self.debuffs[key]

        return dot_total

    def is_frozen(self):
        return self.frozen_turns > 0

    def is_alive(self):
        return not self.dead


class BattleEngine:
    """回合制战斗引擎"""

    def __init__(self, team_chars, enemies_config, resonances=None, stage_level=1):
        """
        team_chars: [(char_data, level), ...] 队伍角色配置
        enemies_config: [{"enemy": "hilichurl", "count": 2}, ...]
        resonances: 激活的元素共鸣列表
        stage_level: 关卡等级
        """
        self.team = []
        for char_data, level in team_chars:
            c = Character(char_data, level)
            self.team.append(c)

        self.enemies = []
        for wave in enemies_config:
            for _ in range(wave["count"]):
                e = Enemy(wave["enemy"], stage_level)
                self.enemies.append(e)

        self.resonances = resonances or []
        self.turn = 0
        self.log = []  # 战斗日志
        self.battle_over = False
        self.victory = False

        # 协同攻击注册表: 角色ID -> {damage_multiplier, element, turns_left}
        self.coordinated_attacks = {}

        # 应用共鸣效果
        self._apply_resonances()

    def _apply_resonances(self):
        """应用元素共鸣效果到全队"""
        for res in self.resonances:
            effects = res.get("effect", {})
            for char in self.team:
                for key, value in effects.items():
                    if key == "atk_pct":
                        char.buffs["atk_pct"] = char.buffs.get("atk_pct", 0) + value
                    elif key == "cr_bonus":
                        char.buffs["cr_bonus"] = char.buffs.get("cr_bonus", 0) + value
                    elif key == "er_bonus":
                        char.buffs["er_bonus"] = char.buffs.get("er_bonus", 0) + value
                    elif key == "heal_bonus":
                        char.buffs["heal_bonus"] = char.buffs.get("heal_bonus", 0) + value
                    elif key == "shield_bonus":
                        char.buffs["shield_bonus"] = char.buffs.get("shield_bonus", 0) + value
                    elif key == "em_bonus":
                        char.em += value

    def _log(self, message, log_type="info"):
        """记录战斗日志"""
        self.log.append({
            "turn": self.turn,
            "type": log_type,  # info, damage, reaction, heal, shield, buff, victory, defeat
            "message": message
        })

    def _calc_damage(self, attacker_atk, multiplier, crit_rate, crit_dmg,
                     target_def=0, amplify_mult=1.0, em_bonus=0):
        """计算最终伤害"""
        base_dmg = attacker_atk * multiplier
        # 暴击判定
        is_crit = random.random() < crit_rate
        if is_crit:
            base_dmg *= (1 + crit_dmg)
        # 减伤（简化处理）
        def_reduction = target_def * 0.15 / (target_def * 0.15 + 200)
        base_dmg *= (1 - def_reduction)
        # 增幅反应加成
        if amplify_mult > 1.0:
            em_mult = 1 + em_bonus * 0.01  # 精通加成
            base_dmg *= amplify_mult * em_mult
        return int(base_dmg), is_crit

    def _calc_transform_dmg(self, level, base_ratio, em):
        """计算剧变反应固定伤害"""
        base = 20 + level * 5
        em_mult = 1 + (16 * em) / (em + 2000)
        return int(base * base_ratio * em_mult)

    def _choose_target(self, attacker=None):
        """选择攻击目标"""
        alive = [e for e in self.enemies if e.is_alive()]
        if not alive:
            return None
        # 优先攻击有元素附着的敌人
        with_aura = [e for e in alive if e.element_aura]
        if with_aura:
            return random.choice(with_aura)
        return random.choice(alive)

    def _process_coordinated_attack(self, char_id):
        """检查并执行协同攻击"""
        if char_id in self.coordinated_attacks:
            coord = self.coordinated_attacks[char_id]
            target = self._choose_target()
            if target:
                dmg, _ = self._calc_damage(
                    self.team[0].atk,  # 简化：取队伍第一个角色攻击力
                    coord["multiplier"],
                    0.05, 0.50
                )
                actual = target.take_damage(dmg)
                reaction = target.apply_element(coord["element"])
                react_msg = ""
                if reaction:
                    react_msg = f"，触发{reaction['name']}！"
                self._log(
                    f"协同攻击 → {target.name} 造成 {actual} 点伤害{react_msg}",
                    "damage"
                )

    def _execute_character_action(self, char, target):
        """执行单个角色的行动"""
        if char.dead or target is None:
            return

        action_name = "普通攻击"
        multiplier = 1.0
        element_apply = True
        damage_dealt = 0

        # 决定行动：Q > E > 普攻
        if char.energy >= char.max_energy and char.burst_data.get("multiplier", 0) > 0:
            # 释放元素爆发
            burst = char.burst_data
            action_name = f"元素爆发·{burst['name']}"
            multiplier = burst["multiplier"]
            element_apply = burst.get("element_apply", True)
            char.energy = 0

            # 处理特殊爆发效果
            if burst.get("target") == "coordinated_atk":
                # 协同攻击
                self.coordinated_attacks[char.id] = {
                    "multiplier": burst["multiplier"],
                    "element": char.element,
                    "turns": burst.get("coordinated_turns", 2)
                }
                self._log(f"{char.name} 释放 {burst['name']}，协战 {burst.get('coordinated_turns', 2)} 回合")
                # 协同攻击在当前回合也触发
                self._process_coordinated_attack(char.id)
                return

            elif burst.get("target") == "all_enemies":
                for enemy in [e for e in self.enemies if e.is_alive()]:
                    dmg, is_crit = self._calc_damage(
                        char.get_effective_atk(), multiplier,
                        char.get_effective_cr(), char.cd,
                        enemy.defense
                    )
                    actual = enemy.take_damage(dmg)
                    reaction = enemy.apply_element(char.element) if element_apply else None
                    react_msg = f"，触发{reaction['name']}！" if reaction else ""
                    crit_msg = " 暴击！" if is_crit else ""
                    self._log(
                        f"{char.name} 的 {burst['name']} → {enemy.name} 造成 {actual} 点伤害{crit_msg}{react_msg}",
                        "damage"
                    )

                    if reaction and reaction["type"] == "transform":
                        r_dmg = self._calc_transform_dmg(char.level, reaction["base_dmg_ratio"], char.em)
                        enemy.take_damage(r_dmg)
                        self._log(f"剧变反应 {reaction['name']} 额外造成 {r_dmg} 点伤害！", "reaction")
                return

            elif burst.get("target") == "team_heal":
                heal_pct = burst.get("heal_pct", 0.3)
                for member in [c for c in self.team if c.is_alive()]:
                    heal_amount = int(member.max_hp * heal_pct)
                    actual_heal = member.heal(heal_amount)
                    self._log(f"{char.name} 的 {burst['name']} → {member.name} 回复 {actual_heal} 点生命", "heal")
                return

            elif burst.get("target") == "team_buff":
                buff = burst.get("buff", {})
                for member in [c for c in self.team if c.is_alive()]:
                    if "atk_pct" in buff:
                        member.buffs["atk_pct"] = member.buffs.get("atk_pct", 0) + buff["atk_pct"]
                self._log(f"{char.name} 释放 {burst['name']}，全队攻击力 +{int(buff.get('atk_pct', 0) * 100)}%！", "buff")
                return

            elif burst.get("target") == "enemy_debuff":
                debuff = burst.get("debuff", {})
                for enemy in [e for e in self.enemies if e.is_alive()]:
                    for key, value in debuff.items():
                        if key == "dmg_taken_pct":
                            enemy.add_debuff("dmg_taken", value, debuff.get("duration", 2))
                self._log(f"{char.name} 释放 {burst['name']}，敌人受到伤害 +{int(debuff.get('dmg_taken_pct', 0) * 100)}%！", "buff")
                return

        elif char.skill_cooldown_remaining <= 0 and char.skill_data.get("cooldown"):
            # 释放元素战技
            skill = char.skill_data
            action_name = f"元素战技·{skill['name']}"

            if skill.get("target") == "team_heal":
                heal_pct = skill.get("heal_pct", 0.2)
                for member in [c for c in self.team if c.is_alive()]:
                    heal_amount = int(member.max_hp * heal_pct)
                    actual_heal = member.heal(heal_amount)
                    self._log(f"{char.name} 的 {skill['name']} → {member.name} 回复 {actual_heal} 点生命", "heal")
                char.skill_cooldown_remaining = char.skill_max_cd
                # 元素战技也给能量
                char.gain_energy(15)
                return

            elif skill.get("target") == "team_shield":
                shield_pct = skill.get("shield_pct", 0.2)
                for member in [c for c in self.team if c.is_alive()]:
                    shield_amount = int(member.max_hp * shield_pct)
                    member.add_shield(shield_amount)
                    self._log(f"{char.name} 的 {skill['name']} → {member.name} 获得 {shield_amount} 点护盾", "shield")
                char.skill_cooldown_remaining = char.skill_max_cd
                char.gain_energy(15)
                return

            multiplier = skill["multiplier"]
            element_apply = skill.get("element_apply", True)
            char.skill_cooldown_remaining = char.skill_max_cd
            # E技能给能量
            char.gain_energy(15)

        else:
            # 普通攻击
            action_name = "普通攻击"
            multiplier = 1.0
            char.gain_energy(10)  # 普攻给少量能量

        # 计算伤害
        dmg, is_crit = self._calc_damage(
            char.get_effective_atk(), multiplier,
            char.get_effective_cr(), char.cd,
            target.defense
        )

        # 检查敌人减益（如莫娜大招）
        dmg_taken_bonus = target.get_debuff("dmg_taken")
        if dmg_taken_bonus > 0:
            dmg = int(dmg * (1 + dmg_taken_bonus))

        # 检查反应
        reaction = None
        amplify_mult = 1.0
        if element_apply:
            reaction = target.apply_element(char.element)
            if reaction and reaction["type"] == "amplify":
                amplify_mult = reaction["multiplier"]
                dmg, _ = self._calc_damage(
                    char.get_effective_atk(), multiplier,
                    char.get_effective_cr(), char.cd,
                    target.defense,
                    amplify_mult,
                    char.em
                )
            elif reaction and reaction["type"] == "transform":
                # 剧变反应额外伤害
                r_dmg = self._calc_transform_dmg(char.level, reaction["base_dmg_ratio"], char.em)
                target.take_damage(r_dmg)
                # 检查DOT
                if reaction.get("dot"):
                    target.dot_damage.append((int(r_dmg * 0.5), reaction["dot_turns"], char.element))
                if reaction.get("debuff"):
                    for dk, dv in reaction["debuff"].items():
                        if dk == "phys_res_down":
                            target.add_debuff("phys_res", dv, reaction["debuff"].get("duration", 2))
            elif reaction and reaction["type"] == "control":
                target.frozen_turns = reaction["freeze_turns"]

        # 应用伤害
        actual = target.take_damage(dmg)
        damage_dealt = actual

        # 日志
        react_msg = ""
        if reaction:
            react_msg = f"，触发{reaction['name']}！"
        crit_msg = " 暴击！" if is_crit else ""
        self._log(
            f"{char.name} {action_name} → {target.name} 造成 {actual} 点伤害{crit_msg}{react_msg}",
            "damage" if actual > 0 else "info"
        )

        # 协同攻击检查
        if action_name == "普通攻击":
            for cid in list(self.coordinated_attacks.keys()):
                self._process_coordinated_attack(cid)

    def _enemy_attack(self, enemy, target):
        """敌人攻击"""
        dmg = enemy.atk
        actual = target.take_damage(dmg)
        self._log(f"{enemy.name} 攻击 {target.name} 造成 {actual} 点伤害", "damage")

    def process_turn(self):
        """处理一个回合"""
        if self.battle_over:
            return self.log

        self.turn += 1
        self._log(f"--- 第 {self.turn} 回合 ---", "info")

        # 1. 更新状态
        for char in self.team:
            char.tick_buffs()
            if char.skill_cooldown_remaining > 0:
                char.skill_cooldown_remaining -= 1

        # 更新协同攻击
        expired_coord = []
        for cid, data in self.coordinated_attacks.items():
            data["turns"] -= 1
            if data["turns"] <= 0:
                expired_coord.append(cid)
        for cid in expired_coord:
            del self.coordinated_attacks[cid]

        # 更新敌人状态
        for enemy in self.enemies:
            dot_dmg = enemy.tick_status()
            if dot_dmg > 0:
                actual = enemy.take_damage(dot_dmg)
                self._log(f"持续伤害 → {enemy.name} 受到 {actual} 点感电伤害", "damage")

        # 2. 存活角色依次行动
        alive_chars = [c for c in self.team if c.is_alive()]
        for char in alive_chars:
            if char.frozen:
                char.frozen = False
                self._log(f"{char.name} 被冻结，无法行动", "info")
                continue

            # 检查是否所有敌人已死亡
            alive_enemies = [e for e in self.enemies if e.is_alive()]
            if not alive_enemies:
                break

            target = self._choose_target()
            self._execute_character_action(char, target)

        # 3. 敌人行动
        alive_enemies = [e for e in self.enemies if e.is_alive()]
        alive_chars = [c for c in self.team if c.is_alive()]
        for enemy in alive_enemies:
            if enemy.is_frozen():
                self._log(f"{enemy.name} 被冻结，无法行动！", "info")
                continue
            if not alive_chars:
                break
            target = random.choice(alive_chars)
            self._enemy_attack(enemy, target)
            # 重新检查存活
            alive_chars = [c for c in self.team if c.is_alive()]

        # 4. 检查胜负
        alive_enemies = [e for e in self.enemies if e.is_alive()]
        alive_chars = [c for c in self.team if c.is_alive()]

        if not alive_enemies:
            self.battle_over = True
            self.victory = True
            self._log("战斗胜利！所有敌人已被击败！", "victory")
        elif not alive_chars:
            self.battle_over = True
            self.victory = False
            self._log("战斗失败！队伍全灭...", "defeat")

        # 限制最大回合数
        if self.turn >= 30:
            self.battle_over = True
            self.victory = False
            self._log("战斗超时！(30回合限制)", "defeat")

        return self.log

    def run_full_battle(self):
        """运行整场战斗直到结束"""
        while not self.battle_over:
            self.process_turn()
        return {
            "victory": self.victory,
            "turns": self.turn,
            "log": self.log,
            "team_survivors": sum(1 for c in self.team if c.is_alive()),
        }

    def get_battle_state(self):
        """获取当前战斗状态（供前端展示）"""
        return {
            "turn": self.turn,
            "battle_over": self.battle_over,
            "victory": self.victory,
            "team": [
                {
                    "name": c.name,
                    "element": ELEMENTS[c.element],
                    "hp": c.hp,
                    "max_hp": c.max_hp,
                    "energy": c.energy,
                    "max_energy": c.max_energy,
                    "shield": c.shield,
                    "dead": c.dead,
                    "skill_cd": c.skill_cooldown_remaining,
                }
                for c in self.team
            ],
            "enemies": [
                {
                    "name": e.name,
                    "hp": e.hp,
                    "max_hp": e.max_hp,
                    "element_aura": e.element_aura,
                    "frozen": e.frozen_turns > 0,
                    "dead": e.dead,
                }
                for e in self.enemies
            ],
            "log": self.log[-10:],  # 最近10条日志
        }