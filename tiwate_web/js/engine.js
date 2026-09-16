/* ==================== 塔防战斗引擎 ==================== */

/* ---------- 弹道 ---------- */
class Projectile {
    constructor(startX, startY, targetX, targetY, color = "#fff") {
        this.x = startX;
        this.y = startY;
        this.startX = startX;
        this.startY = startY;
        this.targetX = targetX;
        this.targetY = targetY;
        this.color = color;
        this.progress = 0;
        this.speed = 8;
    }

    update(dt) {
        this.progress += this.speed * dt;
        const t = Math.min(this.progress, 1);
        this.x = this.startX + (this.targetX - this.startX) * t;
        this.y = this.startY + (this.targetY - this.startY) * t;
        return this.progress >= 1;
    }
}

/* ---------- 陷阱 ---------- */
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
        this.cellSize = cellSize;
        this.px = gridX * cellSize + cellSize / 2;
        this.py = gridY * cellSize + cellSize / 2;
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

/* ---------- 塔 ---------- */
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
        this.cellSize = cellSize;
        this.px = gridX * cellSize + cellSize / 2;
        this.py = gridY * cellSize + cellSize / 2;
        this.attackCooldown = 0;
        this.target = null;
        this.dmgBonus = 0;
    }

    getEffectiveDamage() { return Math.floor(this.damage * (1 + this.dmgBonus)); }
    canAttack() { return this.attackCooldown <= 0; }
    resetCooldown() { this.attackCooldown = 1.0 / Math.max(this.atkSpeed, 0.1); }

    findTarget(enemies) {
        let best = null, bestProgress = -1;
        for (const e of enemies) {
            if (e.dead || e.reachedEnd) continue;
            const dist = Math.hypot(e.px - this.px, e.py - this.py);
            if (dist / this.cellSize <= this.range) {
                if (e.pathIndex > bestProgress) {
                    best = e; bestProgress = e.pathIndex;
                } else if (e.pathIndex === bestProgress && best) {
                    if (dist < Math.hypot(best.px - this.px, best.py - this.py)) best = e;
                }
            }
        }
        return best;
    }

    takeDamage(dmg) {
        if (this.shield > 0) {
            if (this.shield >= dmg) { this.shield -= dmg; return 0; }
            dmg -= this.shield; this.shield = 0;
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

/* ---------- 敌人 ---------- */
class Enemy {
    constructor(enemyId, path, cellSize, waveLevel = 1) {
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
        const p0 = this._pathPos(0);
        this.px = p0[0]; this.py = p0[1];
        this.dead = false;
        this.reachedEnd = false;
        this.frozen = false; this.frozenTimer = 0;
        this.slowed = false; this.slowTimer = 0; this.slowAmount = 0;
        this.defDown = 0; this.defDownTimer = 0;
        this.dotDamage = 0; this.dotTimer = 0;
        this.lastTrapTrigger = {};
        this.elementHits = [];
    }

    _pathPos(idx) {
        const gx = this.path[Math.min(idx, this.path.length - 1)][0];
        const gy = this.path[Math.min(idx, this.path.length - 1)][1];
        return [gx * this.cellSize + this.cellSize / 2, gy * this.cellSize + this.cellSize / 2];
    }

    update(dt) {
        if (this.frozen) {
            this.frozenTimer -= dt;
            if (this.frozenTimer <= 0) this.frozen = false;
            return;
        }
        let effSpeed = this.speed;
        if (this.slowed) {
            this.slowTimer -= dt;
            effSpeed *= (1 - this.slowAmount);
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
        this.pathIndex += (effSpeed * dt) / this.cellSize;
        const idx = Math.floor(this.pathIndex);
        if (idx >= this.path.length - 1) {
            this.reachedEnd = true;
            const p = this._pathPos(this.path.length - 1);
            this.px = p[0]; this.py = p[1];
        } else {
            const frac = this.pathIndex - idx;
            const [x1, y1] = this._pathPos(idx);
            const [x2, y2] = this._pathPos(idx + 1);
            this.px = x1 + (x2 - x1) * frac;
            this.py = y1 + (y2 - y1) * frac;
        }
        if (this.hp <= 0) { this.hp = 0; this.dead = true; }
    }

    takeDamage(dmg, element = null) {
        if (this.dead) return 0;
        if (this.defDown > 0) dmg = Math.floor(dmg * (1 + this.defDown));
        const actual = Math.min(this.hp, dmg);
        this.hp -= actual;
        if (element) {
            const now = performance.now() / 1000;
            this.elementHits.push([element, now]);
            this.elementHits = this.elementHits.filter(([_, t]) => now - t < TD_REACTION_WINDOW);
        }
        if (this.hp <= 0) this.dead = true;
        return actual;
    }

    applyElement(element) {
        const now = performance.now() / 1000;
        this.elementHits.push([element, now]);
        this.elementHits = this.elementHits.filter(([_, t]) => now - t < TD_REACTION_WINDOW);
    }

    getActiveElement() {
        const now = performance.now() / 1000;
        this.elementHits = this.elementHits.filter(([_, t]) => now - t < TD_REACTION_WINDOW);
        if (this.elementHits.length > 0) return this.elementHits[this.elementHits.length - 1][0];
        return this.element;
    }

    checkReaction(newElement) {
        const now = performance.now() / 1000;
        let other = null;
        for (const [elem, ts] of this.elementHits) {
            if (elem !== newElement && now - ts < TD_REACTION_WINDOW) { other = elem; break; }
        }
        if (!other) return null;
        return TD_REACTIONS[`${newElement}+${other}`] || null;
    }

    applyFreeze(duration) { this.frozen = true; this.frozenTimer = duration; }
    applySlow(amount, duration) { this.slowed = true; this.slowAmount = Math.max(this.slowAmount, amount); this.slowTimer = Math.max(this.slowTimer, duration); }
    applyDot(dps, duration) { this.dotDamage = dps; this.dotTimer = duration; }
    applyDefDown(amount, duration) { this.defDown = amount; this.defDownTimer = duration; }
}

/* ---------- 塔防引擎 ---------- */
class TDEngine {
    constructor(mapData) {
        this.map = mapData;
        this.width = mapData.width;
        this.height = mapData.height;
        this.cellSize = mapData.cell_size;
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
        this.projectiles = [];
        this.killCount = 0;
        this.goldEarned = 0;
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

    sellTrapOrTower(gx, gy) {
        const ti = this.towers.findIndex(t => t.gridX === gx && t.gridY === gy);
        if (ti >= 0) { this.gold += Math.floor(this.towers[ti].cost / 2); this.towers.splice(ti, 1); return true; }
        const tri = this.traps.findIndex(t => t.gridX === gx && t.gridY === gy);
        if (tri >= 0) { this.gold += Math.floor(this.traps[tri].cost / 2); this.traps.splice(tri, 1); return true; }
        return false;
    }

    start() {
        this.running = true;
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
        for (const [eid, count] of wave.enemies) {
            for (let i = 0; i < count; i++) queue.push(eid);
        }
        // shuffle
        for (let i = queue.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [queue[i], queue[j]] = [queue[j], queue[i]];
        }
        this.waveSpawnQueue = queue;
    }

    _spawnEnemy() {
        if (this.waveSpawnQueue.length === 0) return;
        const eid = this.waveSpawnQueue.shift();
        this.enemies.push(new Enemy(eid, this.path, this.cellSize, this.waveIndex + 1));
    }

    _checkEnemyReaction(enemy, newElement) {
        const reaction = enemy.checkReaction(newElement);
        if (!reaction) return;
        const posX = enemy.px, posY = enemy.py;
        if (reaction.freeze) {
            enemy.applyFreeze(reaction.freeze_duration);
            this._addEffect("reaction", posX, posY, "❄️冻结", "#7df");
        } else if (reaction.dot) {
            enemy.applyDot(reaction.dot_dmg, reaction.dot_duration);
            this._addEffect("reaction", posX, posY, "⚡感电", "#a0f");
        } else if (reaction.aoe) {
            const radius = reaction.aoe_radius * this.cellSize;
            let aoeDmg = Math.floor(enemy.maxHp * 0.1 * reaction.aoe_dmg_ratio);
            aoeDmg = Math.max(aoeDmg, 20);
            for (const other of this.enemies) {
                if (other === enemy || other.dead) continue;
                const dist = Math.hypot(other.px - posX, other.py - posY);
                if (dist <= radius) other.takeDamage(aoeDmg, enemy.element);
            }
            if (reaction.def_down) enemy.applyDefDown(reaction.def_down, reaction.def_down_dur || 4.0);
            this._addEffect("reaction", posX, posY, `💥${reaction.name}`, "#f80");
        } else if (reaction.dmg_mult) {
            this._addEffect("reaction", posX, posY, `✨${reaction.name}`, "#ff0");
        }
    }

    _addEffect(type, px, py, text, color) {
        this.effects.push({ type, px, py, timer: 1.2, text, color });
    }

    update(dt) {
        if (!this.running || this.gameOver) return;
        this.gameTime += dt;

        /* 波次管理 */
        if (this.waveActive) {
            this.waveSpawnTimer -= dt;
            if (this.waveSpawnTimer <= 0 && this.waveSpawnQueue.length > 0) {
                this._spawnEnemy();
                this.waveSpawnTimer = this.waveSpawnInterval;
            }
            if (this.waveSpawnQueue.length === 0) {
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

        /* 更新塔 + 攻击 */
        for (const tower of this.towers) {
            tower.update(dt);
            if (tower.canAttack()) {
                const target = tower.findTarget(this.enemies);
                if (target) {
                    let dmg = tower.getEffectiveDamage();
                    const targetEl = target.getActiveElement();
                    const reaction = targetEl ? TD_REACTIONS[`${tower.element}+${targetEl}`] : null;
                    if (reaction && reaction.dmg_mult) dmg = Math.floor(dmg * reaction.dmg_mult);
                    const actual = target.takeDamage(dmg, tower.element);
                    this._checkEnemyReaction(target, tower.element);
                    tower.resetCooldown();
                    this.projectiles.push(new Projectile(
                        tower.px, tower.py, target.px, target.py, ELEMENTS[tower.element].color
                    ));
                    if (actual > 0) {
                        this._addEffect("damage", target.px, target.py, `-${actual}`, ELEMENTS[tower.element].color);
                    }
                }
            }
        }

        /* 更新陷阱 */
        for (const trap of this.traps) {
            trap.update(dt);
            if (trap.canTrigger()) {
                for (const enemy of this.enemies) {
                    if (enemy.dead || enemy.reachedEnd) continue;
                    const egx = Math.floor(enemy.px / this.cellSize);
                    const egy = Math.floor(enemy.py / this.cellSize);
                    if (egx === trap.gridX && egy === trap.gridY) {
                        const lastT = enemy.lastTrapTrigger[trap.bid] || 0;
                        if (performance.now() / 1000 - lastT >= trap.cooldown) {
                            enemy.applyElement(trap.element);
                            trap.trigger();
                            enemy.lastTrapTrigger[trap.bid] = performance.now() / 1000;
                            this._addEffect("trap", enemy.px, enemy.py, "💧附着", ELEMENTS[trap.element].color);
                        }
                    }
                }
            }
        }

        /* 更新敌人 */
        for (const enemy of this.enemies) {
            if (enemy.dead || enemy.reachedEnd) continue;
            enemy.update(dt);
            if (enemy.reachedEnd) {
                this.lives--;
                this._addEffect("leak", enemy.px, enemy.py, "漏怪! ❤️-1", "#f44");
                if (this.lives <= 0) { this.gameOver = true; this.victory = false; }
            } else if (enemy.dead) {
                this.gold += enemy.goldReward;
                this.goldEarned += enemy.goldReward;
                this.killCount++;
                this._addEffect("gold", enemy.px, enemy.py, `+${enemy.goldReward}💰`, "#ff0");
            }
        }

        this.enemies = this.enemies.filter(e => !e.dead && !e.reachedEnd);
        this.effects = this.effects.filter(e => { e.timer -= dt; return e.timer > 0; });
        this.projectiles = this.projectiles.filter(p => !p.update(dt));
        this.towers = this.towers.filter(t => !t.isDestroyed());
    }

    resize(newCellSize) {
        if (newCellSize === this.cellSize) return;
        const ratio = newCellSize / this.cellSize;
        this.cellSize = newCellSize;
        for (const t of this.towers) {
            t.cellSize = newCellSize;
            t.px = t.gridX * newCellSize + newCellSize / 2;
            t.py = t.gridY * newCellSize + newCellSize / 2;
        }
        for (const tr of this.traps) {
            tr.cellSize = newCellSize;
            tr.px = tr.gridX * newCellSize + newCellSize / 2;
            tr.py = tr.gridY * newCellSize + newCellSize / 2;
        }
        for (const e of this.enemies) {
            if (e.dead || e.reachedEnd) continue;
            e.speed = e.baseSpeed * ratio;
            e.cellSize = newCellSize;
            const idx = Math.floor(e.pathIndex);
            if (idx >= e.path.length - 1) {
                e.px = e.path[e.path.length - 1][0] * newCellSize + newCellSize / 2;
                e.py = e.path[e.path.length - 1][1] * newCellSize + newCellSize / 2;
            } else {
                const frac = e.pathIndex - idx;
                e.px = (e.path[idx][0] * newCellSize + newCellSize / 2) +
                    ((e.path[idx + 1][0] * newCellSize + newCellSize / 2) - (e.path[idx][0] * newCellSize + newCellSize / 2)) * frac;
                e.py = (e.path[idx][1] * newCellSize + newCellSize / 2) +
                    ((e.path[idx + 1][1] * newCellSize + newCellSize / 2) - (e.path[idx][1] * newCellSize + newCellSize / 2)) * frac;
            }
        }
        for (const ef of this.effects) { ef.px *= ratio; ef.py *= ratio; }
        for (const p of this.projectiles) {
            p.x *= ratio; p.y *= ratio;
            p.startX *= ratio; p.startY *= ratio;
            p.targetX *= ratio; p.targetY *= ratio;
        }
    }
}