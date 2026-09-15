"""
提瓦特放置游戏 - 抽卡系统
实现：概率计算、软保底、硬保底、大保底机制
"""
import random
import math
from .data import (
    GACHA_RATES, GACHA_PITY, GACHA_SOFT_PITY_START,
    STANDARD_5STAR, STANDARD_4STAR, CHARACTERS
)


class GachaSystem:
    """抽卡系统"""

    def __init__(self, pity_state=None):
        """
        pity_state: {
            "standard": {"pity_5": 0, "pity_4": 0, "guaranteed": False},
            "limited": {"pity_5": 0, "pity_4": 0, "guaranteed": False, "fate_points": 0},
            "beginner": {"pulls_used": 0, "total_pulls": 20},  # 新手池20抽后消失
        }
        """
        self.pity = pity_state or {
            "standard": {"pity_5": 0, "pity_4": 0, "guaranteed": False},
            "limited": {"pity_5": 0, "pity_4": 0, "guaranteed": False},
            "beginner": {"pulls_used": 0, "pity_5": 0, "pity_4": 0},
        }

    def _calc_rate(self, pity_count, base_rate, hard_pity):
        """计算当前实际概率（含软保底）"""
        if pity_count >= hard_pity - 1:
            return 1.0  # 保底触发
        if pity_count >= GACHA_SOFT_PITY_START - 1:
            # 软保底：概率线性增长
            remaining = hard_pity - pity_count
            soft_increase = (1.0 - base_rate) / (hard_pity - GACHA_SOFT_PITY_START)
            return base_rate + soft_increase * (pity_count - GACHA_SOFT_PITY_START + 1)
        return base_rate

    def pull(self, banner_type="standard", count=1):
        """
        抽卡
        banner_type: "standard" | "limited" | "beginner"
        count: 抽卡次数（1或10）
        返回: [{"rarity": "5star"|"4star", "character_id": "diluc", "is_new": bool}, ...]
        """
        results = []
        rates = GACHA_RATES[banner_type]
        pity_state = self.pity[banner_type]

        for _ in range(count):
            # 新手池特殊处理
            if banner_type == "beginner":
                pity_state["pulls_used"] += 1

            # 判定星级
            rate_5 = self._calc_rate(pity_state["pity_5"], rates["5star"], GACHA_PITY[banner_type])
            rand = random.random()

            if rand < rate_5:
                # 五星
                char_id = self._pick_5star(banner_type)
                results.append({"rarity": "5star", "character_id": char_id})
                pity_state["pity_5"] = 0
                pity_state["pity_4"] += 1
            elif rand < rate_5 + rates["4star"]:
                # 四星
                char_id = self._pick_4star(banner_type)
                results.append({"rarity": "4star", "character_id": char_id})
                pity_state["pity_5"] += 1
                pity_state["pity_4"] = 0
            else:
                # 三星（武器，MVP中简化：给莫拉补偿）
                results.append({"rarity": "3star", "character_id": None})
                pity_state["pity_5"] += 1
                pity_state["pity_4"] += 1

        # 十连保底：至少1个四星
        if count == 10:
            has_4star = any(r["rarity"] in ("4star", "5star") for r in results)
            if not has_4star:
                # 替换最后一个为四星
                results[-1] = {
                    "rarity": "4star",
                    "character_id": random.choice(STANDARD_4STAR)
                }
                pity_state["pity_4"] = 0

        return results

    def _pick_5star(self, banner_type):
        """选择五星角色"""
        if banner_type == "beginner":
            # 新手池固定随机五星
            return random.choice(STANDARD_5STAR)

        pity_state = self.pity[banner_type]

        if banner_type == "standard":
            chars = STANDARD_5STAR
        else:
            # 限定池：50%是UP角色（MVP中用刻晴作为示例UP）
            if pity_state.get("guaranteed"):
                pity_state["guaranteed"] = False
                return "keqing"  # 大保底，出UP
            if random.random() < 0.5:
                return "keqing"  # 出UP
            else:
                pity_state["guaranteed"] = True  # 歪了，下次大保底
                return random.choice(STANDARD_5STAR)

        return random.choice(chars) if chars else STANDARD_5STAR[0]

    def _pick_4star(self, banner_type):
        """选择四星角色"""
        return random.choice(STANDARD_4STAR)

    def get_pity_info(self):
        """获取各卡池保底信息"""
        info = {}
        for banner in ["standard", "limited", "beginner"]:
            ps = self.pity[banner]
            hard = GACHA_PITY[banner]
            info[banner] = {
                "pity_5": ps["pity_5"],
                "pity_4": ps["pity_4"],
                "hard_pity": hard,
                "pulls_until_guaranteed_5": hard - ps["pity_5"],
            }
            if banner == "limited":
                info[banner]["guaranteed"] = ps.get("guaranteed", False)
            if banner == "beginner":
                info[banner]["pulls_used"] = ps.get("pulls_used", 0)
                info[banner]["is_active"] = ps.get("pulls_used", 0) < 20
        return info

    def to_dict(self):
        """序列化"""
        return self.pity

    @classmethod
    def from_dict(cls, data):
        """反序列化"""
        return cls(pity_state=data)