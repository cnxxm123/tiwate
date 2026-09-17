// ==================== 地图渲染器 ====================
class MapRenderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext("2d");
        this.battle = null;
        this.cellSize = 66;
    }

    setBattle(battle) {
        this.battle = battle;
        if (battle) {
            this.cellSize = battle.cellSize;
            this._resize();
        }
    }

    _resize() {
        if (!this.battle) return;
        const w = this.battle.width * this.cellSize;
        const h = this.battle.height * this.cellSize;
        this.canvas.width = w;
        this.canvas.height = h;
        this.canvas.style.width = w + "px";
        this.canvas.style.height = h + "px";
    }

    render() {
        if (!this.battle) return;
        const ctx = this.ctx;
        const cs = this.cellSize;
        const w = this.battle.width;
        const h = this.battle.height;
        ctx.clearRect(0, 0, w * cs, h * cs);

        this._drawGround(ctx, w, h, cs);
        this._drawPath(ctx, cs);
        this._drawDecorations(ctx, w, h, cs);
        this._drawBuildings(ctx, cs);
        this._drawEnemies(ctx, cs);
        this._drawEffects(ctx);
    }

    _drawGround(ctx, w, h, cs) {
        // 草地渐变
        const grad = ctx.createLinearGradient(0, 0, 0, h * cs);
        grad.addColorStop(0, "#4a7c3f");
        grad.addColorStop(0.5, "#3d6b35");
        grad.addColorStop(1, "#345a2e");
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, w * cs, h * cs);

        // 网格线
        ctx.strokeStyle = "rgba(0,0,0,0.08)";
        ctx.lineWidth = 0.5;
        for (let x = 0; x <= w; x++) {
            ctx.beginPath();
            ctx.moveTo(x * cs, 0);
            ctx.lineTo(x * cs, h * cs);
            ctx.stroke();
        }
        for (let y = 0; y <= h; y++) {
            ctx.beginPath();
            ctx.moveTo(0, y * cs);
            ctx.lineTo(w * cs, y * cs);
            ctx.stroke();
        }
    }

    _drawPath(ctx, cs) {
        const path = this.battle.path;

        // 路径底色
        ctx.fillStyle = "#b8956a";
        ctx.strokeStyle = "#8b6b4a";
        ctx.lineWidth = cs * 0.85;
        ctx.lineCap = "round";
        ctx.lineJoin = "round";
        ctx.beginPath();
        const first = path[0];
        ctx.moveTo(first[0] * cs + cs / 2, first[1] * cs + cs / 2);
        for (let i = 1; i < path.length; i++) {
            ctx.lineTo(path[i][0] * cs + cs / 2, path[i][1] * cs + cs / 2);
        }
        ctx.stroke();

        // 路径内部纹理
        ctx.strokeStyle = "#c9a87c";
        ctx.lineWidth = cs * 0.65;
        ctx.stroke();

        // 路径中心虚线
        ctx.strokeStyle = "rgba(139,107,74,0.4)";
        ctx.lineWidth = 2;
        ctx.setLineDash([cs * 0.2, cs * 0.3]);
        ctx.stroke();
        ctx.setLineDash([]);

        // 路径边缘深色
        ctx.strokeStyle = "rgba(80,50,20,0.15)";
        ctx.lineWidth = cs * 0.9;
        ctx.stroke();

        // 起点标记
        const [sx, sy] = path[0];
        ctx.fillStyle = "#4ade80";
        ctx.beginPath();
        ctx.arc(sx * cs + cs / 2, sy * cs + cs / 2, cs * 0.3, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "#fff";
        ctx.font = `${Math.floor(cs * 0.35)}px Arial`;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("S", sx * cs + cs / 2, sy * cs + cs / 2);

        // 终点标记
        const [ex, ey] = path[path.length - 1];
        ctx.fillStyle = "#ef4444";
        ctx.beginPath();
        ctx.arc(ex * cs + cs / 2, ey * cs + cs / 2, cs * 0.3, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "#fff";
        ctx.fillText("E", ex * cs + cs / 2, ey * cs + cs / 2);

        // 路径箭头
        for (let i = 0; i < path.length - 1; i++) {
            const [x1, y1] = path[i];
            const [x2, y2] = path[i + 1];
            const mx = (x1 + x2) / 2 * cs + cs / 2;
            const my = (y1 + y2) / 2 * cs + cs / 2;
            const angle = Math.atan2(y2 - y1, x2 - x1);
            ctx.save();
            ctx.translate(mx, my);
            ctx.rotate(angle);
            ctx.fillStyle = "rgba(80,50,20,0.25)";
            ctx.beginPath();
            ctx.moveTo(cs * 0.15, 0);
            ctx.lineTo(-cs * 0.1, -cs * 0.08);
            ctx.lineTo(-cs * 0.1, cs * 0.08);
            ctx.closePath();
            ctx.fill();
            ctx.restore();
        }
    }

    _drawDecorations(ctx, w, h, cs) {
        // 使用确定性种子基于格子坐标
        const pathSet = this.battle.pathSet;

        for (let y = 0; y < h; y++) {
            for (let x = 0; x < w; x++) {
                if (pathSet.has(`${x},${y}`)) continue;
                const seed = (x * 31 + y * 17) % 100;
                const cx = x * cs + cs / 2;
                const cy = y * cs + cs / 2;

                if (seed < 8) { // 花
                    ctx.fillStyle = ["#fbbf24", "#f472b6", "#a78bfa", "#fff"][seed % 4];
                    const r = cs * 0.08;
                    ctx.beginPath();
                    for (let i = 0; i < 5; i++) {
                        const a = (i / 5) * Math.PI * 2;
                        ctx.arc(cx + Math.cos(a) * r, cy + Math.sin(a) * r, r * 0.6, 0, Math.PI * 2);
                        ctx.fill();
                    }
                } else if (seed < 20) { // 草丛
                    ctx.fillStyle = "#3d8b37";
                    for (let i = 0; i < 3; i++) {
                        const ox = (seed * 7 + i * 13) % 7 - 3;
                        const oy = (seed * 11 + i * 19) % 7 - 3;
                        ctx.beginPath();
                        ctx.arc(cx + ox, cy + oy, cs * 0.1, 0, Math.PI * 2);
                        ctx.fill();
                    }
                } else if (seed < 25) { // 石子
                    ctx.fillStyle = "#9ca3af";
                    ctx.beginPath();
                    ctx.arc(cx + (seed % 5 - 2), cy + ((seed * 3) % 5 - 2), cs * 0.06, 0, Math.PI * 2);
                    ctx.fill();
                }
            }
        }
    }

    _drawBuildings(ctx, cs) {
        // 塔
        for (const tower of this.battle.towers) {
            const px = tower.px, py = tower.py;
            const r = cs * 0.4;

            // 底座
            ctx.fillStyle = "#333";
            ctx.fillRect(px - r, py - r, r * 2, r * 2);
            ctx.fillStyle = tower.color;
            ctx.fillRect(px - r + 2, py - r + 2, r * 2 - 4, r * 2 - 4);

            // 图标
            ctx.font = `${Math.floor(cs * 0.4)}px Arial`;
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText(tower.icon, px, py);

            // 范围圈
            if (tower.hp === tower.maxHp) {
                ctx.strokeStyle = "rgba(255,255,255,0.1)";
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.arc(px, py, tower.range * cs, 0, Math.PI * 2);
                ctx.stroke();
            }
        }

        // 陷阱
        for (const trap of this.battle.traps) {
            const px = trap.px, py = trap.py;
            const r = cs * 0.35;

            ctx.fillStyle = trap.color;
            ctx.globalAlpha = 0.7;
            ctx.beginPath();
            ctx.moveTo(px, py - r);
            ctx.lineTo(px + r, py);
            ctx.lineTo(px, py + r);
            ctx.lineTo(px - r, py);
            ctx.closePath();
            ctx.fill();
            ctx.globalAlpha = 1;

            ctx.font = `${Math.floor(cs * 0.3)}px Arial`;
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText(trap.icon, px, py);
        }
    }

    _drawEnemies(ctx, cs) {
        for (const enemy of this.battle.enemies) {
            if (enemy.dead || enemy.reachedEnd) continue;
            const px = enemy.px, py = enemy.py;
            const r = cs * 0.3;

            // 阴影
            ctx.fillStyle = "rgba(0,0,0,0.3)";
            ctx.beginPath();
            ctx.ellipse(px, py + r * 0.7, r * 0.8, r * 0.25, 0, 0, Math.PI * 2);
            ctx.fill();

            // 冻结特效
            if (enemy.frozen) {
                ctx.fillStyle = "rgba(125,211,252,0.3)";
                ctx.beginPath();
                ctx.arc(px, py, r + 3, 0, Math.PI * 2);
                ctx.fill();
            }

            // 身体颜色
            let bodyColor = enemy.color;
            if (enemy.id === "slime_fire") bodyColor = "#e44";
            else if (enemy.id === "slime_water") bodyColor = "#38b";
            ctx.fillStyle = bodyColor;
            ctx.beginPath();
            ctx.arc(px, py, r, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = "#222";
            ctx.lineWidth = 1;
            ctx.stroke();

            // 元素标记
            const activeElem = enemy.getActiveElement();
            if (activeElem && ELEMENTS[activeElem]) {
                ctx.fillStyle = ELEMENTS[activeElem].color;
                ctx.beginPath();
                ctx.arc(px - r * 0.6, py - r * 0.6, cs * 0.08, 0, Math.PI * 2);
                ctx.fill();
            }

            // 生命条
            const barW = r * 1.8;
            const barH = 3;
            const barY = py - r - 6;
            ctx.fillStyle = "#333";
            ctx.fillRect(px - barW / 2, barY, barW, barH);
            const hpRatio = enemy.hp / enemy.maxHp;
            const hpColor = hpRatio > 0.5 ? "#4ade80" : hpRatio > 0.25 ? "#fbbf24" : "#ef4444";
            ctx.fillStyle = hpColor;
            ctx.fillRect(px - barW / 2, barY, barW * hpRatio, barH);
        }
    }

    _drawEffects(ctx) {
        for (const ef of this.battle.effects) {
            const alpha = Math.min(1, ef.timer / 0.3);
            ctx.globalAlpha = alpha;
            ctx.fillStyle = ef.color;
            ctx.font = "bold 14px Arial";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            const yOff = (1.2 - ef.timer) * 30;
            ctx.fillText(ef.text, ef.px, ef.py - yOff);
        }
        ctx.globalAlpha = 1;
    }
}