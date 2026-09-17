// ==================== 元素定义 ====================
const ELEMENTS = {
    fire:    { name: "火", icon: "🔥", color: "#ef4444" },
    water:   { name: "水", icon: "💧", color: "#3b82f6" },
    thunder: { name: "雷", icon: "⚡", color: "#a855f7" },
    ice:     { name: "冰", icon: "❄️", color: "#7dd3fc" },
    wind:    { name: "风", icon: "🍃", color: "#4ade80" },
    rock:    { name: "岩", icon: "🪨", color: "#fbbf24" },
    grass:   { name: "草", icon: "🌿", color: "#22c55e" },
};

// ==================== 七元素陷阱与塔定义 ====================
const BUILDING_DEFS = {
    // ========== 陷阱（放在路径上触发） ==========
    fire_trap: {
        bid: "fire_trap", type: "trap", name: "爆裂陷阱",
        element: "fire", cost: 150, icon: "💥", color: "#ef4444",
        cooldown: 3.0,
        effect: { type: "explode", damage: 80, aoe_radius: 1.0 }
    },
    water_trap: {
        bid: "water_trap", type: "trap", name: "水牢陷阱",
        element: "water", cost: 100, icon: "💧", color: "#3b82f6",
        cooldown: 2.5,
        effect: { type: "slow", amount: 0.5, duration: 3.0 }
    },
    thunder_trap: {
        bid: "thunder_trap", type: "trap", name: "雷击陷阱",
        element: "thunder", cost: 200, icon: "⚡", color: "#a855f7",
        cooldown: 3.5,
        effect: { type: "stun", duration: 1.0, damage: 50 }
    },
    ice_trap: {
        bid: "ice_trap", type: "trap", name: "冰冻陷阱",
        element: "ice", cost: 150, icon: "❄️", color: "#7dd3fc",
        cooldown: 3.0,
        effect: { type: "freeze", duration: 2.5 }
    },
    wind_trap: {
        bid: "wind_trap", type: "trap", name: "吹飞陷阱",
        element: "wind", cost: 150, icon: "🍃", color: "#4ade80",
        cooldown: 3.0,
        effect: { type: "push", tiles: 2 }
    },
    rock_trap: {
        bid: "rock_trap", type: "trap", name: "岩壁陷阱",
        element: "rock", cost: 200, icon: "🪨", color: "#fbbf24",
        cooldown: 4.0,
        effect: { type: "stun", duration: 1.5, damage: 100 }
    },
    grass_trap: {
        bid: "grass_trap", type: "trap", name: "缠绕陷阱",
        element: "grass", cost: 150, icon: "🌿", color: "#22c55e",
        cooldown: 2.5,
        effect: { type: "root", duration: 2.0, dot_dps: 15 }
    },

    // ========== 塔（放在路径旁自动攻击） ==========
    fire_tower: {
        bid: "fire_tower", type: "tower", name: "烈焰弩塔",
        element: "fire", cost: 200, range: 2.5, atk_speed: 1.0, damage: 60,
        icon: "🏹", color: "#ef4444",
        special: null
    },
    water_tower: {
        bid: "water_tower", type: "tower", name: "激流塔",
        element: "water", cost: 250, range: 2.0, atk_speed: 0.8, damage: 45,
        icon: "🌊", color: "#3b82f6",
        special: { type: "splash", radius: 1.0, ratio: 0.4 }
    },
    thunder_tower: {
        bid: "thunder_tower", type: "tower", name: "雷击塔",
        element: "thunder", cost: 300, range: 2.5, atk_speed: 1.5, damage: 35,
        icon: "⚡", color: "#a855f7",
        special: { type: "chain", count: 2, ratio: 0.5 }
    },
    ice_tower: {
        bid: "ice_tower", type: "tower", name: "寒冰塔",
        element: "ice", cost: 250, range: 2.5, atk_speed: 0.7, damage: 40,
        icon: "❄️", color: "#7dd3fc",
        special: { type: "slow", amount: 0.3, duration: 2.0 }
    },
    wind_tower: {
        bid: "wind_tower", type: "tower", name: "旋风塔",
        element: "wind", cost: 300, range: 2.0, atk_speed: 1.2, damage: 30,
        icon: "🍃", color: "#4ade80",
        special: { type: "spread", radius: 1.5 }
    },
    rock_tower: {
        bid: "rock_tower", type: "tower", name: "岩柱塔",
        element: "rock", cost: 350, range: 2.0, atk_speed: 0.6, damage: 80,
        icon: "🪨", color: "#fbbf24",
        special: null
    },
    grass_tower: {
        bid: "grass_tower", type: "tower", name: "蔓生塔",
        element: "grass", cost: 250, range: 2.5, atk_speed: 0.9, damage: 35,
        icon: "🌿", color: "#22c55e",
        special: { type: "dot", dps: 15, duration: 3.0 }
    },
};

// ==================== 塔防地图 ====================
const TD_MAPS = [
    {
        id: 1,
        name: "蒙德·低语森林",
        width: 14,
        height: 14,
        path: [
            [0,4],[1,4],[2,4],[3,4],                            // → 右 4
            [3,5],[3,6],[3,7],[3,8],                             // ↓ 下 4
            [4,8],[5,8],[6,8],                                     // → 右 3
            [6,7],[6,6],[6,5],                                     // ↑ 上 3
            [7,5],[8,5],[9,5],                                     // → 右 3
            [9,6],[9,7],[9,8],[9,9],[9,10],                       // ↓ 下 5
            [10,10],[11,10],[12,10],[13,10],                       // → 右 4
        ],
        waves: [
            { enemies: [["hilichurl", 8]], interval: 1.4 },
            { enemies: [["hilichurl", 6], ["slime_fire", 4]], interval: 1.3 },
            { enemies: [["hilichurl_fighter", 5], ["slime_water", 4], ["slime_thunder", 3]], interval: 1.2 },
            { enemies: [["hilichurl_fighter", 4], ["slime_ice", 4], ["slime_wind", 3]], interval: 1.2 },
            { enemies: [["hilichurl", 5], ["slime_rock", 3], ["slime_grass", 3]], interval: 1.1 },
            { enemies: [["mitachurl", 3], ["slime_fire", 5], ["slime_thunder", 3]], interval: 1.8 },
            { enemies: [["abyss_mage", 4], ["hilichurl_fighter", 6]], interval: 1.5 },
            { enemies: [["ruin_guard", 2], ["lawachurl", 1]], interval: 2.5 },
        ],
        starting_gold: 800,
        lives: 25,
        available_towers: ["fire_tower", "water_tower"],
        available_traps: ["fire_trap", "water_trap"],
        map_theme: "mondstadt",  // 蒙德草原风格
    },
    {
        id: 2,
        name: "璃月·归离原",
        width: 14,
        height: 14,
        path: [
            [0,6],[1,6],[2,6],[3,6],                                    // → 右 4
            [3,7],[3,8],[3,9],[3,10],                                    // ↓ 下 4
            [4,10],[5,10],[6,10],[7,10],[8,10],                          // → 右 5
            [8,9],[8,8],[8,7],[8,6],                                     // ↑ 上 4
            [9,6],[10,6],[11,6],[12,6],                                   // → 右 4
            [12,7],[12,8],[12,9],[12,10],                                 // ↓ 下 4
            [13,10],                                                       // → 右 1
        ],
        waves: [
            { enemies: [["hilichurl", 6], ["slime_thunder", 4]], interval: 1.4 },
            { enemies: [["hilichurl_fighter", 5], ["slime_ice", 4]], interval: 1.3 },
            { enemies: [["slime_thunder", 5], ["slime_water", 3], ["hilichurl", 4]], interval: 1.2 },
            { enemies: [["mitachurl", 2], ["slime_ice", 5], ["slime_wind", 3]], interval: 1.6 },
            { enemies: [["abyss_mage", 3], ["slime_thunder", 6]], interval: 1.5 },
            { enemies: [["slime_fire", 4], ["slime_ice", 4], ["slime_grass", 4]], interval: 1.2 },
            { enemies: [["lawachurl", 1], ["mitachurl", 3], ["ruin_guard", 1]], interval: 2.5 },
        ],
        starting_gold: 800,
        lives: 25,
        available_towers: ["thunder_tower", "ice_tower"],
        available_traps: ["thunder_trap", "ice_trap"],
        map_theme: "liyue",  // 璃月岩山风格
    },
];

// ==================== 塔防敌人属性 ====================
const TD_ENEMY_STATS = {
    hilichurl: {
        name: "丘丘人", hp: 150, speed: 1.2, gold: 30, element: null, color: "#888",
    },
    hilichurl_fighter: {
        name: "丘丘人战士", hp: 400, speed: 1.0, gold: 60, element: null, color: "#a66",
    },
    mitachurl: {
        name: "丘丘暴徒", hp: 1200, speed: 0.7, gold: 100, element: null, color: "#c84",
    },
    lawachurl: {
        name: "丘丘王", hp: 3500, speed: 0.45, gold: 250, element: null, color: "#f44",
    },
    slime_fire: {
        name: "火史莱姆", hp: 250, speed: 0.9, gold: 45, element: "fire", color: "#e44",
    },
    slime_water: {
        name: "水史莱姆", hp: 280, speed: 1.0, gold: 45, element: "water", color: "#38b",
    },
    slime_thunder: {
        name: "雷史莱姆", hp: 220, speed: 1.1, gold: 50, element: "thunder", color: "#a5f",
    },
    slime_ice: {
        name: "冰史莱姆", hp: 260, speed: 0.85, gold: 45, element: "ice", color: "#7df",
    },
    slime_wind: {
        name: "风史莱姆", hp: 200, speed: 1.3, gold: 50, element: "wind", color: "#4e8",
    },
    slime_rock: {
        name: "岩史莱姆", hp: 400, speed: 0.6, gold: 55, element: "rock", color: "#fb4",
    },
    slime_grass: {
        name: "草史莱姆", hp: 230, speed: 0.95, gold: 45, element: "grass", color: "#2c5",
    },
    abyss_mage: {
        name: "深渊法师", hp: 900, speed: 0.7, gold: 120, element: null, color: "#66c",
    },
    ruin_guard: {
        name: "遗迹守卫", hp: 3000, speed: 0.4, gold: 300, element: null, color: "#aaa",
    },
};

// ==================== 元素量系统（原神元素论）====================
// 1U = 标准附着量，衰减时间约 9.5 秒
// 2U = 强附着量，衰减时间约 12 秒
// 衰减速率 ≈ 0.105 U/s（1U） / 0.167 U/s（2U）
const ELEMENTAL_GAUGE = {
    DECAY_RATE: 0.105,        // 1U 每秒衰减量
    STRONG_DECAY_RATE: 0.167, // 2U 每秒衰减量
    STANDARD_U: 1.0,           // 标准附着（塔攻击/陷阱）
    STRONG_U: 2.0,             // 强附着
    DURATION_1U: 9.5,          // 1U 理论持续时间
    DURATION_2U: 12.0,         // 2U 理论持续时间
    REACTION_WINDOW: 0.3,      // 反应检测窗口（秒）
};

// ==================== 元素反应表（原神机制：蒸发/融化/超载/超导/感电/冻结/扩散/结晶）====================
// 每个反应定义：倍率、元素量消耗、特殊效果
const TD_REACTIONS = {
    // ======== 蒸发 Vaporize（火×水）========
    "fire+water": {
        name: "蒸发", type: "vaporize", icon: "💨",
        multiplier: 2.0,          // 火打水：正向蒸发 2.0x
        gauge_consume: 2.0,       // 消耗 2U 水元素量（强反应）
        is_forward: true,
    },
    "water+fire": {
        name: "蒸发", type: "vaporize", icon: "💨",
        multiplier: 1.5,          // 水打火：反向蒸发 1.5x
        gauge_consume: 0.5,       // 只消耗 0.5U 火元素量（弱反应）
        is_forward: false,
    },

    // ======== 融化 Melt（火×冰）========
    "fire+ice": {
        name: "融化", type: "melt", icon: "💧➡💨",
        multiplier: 2.0,          // 火打冰：正向融化 2.0x
        gauge_consume: 2.0,
        is_forward: true,
    },
    "ice+fire": {
        name: "融化", type: "melt", icon: "💧➡💨",
        multiplier: 1.5,          // 冰打火：反向融化 1.5x
        gauge_consume: 0.5,
        is_forward: false,
    },

    // ======== 超载 Overloaded（火×雷）========
    "fire+thunder": {
        name: "超载", type: "overloaded", icon: "💥",
        aoe: true, aoe_radius: 1.8,
        dmg_ratio: 2.0,           // 范围火伤 = 触发伤害 × 2.0
        gauge_consume: 1.0,       // 双方各消耗 1U
        knockback: true,
    },
    "thunder+fire": {
        name: "超载", type: "overloaded", icon: "💥",
        aoe: true, aoe_radius: 1.8,
        dmg_ratio: 2.0,
        gauge_consume: 1.0,
        knockback: true,
    },

    // ======== 超导 Superconduct（冰×雷）========
    "ice+thunder": {
        name: "超导", type: "superconduct", icon: "❄️⚡",
        aoe: true, aoe_radius: 1.5,
        dmg_ratio: 0.5,           // 冰范围伤害 = 触发伤害 × 0.5
        gauge_consume: 1.0,
        phys_res_down: 0.4,       // 降低 40% 物理抗性
        phys_res_duration: 12.0,  // 持续 12 秒
    },
    "thunder+ice": {
        name: "超导", type: "superconduct", icon: "❄️⚡",
        aoe: true, aoe_radius: 1.5,
        dmg_ratio: 0.5,
        gauge_consume: 1.0,
        phys_res_down: 0.4,
        phys_res_duration: 12.0,
    },

    // ======== 感电 Electro-Charged（水×雷）========
    // 感电特殊：水雷短暂共存，每秒跳一次雷伤
    "water+thunder": {
        name: "感电", type: "electro_charged", icon: "⚡💧",
        dot_tick: 20,             // 每跳伤害
        tick_interval: 1.0,       // 每 1.0 秒跳一次
        tick_count: 2,            // 共 2 跳
        gauge_consume: 0.4,       // 每次跳消耗 0.4U 双方元素
        chain: true,              // 连锁附近潮湿敌人
        chain_radius: 2.0,
    },
    "thunder+water": {
        name: "感电", type: "electro_charged", icon: "⚡💧",
        dot_tick: 20,
        tick_interval: 1.0,
        tick_count: 2,
        gauge_consume: 0.4,
        chain: true,
        chain_radius: 2.0,
    },

    // ======== 冻结 Frozen（水×冰）========
    // 冻结：敌人完全无法移动，冰元素残留
    "water+ice": {
        name: "冻结", type: "frozen", icon: "🧊",
        freeze_duration: 2.5,     // 冻结持续时间
        gauge_consume: 1.0,       // 各消耗 1U
        // 冻结后冰元素残留在敌人身上（冻元素）
        // 碎冰：被岩/强攻击击中时解除冻结并造成额外伤害
        shatter_dmg_ratio: 1.5,
    },
    "ice+water": {
        name: "冻结", type: "frozen", icon: "🧊",
        freeze_duration: 2.5,
        gauge_consume: 1.0,
        shatter_dmg_ratio: 1.5,
    },

    // ======== 扩散 Swirl（风×火/水/雷/冰）========
    // 风打已附着元素的敌人：AOE传播该元素
    "wind+fire": {
        name: "火扩散", type: "swirl", icon: "🍃🔥",
        swirl_element: "fire",
        aoe: true, aoe_radius: 2.0,
        dmg_ratio: 0.6,           // 风伤 = 触发伤害 × 0.6
        swirl_dmg: 30,            // 扩散基础伤害
        gauge_consume: 0.5,
    },
    "wind+water": {
        name: "水扩散", type: "swirl", icon: "🍃💧",
        swirl_element: "water",
        aoe: true, aoe_radius: 2.0,
        dmg_ratio: 0.6,
        swirl_dmg: 30,
        gauge_consume: 0.5,
    },
    "wind+thunder": {
        name: "雷扩散", type: "swirl", icon: "🍃⚡",
        swirl_element: "thunder",
        aoe: true, aoe_radius: 2.0,
        dmg_ratio: 0.6,
        swirl_dmg: 30,
        gauge_consume: 0.5,
    },
    "wind+ice": {
        name: "冰扩散", type: "swirl", icon: "🍃❄️",
        swirl_element: "ice",
        aoe: true, aoe_radius: 2.0,
        dmg_ratio: 0.6,
        swirl_dmg: 30,
        gauge_consume: 0.5,
    },

    // ======== 结晶 Crystallize（岩×火/水/雷/冰）========
    // 岩打已附着元素的敌人：生成对应元素护盾
    "rock+fire": {
        name: "火结晶", type: "crystallize", icon: "💎🔥",
        shield_amt: 300,          // 护盾值（基于触发者等级）
        gauge_consume: 0.5,
    },
    "rock+water": {
        name: "水结晶", type: "crystallize", icon: "💎💧",
        shield_amt: 300,
        gauge_consume: 0.5,
    },
    "rock+thunder": {
        name: "雷结晶", type: "crystallize", icon: "💎⚡",
        shield_amt: 300,
        gauge_consume: 0.5,
    },
    "rock+ice": {
        name: "冰结晶", type: "crystallize", icon: "💎❄️",
        shield_amt: 300,
        gauge_consume: 0.5,
    },

    // ======== 草元素反应（保留但简化）========
    "fire+grass": {
        name: "燃烧", type: "burning", icon: "🔥🌿",
        dot_dps: 30,              // 持续火伤 30/秒
        dot_duration: 3.0,
        gauge_consume: 0.5,
    },
    "grass+fire": {
        name: "燃烧", type: "burning", icon: "🔥🌿",
        dot_dps: 30,
        dot_duration: 3.0,
        gauge_consume: 0.5,
    },
    "water+grass": {
        name: "绽放", type: "bloom", icon: "💧🌿",
        aoe: true, aoe_radius: 1.5,
        dmg_ratio: 0.8,
        gauge_consume: 1.0,
    },
    "grass+water": {
        name: "绽放", type: "bloom", icon: "💧🌿",
        aoe: true, aoe_radius: 1.5,
        dmg_ratio: 0.8,
        gauge_consume: 1.0,
    },
    "thunder+grass": {
        name: "激化", type: "quicken", icon: "⚡🌿",
        multiplier: 1.3,          // 后续雷/草伤害 ×1.3
        gauge_consume: 0.5,
    },
    "grass+thunder": {
        name: "激化", type: "quicken", icon: "⚡🌿",
        multiplier: 1.3,
        gauge_consume: 0.5,
    },
};