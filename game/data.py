"""
提瓦特放置游戏 - 游戏数据定义（陷阱+塔版本）
"""
# ==================== 元素定义 ====================
ELEMENTS = {
    "fire":    {"name": "火", "icon": "🔥", "color": "#ef4444"},
    "water":   {"name": "水", "icon": "💧", "color": "#3b82f6"},
    "thunder": {"name": "雷", "icon": "⚡", "color": "#a855f7"},
    "ice":     {"name": "冰", "icon": "❄️", "color": "#7dd3fc"},
    "wind":    {"name": "风", "icon": "🍃", "color": "#4ade80"},
    "rock":    {"name": "岩", "icon": "🪨", "color": "#fbbf24"},
    "grass":   {"name": "草", "icon": "🌿", "color": "#22c55e"},
}

# ==================== 陷阱与塔定义 ====================
# type: "trap" = 放在路径上, "tower" = 放在空地
BUILDING_DEFS = {
    "hydro_trap": {
        "bid": "hydro_trap",
        "type": "trap",
        "name": "挂水装置",
        "element": "water",
        "cost": 100,
        "icon": "💧",
        "color": "#4488cc",
        "cooldown": 2.0,       # 同个敌人再次触发间隔
        "description": "放在怪物路径上，经过时附着水元素",
    },
    "crossbow": {
        "bid": "crossbow",
        "type": "tower",
        "name": "弩塔",
        "element": "fire",
        "cost": 200,
        "range": 2.5,
        "atk_speed": 2.0,
        "damage": 60,
        "icon": "🏹",
        "color": "#cc4444",
        "description": "射出带火元素的箭矢，与水元素触发蒸发反应",
    },
}

# ==================== 塔防地图（仅一张） ====================
TD_MAPS = [
    {
        "id": 1, "name": "蒙德·低语森林",
        "width": 14, "height": 10, "cell_size": 66,
        "path": [
            (0,4), (1,4), (2,4), (2,3), (2,2), (3,2), (4,2),
            (5,2), (5,3), (5,4), (5,5), (4,5), (3,5), (2,5),
            (2,6), (2,7), (2,8), (3,8), (4,8), (5,8), (5,9),
        ],
        "waves": [
            {"enemies": [("hilichurl", 5)], "interval": 1.5},
            {"enemies": [("hilichurl", 4), ("slime_fire", 3)], "interval": 1.4},
            {"enemies": [("hilichurl_fighter", 4), ("slime_water", 3)], "interval": 1.2},
        ],
        "starting_gold": 350, "lives": 20,
    },
]

# ==================== 塔防敌人属性 ====================
TD_ENEMY_STATS = {
    "hilichurl": {
        "name": "丘丘人", "hp": 150, "speed": 1.2, "gold": 30,
        "element": None, "color": "#888",
    },
    "hilichurl_fighter": {
        "name": "丘丘人战士", "hp": 400, "speed": 1.0, "gold": 60,
        "element": None, "color": "#a66",
    },
    "slime_fire": {
        "name": "火史莱姆", "hp": 250, "speed": 0.9, "gold": 45,
        "element": "fire", "color": "#e44",
    },
    "slime_water": {
        "name": "水史莱姆", "hp": 280, "speed": 1.0, "gold": 45,
        "element": "water", "color": "#38b",
    },
    "abyss_mage": {
        "name": "深渊法师", "hp": 900, "speed": 0.7, "gold": 120,
        "element": None, "color": "#66c",
    },
    "ruin_guard": {
        "name": "遗迹守卫", "hp": 3000, "speed": 0.4, "gold": 300,
        "element": None, "color": "#aaa",
    },
}

# ==================== 塔防元素反应 ====================
TD_REACTIONS = {
    "fire+water":   {"name": "蒸发", "dmg_mult": 1.5, "desc": "伤害×1.5"},
    "water+fire":   {"name": "蒸发", "dmg_mult": 2.0, "desc": "伤害×2.0"},
    "fire+ice":     {"name": "融化", "dmg_mult": 2.0, "desc": "伤害×2.0"},
    "ice+fire":     {"name": "融化", "dmg_mult": 1.5, "desc": "伤害×1.5"},
    "fire+thunder": {"name": "超载", "aoe": True, "aoe_radius": 1.5, "aoe_dmg_ratio": 0.8, "desc": "范围爆炸"},
    "thunder+fire": {"name": "超载", "aoe": True, "aoe_radius": 1.5, "aoe_dmg_ratio": 0.8, "desc": "范围爆炸"},
    "water+thunder":{"name": "感电", "dot": True, "dot_duration": 3.0, "dot_dmg": 20, "desc": "持续雷伤3秒"},
    "thunder+water":{"name": "感电", "dot": True, "dot_duration": 3.0, "dot_dmg": 20, "desc": "持续雷伤3秒"},
    "ice+thunder":  {"name": "超导", "aoe": True, "aoe_radius": 1.2, "aoe_dmg_ratio": 0.5, "def_down": 0.3, "def_down_dur": 4.0, "desc": "范围冰伤+减防"},
    "thunder+ice":  {"name": "超导", "aoe": True, "aoe_radius": 1.2, "aoe_dmg_ratio": 0.5, "def_down": 0.3, "def_down_dur": 4.0, "desc": "范围冰伤+减防"},
    "water+ice":    {"name": "冻结", "freeze": True, "freeze_duration": 2.0, "desc": "冻结2秒"},
    "ice+water":    {"name": "冻结", "freeze": True, "freeze_duration": 2.0, "desc": "冻结2秒"},
}

TD_REACTION_WINDOW = 1.5