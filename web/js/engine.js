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
        this.gridX = gridX;
        this.gridY = gridY;
        this.px = gridX * cellSize + cellSize / 2;
        this.py = gridY * cellSize + cellSize / 2;
        this.cellSize = cellSize;
        this.triggerCount = 0;
    }

    canTrigger() { return this.cooldownRemaining <= 0; }

    trigger() {
        this.cooldownRemaining = this.cooldown;
        this.triggerCount++;
    }

    update(dt) {
        if (this.cooldownRemaining > 0) this.cooldownRemaining -= dt;
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
    }

    getEffectiveDamage() { return Math.floor(this.damage * (1 + this.dmgBonus)); }

    canAttack() { return this.attackCooldown <= 0; }

    resetCooldown() { this.attackCooldown = 1.0 / Math.max(this.atkSpeed, 0.1); }

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
        this.elementHits = [];
    }

    _pathPos(idx) {
        if (idx >= this.path.length) idx = this.path.length - 1;
        const [gx, gy] = this.path[idx];
        return [gx * this.cellSize + this.cellSize / 2, gy * this.cellSize + this.cellSize / 2];
    }

    update(dt) {
        if (this.frozen) {
            this.frozenTimer -= dt;
            if (this.frozenTimer <= 0) this.frozen = false;
            return;
        }

        let effectiveSpeed = this.speed;
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

    takeDamage(dmg, element) {
        if (this.dead) return 0;
        if (this.defDown > 0) dmg = Math.floor(dmg * (1 + this.defDown));
        const actual = Math.min(this.hp, dmg);
        this.hp -= actual;
        if (element) {
            const now = performance.now() / 1000;
            this.elementHits.push([element, now]);
            this.elementHits = this.elementHits.filter(([, t]) => now - t < TD_REACTION_WINDOW);
        }
        if (this.hp <= 0) this.dead = true;
        return actual;
    }

    applyElement(element) {
        const now = performance.now() / 1000;
        this.elementHits.push([element, now]);
        this.elementHits = this.elementHits.filter(([, t]) => now - t < TD_REACTION_WINDOW);
    }

    getActiveElement() {
        const now = performance.now() / 1000;
        this.elementHits = this.elementHits.filter(([, t]) => now - t < TD_REACTION_WINDOW);
        if (this.elementHits.length > 0) return this.elementHits[this.elementHits.length - 1][0];
        return this.element;
    }

    checkReaction(newElement) {
        const now = performance.now() / 1000;
        let other = null;
        for (const [elem, ts] of this.elementHits) {
            if (elem !== newElement && now - ts < TD_REACTION_WINDOW) {
                other = elem;
                break;
            }
        }
        if (!other) return null;
        return TD_REACTIONS[`${newElement}+${other}`] || null;
    }

    applyFreeze(duration) { this.frozen = true; this.frozenTimer = duration; }
    applySlow(amount, duration) {
        this.slowed = true;
        this.slowAmount = Math.max(this.slowAmount, amount);
        this.slowTimer = Math.max(this.slowTimer, duration);
    }
    applyDot(dps, duration) { this.dotDamage = dps; this.dotTimer = duration; }
    applyDefDown(amount, duration) { this.defDown = amount; this.defDownTimer = duration; }
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

    _checkEnemyReaction(enemy, newElement) {
        const reaction = enemy.checkReaction(newElement);
        if (!reaction) return;
        const px = enemy.px, py = enemy.py;
        if (reaction.freeze) {
            enemy.applyFreeze(reaction.freeze_duration);
            this._addEffect("reaction", px, py, "❄️冻结", "#7df");
        } else if (reaction.dot) {
            enemy.applyDot(reaction.dot_dmg, reaction.dot_duration);
            this._addEffect("reaction", px, py, "⚡感电", "#a0f");
        } else if (reaction.aoe) {
            const radius = reaction.aoe_radius * this.cellSize;
            let aoeDmg = Math.floor(enemy.maxHp * 0.1 * reaction.aoe_dmg_ratio);
            aoeDmg = Math.max(aoeDmg, 20);
            for (const other of this.enemies) {
                if (other === enemy || other.dead) continue;
                if (Math.hypot(other.px - px, other.py - py) <= radius) {
                    other.takeDamage(aoeDmg, enemy.element);
                }
            }
            if (reaction.def_down) {
                enemy.applyDefDown(reaction.def_down, reaction.def_down_dur || 4.0);
            }
            this._addEffect("reaction", px, py, `💥${reaction.name}`, "#f80");
        } else if (reaction.dmg_mult) {
            this._addEffect("reaction", px, py, `✨${reaction.name}`, "#ff0");
        }
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
            if (tower.canAttack()) {
                const target = tower.findTarget(this.enemies);
                if (target) {
                    let dmg = tower.getEffectiveDamage();
                    const targetElem = target.getActiveElement();
                    const reaction = targetElem ? TD_REACTIONS[`${tower.element}+${targetElem}`] : null;
                    if (reaction && reaction.dmg_mult) {
                        dmg = Math.floor(dmg * reaction.dmg_mult);
                    }
                    const actual = target.takeDamage(dmg, tower.element);
                    this._checkEnemyReaction(target, tower.element);
                    tower.resetCooldown();
                    if (actual > 0) {
                        this._addEffect("damage", target.px, target.py,
                            `-${actual}`, ELEMENTS[tower.element].color);
                    }
                }
            }
        }

        // traps
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
                            enemy.applyElement(trap.element);
                            trap.trigger();
                            enemy.lastTrapTrigger[trap.bid] = nowSec;
                            this._addEffect("trap", enemy.px, enemy.py,
                                `💧附着`, ELEMENTS[trap.element].color);
                        }
                    }
                }
            }
        }

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