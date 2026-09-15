"""
提瓦特放置游戏 - 游戏数据定义
包含：角色、元素反应、元素共鸣、敌人、等级曲线
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

# ==================== 角色定义（全角色，共93名） ====================
# 角色属性随等级成长公式: base * (1 + (level-1) * growth_rate)
# 5★: base_atk=280, base_def=200, base_hp=1100, atk_growth=0.028, def_growth=0.025, hp_growth=0.028
# 4★: base_atk=210, base_def=180, base_hp=1000, atk_growth=0.025, def_growth=0.022, hp_growth=0.026
CHARACTERS = {
    # ========== 火元素 (Fire) - 16角色 ==========
    "diluc": {
        "id": "diluc", "name": "迪卢克", "element": "fire", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "晨曦酒庄的贵公子，手持大剑的烈焰战士。"
    },
    "klee": {
        "id": "klee", "name": "可莉", "element": "fire", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "西风骑士团的火花骑士，炸弹狂魔小萝莉。"
    },
    "hutao": {
        "id": "hutao", "name": "胡桃", "element": "fire", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "往生堂第七十七代堂主，古灵精怪的少女。"
    },
    "yoimiya": {
        "id": "yoimiya", "name": "宵宫", "element": "fire", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "长野原烟花店的店长，热情洋溢的夏祭女王。"
    },
    "dehya": {
        "id": "dehya", "name": "迪希雅", "element": "fire", "stars": 5, "role": "辅助",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "镀金旅团的炽鬃之狮，豪爽仗义的沙漠佣兵。"
    },
    "lyney": {
        "id": "lyney", "name": "林尼", "element": "fire", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "枫丹最伟大的魔术师，华丽而狡黠的表演者。"
    },
    "arlecchino": {
        "id": "arlecchino", "name": "阿蕾奇诺", "element": "fire", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "愚人众执行官第四席「仆人」，冷酷威严。"
    },
    "mavuika": {
        "id": "mavuika", "name": "玛薇卡", "element": "fire", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "纳塔的现任火神，燃烧一切的战争之神。"
    },
    "bennett": {
        "id": "bennett", "name": "班尼特", "element": "fire", "stars": 4, "role": "增伤",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "蒙德城的冒险少年，虽运气不佳却鼓舞人心。"
    },
    "xiangling": {
        "id": "xiangling", "name": "香菱", "element": "fire", "stars": 4, "role": "副C",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "万民堂的天才厨师，锅巴是她最忠实的伙伴。"
    },
    "amber": {
        "id": "amber", "name": "安柏", "element": "fire", "stars": 4, "role": "主C",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "西风骑士团唯一的侦察骑士，热情活泼的兔兔伯爵使者。"
    },
    "xinyan": {
        "id": "xinyan", "name": "辛焱", "element": "fire", "stars": 4, "role": "护盾",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "璃月的摇滚女歌手，用吉他点燃舞台的火焰。"
    },
    "yanfei": {
        "id": "yanfei", "name": "烟绯", "element": "fire", "stars": 4, "role": "主C",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "璃月港的天才律师，半仙之兽的混血少女。"
    },
    "thoma": {
        "id": "thoma", "name": "托马", "element": "fire", "stars": 4, "role": "护盾",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "神里家的家政官，来自蒙德的忠诚护卫。"
    },
    "gaming": {
        "id": "gaming", "name": "嘉明", "element": "fire", "stars": 4, "role": "主C",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "沉玉谷的舞狮少年，热情洋溢的街巷护卫。"
    },
    "chevreuse": {
        "id": "chevreuse", "name": "夏沃蕾", "element": "fire", "stars": 4, "role": "增伤",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "枫丹特巡队队长，恪守正义的铳枪射手。"
    },

    # ========== 水元素 (Water) - 13角色 ==========
    "mona": {
        "id": "mona", "name": "莫娜", "element": "water", "stars": 5, "role": "辅助",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 30, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "神秘的占星术士，以水镜之术洞悉天命。"
    },
    "tartaglia": {
        "id": "tartaglia", "name": "达达利亚", "element": "water", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "愚人众执行官第十一席「公子」，追求极致战斗的武人。"
    },
    "kokomi": {
        "id": "kokomi", "name": "珊瑚宫心海", "element": "water", "stars": 5, "role": "治疗",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "海祇岛的现人神巫女，足智多谋的战略家。"
    },
    "ayato": {
        "id": "ayato", "name": "神里绫人", "element": "water", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "社奉行神里家的家主，深藏不露的剑术大师。"
    },
    "yelan": {
        "id": "yelan", "name": "夜兰", "element": "water", "stars": 5, "role": "副C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "层岩巨渊的神秘来客，总务司的秘密特工。"
    },
    "nilou": {
        "id": "nilou", "name": "妮露", "element": "water", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "祖拜尔剧场的舞者，以舞姿诠释水之温柔。"
    },
    "neuvillette": {
        "id": "neuvillette", "name": "那维莱特", "element": "water", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "枫丹最高审判官，掌控公义之水龙。"
    },
    "furina": {
        "id": "furina", "name": "芙宁娜", "element": "water", "stars": 5, "role": "增伤",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "众水、众方、众民与众律法的女王。"
    },
    "sigewinne": {
        "id": "sigewinne", "name": "希格雯", "element": "water", "stars": 5, "role": "治疗",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "梅洛彼得堡的护士长，温柔可爱的小美露莘。"
    },
    "mualani": {
        "id": "mualani", "name": "玛拉妮", "element": "water", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "纳塔的水上滑板少女，海浪般自由的灵魂。"
    },
    "xingqiu": {
        "id": "xingqiu", "name": "行秋", "element": "water", "stars": 4, "role": "副C",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 20, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "飞云商会的二少爷，剑术精湛的书生。"
    },
    "barbara": {
        "id": "barbara", "name": "芭芭拉", "element": "water", "stars": 4, "role": "治疗",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "西风教会的祈礼牧师，用歌声治愈众人的偶像。"
    },
    "candace": {
        "id": "candace", "name": "坎蒂丝", "element": "water", "stars": 4, "role": "辅助",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "阿如村的守护者，温柔而坚定的沙漠之盾。"
    },

    # ========== 雷元素 (Thunder) - 15角色 ==========
    "keqing": {
        "id": "keqing", "name": "刻晴", "element": "thunder", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "璃月七星中的玉衡星，以雷厉风行著称。"
    },
    "raiden": {
        "id": "raiden", "name": "雷电将军", "element": "thunder", "stars": 5, "role": "副C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "稻妻的统治者，威严无双的雷电之神。"
    },
    "yae_miko": {
        "id": "yae_miko", "name": "八重神子", "element": "thunder", "stars": 5, "role": "副C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "鸣神大社的宫司，狡黠美丽的狐狸大人。"
    },
    "cyno": {
        "id": "cyno", "name": "赛诺", "element": "thunder", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "教令院的大风纪官，以冷面与狼灵维护正义。"
    },
    "clorinde": {
        "id": "clorinde", "name": "克洛琳德", "element": "thunder", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "枫丹决斗代理人，枪剑双绝的雷电决斗士。"
    },
    "varesa": {
        "id": "varesa", "name": "瓦蕾莎", "element": "thunder", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "纳塔的无畏战士，以雷霆之势横扫一切。"
    },
    "fischl": {
        "id": "fischl", "name": "菲谢尔", "element": "thunder", "stars": 4, "role": "副C",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 20, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "自称「断罪之皇女」的奇异少女，与夜鸦奥兹同行。"
    },
    "beidou": {
        "id": "beidou", "name": "北斗", "element": "thunder", "stars": 4, "role": "副C",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "南十字船队的首领，斩灭海山的无冕龙王。"
    },
    "lisa": {
        "id": "lisa", "name": "丽莎", "element": "thunder", "stars": 4, "role": "辅助",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 30, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "西风骑士团的图书管理员，慵懒而博学的魔女。"
    },
    "razor": {
        "id": "razor", "name": "雷泽", "element": "thunder", "stars": 4, "role": "主C",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "奔狼领的狼少年，以雷电与利爪撕碎敌人。"
    },
    "sara": {
        "id": "sara", "name": "九条裟罗", "element": "thunder", "stars": 4, "role": "增伤",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "天领奉行的大将，忠贞不渝的雷电将军追随者。"
    },
    "dori": {
        "id": "dori", "name": "多莉", "element": "thunder", "stars": 4, "role": "治疗",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "须弥的百宝商人，摩拉永远不嫌多的精明少女。"
    },
    "kuki": {
        "id": "kuki", "name": "久岐忍", "element": "thunder", "stars": 4, "role": "治疗",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "荒泷派的第一把手，持证上岗的律法专家兼医师。"
    },
    "sethos": {
        "id": "sethos", "name": "赛索斯", "element": "thunder", "stars": 4, "role": "主C",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "沙漠的年轻弓手，以雷霆之箭守护绿洲。"
    },
    "ororon": {
        "id": "ororon", "name": "欧洛伦", "element": "thunder", "stars": 4, "role": "副C",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "烟谜主的雾之影，隐于暗处的雷光猎手。"
    },

    # ========== 冰元素 (Ice) - 15角色 ==========
    "qiqi": {
        "id": "qiqi", "name": "七七", "element": "ice", "stars": 5, "role": "治疗",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "不卜庐的采药童子，身为僵尸却心地善良。"
    },
    "ganyu": {
        "id": "ganyu", "name": "甘雨", "element": "ice", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "璃月七星的月海亭秘书，温柔可靠的半仙之兽。"
    },
    "eula": {
        "id": "eula", "name": "优菈", "element": "ice", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "西风骑士团游击小队长，优雅复仇的贵族之女。"
    },
    "ayaka": {
        "id": "ayaka", "name": "神里绫华", "element": "ice", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "社奉行神里家的大小姐，白鹭般的冰华剑士。"
    },
    "shenhe": {
        "id": "shenhe", "name": "申鹤", "element": "ice", "stars": 5, "role": "增伤",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "留云借风真君的弟子，以冰寒之力增幅队友。"
    },
    "wriothesley": {
        "id": "wriothesley", "name": "莱欧斯利", "element": "ice", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "梅洛彼得堡的公爵，以冰拳统治要塞的王者。"
    },
    "citlali": {
        "id": "citlali", "name": "茜特菈莉", "element": "ice", "stars": 5, "role": "护盾",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "烟谜主的祖母，以冰盾守护族人的智者。"
    },
    "diona": {
        "id": "diona", "name": "迪奥娜", "element": "ice", "stars": 4, "role": "护盾",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "猫尾酒馆的调酒师，讨厌酒却调得一手好酒。"
    },
    "kaeya": {
        "id": "kaeya", "name": "凯亚", "element": "ice", "stars": 4, "role": "副C",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "西风骑士团骑兵队长，神秘而迷人的冰剑骑士。"
    },
    "chongyun": {
        "id": "chongyun", "name": "重云", "element": "ice", "stars": 4, "role": "辅助",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "驱邪世家的少年方士，以冰剑镇压妖邪。"
    },
    "rosaria": {
        "id": "rosaria", "name": "罗莎莉亚", "element": "ice", "stars": 4, "role": "副C",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "西风教会的不羁修女，冰冷的暗夜处刑人。"
    },
    "layla": {
        "id": "layla", "name": "莱依拉", "element": "ice", "stars": 4, "role": "护盾",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "梨多梵谛学院的学生，在星空下构筑冰之护盾。"
    },
    "mika": {
        "id": "mika", "name": "米卡", "element": "ice", "stars": 4, "role": "增伤",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "西风骑士团的测绘员，以精准制导支援队友。"
    },
    "charlotte": {
        "id": "charlotte", "name": "夏洛蒂", "element": "ice", "stars": 4, "role": "治疗",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "蒸汽鸟报的热血记者，以冰霜镜头记录真相。"
    },
    "freminet": {
        "id": "freminet", "name": "菲米尼", "element": "ice", "stars": 4, "role": "主C",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "枫丹的潜水少年，冷酷外表下藏着温柔的心。"
    },

    # ========== 风元素 (Wind) - 13角色 ==========
    "jean": {
        "id": "jean", "name": "琴", "element": "wind", "stars": 5, "role": "治疗",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "西风骑士团代理团长，以风之剑守护蒙德的蒲公英骑士。"
    },
    "venti": {
        "id": "venti", "name": "温迪", "element": "wind", "stars": 5, "role": "控制",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 30, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "蒙德的吟游诗人，真实身份为风神巴巴托斯。"
    },
    "xiao": {
        "id": "xiao", "name": "魈", "element": "wind", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "守护璃月的夜叉仙人，以风枪扫荡群魔。"
    },
    "kazuha": {
        "id": "kazuha", "name": "枫原万叶", "element": "wind", "stars": 5, "role": "增伤",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 30, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "南十字舰队的浪人，以秋风之刃聚敌增伤。"
    },
    "wanderer": {
        "id": "wanderer", "name": "流浪者", "element": "wind", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "漂泊世间的倾奇者，以风之翼俯瞰众生。"
    },
    "xianyun": {
        "id": "xianyun", "name": "闲云", "element": "wind", "stars": 5, "role": "治疗",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "留云借风真君的人间化身，以仙法疗愈众生。"
    },
    "chasca": {
        "id": "chasca", "name": "恰斯卡", "element": "wind", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "纳塔的天空射手，以风之子弹洞穿一切。"
    },
    "sucrose": {
        "id": "sucrose", "name": "砂糖", "element": "wind", "stars": 4, "role": "增伤",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 30, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "西风骑士团的天才炼金术士，研究生物炼成的少女。"
    },
    "sayu": {
        "id": "sayu", "name": "早柚", "element": "wind", "stars": 4, "role": "治疗",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "终末番的小忍者，只想睡觉长高的小狸猫。"
    },
    "heizou": {
        "id": "heizou", "name": "鹿野院平藏", "element": "wind", "stars": 4, "role": "主C",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "天领奉行的天才侦探，以风拳破案的少年。"
    },
    "faruzan": {
        "id": "faruzan", "name": "珐露珊", "element": "wind", "stars": 4, "role": "增伤",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "教令院百年难遇的天才，穿越时空的机关大师。"
    },
    "lynette": {
        "id": "lynette", "name": "琳妮特", "element": "wind", "stars": 4, "role": "辅助",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "枫丹的魔术助手，沉默寡言却身手矫健的猫娘。"
    },
    "lanyan": {
        "id": "lanyan", "name": "蓝燕", "element": "wind", "stars": 4, "role": "护盾",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "沉玉谷的风之舞者，以羽扇抵挡伤害的燕子少女。"
    },

    # ========== 岩元素 (Rock) - 11角色 ==========
    "zhongli": {
        "id": "zhongli", "name": "钟离", "element": "rock", "stars": 5, "role": "护盾",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "往生堂的神秘客卿，磐岩般不可撼动的岩王帝君。"
    },
    "albedo": {
        "id": "albedo", "name": "阿贝多", "element": "rock", "stars": 5, "role": "副C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 30, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "西风骑士团首席炼金术士，以岩花绽放创造之力。"
    },
    "itto": {
        "id": "itto", "name": "荒泷一斗", "element": "rock", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "荒泷派的老大，以岩拳粉碎一切的鬼族少年。"
    },
    "navia": {
        "id": "navia", "name": "娜维娅", "element": "rock", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "刺玫会的会长，岩晶弹雨倾泻的优雅淑女。"
    },
    "chiori": {
        "id": "chiori", "name": "千织", "element": "rock", "stars": 5, "role": "副C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "枫丹的时尚设计师，以绸缎与岩刃编织优雅杀阵。"
    },
    "xilonen": {
        "id": "xilonen", "name": "希诺宁", "element": "rock", "stars": 5, "role": "增伤",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "回声之子的铁匠少女，以岩之歌谣增幅队友之力。"
    },
    "ningguang": {
        "id": "ningguang", "name": "凝光", "element": "rock", "stars": 4, "role": "主C",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "璃月七星的天权星，以宝石之雨掌握财富与权力。"
    },
    "noelle": {
        "id": "noelle", "name": "诺艾尔", "element": "rock", "stars": 4, "role": "护盾",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "西风骑士团的万能女仆，以岩盾守护一切。"
    },
    "gorou": {
        "id": "gorou", "name": "五郎", "element": "rock", "stars": 4, "role": "增伤",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "珊瑚宫的大将，忠诚可靠的兽耳少年将领。"
    },
    "yunjin": {
        "id": "yunjin", "name": "云堇", "element": "rock", "stars": 4, "role": "增伤",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "和裕茶室的戏班班主，以岩韵戏曲鼓舞友人。"
    },
    "kachina": {
        "id": "kachina", "name": "卡齐娜", "element": "rock", "stars": 4, "role": "辅助",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "回声之子的旅者，以岩之图腾引领前路。"
    },

    # ========== 草元素 (Grass) - 10角色 ==========
    "nahida": {
        "id": "nahida", "name": "纳西妲", "element": "grass", "stars": 5, "role": "辅助",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 50, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "须弥的小吉祥草王，以智慧之种联结万物。"
    },
    "tighnari": {
        "id": "tighnari", "name": "提纳里", "element": "grass", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "化城郭的巡林官，以藤蔓之箭守护雨林的狐人。"
    },
    "alhaitham": {
        "id": "alhaitham", "name": "艾尔海森", "element": "grass", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "教令院的书记官，以理性之叶刃斩断纷扰。"
    },
    "baizhu": {
        "id": "baizhu", "name": "白术", "element": "grass", "stars": 5, "role": "治疗",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "不卜庐的老板，以仙草之息治愈万物的医师。"
    },
    "kinich": {
        "id": "kinich", "name": "基尼奇", "element": "grass", "stars": 5, "role": "主C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "悬木人的草之猎手，以荆棘之枪贯穿猎物。"
    },
    "emilie": {
        "id": "emilie", "name": "艾梅莉埃", "element": "grass", "stars": 5, "role": "副C",
        "base_atk": 280, "base_def": 200, "base_hp": 1100,
        "atk_growth": 0.028, "def_growth": 0.025, "hp_growth": 0.028,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "枫丹的香水师，以芬芳之毒麻痹敌人的调香师。"
    },
    "collei": {
        "id": "collei", "name": "柯莱", "element": "grass", "stars": 4, "role": "副C",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "化城郭的见习巡林员，以藤蔓与希望抗争命运的少女。"
    },
    "yaoyao": {
        "id": "yaoyao", "name": "瑶瑶", "element": "grass", "stars": 4, "role": "治疗",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "歌尘浪市真君的弟子，以月桂之灵治愈同伴的可爱少女。"
    },
    "kaveh": {
        "id": "kaveh", "name": "卡维", "element": "grass", "stars": 4, "role": "主C",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "须弥的天才建筑师，以草之种子绽放毁灭之美。"
    },
    "kirara": {
        "id": "kirara", "name": "绮良良", "element": "grass", "stars": 4, "role": "护盾",
        "base_atk": 210, "base_def": 180, "base_hp": 1000,
        "atk_growth": 0.025, "def_growth": 0.022, "hp_growth": 0.026,
        "base_em": 0, "base_er": 1.0, "base_cr": 0.05, "base_cd": 0.50,
        "description": "狛荷屋的猫又快递员，以草之猫箱守护同伴。"
    },
}

# ==================== 元素反应定义 ====================
REACTIONS = {
    # --- 增幅反应（伤害倍率加成）---
    "fire+water": {
        "name": "蒸发", "type": "amplify", "multiplier": 1.5,
        "description": "火打水，伤害×1.5"
    },
    "water+fire": {
        "name": "蒸发", "type": "amplify", "multiplier": 2.0,
        "description": "水打火，伤害×2.0"
    },
    "fire+ice": {
        "name": "融化", "type": "amplify", "multiplier": 2.0,
        "description": "火打冰，伤害×2.0"
    },
    "ice+fire": {
        "name": "融化", "type": "amplify", "multiplier": 1.5,
        "description": "冰打火，伤害×1.5"
    },
    # --- 剧变反应（固定伤害）---
    "fire+thunder": {
        "name": "超载", "type": "transform", "base_dmg_ratio": 2.0,
        "aoe": True,
        "description": "范围火伤 + 击退"
    },
    "thunder+fire": {
        "name": "超载", "type": "transform", "base_dmg_ratio": 2.0,
        "aoe": True,
        "description": "范围火伤 + 击退"
    },
    "ice+thunder": {
        "name": "超导", "type": "transform", "base_dmg_ratio": 1.0,
        "debuff": {"phys_res_down": 0.40, "duration": 2},
        "description": "范围冰伤 + 减物抗40%"
    },
    "thunder+ice": {
        "name": "超导", "type": "transform", "base_dmg_ratio": 1.0,
        "debuff": {"phys_res_down": 0.40, "duration": 2},
        "description": "范围冰伤 + 减物抗40%"
    },
    "water+thunder": {
        "name": "感电", "type": "transform", "base_dmg_ratio": 1.5,
        "dot": True, "dot_turns": 2,
        "description": "持续雷伤2回合，可连锁"
    },
    "thunder+water": {
        "name": "感电", "type": "transform", "base_dmg_ratio": 1.5,
        "dot": True, "dot_turns": 2,
        "description": "持续雷伤2回合，可连锁"
    },
    # --- 控制反应 ---
    "water+ice": {
        "name": "冻结", "type": "control", "freeze_turns": 1,
        "description": "冻结敌人1回合"
    },
    "ice+water": {
        "name": "冻结", "type": "control", "freeze_turns": 1,
        "description": "冻结敌人1回合"
    },
}

# ==================== 元素共鸣 ====================
RESONANCES = {
    "fire": {
        "name": "热诚之火", "condition": 2,
        "effect": {"atk_pct": 0.25},
        "description": "全队攻击力+25%"
    },
    "water": {
        "name": "愈疗之水", "condition": 2,
        "effect": {"heal_bonus": 0.30},
        "description": "全队受治疗+30%"
    },
    "thunder": {
        "name": "强能之雷", "condition": 2,
        "effect": {"er_bonus": 0.30},
        "description": "充能效率+30%"
    },
    "ice": {
        "name": "粉碎之冰", "condition": 2,
        "effect": {"cr_bonus": 0.15},
        "description": "暴击率+15%"
    },
    "wind": {
        "name": "迅捷之风", "condition": 2,
        "effect": {"cd_reduction": 0.15},
        "description": "冷却时间-15%"
    },
    "rock": {
        "name": "坚定之岩", "condition": 2,
        "effect": {"shield_bonus": 0.15, "shield_dmg_bonus": 0.15},
        "description": "护盾强效+15%，护盾下伤害+15%"
    },
    "grass": {
        "name": "蔓生之草", "condition": 2,
        "effect": {"em_bonus": 80},
        "description": "全队精通+80"
    },
}

# ==================== 敌人定义 ====================
ENEMIES = {
    "hilichurl": {
        "id": "hilichurl", "name": "丘丘人",
        "base_hp": 200, "base_atk": 30, "base_def": 30,
        "level_scale": 1.0,
        "rewards": {"mora": (50, 100), "exp_books": (0, 1)},
    },
    "hilichurl_fighter": {
        "id": "hilichurl_fighter", "name": "丘丘人战士",
        "base_hp": 500, "base_atk": 60, "base_def": 50,
        "level_scale": 1.2,
        "rewards": {"mora": (100, 200), "exp_books": (1, 2)},
    },
    "slime_fire": {
        "id": "slime_fire", "name": "火史莱姆",
        "element": "fire",
        "base_hp": 300, "base_atk": 50, "base_def": 40,
        "level_scale": 1.0,
        "rewards": {"mora": (80, 150), "exp_books": (0, 1)},
    },
    "slime_water": {
        "id": "slime_water", "name": "水史莱姆",
        "element": "water",
        "base_hp": 350, "base_atk": 45, "base_def": 45,
        "level_scale": 1.0,
        "rewards": {"mora": (80, 150), "exp_books": (0, 1)},
    },
    "abyss_mage": {
        "id": "abyss_mage", "name": "深渊法师",
        "base_hp": 1500, "base_atk": 100, "base_def": 80,
        "level_scale": 1.5,
        "rewards": {"mora": (300, 500), "exp_books": (2, 4)},
    },
    "ruin_guard": {
        "id": "ruin_guard", "name": "遗迹守卫",
        "base_hp": 5000, "base_atk": 200, "base_def": 150,
        "level_scale": 2.0,
        "rewards": {"mora": (800, 1200), "exp_books": (4, 8)},
    },
}

# ==================== 关卡定义 ====================
STAGES = [
    {
        "id": 1, "name": "蒙德·低语森林",
        "waves": [
            {"enemy": "hilichurl", "count": 2},
            {"enemy": "slime_fire", "count": 1},
        ],
        "level": 1, "unlock_cost": 0, "mora_per_hour": 100,
    },
    {
        "id": 2, "name": "蒙德·风起地",
        "waves": [
            {"enemy": "hilichurl_fighter", "count": 2},
            {"enemy": "slime_water", "count": 1},
        ],
        "level": 5, "unlock_cost": 0, "mora_per_hour": 200,
    },
    {
        "id": 3, "name": "蒙德·风龙废墟",
        "waves": [
            {"enemy": "hilichurl_fighter", "count": 2},
            {"enemy": "abyss_mage", "count": 1},
        ],
        "level": 10, "unlock_cost": 0, "mora_per_hour": 400,
    },
    {
        "id": 4, "name": "璃月·归离原",
        "waves": [
            {"enemy": "abyss_mage", "count": 2},
            {"enemy": "slime_fire", "count": 1},
        ],
        "level": 20, "unlock_cost": 1000, "mora_per_hour": 800,
    },
    {
        "id": 5, "name": "璃月·孤云阁",
        "waves": [
            {"enemy": "ruin_guard", "count": 1},
            {"enemy": "abyss_mage", "count": 1},
        ],
        "level": 35, "unlock_cost": 5000, "mora_per_hour": 1500,
    },
]

# ==================== 等级相关 ====================
MAX_LEVEL = {3: 40, 4: 60, 5: 90}

def get_exp_books_for_level(level):
    """返回从当前等级升到下一级需要的经验书数量"""
    return int(2 + level * 0.5)

# ==================== 抽卡概率 ====================
GACHA_RATES = {
    "standard": {"5star": 0.016, "4star": 0.13, "3star": 0.854},
    "limited":  {"5star": 0.016, "4star": 0.13, "3star": 0.854},
    "beginner": {"5star": 0.016, "4star": 0.20, "3star": 0.784},
}

GACHA_PITY = {
    "standard": 90,
    "limited": 90,
    "beginner": 50,
}

GACHA_SOFT_PITY_START = 74

STANDARD_5STAR = ["diluc", "mona", "keqing", "qiqi", "jean", "tighnari", "dehya"]
STANDARD_4STAR = ["bennett", "xingqiu", "fischl", "diona"]

# ==================== 塔防属性（叠加到角色上） ====================
# 每个角色的塔防塔属性: cost(部署费用), range(射程格数), atk_speed(每秒攻击次数),
#   td_dmg(基础伤害), td_ability(特殊能力), td_ability_cd(技能冷却秒数)
TD_TOWER_STATS = {
    # ========== 火元素 ==========
    "diluc": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "flame_slash", "td_ability_cd": 8,
        "td_ability_desc": "火焰斩：对前方扇形造成200%伤害并挂火"
    },
    "klee": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "flame_slash", "td_ability_cd": 8,
        "td_ability_desc": "火焰斩：对前方扇形造成200%伤害并挂火"
    },
    "hutao": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "flame_slash", "td_ability_cd": 8,
        "td_ability_desc": "火焰斩：对前方扇形造成200%伤害并挂火"
    },
    "yoimiya": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "flame_slash", "td_ability_cd": 8,
        "td_ability_desc": "火焰斩：对前方扇形造成200%伤害并挂火"
    },
    "dehya": {
        "cost": 250, "range": 2.0, "atk_speed": 1.0, "td_dmg": 30,
        "td_ability": "atk_buff", "td_ability_cd": 12,
        "td_ability_desc": "增伤：周围友方塔攻击力+40%，持续6秒"
    },
    "lyney": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "flame_slash", "td_ability_cd": 8,
        "td_ability_desc": "火焰斩：对前方扇形造成200%伤害并挂火"
    },
    "arlecchino": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "flame_slash", "td_ability_cd": 8,
        "td_ability_desc": "火焰斩：对前方扇形造成200%伤害并挂火"
    },
    "mavuika": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "flame_slash", "td_ability_cd": 8,
        "td_ability_desc": "火焰斩：对前方扇形造成200%伤害并挂火"
    },
    "bennett": {
        "cost": 300, "range": 2.5, "atk_speed": 0.9, "td_dmg": 35,
        "td_ability": "atk_buff", "td_ability_cd": 12,
        "td_ability_desc": "增伤：周围友方塔攻击力+40%，持续6秒"
    },
    "xiangling": {
        "cost": 350, "range": 2.5, "atk_speed": 1.5, "td_dmg": 45,
        "td_ability": "flame_slash", "td_ability_cd": 8,
        "td_ability_desc": "火焰斩：对前方扇形造成200%伤害并挂火"
    },
    "amber": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "flame_slash", "td_ability_cd": 8,
        "td_ability_desc": "火焰斩：对前方扇形造成200%伤害并挂火"
    },
    "xinyan": {
        "cost": 300, "range": 2.0, "atk_speed": 0.7, "td_dmg": 25,
        "td_ability": "flame_slash", "td_ability_cd": 8,
        "td_ability_desc": "火焰斩：对前方扇形造成200%伤害并挂火"
    },
    "yanfei": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "flame_slash", "td_ability_cd": 8,
        "td_ability_desc": "火焰斩：对前方扇形造成200%伤害并挂火"
    },
    "thoma": {
        "cost": 300, "range": 2.0, "atk_speed": 0.7, "td_dmg": 25,
        "td_ability": "flame_slash", "td_ability_cd": 8,
        "td_ability_desc": "火焰斩：对前方扇形造成200%伤害并挂火"
    },
    "gaming": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "flame_slash", "td_ability_cd": 8,
        "td_ability_desc": "火焰斩：对前方扇形造成200%伤害并挂火"
    },
    "chevreuse": {
        "cost": 300, "range": 2.5, "atk_speed": 0.9, "td_dmg": 35,
        "td_ability": "atk_buff", "td_ability_cd": 12,
        "td_ability_desc": "增伤：周围友方塔攻击力+40%，持续6秒"
    },

    # ========== 水元素 ==========
    "mona": {
        "cost": 250, "range": 2.0, "atk_speed": 1.0, "td_dmg": 30,
        "td_ability": "dmg_debuff", "td_ability_cd": 14,
        "td_ability_desc": "减益：范围内敌人受到伤害+50%，持续5秒"
    },
    "tartaglia": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "coordinated_atk", "td_ability_cd": 10,
        "td_ability_desc": "协同攻击：攻速翻倍+额外挂水，持续5秒"
    },
    "kokomi": {
        "cost": 400, "range": 2.0, "atk_speed": 0.6, "td_dmg": 20,
        "td_ability": "coordinated_atk", "td_ability_cd": 10,
        "td_ability_desc": "协同攻击：攻速翻倍+额外挂水，持续5秒"
    },
    "ayato": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "coordinated_atk", "td_ability_cd": 10,
        "td_ability_desc": "协同攻击：攻速翻倍+额外挂水，持续5秒"
    },
    "yelan": {
        "cost": 350, "range": 2.5, "atk_speed": 1.5, "td_dmg": 45,
        "td_ability": "coordinated_atk", "td_ability_cd": 10,
        "td_ability_desc": "协同攻击：攻速翻倍+额外挂水，持续5秒"
    },
    "nilou": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "coordinated_atk", "td_ability_cd": 10,
        "td_ability_desc": "协同攻击：攻速翻倍+额外挂水，持续5秒"
    },
    "neuvillette": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "coordinated_atk", "td_ability_cd": 10,
        "td_ability_desc": "协同攻击：攻速翻倍+额外挂水，持续5秒"
    },
    "furina": {
        "cost": 300, "range": 2.5, "atk_speed": 0.9, "td_dmg": 35,
        "td_ability": "dmg_debuff", "td_ability_cd": 14,
        "td_ability_desc": "减益：范围内敌人受到伤害+50%，持续5秒"
    },
    "sigewinne": {
        "cost": 400, "range": 2.0, "atk_speed": 0.6, "td_dmg": 20,
        "td_ability": "coordinated_atk", "td_ability_cd": 10,
        "td_ability_desc": "协同攻击：攻速翻倍+额外挂水，持续5秒"
    },
    "mualani": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "coordinated_atk", "td_ability_cd": 10,
        "td_ability_desc": "协同攻击：攻速翻倍+额外挂水，持续5秒"
    },
    "xingqiu": {
        "cost": 350, "range": 2.5, "atk_speed": 1.5, "td_dmg": 45,
        "td_ability": "coordinated_atk", "td_ability_cd": 10,
        "td_ability_desc": "协同攻击：攻速翻倍+额外挂水，持续5秒"
    },
    "barbara": {
        "cost": 400, "range": 2.0, "atk_speed": 0.6, "td_dmg": 20,
        "td_ability": "coordinated_atk", "td_ability_cd": 10,
        "td_ability_desc": "协同攻击：攻速翻倍+额外挂水，持续5秒"
    },
    "candace": {
        "cost": 250, "range": 2.0, "atk_speed": 1.0, "td_dmg": 30,
        "td_ability": "dmg_debuff", "td_ability_cd": 14,
        "td_ability_desc": "减益：范围内敌人受到伤害+50%，持续5秒"
    },

    # ========== 雷元素 ==========
    "keqing": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "teleport_strike", "td_ability_cd": 6,
        "td_ability_desc": "瞬击：对范围内最强敌人造成340%雷伤"
    },
    "raiden": {
        "cost": 350, "range": 2.5, "atk_speed": 1.5, "td_dmg": 45,
        "td_ability": "summon_oz", "td_ability_cd": 12,
        "td_ability_desc": "召唤：召唤独立攻击单位，持续8秒"
    },
    "yae_miko": {
        "cost": 350, "range": 2.5, "atk_speed": 1.5, "td_dmg": 45,
        "td_ability": "summon_oz", "td_ability_cd": 12,
        "td_ability_desc": "召唤：召唤独立攻击单位，持续8秒"
    },
    "cyno": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "teleport_strike", "td_ability_cd": 6,
        "td_ability_desc": "瞬击：对范围内最强敌人造成340%雷伤"
    },
    "clorinde": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "teleport_strike", "td_ability_cd": 6,
        "td_ability_desc": "瞬击：对范围内最强敌人造成340%雷伤"
    },
    "varesa": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "teleport_strike", "td_ability_cd": 6,
        "td_ability_desc": "瞬击：对范围内最强敌人造成340%雷伤"
    },
    "fischl": {
        "cost": 350, "range": 2.5, "atk_speed": 1.5, "td_dmg": 45,
        "td_ability": "summon_oz", "td_ability_cd": 12,
        "td_ability_desc": "召唤：召唤独立攻击单位，持续8秒"
    },
    "beidou": {
        "cost": 350, "range": 2.5, "atk_speed": 1.5, "td_dmg": 45,
        "td_ability": "summon_oz", "td_ability_cd": 12,
        "td_ability_desc": "召唤：召唤独立攻击单位，持续8秒"
    },
    "lisa": {
        "cost": 250, "range": 2.0, "atk_speed": 1.0, "td_dmg": 30,
        "td_ability": "teleport_strike", "td_ability_cd": 6,
        "td_ability_desc": "瞬击：对范围内最强敌人造成340%雷伤"
    },
    "razor": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "teleport_strike", "td_ability_cd": 6,
        "td_ability_desc": "瞬击：对范围内最强敌人造成340%雷伤"
    },
    "sara": {
        "cost": 300, "range": 2.5, "atk_speed": 0.9, "td_dmg": 35,
        "td_ability": "teleport_strike", "td_ability_cd": 6,
        "td_ability_desc": "瞬击：对范围内最强敌人造成340%雷伤"
    },
    "dori": {
        "cost": 400, "range": 2.0, "atk_speed": 0.6, "td_dmg": 20,
        "td_ability": "teleport_strike", "td_ability_cd": 6,
        "td_ability_desc": "瞬击：对范围内最强敌人造成340%雷伤"
    },
    "kuki": {
        "cost": 400, "range": 2.0, "atk_speed": 0.6, "td_dmg": 20,
        "td_ability": "teleport_strike", "td_ability_cd": 6,
        "td_ability_desc": "瞬击：对范围内最强敌人造成340%雷伤"
    },
    "sethos": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "teleport_strike", "td_ability_cd": 6,
        "td_ability_desc": "瞬击：对范围内最强敌人造成340%雷伤"
    },
    "ororon": {
        "cost": 350, "range": 2.5, "atk_speed": 1.5, "td_dmg": 45,
        "td_ability": "summon_oz", "td_ability_cd": 12,
        "td_ability_desc": "召唤：召唤独立攻击单位，持续8秒"
    },

    # ========== 冰元素 ==========
    "qiqi": {
        "cost": 400, "range": 2.0, "atk_speed": 0.6, "td_dmg": 20,
        "td_ability": "party_heal", "td_ability_cd": 15,
        "td_ability_desc": "治疗：全场友方塔回复40%生命"
    },
    "ganyu": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "party_heal", "td_ability_cd": 15,
        "td_ability_desc": "治疗：全场友方塔回复40%生命"
    },
    "eula": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "party_heal", "td_ability_cd": 15,
        "td_ability_desc": "治疗：全场友方塔回复40%生命"
    },
    "ayaka": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "party_heal", "td_ability_cd": 15,
        "td_ability_desc": "治疗：全场友方塔回复40%生命"
    },
    "shenhe": {
        "cost": 300, "range": 2.5, "atk_speed": 0.9, "td_dmg": 35,
        "td_ability": "party_heal", "td_ability_cd": 15,
        "td_ability_desc": "治疗：全场友方塔回复40%生命"
    },
    "wriothesley": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "party_heal", "td_ability_cd": 15,
        "td_ability_desc": "治疗：全场友方塔回复40%生命"
    },
    "citlali": {
        "cost": 300, "range": 2.0, "atk_speed": 0.7, "td_dmg": 25,
        "td_ability": "shield_slow", "td_ability_cd": 12,
        "td_ability_desc": "护盾减速：周围友方塔获得护盾+范围敌人减速50%"
    },
    "diona": {
        "cost": 300, "range": 2.0, "atk_speed": 0.7, "td_dmg": 25,
        "td_ability": "shield_slow", "td_ability_cd": 12,
        "td_ability_desc": "护盾减速：周围友方塔获得护盾+范围敌人减速50%"
    },
    "kaeya": {
        "cost": 350, "range": 2.5, "atk_speed": 1.5, "td_dmg": 45,
        "td_ability": "party_heal", "td_ability_cd": 15,
        "td_ability_desc": "治疗：全场友方塔回复40%生命"
    },
    "chongyun": {
        "cost": 250, "range": 2.0, "atk_speed": 1.0, "td_dmg": 30,
        "td_ability": "party_heal", "td_ability_cd": 15,
        "td_ability_desc": "治疗：全场友方塔回复40%生命"
    },
    "rosaria": {
        "cost": 350, "range": 2.5, "atk_speed": 1.5, "td_dmg": 45,
        "td_ability": "party_heal", "td_ability_cd": 15,
        "td_ability_desc": "治疗：全场友方塔回复40%生命"
    },
    "layla": {
        "cost": 300, "range": 2.0, "atk_speed": 0.7, "td_dmg": 25,
        "td_ability": "shield_slow", "td_ability_cd": 12,
        "td_ability_desc": "护盾减速：周围友方塔获得护盾+范围敌人减速50%"
    },
    "mika": {
        "cost": 300, "range": 2.5, "atk_speed": 0.9, "td_dmg": 35,
        "td_ability": "party_heal", "td_ability_cd": 15,
        "td_ability_desc": "治疗：全场友方塔回复40%生命"
    },
    "charlotte": {
        "cost": 400, "range": 2.0, "atk_speed": 0.6, "td_dmg": 20,
        "td_ability": "party_heal", "td_ability_cd": 15,
        "td_ability_desc": "治疗：全场友方塔回复40%生命"
    },
    "freminet": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "party_heal", "td_ability_cd": 15,
        "td_ability_desc": "治疗：全场友方塔回复40%生命"
    },

    # ========== 风元素 ==========
    "jean": {
        "cost": 400, "range": 2.0, "atk_speed": 0.6, "td_dmg": 20,
        "td_ability": "atk_buff", "td_ability_cd": 12,
        "td_ability_desc": "增伤：周围友方塔攻击力+40%，持续6秒"
    },
    "venti": {
        "cost": 350, "range": 3.0, "atk_speed": 1.0, "td_dmg": 35,
        "td_ability": "atk_buff", "td_ability_cd": 12,
        "td_ability_desc": "增伤：周围友方塔攻击力+40%，持续6秒"
    },
    "xiao": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "coordinated_atk", "td_ability_cd": 10,
        "td_ability_desc": "协同：攻速翻倍，持续5秒"
    },
    "kazuha": {
        "cost": 300, "range": 2.5, "atk_speed": 0.9, "td_dmg": 35,
        "td_ability": "atk_buff", "td_ability_cd": 12,
        "td_ability_desc": "增伤：周围友方塔攻击力+40%，持续6秒"
    },
    "wanderer": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "coordinated_atk", "td_ability_cd": 10,
        "td_ability_desc": "协同：攻速翻倍，持续5秒"
    },
    "xianyun": {
        "cost": 400, "range": 2.0, "atk_speed": 0.6, "td_dmg": 20,
        "td_ability": "atk_buff", "td_ability_cd": 12,
        "td_ability_desc": "增伤：周围友方塔攻击力+40%，持续6秒"
    },
    "chasca": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "coordinated_atk", "td_ability_cd": 10,
        "td_ability_desc": "协同：攻速翻倍，持续5秒"
    },
    "sucrose": {
        "cost": 300, "range": 2.5, "atk_speed": 0.9, "td_dmg": 35,
        "td_ability": "atk_buff", "td_ability_cd": 12,
        "td_ability_desc": "增伤：周围友方塔攻击力+40%，持续6秒"
    },
    "sayu": {
        "cost": 400, "range": 2.0, "atk_speed": 0.6, "td_dmg": 20,
        "td_ability": "atk_buff", "td_ability_cd": 12,
        "td_ability_desc": "增伤：周围友方塔攻击力+40%，持续6秒"
    },
    "heizou": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "coordinated_atk", "td_ability_cd": 10,
        "td_ability_desc": "协同：攻速翻倍，持续5秒"
    },
    "faruzan": {
        "cost": 300, "range": 2.5, "atk_speed": 0.9, "td_dmg": 35,
        "td_ability": "atk_buff", "td_ability_cd": 12,
        "td_ability_desc": "增伤：周围友方塔攻击力+40%，持续6秒"
    },
    "lynette": {
        "cost": 250, "range": 2.0, "atk_speed": 1.0, "td_dmg": 30,
        "td_ability": "atk_buff", "td_ability_cd": 12,
        "td_ability_desc": "增伤：周围友方塔攻击力+40%，持续6秒"
    },
    "lanyan": {
        "cost": 300, "range": 2.0, "atk_speed": 0.7, "td_dmg": 25,
        "td_ability": "atk_buff", "td_ability_cd": 12,
        "td_ability_desc": "增伤：周围友方塔攻击力+40%，持续6秒"
    },

    # ========== 岩元素 ==========
    "zhongli": {
        "cost": 300, "range": 2.0, "atk_speed": 0.7, "td_dmg": 25,
        "td_ability": "shield_slow", "td_ability_cd": 12,
        "td_ability_desc": "护盾：周围友方塔获得护盾+范围敌人减速50%"
    },
    "albedo": {
        "cost": 350, "range": 2.5, "atk_speed": 1.5, "td_dmg": 45,
        "td_ability": "shield_slow", "td_ability_cd": 12,
        "td_ability_desc": "护盾：周围友方塔获得护盾+范围敌人减速50%"
    },
    "itto": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "atk_buff", "td_ability_cd": 12,
        "td_ability_desc": "增幅：自身和周围友方塔攻击力+40%"
    },
    "navia": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "atk_buff", "td_ability_cd": 12,
        "td_ability_desc": "增幅：自身和周围友方塔攻击力+40%"
    },
    "chiori": {
        "cost": 350, "range": 2.5, "atk_speed": 1.5, "td_dmg": 45,
        "td_ability": "shield_slow", "td_ability_cd": 12,
        "td_ability_desc": "护盾：周围友方塔获得护盾+范围敌人减速50%"
    },
    "xilonen": {
        "cost": 300, "range": 2.5, "atk_speed": 0.9, "td_dmg": 35,
        "td_ability": "shield_slow", "td_ability_cd": 12,
        "td_ability_desc": "护盾：周围友方塔获得护盾+范围敌人减速50%"
    },
    "ningguang": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "atk_buff", "td_ability_cd": 12,
        "td_ability_desc": "增幅：自身和周围友方塔攻击力+40%"
    },
    "noelle": {
        "cost": 300, "range": 2.0, "atk_speed": 0.7, "td_dmg": 25,
        "td_ability": "shield_slow", "td_ability_cd": 12,
        "td_ability_desc": "护盾：周围友方塔获得护盾+范围敌人减速50%"
    },
    "gorou": {
        "cost": 300, "range": 2.5, "atk_speed": 0.9, "td_dmg": 35,
        "td_ability": "shield_slow", "td_ability_cd": 12,
        "td_ability_desc": "护盾：周围友方塔获得护盾+范围敌人减速50%"
    },
    "yunjin": {
        "cost": 300, "range": 2.5, "atk_speed": 0.9, "td_dmg": 35,
        "td_ability": "shield_slow", "td_ability_cd": 12,
        "td_ability_desc": "护盾：周围友方塔获得护盾+范围敌人减速50%"
    },
    "kachina": {
        "cost": 250, "range": 2.0, "atk_speed": 1.0, "td_dmg": 30,
        "td_ability": "shield_slow", "td_ability_cd": 12,
        "td_ability_desc": "护盾：周围友方塔获得护盾+范围敌人减速50%"
    },

    # ========== 草元素 ==========
    "nahida": {
        "cost": 250, "range": 2.0, "atk_speed": 1.0, "td_dmg": 30,
        "td_ability": "dmg_debuff", "td_ability_cd": 14,
        "td_ability_desc": "减益：范围内敌人受到伤害+50%"
    },
    "tighnari": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "dmg_debuff", "td_ability_cd": 14,
        "td_ability_desc": "减益：范围内敌人受到伤害+50%"
    },
    "alhaitham": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "dmg_debuff", "td_ability_cd": 14,
        "td_ability_desc": "减益：范围内敌人受到伤害+50%"
    },
    "baizhu": {
        "cost": 400, "range": 2.0, "atk_speed": 0.6, "td_dmg": 20,
        "td_ability": "party_heal", "td_ability_cd": 15,
        "td_ability_desc": "治疗：全场友方塔回复40%生命"
    },
    "kinich": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "dmg_debuff", "td_ability_cd": 14,
        "td_ability_desc": "减益：范围内敌人受到伤害+50%"
    },
    "emilie": {
        "cost": 350, "range": 2.5, "atk_speed": 1.5, "td_dmg": 45,
        "td_ability": "dmg_debuff", "td_ability_cd": 14,
        "td_ability_desc": "减益：范围内敌人受到伤害+50%"
    },
    "collei": {
        "cost": 350, "range": 2.5, "atk_speed": 1.5, "td_dmg": 45,
        "td_ability": "dmg_debuff", "td_ability_cd": 14,
        "td_ability_desc": "减益：范围内敌人受到伤害+50%"
    },
    "yaoyao": {
        "cost": 400, "range": 2.0, "atk_speed": 0.6, "td_dmg": 20,
        "td_ability": "party_heal", "td_ability_cd": 15,
        "td_ability_desc": "治疗：全场友方塔回复40%生命"
    },
    "kaveh": {
        "cost": 500, "range": 2.0, "atk_speed": 1.2, "td_dmg": 60,
        "td_ability": "dmg_debuff", "td_ability_cd": 14,
        "td_ability_desc": "减益：范围内敌人受到伤害+50%"
    },
    "kirara": {
        "cost": 300, "range": 2.0, "atk_speed": 0.7, "td_dmg": 25,
        "td_ability": "dmg_debuff", "td_ability_cd": 14,
        "td_ability_desc": "减益：范围内敌人受到伤害+50%"
    },
}

# ==================== 塔防地图定义 ====================
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
    {
        "id": 2, "name": "蒙德·风起地",
        "width": 14, "height": 10, "cell_size": 66,
        "path": [
            (0,2), (1,2), (2,2), (3,2), (3,3), (3,4),
            (2,4), (1,4), (0,4), (0,5), (0,6), (1,6),
            (2,6), (3,6), (3,7), (3,8), (4,8), (5,8),
            (5,7), (5,6), (6,6), (6,5), (6,4), (5,4),
            (4,4), (4,3), (4,2), (5,2), (6,2), (6,1),
            (6,0),
        ],
        "waves": [
            {"enemies": [("hilichurl", 6)], "interval": 1.3},
            {"enemies": [("hilichurl_fighter", 4), ("slime_fire", 4)], "interval": 1.2},
            {"enemies": [("abyss_mage", 2), ("hilichurl_fighter", 4)], "interval": 1.0},
        ],
        "starting_gold": 400, "lives": 20,
    },
    {
        "id": 3, "name": "璃月·归离原",
        "width": 16, "height": 10, "cell_size": 64,
        "path": [
            (0,3), (1,3), (2,3), (3,3), (3,2), (3,1),
            (2,1), (1,1), (0,1), (0,0), (1,0), (2,0),
            (3,0), (4,0), (4,1), (4,2), (5,2), (6,2),
            (7,2), (8,2), (8,3), (8,4), (7,4), (6,4),
            (5,4), (4,4), (4,5), (4,6), (4,7), (5,7),
            (6,7), (7,7), (8,7), (8,8), (8,9), (9,9),
            (10,9), (11,9), (12,9), (13,9), (14,9), (15,9),
        ],
        "waves": [
            {"enemies": [("hilichurl_fighter", 6), ("slime_water", 4)], "interval": 1.2},
            {"enemies": [("abyss_mage", 3), ("slime_fire", 4)], "interval": 1.0},
            {"enemies": [("abyss_mage", 4), ("hilichurl_fighter", 5)], "interval": 0.9},
            {"enemies": [("ruin_guard", 1), ("abyss_mage", 3)], "interval": 1.5},
        ],
        "starting_gold": 500, "lives": 18,
    },
    {
        "id": 4, "name": "璃月·层岩巨渊",
        "width": 16, "height": 10, "cell_size": 64,
        "path": [
            (15,4), (14,4), (13,4), (12,4), (12,3), (12,2),
            (13,2), (14,2), (15,2), (15,1), (15,0), (14,0),
            (13,0), (12,0), (11,0), (10,0), (9,0), (9,1),
            (9,2), (9,3), (9,4), (8,4), (7,4), (6,4),
            (5,4), (4,4), (4,3), (4,2), (5,2), (6,2),
            (7,2), (7,1), (7,0), (6,0), (5,0), (4,0),
            (3,0), (2,0), (1,0), (0,0),
        ],
        "waves": [
            {"enemies": [("hilichurl_fighter", 5), ("slime_fire", 5)], "interval": 1.2},
            {"enemies": [("abyss_mage", 3), ("slime_water", 4)], "interval": 1.0},
            {"enemies": [("ruin_guard", 1), ("abyss_mage", 4), ("hilichurl_fighter", 4)], "interval": 1.1},
            {"enemies": [("ruin_guard", 2), ("abyss_mage", 3), ("slime_fire", 4)], "interval": 1.2},
        ],
        "starting_gold": 550, "lives": 15,
    },
    {
        "id": 5, "name": "稻妻·鸣神大社",
        "width": 18, "height": 10, "cell_size": 62,
        "path": [
            (0,4), (1,4), (2,4), (2,5), (2,6), (1,6),
            (0,6), (0,7), (0,8), (1,8), (2,8), (3,8),
            (3,7), (3,6), (4,6), (5,6), (5,5), (5,4),
            (4,4), (3,4), (3,3), (3,2), (4,2), (5,2),
            (6,2), (6,3), (6,4), (7,4), (8,4), (8,3),
            (8,2), (8,1), (8,0), (9,0), (10,0), (11,0),
            (12,0), (12,1), (12,2), (12,3), (12,4), (13,4),
            (14,4), (14,3), (14,2), (14,1), (14,0), (15,0),
            (16,0), (17,0), (17,1), (17,2), (17,3), (17,4),
        ],
        "waves": [
            {"enemies": [("hilichurl_fighter", 6), ("slime_fire", 5), ("slime_water", 4)], "interval": 1.1},
            {"enemies": [("abyss_mage", 4), ("slime_water", 5)], "interval": 0.9},
            {"enemies": [("ruin_guard", 2), ("abyss_mage", 4), ("hilichurl_fighter", 5)], "interval": 1.0},
            {"enemies": [("ruin_guard", 3), ("slime_fire", 5), ("abyss_mage", 4)], "interval": 1.0},
            {"enemies": [("ruin_guard", 2), ("abyss_mage", 6)], "interval": 0.8},
        ],
        "starting_gold": 600, "lives": 12,
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

# ==================== 塔防元素反应（实时版） ====================
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