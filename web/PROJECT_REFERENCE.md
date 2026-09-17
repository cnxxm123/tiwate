# Tiwate 塔防项目参考文档

> 基于原神元素的 Web 塔防游戏。本文档供 AI 助手快速理解项目结构和核心机制。

---

## 1. 项目结构

```
e:\tiwate\web\
├── index.html          # 主页面 (v=7)
├── server.py           # Python HTTP 服务 (端口 8080)
├── img/                # 元素图标
│   ├── fire.png        # 火元素图标
│   ├── water.png       # 水元素图标
│   ├── thunder.png     # 雷元素图标
│   └── ice.png         # 冰元素图标
└── js/
    ├── data.js         # 所有静态数据定义
    ├── engine.js       # 游戏引擎（战斗逻辑）
    ├── render.js       # Canvas 渲染器
    ├── ui.js           # UI 交互
    └── app.js          # 应用入口
```

**启动方式**：
```powershell
cd e:\tiwate\web
python server.py
# 浏览器访问 http://localhost:8080/
```

**重启**（端口被占用时）：
```powershell
$p = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -First 1
if ($p) { Stop-Process -Id $p -Force }
python server.py
```

---

## 2. 核心数据结构 (`data.js`)

### 2.1 七元素定义 (`ELEMENTS`)
```js
fire:    { icon: "🔥", color: "#ef4444" }
water:   { icon: "💧", color: "#3b82f6" }
thunder: { icon: "⚡", color: "#a855f7" }
ice:     { icon: "❄️", color: "#7dd3fc" }
wind:    { icon: "🍃", color: "#4ade80" }
rock:    { icon: "🪨", color: "#fbbf24" }
grass:   { icon: "🌿", color: "#22c55e" }
```

### 2.2 元素量系统 (`ELEMENTAL_GAUGE`)
```js
DECAY_RATE: 0.105          // 1U 每秒衰减量（~9.5秒耗尽）
STRONG_DECAY_RATE: 0.167   // 2U 每秒衰减量（~12秒耗尽）
STANDARD_U: 1.0            // 标准附着（塔攻击）
STRONG_U: 2.0              // 强附着（陷阱）
```

### 2.3 建筑定义 (`BUILDING_DEFS`)

每座建筑包含 `bid`, `type`(tower/trap), `element`, `cost`, `icon`, `color`, 以及专属效果字段。

**塔（tower）通用字段**: `range`, `atk_speed`, `damage`, `special`
**陷阱（trap）通用字段**: `cooldown`, `effect`（含 `type` + 类型专属参数）

### 2.4 元素反应表 (`TD_REACTIONS`)

以 `"新元素+已有元素"` 为 key，每种反应含以下结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 中文名（蒸发/融化/超载...） |
| `type` | string | 内部类型标识 |
| `icon` | string | 显示图标 |
| `multiplier` | number | 伤害倍率（蒸发/融化） |
| `gauge_consume` | number | 消耗元素量（U） |
| `is_forward` | bool | 是否正向反应 |
| `aoe` | bool | 是否范围伤害 |
| `aoe_radius` | number | 范围半径（格） |
| `dmg_ratio` | number | 范围伤害比例 |
| `dot_tick/interval/count` | — | 感电专有 |
| `freeze_duration` | number | 冻结时长 |
| `swirl_element` | string | 扩散的目标元素 |
| `swirl_dmg` | number | 扩散伤害 |
| `shield_amt` | number | 结晶护盾值 |
| `phys_res_down/duration` | — | 超导物抗降低 |
| `knockback` | bool | 超载击退 |

### 2.5 地图 (`TD_MAPS`)

```js
{
  id: 1,
  name: "蒙德·低语森林",
  width: 14, height: 14,     // 14×14 网格
  path: [[0,4], [1,4], ...], // 路径坐标序列 [gridX, gridY]
  waves: [                   // 波次定义
    { enemies: [["hilichurl", 8]], interval: 1.4 },
    ...
  ],
  starting_gold: 800,
  lives: 25,
  available_towers: ["fire_tower", "water_tower"],
  available_traps: ["fire_trap", "water_trap"],
  map_theme: "mondstadt",    // "mondstadt" | "liyue"
}
```

地图主题：
- `mondstadt`：翠绿草原渐变，花朵/灌木/小树/萤火虫粒子
- `liyue`：金黄大地渐变，石笋/秋树/暖光粒子

### 2.6 敌人定义 (`TD_ENEMY_STATS`)

```js
hilichurl:      { hp:150,  speed:1.2, gold:30,  element:null }
hilichurl_fighter: { hp:400, speed:1.0, gold:60, element:null }
mitachurl:      { hp:1200, speed:0.7, gold:100, element:null }
lawachurl:      { hp:3500, speed:0.45,gold:250, element:null }
abyss_mage:     { hp:900,  speed:0.7, gold:120, element:null }
ruin_guard:     { hp:3000, speed:0.4, gold:300, element:null }
slime_fire:     { hp:250,  speed:0.9, gold:45,  element:"fire" }
slime_water:    { hp:280,  speed:1.0, gold:45,  element:"water" }
slime_thunder:  { hp:220,  speed:1.1, gold:50,  element:"thunder" }
slime_ice:      { hp:260,  speed:0.85,gold:45,  element:"ice" }
slime_wind:     { hp:200,  speed:1.3, gold:50,  element:"wind" }
slime_rock:     { hp:400,  speed:0.6, gold:55,  element:"rock" }
slime_grass:    { hp:230,  speed:0.95,gold:45,  element:"grass" }
```

**注意**：自带 `element` 的敌人在出生时即附带 1U 元素附着（史莱姆系列）。

---

## 3. 游戏引擎 (`engine.js`)

### 3.1 类层次

```
TDEngine ─── 管理整个战斗
  ├── Tower[]  ── 塔（自动攻击）
  ├── Trap[]   ── 陷阱（敌人踩中触发）
  ├── Enemy[]  ── 敌人（沿路径移动）
  ├── Projectile[] ── 弹道（箭矢飞行）
  └── effects[]  ── 飘字特效
```

### 3.2 Enemy 类关键属性

```js
enemy.element        // 自带元素（史莱姆等），null 表示无
enemy.hp / maxHp     // 生命值
enemy.speed          // 移动速度
enemy.pathIndex      // 当前路径位置（浮点数）
enemy.px / py        // 像素坐标

// 元素量系统
enemy.auraElement    // 当前附着元素
enemy.auraGauge      // 当前剩余元素量（U）

// 状态
enemy.frozen         // 冻结状态（不可移动）
enemy.slowed / slowAmount / slowTimer
enemy.rooted         // 缠绕状态（不可移动）
enemy.electroCharged // 感电共存
enemy.quickenAura    // 激化状态
enemy.physResDown    // 物抗降低
enemy.defDown        // 防御降低
enemy.dotDamage / dotTimer  // 持续伤害
enemy.frozenAuraElement     // 冻结解除后的冰残留
```

### 3.3 元素附着流程

```
Tower.attack() → Projectile 飞行 → 命中 enemy

1. enemy.applyElement(element, 1U)
2. _detectReaction(newElement, newGauge)
   → 检查 enemy.getActiveElement()（优先 auraGauge > auroraElement > frozenAuraElement > this.element）
   → 查 TD_REACTIONS["newElement+auraElement"]
3. 有反应：_applyReactionGaugeConsume() 消耗元素量
4. 无反应：直接设置 auraElement/auraGauge
5. enemy.takeDamage(dmg, element, reactionMultiplier)
```

### 3.4 元素量衰减

```js
// 每帧 update(dt) 执行：
if (auraGauge > 0) {
    decayRate = auraGauge > 1.5 ? STRONG_DECAY_RATE : DECAY_RATE
    auraGauge -= decayRate * dt
    if (auraGauge <= 0) { auraElement = null; auraGauge = 0 }
}
```

### 3.5 反应效果参考

| 反应 | 伤害倍率 | 额外效果 |
|------|----------|----------|
| 蒸发 | 2.0x / 1.5x | 正向/反向 |
| 融化 | 2.0x / 1.5x | 正向/反向 |
| 超载 | AOE ×2.0 | 1.8格火AOE + 击退 |
| 超导 | AOE ×0.5 | 物抗-40%×12s |
| 感电 | 20/跳×2 | DoT + 连锁潮湿 |
| 冻结 | — | 冻结2.5s + 冰残留 |
| 扩散 | AOE ×0.6 | 传播元素 |
| 结晶 | — | 300护盾给塔 |
| 燃烧 | — | 30dps×3s |
| 绽放 | AOE ×0.8 | 1.5格AOE |
| 激化 | ×1.3 | 雷草增伤 |

---

## 4. 渲染器 (`render.js`)

### 4.1 `MapRenderer` 类

构造函数加载元素图片到 `elementImages` 缓存。

#### 渲染顺序（每帧）
```
_drawGround()          → 主题渐变 + 纹理斑块 + 网格线
_drawPath()            → 石板路 + 起点终点传送门 + 方向箭头
_drawDecorations()     → 花/灌木/树/岩石/石笋/草簇
_drawBorder()          → 暗框 + 主题金框 + 四角菱形
_drawBuildings()       → 塔 + 陷阱
_drawProjectiles()     → 弹道箭矢
_drawEnemies()         → 敌人 + 元素光环
_drawEffects()         → 飘字特效
_drawSelection()       → 选中格高亮
_drawAmbientParticles() → 萤火虫/花瓣
```

### 4.2 陷阱图片替换

`elementImages` 缓存了 `fire/water/thunder/ice` 四张图片。渲染陷阱时：
- 有对应图片 → 圆形裁剪显示图片，隐藏文字图标
- 无图片（风/岩/草） → 使用绘制函数

---

## 5. UI 交互 (`ui.js`)

- **点击格子**：打开弹窗，显示可建造塔/陷阱（根据关卡 `available_towers/traps` 过滤）
- **作弊按钮**（紫色 🧪）：加 5000 金币 + 回满生命
- **弹窗按钮**：建造/出售/关闭

---

## 6. 版本号

在所有 JS 引用 URL 上使用 `?v=N` 版本号强制刷新缓存。当前版本：`v=7`。

---

## 7. 常见问题

### 图片不显示
确保 `e:\tiwate\img\*.png` 已复制到 `e:\tiwate\web\img\`。

### 修改后无效果
增加 `index.html` 中的版本号 `?v=N`，清除浏览器缓存后刷新。

### 端口占用
```powershell
Get-NetTCPConnection -LocalPort 8080 | Select -ExpandProperty OwningProcess | ForEach { Stop-Process -Id $_ -Force }
```

### 新增关卡
在 `TD_MAPS` 数组中添加新对象，设置 `available_towers/traps` 数组来控制该关卡可用建筑。