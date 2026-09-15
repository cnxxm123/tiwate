"""
提瓦特放置游戏 - 存档系统
使用JSON文件存储玩家数据
"""
import json
import os
import time
from pathlib import Path

SAVE_DIR = Path(__file__).parent.parent / "data" / "saves"


class SaveManager:
    """存档管理器"""

    def __init__(self):
        SAVE_DIR.mkdir(parents=True, exist_ok=True)

    def _get_save_path(self, save_id="default"):
        """获取存档文件路径"""
        return SAVE_DIR / f"{save_id}.json"

    def save(self, game_state, save_id="default"):
        """保存游戏状态"""
        filepath = self._get_save_path(save_id)
        game_state["last_save_time"] = time.time()
        game_state["save_version"] = 1
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(game_state, f, ensure_ascii=False, indent=2)
        return True

    def load(self, save_id="default"):
        """加载游戏状态"""
        filepath = self._get_save_path(save_id)
        if not filepath.exists():
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def delete(self, save_id="default"):
        """删除存档"""
        filepath = self._get_save_path(save_id)
        if filepath.exists():
            filepath.unlink()
            return True
        return False

    def list_saves(self):
        """列出所有存档"""
        saves = []
        for f in SAVE_DIR.glob("*.json"):
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                saves.append({
                    "id": f.stem,
                    "player_name": data.get("player_name", "旅行者"),
                    "adventure_rank": data.get("adventure_rank", 1),
                    "last_save_time": data.get("last_save_time", 0),
                    "play_time": data.get("play_time", 0),
                })
            except Exception:
                pass
        return saves


def create_new_game():
    """创建新游戏状态"""
    return {
        "player_name": "旅行者",
        "adventure_rank": 1,
        "adventure_exp": 0,
        "play_time": 0,  # 总游玩时间（秒）
        "last_online": time.time(),
        "resources": {
            "mora": 25000,         # 摩拉（初始可购买一个五星或两个四星）
            "primogems": 0,        # 原石（已移除抽卡，保留兼容）
            "stardust": 0,         # 星尘
            "starglitter": 0,      # 星辉
            "resin": 160,          # 树脂
            "exp_books": 20,       # 经验书
            "resin_last_update": time.time(),
        },
        "characters": {
            # character_id: {level, constellation, exp, obtained_at}
            # 初始赠送一个四星角色
            "bennett": {"level": 1, "constellation": 0, "exp": 0},
        },
        "weapons": {},
        "artifacts": {},
        "team": ["bennett"],  # 当前队伍（最多4人）
        "stage_progress": {
            "current_stage": 1,             # 当前关卡
            "highest_stage_unlocked": 1,    # 最高解锁关卡
            "completed_stages": [],         # 已完成的关卡ID列表
        },
        "gacha_pity": {
            "standard": {"pity_5": 0, "pity_4": 0, "guaranteed": False},
            "limited": {"pity_5": 0, "pity_4": 0, "guaranteed": False},
            "beginner": {"pulls_used": 0, "pity_5": 0, "pity_4": 0},
        },
        "dailies": {
            "commissions_done": 0,          # 今日已完成委托数
            "last_daily_reset": time.time(),
            "weekly_bosses_done": 0,
            "last_weekly_reset": time.time(),
        },
        "offline_rewards": {
            "accumulated_seconds": 0,       # 累积离线时间
            "max_accumulate": 43200,        # 最多12小时
            "last_collect_time": time.time(),
        },
    }