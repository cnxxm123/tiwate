// ==================== 陷阱 ====================
class Trap {
    constructor(bid, bdef, gridX, gridY, cellSize) {
        this.bid = bid;
        this.name = bdef.name;
        this.element = bdef.element;
        this.cost = bdef.cost;
        this.icon = bdef.icon || "?";
        this.color = bdef.color || "#fff";
        this.cooldown = bdef.cooldown || 2.0;
        this.cooldownRemaining = 0;
        this.effect = bdef.effect || { type: "apply" };  // 陷阱效果配置
        this.gridX = gridX;
        this.gridY = gridY;
        this.px = gridX * cellSize + cellSize / 2;
        this.py = gridY * cellSize + cellSize / 2;
        this.cellSize = cellSize;
        this.triggerCount = 0;
        // 动画状态
        this.bobPhase = Math.random() * Math.PI * 2;  // 浮动相位
        this.triggerFlash = 0;  // 触发闪光 0~1
    }

    canTrigger() { return this.cooldownRemaining <= 0; }

    trigger() {
        this.cooldownRemaining = this.cooldown;
        this.triggerCount++;
        this.triggerFlash = 1.0;
    }

    update(dt) {
        if (this.cooldownRemaining > 0) this.cooldownRemaining -= dt;
        this.bobPhase += dt * 2;
        if (this.triggerFlash > 0) this.triggerFlash -= dt * 4;
    }
}

// ==================== 塔 ====================
class Tower {
    constructor(bid, bdef, gridX, gridY, cellSize) {
        this.bid = bid;
        this.name = bdef.name;
        this.element = bdef.element;
        this.cost = bdef.cost;
        this.range = bdef.range;
        this.atkSpeed = bdef.atk_speed;
        this.damage = bdef.damage;
        this.icon = bdef.icon || "?";
        this.color = bdef.color || "#fff";
        this.maxHp = 300;
        this.hp = this.maxHp;
        this.shield = 0;
        this.gridX = gridX;
        this.gridY = gridY;
        this.px = gridX * cellSize + cellSize / 2;
        this.py = gridY * cellSize + cellSize / 2;
        this.cellSize = cellSize;
        this.attackCooldown = 0;
        this.dmgBonus = 0;
        this.special = bdef.special || null;  // 特殊效果配置
        // 转向与动画
        this.angle = 0;             // 当前朝向角度（弧度）
        this.targetAngle = 0;       // 目标朝向角度
        this.recoil = 0;            // 后坐力动画 0~1
        this.recoiling = false;     // 是否正在后坐力动画中
    }

    getEffectiveDamage() { return Math.floor(this.damage * (1 + this.dmgBonus)); }

    canAttack() { return this.attackCooldown <= 0; }

    resetCooldown() { this.attackCooldown = 1.0 / Math.max(this.atkSpeed, 0.1); }

    /** 看向目标敌人 */
    lookAt(tx, ty) {
        this.targetAngle = Math.atan2(ty - this.py, tx - this.px);
    }

    /** 触发攻击后坐力动画 */
    fire() {
        this.recoil = 1.0;
        this.recoiling = true;
    }

    /** 每帧更新动画 */
    updateAnimation(dt) {
        // 平滑转向
        const diff = this.targetAngle - this.angle;
        const shortDiff = Math.atan2(Math.sin(diff), Math.cos(diff));
        this.angle += shortDiff * Math.min(1, dt * 10);

        // 后坐力回弹
        if (this.recoiling) {
            this.recoil -= dt * 5;
            if (this.recoil <= 0) {
                this.recoil = 0;
                this.recoiling = false;
            }
        }
    }

    findTarget(enemies) {
        let best = null;
        let bestProgress = -1;
        for (const enemy of enemies) {
            if (enemy.dead || enemy.reachedEnd) continue;
            const dist = Math.hypot(enemy.px - this.px, enemy.py - this.py);
            if (dist / this.cellSize <= this.range) {
                if (enemy.pathIndex > bestProgress) {
                    best = enemy;
                    bestProgress = enemy.pathIndex;
                } else if (enemy.pathIndex === bestProgress && best) {
                    if (dist < Math.hypot(best.px - this.px, best.py - this.py)) {
                        best = enemy;
                    }
                }
            }
        }
        return best;
    }

    takeDamage(dmg) {
        if (this.shield > 0) {
            if (this.shield >= dmg) { this.shield -= dmg; return 0; }
            dmg -= this.shield;
            this.shield = 0;
        }
        const actual = Math.min(this.hp, dmg);
        this.hp -= actual;
        return actual;
    }

    isDestroyed() { return this.hp <= 0; }

    update(dt) {
        if (this.attackCooldown > 0) this.attackCooldown -= dt;
    }
}

// ==================== 敌人 ====================
class Enemy {
    constructor(enemyId, path, cellSize, waveLevel) {
        const stats = TD_ENEMY_STATS[enemyId];
        this.id = enemyId;
        this.name = stats.name;
        this.element = stats.element || null;
        this.color = stats.color;
        this.maxHp = Math.floor(stats.hp * (1 + (waveLevel - 1) * 0.3));
        this.hp = this.maxHp;
        this.baseSpeed = stats.speed * cellSize;
        this.speed = this.baseSpeed;
        this.goldReward = stats.gold;
        this.path = path;
        this.cellSize = cellSize;
        this.pathIndex = 0;
        const pos = this._pathPos(0);
        this.px = pos[0]; this.py = pos[1];
        this.dead = false;
        this.reachedEnd = false;
        this.frozen = false;
        this.frozenTimer = 0;
        this.slowed = false;
        this.slowTimer = 0;
        this.slowAmount = 0;
        this.defDown = 0;
        this.defDownTimer = 0;
        this.dotDamage = 0;
        this.dotTimer = 0;
        this.lastTrapTrigger = {};
        // ---- 原神元素量系统 ----
        this.auraElement = null;    // 当前附着元素（火/水/雷/冰/草）
        this.auraGauge = 0;         // 当前元素量（U），按衰减率减少
        // 特殊状态
        this.electroCharged = false;    // 感电共存状态
        this.electroChargedTimer = 0;
        this.electroChargedTicks = 0;
        this.frozenAuraElement = null;  // 冻结后残留的冰元素
        this.quickenAura = false;       // 激化状态（雷草共存）
        this.quickenTimer = 0;
        this.physResDown = false;
        this.physResDownTimer = 0;
        this.rooted = false;
        this.rootedTimer = 0;
        // 如果敌人自带元素（如史莱姆），预设常驻附着
        if (this.element) {
            this.auraElement = this.element;
            this.auraGauge = ELEMENTAL_GAUGE.STANDARD_U;  // 初始 1U
        }
    }

    _pathPos(idx) {
        if (idx >= this.path.length) idx = this.path.length - 1;
        const [gx, gy] = this.path[idx];
        return [gx * this.cellSize + this.cellSize / 2, gy * this.cellSize + this.cellSize / 2];
    }

    update(dt) {
        if (this.frozen) {
            this.frozenTimer -= dt;
            if (this.frozenTimer <= 0) {
                this.frozen = false;
                this.frozenAuraElement = null;  // 解除冻结清除残留冰
            }
            return;
        }

        let effectiveSpeed = this.speed;
        // 缠绕效果：速度降为0
        if (this.rooted) {
            this.rootedTimer -= dt;
            effectiveSpeed = 0;
            if (this.rootedTimer <= 0) this.rooted = false;
        }
        if (this.slowed) {
            this.slowTimer -= dt;
            effectiveSpeed *= (1 - this.slowAmount);
            if (this.slowTimer <= 0) this.slowed = false;
        }
        if (this.defDown > 0) {
            this.defDownTimer -= dt;
            if (this.defDownTimer <= 0) this.defDown = 0;
        }
        if (this.dotDamage > 0) {
            this.dotTimer -= dt;
            this.hp -= Math.floor(this.dotDamage * dt);
            if (this.dotTimer <= 0) this.dotDamage = 0;
        }
        // 元素量随时间衰减
        if (this.auraGauge > 0) {
            const decayRate = this.auraGauge > 1.5 ? ELEMENTAL_GAUGE.STRONG_DECAY_RATE : ELEMENTAL_GAUGE.DECAY_RATE;
            this.auraGauge -= decayRate * dt;
            if (this.auraGauge <= 0) {
                this.auraGauge = 0;
                this.auraElement = null;
            }
        }
        // 感电共存衰减
        if (this.electroCharged) {
            this.electroChargedTimer -= dt;
            if (this.electroChargedTimer <= 0) this.electroCharged = false;
        }
        // 激化状态衰减
        if (this.quickenAura) {
            this.quickenTimer -= dt;
            if (this.quickenTimer <= 0) this.quickenAura = false;
        }
        // 物理减抗
        if (this.physResDown) {
            this.physResDownTimer -= dt;
            if (this.physResDownTimer <= 0) this.physResDown = false;
        }

        this.pathIndex += (effectiveSpeed * dt) / this.cellSize;
        const idx = Math.floor(this.pathIndex);
        if (idx >= this.path.length - 1) {
            this.reachedEnd = true;
            const pos = this._pathPos(this.path.length - 1);
            this.px = pos[0]; this.py = pos[1];
        } else {
            const frac = this.pathIndex - idx;
            const [x1, y1] = this._pathPos(idx);
            const [x2, y2] = this._pathPos(idx + 1);
            this.px = x1 + (x2 - x1) * frac;
            this.py = y1 + (y2 - y1) * frac;
        }

        if (this.hp <= 0) { this.hp = 0; this.dead = true; }
    }

    takeDamage(dmg, element, reactionMultiplier = 1.0) {
        if (this.dead) return 0;
        // 物理减抗：降低 40% 抗性 ≈ 提升伤害
        if (this.physResDown && !element) dmg = Math.floor(dmg * 1.4);
        if (this.defDown > 0) dmg = Math.floor(dmg * (1 + this.defDown));
        dmg = Math.floor(dmg * reactionMultiplier);
        const actual = Math.min(this.hp, dmg);
        this.hp -= actual;
        if (this.hp <= 0) this.dead = true;
        return actual;
    }

    /** 给敌人施加元素附着（原神元素论）
     *  @param {string} element - 元素类型
     *  @param {number} gauge - 元素量（U），默认 1U
     *  @returns {object|null} 反应信息，无反应返回 null
     */
    applyElement(element, gauge = ELEMENTAL_GAUGE.STANDARD_U) {
        if (!element) return null;
        if (this.dead) return null;

        const reaction = this._detectReaction(element, gauge);
        if (reaction) {
            this._applyReactionGaugeConsume(reaction, element, gauge);
            return reaction;
        }

        // 无反应：直接附着元素
        this.auraElement = element;
        this.auraGauge = gauge;
        return null;
    }

    /** 获取当前附着元素（有足够元素量才返回） */
    getActiveElement() {
        if (this.auraGauge > 0.01) return this.auraElement;
        if (this.frozenAuraElement) return this.frozenAuraElement;
        return this.element;  // 敌人自身元素（如史莱姆）
    }

    /** 检测反应：新元素 vs 当前附着元素 */
    _detectReaction(newElement, newGauge) {
        const auraElem = this.getActiveElement();
        if (!auraElem || auraElem === newElement) return null;

        const key = `${newElement}+${auraElem}`;
        return TD_REACTIONS[key] || null;
    }

    /** 执行反应的元素量消耗 */
    _applyReactionGaugeConsume(reaction, newElement, newGauge) {
        const consume = reaction.gauge_consume || 1.0;

        if (reaction.type === "electro_charged") {
            // 感电特殊：双方共存，各减少部分元素量
            this.auraGauge = Math.max(0, this.auraGauge - consume);
            this.electroCharged = true;
            this.electroChargedTimer = reaction.tick_interval * reaction.tick_count;
            this.electroChargedTicks = reaction.tick_count;
            if (this.auraGauge <= 0) this.auraElement = null;
            return;
        }

        // 一般反应：双方元素被消耗
        const consumed = Math.min(consume, this.auraGauge);
        this.auraGauge -= consumed;

        if (this.auraGauge <= 0.01) {
            // 附着元素被完全消耗
            this.auraElement = null;
            this.auraGauge = 0;
        }

        // 冻结特殊：残留冰元素
        if (reaction.type === "frozen") {
            this.frozenAuraElement = "ice";
        }
    }

    applyFreeze(duration) { this.frozen = true; this.frozenTimer = duration; }
    applySlow(amount, duration) {
        this.slowed = true;
        this.slowAmount = Math.max(this.slowAmount, amount);
        this.slowTimer = Math.max(this.slowTimer, duration);
    }
    applyDot(dps, duration) { this.dotDamage = dps; this.dotTimer = duration; }
    applyDefDown(amount, duration) { this.defDown = amount; this.defDownTimer = duration; }
    applyRoot(duration) { this.rooted = true; this.rootedTimer = duration; }
}

// ==================== 弹道（箭矢） ====================
class Projectile {
    constructor(sx, sy, targetEnemy, damage, element, speed, color, towerSpecial) {
        this.px = sx;
        this.py = sy;
        this.target = targetEnemy;
        this.damage = damage;
        this.element = element;
        this.speed = speed;      // 像素/秒
        this.color = color || "#ff0";
        this.hit = false;
        this.towerSpecial = towerSpecial || null;  // 携带塔的特殊效果
    }

    update(dt) {
        if (this.hit) return;
        // 追踪目标位置
        const dx = this.target.px - this.px;
        const dy = this.target.py - this.py;
        const dist = Math.hypot(dx, dy);
        if (dist < this.speed * dt || dist < 3) {
            // 命中
            this.px = this.target.px;
            this.py = this.target.py;
            this.hit = true;
        } else {
            this.px += (dx / dist) * this.speed * dt;
            this.py += (dy / dist) * this.speed * dt;
        }
    }
}

// ==================== 塔防引擎 ====================
class TDEngine {
    constructor(mapData) {
        this.map = mapData;
        this.width = mapData.width;
        this.height = mapData.height;
        this.cellSize = mapData.cell_size || 66;
        this.path = mapData.path;
        this.waves = mapData.waves;
        this.gold = mapData.starting_gold;
        this.maxLives = mapData.lives;
        this.lives = this.maxLives;
        this.mapTheme = mapData.map_theme || "mondstadt";  // 地图主题

        this.towers = [];
        this.traps = [];
        this.enemies = [];
        this.waveIndex = -1;
        this.waveActive = false;
        this.waveSpawnInterval = 1.0;
        this.waveSpawnTimer = 0;
        this.waveSpawnQueue = [];

        this.running = false;
        this.paused = false;
        this.gameOver = false;
        this.victory = false;
        this.gameTime = 0;

        this.effects = [];
        this.projectiles = [];
        this.killCount = 0;
        this.goldEarned = 0;
        this._lastTime = performance.now();

        this.pathSet = new Set(this.path.map(([x, y]) => `${x},${y}`));
    }

    canPlaceTower(gx, gy) {
        if (this.pathSet.has(`${gx},${gy}`)) return false;
        if (gx < 0 || gx >= this.width || gy < 0 || gy >= this.height) return false;
        return !this.towers.some(t => t.gridX === gx && t.gridY === gy);
    }

    canPlaceTrap(gx, gy) {
        if (!this.pathSet.has(`${gx},${gy}`)) return false;
        if (gx < 0 || gx >= this.width || gy < 0 || gy >= this.height) return false;
        return !this.traps.some(t => t.gridX === gx && t.gridY === gy);
    }

    placeTower(bid, gx, gy) {
        const bdef = BUILDING_DEFS[bid];
        if (!bdef || bdef.type !== "tower") return null;
        if (!this.canPlaceTower(gx, gy)) return null;
        if (this.gold < bdef.cost) return null;
        const tower = new Tower(bid, bdef, gx, gy, this.cellSize);
        this.gold -= tower.cost;
        this.towers.push(tower);
        return tower;
    }

    placeTrap(bid, gx, gy) {
        const bdef = BUILDING_DEFS[bid];
        if (!bdef || bdef.type !== "trap") return null;
        if (!this.canPlaceTrap(gx, gy)) return null;
        if (this.gold < bdef.cost) return null;
        const trap = new Trap(bid, bdef, gx, gy, this.cellSize);
        this.gold -= trap.cost;
        this.traps.push(trap);
        return trap;
    }

    sellBuilding(gx, gy) {
        for (let i = 0; i < this.towers.length; i++) {
            if (this.towers[i].gridX === gx && this.towers[i].gridY === gy) {
                const refund = Math.floor(this.towers[i].cost / 2);
                this.gold += refund;
                this.towers.splice(i, 1);
                return true;
            }
        }
        for (let i = 0; i < this.traps.length; i++) {
            if (this.traps[i].gridX === gx && this.traps[i].gridY === gy) {
                const refund = Math.floor(this.traps[i].cost / 2);
                this.gold += refund;
                this.traps.splice(i, 1);
                return true;
            }
        }
        return false;
    }

    start() {
        this.running = true;
        this._lastTime = performance.now();
        this._startNextWave();
    }

    _startNextWave() {
        this.waveIndex++;
        if (this.waveIndex >= this.waves.length) return;
        const wave = this.waves[this.waveIndex];
        this.waveActive = true;
        this.waveSpawnInterval = wave.interval;
        this.waveSpawnTimer = 0;
        const queue = [];
        for (const [enemyId, count] of wave.enemies) {
            for (let i = 0; i < count; i++) queue.push(enemyId);
        }
        // fisher-yates shuffle
        for (let i = queue.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [queue[i], queue[j]] = [queue[j], queue[i]];
        }
        this.waveSpawnQueue = queue;
    }

    _spawnEnemy() {
        if (!this.waveSpawnQueue.length) return;
        const eid = this.waveSpawnQueue.shift();
        this.enemies.push(new Enemy(eid, this.path, this.cellSize, this.waveIndex + 1));
    }

    _addEffect(type, px, py, text, color) {
        this.effects.push({ type, px, py, timer: 1.2, text, color });
    }

    update() {
        if (!this.running || this.gameOver) return;

        const now = performance.now();
        const dt = Math.min((now - this._lastTime) / 1000, 0.1); // cap dt
        this._lastTime = now;
        this.gameTime += dt;

        // wave management
        if (this.waveActive) {
            this.waveSpawnTimer -= dt;
            if (this.waveSpawnTimer <= 0 && this.waveSpawnQueue.length) {
                this._spawnEnemy();
                this.waveSpawnTimer = this.waveSpawnInterval;
            }
            if (!this.waveSpawnQueue.length) {
                const alive = this.enemies.some(e => !e.dead && !e.reachedEnd);
                if (!alive) {
                    this.waveActive = false;
                    const bonus = 50 + this.waveIndex * 30;
                    this.gold += bonus;
                    this._addEffect("wave", this.width * this.cellSize / 2,
                        this.height * this.cellSize / 2,
                        `第${this.waveIndex + 1}波完成! +${bonus}💰`, "#ff0");
                    if (this.waveIndex >= this.waves.length - 1) {
                        this.gameOver = true;
                        this.victory = true;
                    } else {
                        this._startNextWave();
                    }
                }
            }
        }

        // towers
        for (const tower of this.towers) {
            tower.update(dt);
            tower.updateAnimation(dt);
            if (tower.canAttack()) {
                const target = tower.findTarget(this.enemies);
                if (target) {
                    tower.lookAt(target.px, target.py);
                    let dmg = tower.getEffectiveDamage();
                    // 激化状态增伤
                    if (target.quickenAura && (tower.element === "thunder" || tower.element === "grass")) {
                        dmg = Math.floor(dmg * 1.3);
                    }
                    // 弹道携带反应倍率占位（实际反应在命中时通过 applyElement 触发）
                    const speed = this.cellSize * 8;
                    const color = ELEMENTS[tower.element] ? ELEMENTS[tower.element].color : "#ff0";
                    this.projectiles.push(new Projectile(
                        tower.px, tower.py, target, dmg, tower.element, speed, color, tower.special
                    ));
                    tower.fire();
                    tower.resetCooldown();
                }
            }
        }

        // traps（处理各种陷阱效果）
        for (const trap of this.traps) {
            trap.update(dt);
            if (trap.canTrigger()) {
                for (const enemy of this.enemies) {
                    if (enemy.dead || enemy.reachedEnd) continue;
                    const egx = Math.floor(enemy.px / this.cellSize);
                    const egy = Math.floor(enemy.py / this.cellSize);
                    if (egx === trap.gridX && egy === trap.gridY) {
                        const lastT = enemy.lastTrapTrigger[trap.bid] || 0;
                        const nowSec = performance.now() / 1000;
                        if (nowSec - lastT >= trap.cooldown) {
                            trap.trigger();
                            enemy.lastTrapTrigger[trap.bid] = nowSec;
                            const eff = trap.effect;
                            const eColor = ELEMENTS[trap.element]?.color || "#fff";

                            // 陷阱附着元素（可能触发反应）
                            const reaction = enemy.applyElement(trap.element, ELEMENTAL_GAUGE.STRONG_U);
                            const reactTag = reaction ? `<${reaction.name}>` : "";

                            switch (eff.type) {
                                case "explode": {
                                    // 范围爆炸
                                    const victims = this.enemies.filter(e => {
                                        return !e.dead && !e.reachedEnd && e !== enemy
                                            && Math.hypot(e.px - enemy.px, e.py - enemy.py) < eff.aoe_radius * this.cellSize;
                                    });
                                    enemy.takeDamage(eff.damage, trap.element);
                                    this._addEffect("trap", enemy.px, enemy.py, `💥${reactTag}-${eff.damage}`, eColor);
                                    for (const v of victims) {
                                        v.takeDamage(Math.floor(eff.damage * 0.6), trap.element);
                                    }
                                    // AOE反应
                                    if (reaction && reaction.aoe) {
                                        const aoeR = (reaction.aoe_radius || 1.5) * this.cellSize;
                                        const aoeDmg = Math.floor(eff.damage * (reaction.dmg_ratio || 1.0));
                                        for (const other of this.enemies) {
                                            if (other === enemy || other.dead || other.reachedEnd) continue;
                                            if (Math.hypot(other.px - enemy.px, other.py - enemy.py) <= aoeR) {
                                                other.takeDamage(aoeDmg, trap.element);
                                            }
                                        }
                                        this._addEffect("reaction", enemy.px, enemy.py,
                                            `${reaction.icon}${reaction.name}!`, "#f80");
                                    }
                                    break;
                                }
                                case "slow":
                                    enemy.applySlow(eff.amount, eff.duration);
                                    this._addEffect("trap", enemy.px, enemy.py, `💧${reactTag}减速`, eColor);
                                    break;
                                case "stun":
                                    enemy.applyFreeze(eff.duration);
                                    if (eff.damage) enemy.takeDamage(eff.damage, trap.element);
                                    this._addEffect("trap", enemy.px, enemy.py,
                                        eff.damage ? `⚡${reactTag}眩晕 -${eff.damage}` : `⚡${reactTag}眩晕`, eColor);
                                    break;
                                case "freeze":
                                    enemy.applyFreeze(eff.duration);
                                    this._addEffect("trap", enemy.px, enemy.py, `❄️${reactTag}冰冻`, eColor);
                                    break;
                                case "push":
                                    enemy.pathIndex = Math.max(0, enemy.pathIndex - eff.tiles);
                                    const [nx, ny] = enemy._pathPos(Math.floor(enemy.pathIndex));
                                    enemy.px = nx; enemy.py = ny;
                                    this._addEffect("trap", enemy.px, enemy.py, `🍃${reactTag}吹飞!`, eColor);
                                    break;
                                case "root":
                                    enemy.applyRoot(eff.duration);
                                    if (eff.dot_dps) enemy.applyDot(eff.dot_dps, eff.duration);
                                    this._addEffect("trap", enemy.px, enemy.py, `🌿${reactTag}缠绕`, eColor);
                                    break;
                                case "apply":
                                default:
                                    this._addEffect("trap", enemy.px, enemy.py, `💧${reactTag}附着`, eColor);
                                    break;
                            }
                        }
                    }
                }
            }
        }

        // projectiles（弹道更新与命中处理）
        for (const proj of this.projectiles) {
            proj.update(dt);
        }
        for (const proj of this.projectiles) {
            if (!proj.hit) continue;
            if (proj.target.dead || proj.target.reachedEnd) continue;

            // ---- 元素反应系统：先附着元素获取反应 ----
            const reaction = proj.target.applyElement(proj.element, ELEMENTAL_GAUGE.STANDARD_U);
            // 计算反应增伤倍率
            let dmgMultiplier = 1.0;
            let reactionAoeDmg = 0;
            let swirlAoeDmg = 0;
            let aoeRadius = 0;
            let knockback = false;

            if (reaction) {
                // 增伤/倍率类反应
                if (reaction.multiplier) {
                    dmgMultiplier = reaction.multiplier;
                }
                // AOE类反应
                if (reaction.aoe) {
                    aoeRadius = reaction.aoe_radius * this.cellSize;
                    reactionAoeDmg = Math.floor(proj.damage * (reaction.dmg_ratio || 1.0));
                    if (reaction.swirl_dmg) {
                        swirlAoeDmg = reaction.swirl_dmg;
                    }
                }
                if (reaction.knockback) knockback = true;
                if (reaction.phys_res_down) {
                    proj.target.physResDown = true;
                    proj.target.physResDownTimer = reaction.phys_res_duration || 12.0;
                }
                if (reaction.type === "frozen" || reaction.freeze_duration) {
                    proj.target.applyFreeze(reaction.freeze_duration);
                }
                if (reaction.type === "quicken") {
                    proj.target.quickenAura = true;
                    proj.target.quickenTimer = 8.0;
                }
                if (reaction.type === "burning" || reaction.dot_dps) {
                    proj.target.applyDot(reaction.dot_dps, reaction.dot_duration);
                }
                if (reaction.type === "crystallize") {
                    // 结晶：给最近的塔加护盾
                    let nearest = null, nearestDist = Infinity;
                    for (const t of this.towers) {
                        const d = Math.hypot(t.px - proj.target.px, t.py - proj.target.py);
                        if (d < nearestDist) { nearest = t; nearestDist = d; }
                    }
                    if (nearest && nearestDist < this.cellSize * 5) {
                        nearest.shield = Math.max(nearest.shield || 0, reaction.shield_amt);
                        this._addEffect("reaction", nearest.px, nearest.py, "🛡️结晶护盾", "#fbbf24");
                    }
                    this._addEffect("reaction", proj.target.px, proj.target.py, `💎${reaction.name}`, "#fbbf24");
                }
                // 扩散：传播元素到周围敌人
                if (reaction.type === "swirl" && reaction.swirl_element) {
                    aoeRadius = Math.max(aoeRadius, reaction.aoe_radius * this.cellSize);
                    swirlAoeDmg = reaction.swirl_dmg || 30;
                    for (const other of this.enemies) {
                        if (other === proj.target || other.dead || other.reachedEnd) continue;
                        if (Math.hypot(other.px - proj.target.px, other.py - proj.target.py) <= reaction.aoe_radius * this.cellSize) {
                            other.applyElement(reaction.swirl_element, ELEMENTAL_GAUGE.STANDARD_U);
                            other.takeDamage(swirlAoeDmg, reaction.swirl_element);
                            this._addEffect("reaction", other.px, other.py,
                                `${reaction.name} ${ELEMENTS[reaction.swirl_element]?.icon || ""}`, "#4ade80");
                        }
                    }
                }
            }

            // ---- 主伤害 ----
            const actual = proj.target.takeDamage(proj.damage, proj.element, dmgMultiplier);
            if (actual > 0) {
                const reactTag = reaction ? `<${reaction.name}>` : "";
                this._addEffect("damage", proj.target.px, proj.target.py,
                    `${reactTag}-${actual}`, proj.color);
            }

            // ---- AOE反应伤害（超载/超导/绽放）----
            if (reactionAoeDmg > 0 && aoeRadius > 0) {
                for (const other of this.enemies) {
                    if (other === proj.target || other.dead || other.reachedEnd) continue;
                    if (Math.hypot(other.px - proj.target.px, other.py - proj.target.py) <= aoeRadius) {
                        other.takeDamage(reactionAoeDmg, proj.element);
                        this._addEffect("reaction", other.px, other.py,
                            `${reaction.icon}${reaction.name}`, proj.color);
                    }
                }
                this._addEffect("reaction", proj.target.px, proj.target.py,
                    `${reaction.icon}${reaction.name}!`, "#f80");
            }

            // ---- 感电DoT ----
            if (reaction && reaction.type === "electro_charged") {
                proj.target.applyDot(reaction.dot_tick / reaction.tick_interval, reaction.tick_interval * reaction.tick_count);
                this._addEffect("reaction", proj.target.px, proj.target.py,
                    `⚡感电!`, "#a5f");
                // 连锁附近潮湿敌人
                if (reaction.chain) {
                    for (const other of this.enemies) {
                        if (other === proj.target || other.dead || other.reachedEnd) continue;
                        if (other.getActiveElement() === "water" &&
                            Math.hypot(other.px - proj.target.px, other.py - proj.target.py) <= reaction.chain_radius * this.cellSize) {
                            other.takeDamage(reaction.dot_tick, "thunder");
                            this._addEffect("reaction", other.px, other.py, "⚡感电连锁!", "#a5f");
                        }
                    }
                }
            }

            // ---- 蒸发/融化效果提示 ----
            if (reaction && (reaction.type === "vaporize" || reaction.type === "melt")) {
                this._addEffect("reaction", proj.target.px, proj.target.py,
                    `${reaction.icon}${reaction.name} x${reaction.multiplier}!`,
                    reaction.type === "vaporize" ? "#3bf" : "#f80");
            }

            // ---- 超导效果提示 ----
            if (reaction && reaction.type === "superconduct") {
                this._addEffect("reaction", proj.target.px, proj.target.py,
                    "❄️⚡超导体力-40%", "#7df");
            }

            // 应用塔的特殊效果
            const sp = proj.towerSpecial;
            if (sp) {
                const targets = [proj.target];
                const px = proj.target.px, py = proj.target.py;
                switch (sp.type) {
                    case "splash":
                        // 溅射：对周围敌人造成百分比伤害
                        for (const e of this.enemies) {
                            if (e === proj.target || e.dead || e.reachedEnd) continue;
                            if (Math.hypot(e.px - px, e.py - py) < sp.radius * this.cellSize) {
                                const splashDmg = Math.floor(proj.damage * sp.ratio);
                                e.takeDamage(splashDmg, proj.element);
                                this._addEffect("damage", e.px, e.py, `-${splashDmg}`, proj.color);
                                targets.push(e);
                            }
                        }
                        break;
                    case "chain":
                        // 连锁闪电：弹跳到附近敌人
                        let lastEnemy = proj.target;
                        for (let i = 0; i < sp.count; i++) {
                            let next = null, nextDist = Infinity;
                            for (const e of this.enemies) {
                                if (targets.includes(e) || e.dead || e.reachedEnd) continue;
                                const d = Math.hypot(e.px - lastEnemy.px, e.py - lastEnemy.py);
                                if (d < this.cellSize * 2 && d < nextDist) {
                                    next = e; nextDist = d;
                                }
                            }
                            if (next) {
                                const chainDmg = Math.floor(proj.damage * sp.ratio);
                                next.takeDamage(chainDmg, proj.element);
                                this._addEffect("damage", next.px, next.py, `⚡-${chainDmg}`, proj.color);
                                targets.push(next);
                                lastEnemy = next;
                            }
                        }
                        break;
                    case "slow":
                        proj.target.applySlow(sp.amount, sp.duration);
                        this._addEffect("effect", px, py, "❄️减速", proj.color);
                        break;
                    case "spread":
                        // 扩散：给周围敌人施加元素
                        for (const e of this.enemies) {
                            if (e === proj.target || e.dead || e.reachedEnd) continue;
                            if (Math.hypot(e.px - px, e.py - py) < sp.radius * this.cellSize) {
                                e.applyElement(proj.element);
                            }
                        }
                        this._addEffect("effect", px, py, "🍃扩散元素", proj.color);
                        break;
                    case "dot":
                        proj.target.applyDot(sp.dps, sp.duration);
                        this._addEffect("effect", px, py, "🌿中毒", proj.color);
                        break;
                }
            }
        }
        this.projectiles = this.projectiles.filter(p => !p.hit);

        // enemies
        for (const enemy of this.enemies) {
            if (enemy.dead || enemy.reachedEnd) continue;
            enemy.update(dt);
            if (enemy.reachedEnd) {
                this.lives -= 1;
                this._addEffect("leak", enemy.px, enemy.py, "漏怪! ❤️-1", "#f44");
                if (this.lives <= 0) { this.gameOver = true; this.victory = false; }
            } else if (enemy.dead) {
                this.gold += enemy.goldReward;
                this.goldEarned += enemy.goldReward;
                this.killCount += 1;
                this._addEffect("gold", enemy.px, enemy.py, `+${enemy.goldReward}💰`, "#ff0");
            }
        }

        this.enemies = this.enemies.filter(e => !e.dead && !e.reachedEnd);
        this.effects = this.effects.filter(ef => ef.timer > 0);
        for (const ef of this.effects) ef.timer -= dt;
        this.towers = this.towers.filter(t => !t.isDestroyed());
    }
}