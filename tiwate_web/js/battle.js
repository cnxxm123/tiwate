/* ==================== 战斗界面渲染模块 ==================== */

const GRASS_COLORS = ["#2d5a2d", "#356c35", "#2a4a2a"];
const FLOWER_COLORS = ["#ffd700", "#ff9a9e", "#a0c4ff", "#fdffb6"];
const GRID_GREEN = ["#1a3320", "#1f3a24", "#1c3522"];

class BattleScreen {
    constructor(app) {
        this.app = app;
    }

    /* 进入地图 */
    enterMap() {
        const app = this.app;
        const tdm = TD_MAPS.find(m => m.id === app.battleStageId);
        if (!tdm) return;

        // 隐藏关卡选择，显示战斗面板
        document.getElementById("top-bar").style.display = "none";
        document.getElementById("bottom-bar").style.display = "none";
        document.getElementById("stage-panel").style.display = "none";
        document.getElementById("battle-panel").classList.remove("hidden");
        app.content.style.padding = "0";

        const mid = document.getElementById("battle-mid");
        const csW = Math.floor(mid.clientWidth / tdm.width);
        const csH = Math.floor(mid.clientHeight / tdm.height);
        const cellSize = Math.max(50, Math.min(csW, csH, 90));
        app.tdCellSize = cellSize;

        const tdmCopy = JSON.parse(JSON.stringify(tdm));
        tdmCopy.cell_size = cellSize;
        app.battle = new TDEngine(tdmCopy);
        app.battleActive = true;

        const canvas = document.getElementById("battle-canvas");
        canvas.width = tdmCopy.width * cellSize;
        canvas.height = tdmCopy.height * cellSize;
        this.renderMap();

        document.getElementById("btn-start").disabled = false;
        document.getElementById("btn-start").textContent = "▶ 开始出怪";
        this.updateTopBar();
    }

    /* 返回选关 */
    returnToStageSelect() {
        const app = this.app;
        if (app.gameLoopId) { cancelAnimationFrame(app.gameLoopId); app.gameLoopId = null; }
        document.getElementById("top-bar").style.display = "flex";
        document.getElementById("bottom-bar").style.display = "flex";
        document.getElementById("stage-panel").style.display = "flex";
        document.getElementById("battle-panel").classList.add("hidden");
        app.content.style.padding = "8px 12px 0";
        app.showStageSelect();
        app.saveState();
    }

    /* 战斗循环 */
    startWave() {
        if (!this.app.battle) return;
        this.app.battle.start();
        document.getElementById("btn-start").disabled = true;
        document.getElementById("btn-start").textContent = "出怪中...";
        this.app.tdLastTime = performance.now() / 1000;
        this.gameLoop();
    }

    gameLoop() {
        const app = this.app;
        if (!app.battle || app.battle.gameOver) {
            this.handleEnd();
            return;
        }
        if (!app.battleActive) return;

        const now = performance.now() / 1000;
        const dt = Math.min(now - app.tdLastTime, 0.1);
        app.tdLastTime = now;

        app.battle.update(dt);
        this.renderMap();
        this.updateTopBar();

        if (!app.battle.gameOver) {
            app.gameLoopId = requestAnimationFrame(() => this.gameLoop());
        }
    }

    updateTopBar() {
        const b = this.app.battle;
        if (!b) return;
        document.getElementById("td-gold").textContent = `💰 ${b.gold}`;
        document.getElementById("td-wave").textContent = `波次: ${b.waveIndex + 1}/${b.waves.length}`;
        document.getElementById("td-lives").textContent = `❤️ ${b.lives}/${b.maxLives}`;
        const t = b.gameTime;
        document.getElementById("td-info").textContent =
            `⏱ ${Math.floor(t / 60)}:${String(Math.floor(t % 60)).padStart(2, "0")}  击杀:${b.killCount}`;
    }

    /* 点击 Canvas */
    onCanvasClick(e) {
        const app = this.app;
        if (!app.battle) return;
        const rect = e.target.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;
        const gx = Math.floor(mx / app.tdCellSize);
        const gy = Math.floor(my / app.tdCellSize);

        const tdm = TD_MAPS.find(m => m.id === app.battleStageId);
        if (!tdm) return;
        if (gx < 0 || gx >= tdm.width || gy < 0 || gy >= tdm.height) return;

        const isPath = app.battle.pathSet.has(`${gx},${gy}`);
        const existing = app.battle.towers.find(t => t.gridX === gx && t.gridY === gy)
                      || app.battle.traps.find(t => t.gridX === gx && t.gridY === gy);

        app.showContextMenu(e.clientX, e.clientY, gx, gy, isPath, existing);
    }

    /* 渲染地图 */
    renderMap() {
        const app = this.app;
        const canvas = document.getElementById("battle-canvas");
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        if (!app.battle) return;

        const tdm = TD_MAPS.find(m => m.id === app.battleStageId);
        if (!tdm) return;
        const cs = app.tdCellSize;
        const battle = app.battle;

        this._drawGrid(ctx, tdm, cs);
        this._drawDecorations(ctx, tdm, cs);
        this._drawPath(ctx, tdm, cs);
        this._drawEntities(ctx, cs);
    }

    _drawGrid(ctx, tdm, cs) {
        const pathSet = this.app.battle.pathSet;
        for (let y = 0; y < tdm.height; y++) {
            for (let x = 0; x < tdm.width; x++) {
                if (pathSet.has(`${x},${y}`)) {
                    ctx.fillStyle = "#4a3728";
                } else {
                    ctx.fillStyle = GRID_GREEN[(x + y) % 3];
                }
                ctx.fillRect(x * cs, y * cs, cs, cs);
            }
        }
    }

    _drawDecorations(ctx, tdm, cs) {
        const pathSet = this.app.battle.pathSet;
        for (let y = 0; y < tdm.height; y++) {
            for (let x = 0; x < tdm.width; x++) {
                if (pathSet.has(`${x},${y}`)) continue;
                const seed = x * 1000 + y;
                const rng = this._seededRand(seed);
                const cx = x * cs + cs / 2, cy = y * cs + cs / 2;
                const s = cs * 0.08;
                for (let i = 0; i < rng() * 3 + 1; i++) {
                    const dx = (rng() - 0.5) * cs * 0.7;
                    const dy = (rng() - 0.5) * cs * 0.7;
                    const kind = Math.floor(rng() * 5);
                    if (kind === 0) {
                        ctx.fillStyle = GRASS_COLORS[Math.floor(rng() * 3)];
                        ctx.beginPath();
                        ctx.moveTo(cx + dx - s * 1.5, cy + dy + s);
                        ctx.lineTo(cx + dx, cy + dy - s * 1.5);
                        ctx.lineTo(cx + dx + s * 1.5, cy + dy + s);
                        ctx.fill();
                    } else if (kind === 1 && cs >= 45) {
                        ctx.fillStyle = FLOWER_COLORS[Math.floor(rng() * 4)];
                        ctx.beginPath();
                        ctx.arc(cx + dx, cy + dy, s, 0, Math.PI * 2);
                        ctx.fill();
                    } else if (kind === 2) {
                        ctx.fillStyle = "#3a3a40";
                        ctx.beginPath();
                        ctx.ellipse(cx + dx, cy + dy, s * 1.2, s * 0.8, 0, 0, Math.PI * 2);
                        ctx.fill();
                    }
                }
            }
        }
    }

    _seededRand(seed) {
        let s = seed;
        return () => { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; };
    }

    _drawPath(ctx, tdm, cs) {
        const path = this.app.battle.path;
        for (let i = 0; i < path.length; i++) {
            const [px, py] = path[i];
            if (i === 0) {
                ctx.fillStyle = "#1a4a2a";
                ctx.fillRect(px * cs + 1, py * cs + 1, cs - 2, cs - 2);
                ctx.strokeStyle = "#4aff8a";
                ctx.lineWidth = 2;
                ctx.strokeRect(px * cs + 1, py * cs + 1, cs - 2, cs - 2);
                ctx.fillStyle = "#0d2818";
                ctx.fillRect(px * cs + cs * 0.2, py * cs + cs * 0.15, cs * 0.6, cs * 0.7);
                ctx.fillStyle = "#e0d8c8";
                ctx.font = `${cs * 0.35}px sans-serif`;
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillText("🚪", px * cs + cs / 2, py * cs + cs / 2);
            } else if (i === path.length - 1) {
                ctx.fillStyle = "#3a1a1a";
                ctx.fillRect(px * cs + 1, py * cs + 1, cs - 2, cs - 2);
                ctx.strokeStyle = "#ff4a4a";
                ctx.lineWidth = 2;
                ctx.strokeRect(px * cs + 1, py * cs + 1, cs - 2, cs - 2);
                ctx.beginPath();
                ctx.arc(px * cs + cs / 2, py * cs + cs / 2, cs * 0.3, 0, Math.PI * 2);
                ctx.fillStyle = "#2a0000";
                ctx.fill();
                ctx.fillStyle = "#e0d8c8";
                ctx.fillText("🎯", px * cs + cs / 2, py * cs + cs / 2);
            } else if (i % 2 === 0 && cs >= 40) {
                const [prevX, prevY] = path[i - 1];
                const [nextX, nextY] = path[i + 1] || path[i];
                const dx = (nextX - prevX) * cs * 0.35;
                const dy = (nextY - prevY) * cs * 0.35;
                const midX = px * cs + cs / 2, midY = py * cs + cs / 2;
                ctx.strokeStyle = "#7a5a3a";
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(midX - dx, midY - dy);
                ctx.lineTo(midX + dx, midY + dy);
                ctx.stroke();
                // arrowhead
                const angle = Math.atan2(dy, dx);
                const headLen = cs * 0.2;
                ctx.beginPath();
                ctx.moveTo(midX + dx, midY + dy);
                ctx.lineTo(midX + dx - headLen * Math.cos(angle - 0.5), midY + dy - headLen * Math.sin(angle - 0.5));
                ctx.lineTo(midX + dx - headLen * Math.cos(angle + 0.5), midY + dy - headLen * Math.sin(angle + 0.5));
                ctx.fillStyle = "#7a5a3a";
                ctx.fill();
            }
        }
    }

    _drawEntities(ctx, cs) {
        const battle = this.app.battle;

        /* 陷阱 */
        for (const tr of battle.traps) {
            const x = tr.gridX * cs + cs / 2, y = tr.gridY * cs + cs / 2;
            const r = cs * 0.4;
            ctx.fillStyle = "#154060";
            ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
            ctx.strokeStyle = "#4a9ad4"; ctx.lineWidth = 2;
            ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.stroke();
            ctx.fillStyle = "#e0d8c8";
            ctx.font = `${cs * 0.3}px sans-serif`;
            ctx.textAlign = "center"; ctx.textBaseline = "middle";
            ctx.fillText("💧", x, y);
        }

        /* 塔 */
        for (const tw of battle.towers) {
            const x = tw.gridX * cs + cs / 2, y = tw.gridY * cs + cs / 2;
            const r = cs * 0.38;
            ctx.fillStyle = "#0a0a0a";
            ctx.beginPath(); ctx.arc(x + 2, y + 2, r, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = "#2a2040";
            ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
            ctx.strokeStyle = "#8b6baa"; ctx.lineWidth = 2;
            ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.stroke();
            ctx.fillStyle = "#e0d8c8";
            ctx.font = `${cs * 0.3}px sans-serif`;
            ctx.textAlign = "center"; ctx.textBaseline = "middle";
            ctx.fillText("🏹", x, y);
        }

        /* 敌人 */
        for (const e of battle.enemies) {
            if (e.dead) continue;
            const x = e.px, y = e.py;
            const r = cs * 0.3;
            // shadow
            ctx.fillStyle = "rgba(0,0,0,0.4)";
            ctx.beginPath(); ctx.ellipse(x + 2, y + 2, r, r * 0.7, 0, 0, Math.PI * 2); ctx.fill();
            // body
            let bodyColor = "#c84040";
            if (e.id === "enemy_2") bodyColor = "#c86020";
            else if (e.id === "enemy_3") bodyColor = "#9050a0";
            else if (e.id === "enemy_4") bodyColor = "#6070a0";
            else if (e.id === "enemy_5") bodyColor = "#a0a0a0";
            ctx.fillStyle = bodyColor;
            ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
            ctx.strokeStyle = "#222"; ctx.lineWidth = 1;
            ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.stroke();
            // hp bar
            const hpRatio = e.hp / e.maxHp;
            const barW = cs * 0.6;
            let hpColor = hpRatio > 0.5 ? "#4aff4a" : hpRatio > 0.2 ? "#ffaa00" : "#ff3333";
            ctx.fillStyle = hpColor;
            ctx.fillRect(x - barW / 2, y - r - 5, barW * hpRatio, 3);
            if (e.frozen) {
                ctx.font = `${cs * 0.1}px sans-serif`;
                ctx.textAlign = "center"; ctx.fillText("❄️", x, y - r - 10);
            }
        }

        /* 特效 */
        for (const ef of battle.effects) {
            const alpha = Math.min(1, ef.timer / 1.2);
            const fontSize = Math.max(8, 10 + (1 - alpha) * 8);
            ctx.fillStyle = ef.color;
            ctx.globalAlpha = alpha;
            ctx.font = `${fontSize}px Microsoft YaHei, sans-serif`;
            ctx.textAlign = "center";
            ctx.fillText(ef.text, ef.px, ef.py - 20 * (1 - alpha));
            ctx.globalAlpha = 1;
        }

        /* 弹道 */
        for (const p of battle.projectiles) {
            const dx = p.x - p.startX, dy = p.y - p.startY;
            const length = Math.hypot(dx, dy);
            if (length > 0) {
                const angle = Math.atan2(dy, dx);
                const arrowLen = cs * 0.25;
                // shaft
                ctx.strokeStyle = p.color;
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(p.startX, p.startY);
                ctx.lineTo(p.x, p.y);
                ctx.stroke();
                // arrowhead
                ctx.fillStyle = p.color;
                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(p.x - arrowLen * Math.cos(angle - 0.5), p.y - arrowLen * Math.sin(angle - 0.5));
                ctx.lineTo(p.x - arrowLen * Math.cos(angle + 0.5), p.y - arrowLen * Math.sin(angle + 0.5));
                ctx.fill();
            }
        }
    }

    /* 结算 */
    handleEnd() {
        const app = this.app;
        if (app.gameLoopId) { cancelAnimationFrame(app.gameLoopId); app.gameLoopId = null; }
        document.getElementById("btn-start").disabled = true;

        if (app.battle.victory) {
            const rewards = {
                mora: app.battle.goldEarned + Math.floor(Math.random() * 300) + 200,
                exp_books: Math.floor(Math.random() * 3) + 1,
                adventure_exp: 15,
            };
            app.applyRewards(rewards);
            app.updateResourceBar();

            if (!app.gs.stage_progress.completed_stages.includes(app.battleStageId)) {
                app.gs.stage_progress.completed_stages.push(app.battleStageId);
            }
            const nextId = app.battleStageId + 1;
            if (nextId > app.gs.stage_progress.highest_stage_unlocked &&
                TD_MAPS.some(m => m.id === nextId)) {
                app.gs.stage_progress.highest_stage_unlocked = nextId;
            }
            app.saveState();
            app.showModal(`✨ 关卡完成！`, `摩拉:${rewards.mora} 书:${rewards.exp_books}`);
            this.returnToStageSelect();
        } else {
            app.showModal("失败", "生命值归零，请重新挑战！");
            this.returnToStageSelect();
        }
    }
}