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
    """创建新游戏状态（陷阱+塔版本）"""
    return {
        "player_name": "旅行者",
        "adventure_rank": 1,
        "adventure_exp": 0,
        "play_time": 0,
        "last_online": time.time(),
        "resources": {
            "mora": 10000,
            "primogems": 0,
            "resin": 160,
            "exp_books": 5,
            "resin_last_update": time.time(),
        },
        "stage_progress": {
            "highest_stage_unlocked": 1,
            "completed_stages": [],
        },
        "dailies": {
            "commissions_done": 0,
            "last_daily_reset": time.time(),
        },
    }