// ==================== 地图渲染器 ====================
class MapRenderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext("2d");
        this.battle = null;
        this.cellSize = 66;
        this.selectedX = null;   // 当前选中格子 X
        this.selectedY = null;   // 当前选中格子 Y
        this.selectTimer = 0;    // 动画计时器
        // 元素图片缓存
        this.elementImages = {};
        this._loadElementImages();
    }

    _loadElementImages() {
        const elements = ["fire", "water", "thunder", "ice"];
        for (const elem of elements) {
            const img = new Image();
            img.src = `img/${elem}.png`;
            this.elementImages[elem] = img;
        }
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
        this._drawBorder(ctx, w, h, cs);
        this._drawBuildings(ctx, cs);
        this._drawProjectiles(ctx);
        this._drawEnemies(ctx, cs);
        this._drawEffects(ctx);
        this._drawSelection(ctx, cs);
        this._drawAmbientParticles(ctx, w, h, cs);

        // 推进选中动画计时器
        if (this.selectedX !== null) {
            this.selectTimer += 0.016; // ~60fps
        }
    }

    _drawSelection(ctx, cs) {
        if (this.selectedX === null || this.selectedY === null) return;
        // 脉冲动画：正弦波 0→1 循环
        const pulse = (Math.sin(this.selectTimer * 4) + 1) / 2;
        const alpha = 0.25 + pulse * 0.2;
        const borderAlpha = 0.5 + pulse * 0.5;

        const x = this.selectedX * cs;
        const y = this.selectedY * cs;

        // 发光填充
        ctx.fillStyle = `rgba(255,255,255,${alpha})`;
        ctx.fillRect(x + 1, y + 1, cs - 2, cs - 2);

        // 脉冲金色边框
        ctx.strokeStyle = `rgba(255,215,0,${borderAlpha})`;
        ctx.lineWidth = 2;
        ctx.strokeRect(x + 1, y + 1, cs - 2, cs - 2);

        // 四角高亮标记
        const corner = 6;
        ctx.strokeStyle = `rgba(255,255,255,${borderAlpha})`;
        ctx.lineWidth = 2;
        ctx.beginPath(); ctx.moveTo(x + 2, y + 2 + corner); ctx.lineTo(x + 2, y + 2); ctx.lineTo(x + 2 + corner, y + 2); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(x + cs - 2 - corner, y + 2); ctx.lineTo(x + cs - 2, y + 2); ctx.lineTo(x + cs - 2, y + 2 + corner); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(x + 2, y + cs - 2 - corner); ctx.lineTo(x + 2, y + cs - 2); ctx.lineTo(x + 2 + corner, y + cs - 2); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(x + cs - 2 - corner, y + cs - 2); ctx.lineTo(x + cs - 2, y + cs - 2); ctx.lineTo(x + cs - 2, y + cs - 2 - corner); ctx.stroke();
    }

    selectCell(gx, gy) {
        this.selectedX = gx;
        this.selectedY = gy;
        this.selectTimer = 0;
    }

    clearSelection() {
        this.selectedX = null;
        this.selectedY = null;
        this.selectTimer = 0;
    }

    _drawGround(ctx, w, h, cs) {
        const theme = this.battle.mapTheme || "mondstadt";
        const totalW = w * cs;
        const totalH = h * cs;

        // ===== 主背景渐变 =====
        if (theme === "mondstadt") {
            // 蒙德：翠绿草原，天空渐亮
            const grad = ctx.createLinearGradient(0, 0, 0, totalH);
            grad.addColorStop(0, "#7ab648");
            grad.addColorStop(0.3, "#5d9a3a");
            grad.addColorStop(0.7, "#4a8530");
            grad.addColorStop(1, "#3d6e28");
            ctx.fillStyle = grad;
        } else {
            // 璃月：金黄大地，暖色调
            const grad = ctx.createLinearGradient(0, 0, 0, totalH);
            grad.addColorStop(0, "#c4a65a");
            grad.addColorStop(0.3, "#b8954a");
            grad.addColorStop(0.7, "#a08040");
            grad.addColorStop(1, "#8b7030");
            ctx.fillStyle = grad;
        }
        ctx.fillRect(0, 0, totalW, totalH);

        // ===== 地形纹理斑块（模拟草地/沙地的不规则纹理）=====
        const textureColors = theme === "mondstadt"
            ? ["rgba(100,180,60,0.12)", "rgba(60,140,40,0.10)", "rgba(120,200,70,0.08)"]
            : ["rgba(200,170,90,0.12)", "rgba(180,150,70,0.10)", "rgba(220,190,100,0.08)"];
        for (let i = 0; i < w * h * 0.4; i++) {
            const tx = ((i * 137 + 53) % totalW);
            const ty = ((i * 251 + 97) % totalH);
            const tr = ((i * 73 + 29) % 25) + 10;
            ctx.fillStyle = textureColors[i % 3];
            ctx.beginPath();
            ctx.arc(tx, ty, tr, 0, Math.PI * 2);
            ctx.fill();
        }

        // ===== 细网格线（半透明）=====
        ctx.strokeStyle = theme === "mondstadt"
            ? "rgba(0,0,0,0.06)"
            : "rgba(0,0,0,0.08)";
        ctx.lineWidth = 0.5;
        for (let x = 0; x <= w; x++) {
            ctx.beginPath();
            ctx.moveTo(x * cs, 0);
            ctx.lineTo(x * cs, totalH);
            ctx.stroke();
        }
        for (let y = 0; y <= h; y++) {
            ctx.beginPath();
            ctx.moveTo(0, y * cs);
            ctx.lineTo(totalW, y * cs);
            ctx.stroke();
        }
    }

    _drawPath(ctx, cs) {
        const path = this.battle.path;
        const theme = this.battle.mapTheme || "mondstadt";

        // ===== 路径阴影/草地衬边 =====
        ctx.strokeStyle = "rgba(0,0,0,0.18)";
        ctx.lineWidth = cs * 0.92;
        ctx.lineCap = "round";
        ctx.lineJoin = "round";
        ctx.beginPath();
        ctx.moveTo(path[0][0] * cs + cs / 2, path[0][1] * cs + cs / 2);
        for (let i = 1; i < path.length; i++) {
            ctx.lineTo(path[i][0] * cs + cs / 2, path[i][1] * cs + cs / 2);
        }
        ctx.stroke();

        // ===== 石板主路面 =====
        const pathColors = theme === "mondstadt"
            ? ["#b8956a", "#c4a070", "#b09060", "#c8a875"]
            : ["#c4a870", "#d4b878", "#c0a068", "#d0b470"];
        for (let i = 0; i < path.length; i++) {
            const [gx, gy] = path[i];
            const cx = gx * cs + cs / 2;
            const cy = gy * cs + cs / 2;
            const tr = cs * 0.38;

            // 石板主体（略不规则的圆角矩形）
            ctx.fillStyle = pathColors[i % 4];
            ctx.beginPath();
            ctx.roundRect(cx - tr, cy - tr, tr * 2, tr * 2, 3);
            ctx.fill();
            // 石板边框
            ctx.strokeStyle = "rgba(80,50,20,0.3)";
            ctx.lineWidth = 1;
            ctx.stroke();

            // 石板纹理线
            if (i % 3 !== 0) {
                ctx.strokeStyle = "rgba(80,50,20,0.12)";
                ctx.lineWidth = 0.8;
                ctx.beginPath();
                if (i % 3 === 1) {
                    ctx.moveTo(cx - tr + 2, cy); ctx.lineTo(cx + tr - 2, cy);
                } else {
                    ctx.moveTo(cx, cy - tr + 2); ctx.lineTo(cx, cy + tr - 2);
                }
                ctx.stroke();
            }
        }

        // ===== 路径边缘石条（两侧小石子修饰）=====
        ctx.strokeStyle = "rgba(100,70,40,0.2)";
        ctx.lineWidth = cs * 0.88;
        ctx.beginPath();
        ctx.moveTo(path[0][0] * cs + cs / 2, path[0][1] * cs + cs / 2);
        for (let i = 1; i < path.length; i++) {
            ctx.lineTo(path[i][0] * cs + cs / 2, path[i][1] * cs + cs / 2);
        }
        ctx.stroke();

        // ===== 起点：翠绿传送门 =====
        {
            const [sx, sy] = path[0];
            const scx = sx * cs + cs / 2;
            const scy = sy * cs + cs / 2;
            const sr = cs * 0.32;
            // 外环发光
            const grad = ctx.createRadialGradient(scx, scy, sr * 0.3, scx, scy, sr * 1.1);
            grad.addColorStop(0, "rgba(74,222,128,0.5)");
            grad.addColorStop(0.6, "rgba(74,222,128,0.15)");
            grad.addColorStop(1, "rgba(74,222,128,0)");
            ctx.fillStyle = grad;
            ctx.beginPath(); ctx.arc(scx, scy, sr * 1.1, 0, Math.PI * 2); ctx.fill();
            // 内圆
            ctx.fillStyle = "#4ade80";
            ctx.beginPath(); ctx.arc(scx, scy, sr, 0, Math.PI * 2); ctx.fill();
            ctx.strokeStyle = "#fff"; ctx.lineWidth = 2;
            ctx.stroke();
            // 文字
            ctx.fillStyle = "#fff";
            ctx.font = `bold ${Math.floor(cs * 0.35)}px Arial`;
            ctx.textAlign = "center"; ctx.textBaseline = "middle";
            ctx.fillText("S", scx, scy);
        }

        // ===== 终点：红色符文门 =====
        {
            const [ex, ey] = path[path.length - 1];
            const ecx = ex * cs + cs / 2;
            const ecy = ey * cs + cs / 2;
            const er = cs * 0.32;
            // 外环发光
            const grad = ctx.createRadialGradient(ecx, ecy, er * 0.3, ecx, ecy, er * 1.1);
            grad.addColorStop(0, "rgba(239,68,68,0.5)");
            grad.addColorStop(0.6, "rgba(239,68,68,0.15)");
            grad.addColorStop(1, "rgba(239,68,68,0)");
            ctx.fillStyle = grad;
            ctx.beginPath(); ctx.arc(ecx, ecy, er * 1.1, 0, Math.PI * 2); ctx.fill();
            // 内圆
            ctx.fillStyle = "#ef4444";
            ctx.beginPath(); ctx.arc(ecx, ecy, er, 0, Math.PI * 2); ctx.fill();
            ctx.strokeStyle = "#fff"; ctx.lineWidth = 2;
            ctx.stroke();
            // 文字
            ctx.fillStyle = "#fff";
            ctx.font = `bold ${Math.floor(cs * 0.35)}px Arial`;
            ctx.textAlign = "center"; ctx.textBaseline = "middle";
            ctx.fillText("E", ecx, ecy);
        }

        // ===== 路径方向标记（小三角箭头）=====
        for (let i = 0; i < path.length - 1; i++) {
            const [x1, y1] = path[i];
            const [x2, y2] = path[i + 1];
            const mx = (x1 + x2) / 2 * cs + cs / 2;
            const my = (y1 + y2) / 2 * cs + cs / 2;
            const angle = Math.atan2(y2 - y1, x2 - x1);
            ctx.save();
            ctx.translate(mx, my);
            ctx.rotate(angle);
            ctx.fillStyle = "rgba(255,255,255,0.25)";
            ctx.beginPath();
            ctx.moveTo(cs * 0.18, 0);
            ctx.lineTo(-cs * 0.12, -cs * 0.07);
            ctx.lineTo(-cs * 0.12, cs * 0.07);
            ctx.closePath();
            ctx.fill();
            ctx.restore();
        }
    }

    _drawDecorations(ctx, w, h, cs) {
        const pathSet = this.battle.pathSet;
        const theme = this.battle.mapTheme || "mondstadt";

        for (let y = 0; y < h; y++) {
            for (let x = 0; x < w; x++) {
                if (pathSet.has(`${x},${y}`)) continue;
                const seed = (x * 31 + y * 17) % 100;
                const cx = x * cs + cs / 2;
                const cy = y * cs + cs / 2;

                if (theme === "mondstadt") {
                    // ====== 蒙德装饰 ======
                    if (seed < 6) {
                        // 塞西莉亚花（白色五瓣花）
                        this._drawFlower(ctx, cx, cy, cs * 0.12, "#fff", "#fef3c7");
                    } else if (seed < 10) {
                        // 风车菊（橙色小花）
                        this._drawFlower(ctx, cx, cy, cs * 0.09, "#fb923c", "#fed7aa");
                    } else if (seed < 14) {
                        // 嘟嘟莲（蓝色小花）
                        this._drawFlower(ctx, cx, cy, cs * 0.1, "#60a5fa", "#bfdbfe");
                    } else if (seed < 22) {
                        // 灌木丛（多层绿圆）
                        this._drawBush(ctx, cx, cy, cs * 0.25, "#3d8b37");
                    } else if (seed < 27) {
                        // 小树
                        this._drawSmallTree(ctx, cx, cy, cs * 0.4);
                    } else if (seed < 30) {
                        // 岩石
                        this._drawRock(ctx, cx, cy, cs * 0.18, "#9ca3af");
                    } else if (seed < 35) {
                        // 草簇
                        this._drawGrassTuft(ctx, cx, cy, cs * 0.12);
                    }
                } else {
                    // ====== 璃月装饰 ======
                    if (seed < 6) {
                        // 琉璃百合（粉色花）
                        this._drawFlower(ctx, cx, cy, cs * 0.11, "#f472b6", "#fce7f3");
                    } else if (seed < 10) {
                        // 霓裳花（红色）
                        this._drawFlower(ctx, cx, cy, cs * 0.1, "#ef4444", "#fee2e2");
                    } else if (seed < 16) {
                        // 灌木丛（深绿偏金）
                        this._drawBush(ctx, cx, cy, cs * 0.22, "#6b8e3a");
                    } else if (seed < 22) {
                        // 岩石（偏黄暖色）
                        this._drawRock(ctx, cx, cy, cs * 0.2, "#c4a870");
                    } else if (seed < 28) {
                        // 石笋
                        this._drawStalagmite(ctx, cx, cy, cs * 0.18);
                    } else if (seed < 33) {
                        // 小树（偏黄）
                        this._drawSmallTree(ctx, cx, cy, cs * 0.35, true);
                    } else if (seed < 37) {
                        // 草簇（枯黄色）
                        this._drawGrassTuft(ctx, cx, cy, cs * 0.1, "#b8954a");
                    }
                }
            }
        }
    }

    // 花（多层花瓣）
    _drawFlower(ctx, cx, cy, r, petalColor, centerColor) {
        // 花瓣
        ctx.fillStyle = petalColor;
        for (let i = 0; i < 5; i++) {
            const a = (i / 5) * Math.PI * 2 - Math.PI / 2;
            ctx.beginPath();
            ctx.arc(cx + Math.cos(a) * r * 0.6, cy + Math.sin(a) * r * 0.6, r * 0.5, 0, Math.PI * 2);
            ctx.fill();
        }
        // 花蕊
        ctx.fillStyle = centerColor;
        ctx.beginPath();
        ctx.arc(cx, cy, r * 0.35, 0, Math.PI * 2);
        ctx.fill();
        // 花茎
        ctx.strokeStyle = "#4a7c3f"; ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(cx, cy + r * 0.5);
        ctx.lineTo(cx, cy + r * 1.2);
        ctx.stroke();
    }

    // 灌木丛
    _drawBush(ctx, cx, cy, r, color) {
        const dk = (p) => {
            const num = parseInt(color.replace("#", ""), 16);
            const rr = Math.max(0, (num >> 16) - Math.floor(255 * p));
            const gg = Math.max(0, ((num >> 8) & 0xff) - Math.floor(255 * p));
            const bb = Math.max(0, (num & 0xff) - Math.floor(255 * p));
            return `rgb(${rr},${gg},${bb})`;
        };
        // 主体圆簇
        for (let i = 0; i < 4; i++) {
            const ox = (i % 2 === 0 ? -1 : 1) * r * 0.3;
            const oy = (i < 2 ? -1 : 1) * r * 0.2;
            ctx.fillStyle = i === 0 ? color : dk(0.1);
            ctx.beginPath();
            ctx.arc(cx + ox, cy + oy, r * 0.55, 0, Math.PI * 2);
            ctx.fill();
        }
        // 高光点
        ctx.fillStyle = "rgba(255,255,255,0.25)";
        ctx.beginPath();
        ctx.arc(cx - r * 0.1, cy - r * 0.2, r * 0.15, 0, Math.PI * 2);
        ctx.fill();
    }

    // 小树
    _drawSmallTree(ctx, cx, cy, r, autumn = false) {
        // 树干
        ctx.fillStyle = "#8b6914";
        ctx.fillRect(cx - r * 0.08, cy, r * 0.16, r * 0.6);
        // 树冠（三层圆）
        const leafColors = autumn
            ? ["#d4a020", "#c89030", "#b88040"]
            : ["#4ade80", "#22c55e", "#16a34a"];
        for (let i = 0; i < 3; i++) {
            ctx.fillStyle = leafColors[i];
            ctx.beginPath();
            ctx.arc(cx, cy - r * 0.1 - i * r * 0.25, r * (0.5 - i * 0.1), 0, Math.PI * 2);
            ctx.fill();
        }
    }

    // 岩石
    _drawRock(ctx, cx, cy, r, color) {
        const dk = (p) => {
            const num = parseInt(color.replace("#", ""), 16);
            const rr = Math.max(0, (num >> 16) - Math.floor(255 * p));
            const gg = Math.max(0, ((num >> 8) & 0xff) - Math.floor(255 * p));
            const bb = Math.max(0, (num & 0xff) - Math.floor(255 * p));
            return `rgb(${rr},${gg},${bb})`;
        };
        ctx.fillStyle = dk(0.15);
        ctx.beginPath();
        ctx.ellipse(cx, cy, r, r * 0.7, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = dk(0.3); ctx.lineWidth = 1;
        ctx.stroke();
        // 高光
        ctx.fillStyle = "rgba(255,255,255,0.2)";
        ctx.beginPath();
        ctx.ellipse(cx - r * 0.2, cy - r * 0.15, r * 0.35, r * 0.2, -0.3, 0, Math.PI * 2);
        ctx.fill();
    }

    // 石笋（璃月特有）
    _drawStalagmite(ctx, cx, cy, r) {
        ctx.fillStyle = "#c4a870";
        ctx.beginPath();
        ctx.moveTo(cx - r * 0.4, cy + r * 0.5);
        ctx.lineTo(cx - r * 0.25, cy);
        ctx.lineTo(cx, cy - r * 0.8);
        ctx.lineTo(cx + r * 0.3, cy - r * 0.1);
        ctx.lineTo(cx + r * 0.35, cy + r * 0.3);
        ctx.closePath();
        ctx.fill();
        ctx.strokeStyle = "rgba(0,0,0,0.15)"; ctx.lineWidth = 1;
        ctx.stroke();
    }

    // 草簇
    _drawGrassTuft(ctx, cx, cy, r, color = "#4ade80") {
        ctx.strokeStyle = color; ctx.lineWidth = 1.2;
        ctx.lineCap = "round";
        for (let i = 0; i < 5; i++) {
            const a = (i / 5) * Math.PI * 0.6 - Math.PI * 0.3 - Math.PI / 2;
            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.lineTo(cx + Math.cos(a) * r, cy + Math.sin(a) * r);
            ctx.stroke();
        }
    }

    // ===== 地图装饰边框 =====
    _drawBorder(ctx, w, h, cs) {
        const theme = this.battle.mapTheme || "mondstadt";
        const totalW = w * cs;
        const totalH = h * cs;
        const b = 5;  // 边框厚度

        // 外层暗框
        ctx.strokeStyle = "rgba(0,0,0,0.3)";
        ctx.lineWidth = b;
        ctx.strokeRect(b / 2, b / 2, totalW - b, totalH - b);

        // 内层金色/主题色细框
        const borderColor = theme === "mondstadt"
            ? "rgba(180,200,140,0.5)"
            : "rgba(220,190,130,0.5)";
        ctx.strokeStyle = borderColor;
        ctx.lineWidth = 1.5;
        ctx.strokeRect(b + 2, b + 2, totalW - b * 2 - 4, totalH - b * 2 - 4);

        // 四角装饰（小菱形标记）
        ctx.fillStyle = theme === "mondstadt"
            ? "rgba(180,200,120,0.6)"
            : "rgba(220,190,120,0.6)";
        const corners = [
            [b + 3, b + 3], [totalW - b - 3, b + 3],
            [b + 3, totalH - b - 3], [totalW - b - 3, totalH - b - 3]
        ];
        for (const [cx, cy] of corners) {
            ctx.beginPath();
            ctx.moveTo(cx - 4, cy); ctx.lineTo(cx, cy - 4);
            ctx.lineTo(cx + 4, cy); ctx.lineTo(cx, cy + 4);
            ctx.closePath();
            ctx.fill();
        }
    }

    // ===== 环境粒子（浮动光点/花瓣）=====
    _drawAmbientParticles(ctx, w, h, cs) {
        const theme = this.battle.mapTheme || "mondstadt";
        const t = Date.now() / 1000;
        const totalW = w * cs;
        const totalH = h * cs;

        // 飘浮光点（萤火虫/元素微粒）
        const particleCount = theme === "mondstadt" ? 6 : 4;
        for (let i = 0; i < particleCount; i++) {
            const px = ((i * 173 + 71) % totalW) + Math.sin(t * 0.7 + i * 2.1) * 30;
            const py = ((i * 257 + 43) % totalH) + Math.cos(t * 0.5 + i * 1.7) * 25;
            const alpha = 0.3 + Math.sin(t * 2 + i * 1.5) * 0.25;

            if (theme === "mondstadt") {
                // 绿色/金色萤火虫
                ctx.fillStyle = `rgba(180,255,100,${alpha})`;
            } else {
                // 金色暖光
                ctx.fillStyle = `rgba(255,220,150,${alpha})`;
            }
            const pr = 2 + Math.sin(t * 3 + i) * 1;
            ctx.beginPath();
            ctx.arc(px, py, pr, 0, Math.PI * 2);
            ctx.fill();

            // 光晕
            ctx.fillStyle = theme === "mondstadt"
                ? `rgba(200,255,140,${alpha * 0.3})`
                : `rgba(255,230,170,${alpha * 0.3})`;
            ctx.beginPath();
            ctx.arc(px, py, pr * 2.5, 0, Math.PI * 2);
            ctx.fill();
        }

        // 飘落花瓣（仅蒙德）
        if (theme === "mondstadt") {
            for (let i = 0; i < 3; i++) {
                const px = ((i * 211 + 53) % totalW) + Math.cos(t * 0.3 + i * 1.3) * 50;
                const py = ((t * 15 + i * 97) % (totalH + 40)) - 20;
                ctx.fillStyle = "rgba(255,255,255,0.35)";
                ctx.beginPath();
                ctx.ellipse(px, py, 3, 1.5, t * 0.5 + i, 0, Math.PI * 2);
                ctx.fill();
            }
        }
    }

    _drawBuildings(ctx, cs) {
        // ====== 塔 ======
        for (const tower of this.battle.towers) {
            const px = tower.px, py = tower.py;
            const r = cs * 0.4;           // 塔半径
            const angle = tower.angle;     // 当前朝向（弧度）
            const recoil = tower.recoil;   // 后坐力 0~1
            const tColor = tower.color;
            const dk = (pct) => this._darken(tColor, pct);
            const lt = (pct) => this._lighten(tColor, pct);

            // ---- 地面阴影 ----
            ctx.fillStyle = "rgba(0,0,0,0.3)";
            ctx.beginPath();
            ctx.ellipse(px, py + r * 0.7, r * 0.8, r * 0.2, 0, 0, Math.PI * 2);
            ctx.fill();

            // ---- 底座：三层六角石台（从下到上逐步变小变亮）----
            for (let layer = 0; layer < 3; layer++) {
                const baseR = r * (0.9 - layer * 0.12);
                const baseY = py + r * (0.5 + layer * 0.12);
                const shade = 0.18 + layer * 0.06;
                this._drawHex(ctx, px, baseY, baseR, `rgba(60,55,75,${0.9 - shade})`, "rgba(100,95,115,0.6)");
            }

            // ---- 塔身：梯形（底部宽顶部窄，3D 渐变）----
            const bodyTopY = py - r * 0.75;
            const bodyBotY = py + r * 0.2;
            const bodyTopW = r * 0.45;
            const bodyBotW = r * 0.55;

            // 身体高光渐变
            const bodyGrad = ctx.createLinearGradient(px - bodyBotW, 0, px + bodyBotW, 0);
            bodyGrad.addColorStop(0, dk(0.25));
            bodyGrad.addColorStop(0.3, lt(0.1));
            bodyGrad.addColorStop(0.5, tColor);
            bodyGrad.addColorStop(0.7, lt(0.1));
            bodyGrad.addColorStop(1, dk(0.35));

            ctx.fillStyle = bodyGrad;
            ctx.beginPath();
            ctx.moveTo(px - bodyBotW, bodyBotY);
            ctx.lineTo(px + bodyBotW, bodyBotY);
            ctx.lineTo(px + bodyTopW, bodyTopY);
            ctx.lineTo(px - bodyTopW, bodyTopY);
            ctx.closePath();
            ctx.fill();
            ctx.strokeStyle = dk(0.5); ctx.lineWidth = 1.5;
            ctx.stroke();

            // ---- 身体横向条纹（装饰）----
            ctx.strokeStyle = lt(0.2);
            ctx.lineWidth = 1;
            for (let s = 0; s < 2; s++) {
                const sy = bodyBotY - (bodyBotY - bodyTopY) * (0.3 + s * 0.35);
                const sw = bodyBotW - (bodyBotW - bodyTopW) * (0.3 + s * 0.35);
                ctx.beginPath();
                ctx.moveTo(px - sw, sy);
                ctx.lineTo(px + sw, sy);
                ctx.stroke();
            }

            // ---- 塔顶装饰（三角屋顶）----
            ctx.fillStyle = lt(0.2);
            ctx.beginPath();
            ctx.moveTo(px, py - r * 1.05);
            ctx.lineTo(px - r * 0.3, bodyTopY + 2);
            ctx.lineTo(px + r * 0.3, bodyTopY + 2);
            ctx.closePath();
            ctx.fill();
            ctx.strokeStyle = dk(0.4); ctx.lineWidth = 1;
            ctx.stroke();

            // ---- 炮管（旋转朝向目标 + 后坐力）----
            const barrelLen = r * 0.85 + recoil * r * 0.15; // 后坐力时炮管缩短
            const barrelW = r * 0.1;
            const barrelBaseY = py - r * 0.25;

            // 计算炮管旋转后的坐标
            const cosA = Math.cos(angle);
            const sinA = Math.sin(angle);
            const bTipX = px + cosA * barrelLen - recoil * cosA * r * 0.25;
            const bTipY = barrelBaseY + sinA * barrelLen - recoil * sinA * r * 0.25;

            // 炮管阴影
            ctx.save();
            ctx.strokeStyle = dk(0.5); ctx.lineWidth = barrelW * 2 + 2;
            ctx.lineCap = "round";
            ctx.beginPath();
            ctx.moveTo(px - cosA * 2, barrelBaseY - sinA * 2);
            ctx.lineTo(bTipX - cosA * 2, bTipY - sinA * 2);
            ctx.stroke();
            ctx.restore();

            // 炮管主体（渐变色）
            const barrelGrad = ctx.createLinearGradient(px, barrelBaseY, bTipX, bTipY);
            barrelGrad.addColorStop(0, dk(0.1));
            barrelGrad.addColorStop(1, lt(0.1));
            ctx.strokeStyle = barrelGrad;
            ctx.lineWidth = barrelW * 2;
            ctx.lineCap = "round";
            ctx.beginPath();
            ctx.moveTo(px, barrelBaseY);
            ctx.lineTo(bTipX, bTipY);
            ctx.stroke();

            // 炮口高光
            ctx.fillStyle = lt(0.3);
            ctx.beginPath();
            ctx.arc(bTipX, bTipY, barrelW * 1.1, 0, Math.PI * 2);
            ctx.fill();

            // 攻击闪光（后坐力时）
            if (recoil > 0.3) {
                const flashAlpha = (recoil - 0.3) * 1.4;
                ctx.fillStyle = `rgba(255,255,200,${flashAlpha})`;
                ctx.beginPath();
                ctx.arc(bTipX, bTipY, r * 0.25, 0, Math.PI * 2);
                ctx.fill();
            }

            // ---- 攻击冷却环 ----
            const cdRatio = tower.attackCooldown / Math.max(tower.attackCooldown, 1 / tower.atkSpeed);
            const cdRatioClamped = Math.max(0, Math.min(1, cdRatio));
            const ringR = r * 0.32;
            const ringY = py - r * 0.35;
            if (cdRatioClamped > 0) {
                ctx.fillStyle = "rgba(0,0,0,0.35)";
                ctx.beginPath();
                ctx.arc(px, ringY, ringR, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * cdRatioClamped, false);
                ctx.lineTo(px, ringY);
                ctx.closePath();
                ctx.fill();
            }
            ctx.strokeStyle = cdRatioClamped > 0 ? "rgba(255,255,255,0.4)" : "#0f0";
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(px, ringY, ringR, 0, Math.PI * 2);
            ctx.stroke();

            // ---- 就绪脉冲 ----
            if (cdRatioClamped <= 0) {
                const pulseAlpha = 0.08 + Math.sin(Date.now() / 500) * 0.04;
                ctx.fillStyle = `rgba(255,255,255,${pulseAlpha})`;
                ctx.beginPath(); ctx.arc(px, ringY, ringR, 0, Math.PI * 2); ctx.fill();
            }

            // ---- 图标 ----
            ctx.font = `bold ${Math.floor(cs * 0.3)}px Arial`;
            ctx.fillStyle = "#fff";
            ctx.textAlign = "center"; ctx.textBaseline = "middle";
            ctx.fillText(tower.icon, px, ringY);

            // ---- 射程圈 ----
            if (tower.shield <= 0) {
                ctx.strokeStyle = "rgba(255,255,255,0.07)";
                ctx.lineWidth = 1;
                ctx.setLineDash([4, 8]);
                ctx.beginPath();
                ctx.arc(px, py, tower.range * cs, 0, Math.PI * 2);
                ctx.stroke();
                ctx.setLineDash([]);
            }

            // ---- 护盾指示器 ----
            if (tower.shield > 0) {
                ctx.strokeStyle = "#fbbf24"; ctx.lineWidth = 3;
                ctx.beginPath(); ctx.arc(px, py, r + 8, 0, Math.PI * 2); ctx.stroke();
                ctx.fillStyle = "rgba(251,191,36,0.15)";
                ctx.beginPath(); ctx.arc(px, py, r + 8, 0, Math.PI * 2); ctx.fill();
                ctx.font = `${Math.floor(cs * 0.17)}px Arial`;
                ctx.fillStyle = "#fbbf24"; ctx.textAlign = "center"; ctx.textBaseline = "bottom";
                ctx.fillText(`🛡${tower.shield}`, px, py - r * 1.1);
            }
        }

        // ====== 陷阱 ======
        for (const trap of this.battle.traps) {
            const px = trap.px, py = trap.py;
            const r = cs * 0.36;
            const eff = trap.effect;
            const color = trap.color;
            const dk = (p) => this._darken(color, p);
            const lt = (p) => this._lighten(color, p);
            const bob = Math.sin(trap.bobPhase) * 2;  // 浮动偏移
            const flash = trap.triggerFlash;
            const ready = trap.cooldownRemaining <= 0;

            // ---- 地面阴影（椭圆）----
            ctx.fillStyle = "rgba(0,0,0,0.35)";
            ctx.beginPath();
            ctx.ellipse(px, py + r * 0.55, r * 0.85, r * 0.2, 0, 0, Math.PI * 2);
            ctx.fill();

            // ---- 3D 底座平台（双层六角石台）----
            for (let layer = 0; layer < 2; layer++) {
                const baseR = r * (0.85 - layer * 0.15);
                const baseY = py + r * (0.3 + layer * 0.13);
                this._drawHex(ctx, px, baseY, baseR,
                    `rgba(55,50,70,${0.85 - layer * 0.1})`,
                    "rgba(90,85,105,0.5)");
            }

            // ---- 陷阱主体（浮动）----
            const bodyY = py + bob;
            const bodyR = r * 0.7;

            // 主体阴影
            ctx.fillStyle = "rgba(0,0,0,0.25)";
            ctx.beginPath();
            ctx.ellipse(px + 2, bodyY + r * 0.2, bodyR * 0.9, bodyR * 0.15, 0, 0, Math.PI * 2);
            ctx.fill();

            // 根据类型绘制 3D 陷阱（有图片的元素用图片替换）
            const elemImg = this.elementImages[trap.element];
            if (elemImg && elemImg.complete && elemImg.naturalWidth > 0) {
                // 用原神元素图标替换陷阱主体
                const imgSize = bodyR * 2;
                ctx.save();
                // 圆形裁剪
                ctx.beginPath();
                ctx.arc(px, bodyY, bodyR, 0, Math.PI * 2);
                ctx.clip();
                ctx.drawImage(elemImg, px - imgSize / 2, bodyY - imgSize / 2, imgSize, imgSize);
                ctx.restore();
                // 圆形边框
                ctx.strokeStyle = "rgba(255,255,255,0.3)"; ctx.lineWidth = 1.5;
                ctx.beginPath(); ctx.arc(px, bodyY, bodyR, 0, Math.PI * 2); ctx.stroke();
            } else {
                // 没有图片的元素保持绘制
                switch (eff?.type) {
                    case "explode": this._drawTrap3D_Explode(ctx, px, bodyY, bodyR, color); break;
                    case "freeze":  this._drawTrap3D_Freeze(ctx, px, bodyY, bodyR, color); break;
                    case "stun":    this._drawTrap3D_Stun(ctx, px, bodyY, bodyR, color); break;
                    case "push":    this._drawTrap3D_Push(ctx, px, bodyY, bodyR, color); break;
                    case "root":    this._drawTrap3D_Root(ctx, px, bodyY, bodyR, color); break;
                    case "slow":
                    default:         this._drawTrap3D_Slow(ctx, px, bodyY, bodyR, color); break;
                }
            }

            // ---- 触发闪光 ----
            if (flash > 0) {
                const fAlpha = flash * 0.7;
                ctx.fillStyle = `rgba(255,255,200,${fAlpha})`;
                ctx.beginPath(); ctx.arc(px, bodyY, bodyR * 1.3, 0, Math.PI * 2); ctx.fill();
                // 冲击波环
                const ringR = bodyR * (1.2 + (1 - flash) * 0.6);
                ctx.strokeStyle = `rgba(255,255,255,${flash * 0.6})`;
                ctx.lineWidth = 2;
                ctx.beginPath(); ctx.arc(px, bodyY, ringR, 0, Math.PI * 2); ctx.stroke();
            }

            // ---- 图标（有图片的陷阱不显示文字图标）----
            const hasElemImg = this.elementImages[trap.element]
                && this.elementImages[trap.element].complete
                && this.elementImages[trap.element].naturalWidth > 0;
            if (!hasElemImg) {
                ctx.font = `bold ${Math.floor(cs * 0.28)}px Arial`;
                ctx.fillStyle = "#fff";
                ctx.textAlign = "center"; ctx.textBaseline = "middle";
                ctx.fillText(trap.icon, px, bodyY);
            }

            // ---- 冷却环 ----
            const cdRatio = trap.cooldown / Math.max(trap.cooldown, 0.01);
            const cdActual = trap.cooldownRemaining / Math.max(trap.cooldown, 0.01);
            if (!ready) {
                // 灰色扇形遮罩
                ctx.fillStyle = "rgba(0,0,0,0.35)";
                ctx.beginPath();
                ctx.arc(px, bodyY, bodyR * 1.15, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * cdActual, false);
                ctx.lineTo(px, bodyY);
                ctx.closePath(); ctx.fill();
                // 白环
                ctx.strokeStyle = "rgba(255,255,255,0.5)"; ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.arc(px, bodyY, bodyR * 1.15, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * cdActual);
                ctx.stroke();
            }

            // ---- 就绪脉冲 ----
            if (ready) {
                const pulse = Math.sin(Date.now() / 500) * 0.2 + 0.5;
                ctx.strokeStyle = `rgba(255,255,255,${pulse})`;
                ctx.lineWidth = 2;
                ctx.beginPath(); ctx.arc(px, bodyY, bodyR * 1.15, 0, Math.PI * 2); ctx.stroke();
                // 内部光晕
                ctx.fillStyle = `rgba(255,255,255,${0.04 + Math.sin(Date.now() / 500) * 0.02})`;
                ctx.beginPath(); ctx.arc(px, bodyY, bodyR * 1.1, 0, Math.PI * 2); ctx.fill();
            }

            // ---- 转动发光粒子（就绪时）----
            if (ready) {
                const t = Date.now() / 1000;
                ctx.fillStyle = `rgba(255,255,255,0.6)`;
                for (let i = 0; i < 2; i++) {
                    const a = t * 1.5 + i * Math.PI;
                    const dotX = px + Math.cos(a) * bodyR * 1.2;
                    const dotY = bodyY + Math.sin(a) * bodyR * 1.2;
                    ctx.beginPath(); ctx.arc(dotX, dotY, 2, 0, Math.PI * 2); ctx.fill();
                }
            }
        }
    }

    _drawEnemies(ctx, cs) {
        for (const enemy of this.battle.enemies) {
            if (enemy.dead || enemy.reachedEnd) continue;
            const px = enemy.px, py = enemy.py;
            const eid = enemy.id;
            // 根据敌人类型确定大小
            let r, bodyColor;
            if (eid.includes("slime")) { r = cs * 0.35; bodyColor = enemy.color; }
            else if (eid === "hilichurl_fighter") { r = cs * 0.33; bodyColor = enemy.color; }
            else if (eid === "mitachurl") { r = cs * 0.4; bodyColor = enemy.color; }
            else if (eid === "lawachurl") { r = cs * 0.48; bodyColor = enemy.color; }
            else if (eid === "abyss_mage") { r = cs * 0.32; bodyColor = enemy.color; }
            else if (eid === "ruin_guard") { r = cs * 0.44; bodyColor = enemy.color; }
            else { r = cs * 0.3; bodyColor = enemy.color; } // hilichurl 默认

            // ---- 阴影 ----
            ctx.fillStyle = "rgba(0,0,0,0.3)";
            ctx.beginPath();
            ctx.ellipse(px, py + r * 0.6, r * 0.75, r * 0.22, 0, 0, Math.PI * 2);
            ctx.fill();

            // ---- 状态特效 ----
            // 冻结冰晶
            if (enemy.frozen) {
                ctx.fillStyle = "rgba(125,211,252,0.35)";
                ctx.beginPath(); ctx.arc(px, py, r + 5, 0, Math.PI * 2); ctx.fill();
                ctx.strokeStyle = "#7dd3fc"; ctx.lineWidth = 2;
                ctx.beginPath(); ctx.arc(px, py, r + 4, 0, Math.PI * 2); ctx.stroke();
            }
            // 减速
            if (enemy.slowed) {
                ctx.fillStyle = "rgba(59,130,246,0.2)";
                ctx.beginPath(); ctx.arc(px, py, r + 3, 0, Math.PI * 2); ctx.fill();
            }
            // 缠绕
            if (enemy.rooted) {
                ctx.strokeStyle = "#22c55e"; ctx.lineWidth = 2;
                ctx.setLineDash([4, 3]);
                ctx.beginPath(); ctx.arc(px, py, r + 3, 0, Math.PI * 2); ctx.stroke();
                ctx.setLineDash([]);
            }

            // ---- 根据类型绘制不同形状 ----
            if (eid.includes("slime")) {
                this._drawSlime(ctx, px, py, r, bodyColor, cs);
            } else if (eid === "hilichurl" || eid === "hilichurl_fighter") {
                this._drawHilichurl(ctx, px, py, r, bodyColor, cs, eid);
            } else if (eid === "mitachurl") {
                this._drawMitachurl(ctx, px, py, r, bodyColor, cs);
            } else if (eid === "lawachurl") {
                this._drawLawachurl(ctx, px, py, r, bodyColor, cs);
            } else if (eid === "abyss_mage") {
                this._drawAbyssMage(ctx, px, py, r, bodyColor, cs);
            } else if (eid === "ruin_guard") {
                this._drawRuinGuard(ctx, px, py, r, bodyColor, cs);
            }

            // ---- 元素附着标记（元素量环指示器） ----
            const activeElem = enemy.getActiveElement();
            const hasAura = enemy.auraGauge > 0.01;
            if (activeElem && ELEMENTS[activeElem]) {
                const eColor = ELEMENTS[activeElem].color;
                // 元素光环（越亮=元素量越高）
                const gaugeRatio = Math.min(1, (enemy.auraGauge || 0) / ELEMENTAL_GAUGE.STANDARD_U);
                const alpha = 0.2 + gaugeRatio * 0.35;
                ctx.fillStyle = this._hexToRGBA(eColor, alpha);
                ctx.beginPath();
                ctx.arc(px, py, r * 1.15, 0, Math.PI * 2);
                ctx.fill();
                // 元素量环
                ctx.strokeStyle = eColor;
                ctx.lineWidth = 2;
                ctx.globalAlpha = 0.7;
                ctx.beginPath();
                ctx.arc(px, py, r * 1.15, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * gaugeRatio);
                ctx.stroke();
                ctx.globalAlpha = 1;
                // 元素图标
                ctx.font = `${Math.floor(cs * 0.2)}px Arial`;
                ctx.textAlign = "center"; ctx.textBaseline = "bottom";
                ctx.fillText(ELEMENTS[activeElem].icon, px, py - r - 2);
            }

            // ---- 生命条 ----
            const barW = r * 2;
            const barH = Math.max(3, cs * 0.04);
            const barY = py - r - 10;
            ctx.fillStyle = "#222";
            ctx.fillRect(px - barW / 2, barY, barW, barH);
            const hpRatio = enemy.hp / enemy.maxHp;
            const hpColor = hpRatio > 0.5 ? "#4ade80" : hpRatio > 0.25 ? "#fbbf24" : "#ef4444";
            ctx.fillStyle = hpColor;
            ctx.fillRect(px - barW / 2, barY, barW * hpRatio, barH);
        }
    }

    // ===== 史莱姆：Q弹圆形 + 表情 =====
    _drawSlime(ctx, px, py, r, color, cs) {
        // 底部高光
        const grad = ctx.createRadialGradient(px - r * 0.3, py - r * 0.3, r * 0.1, px, py, r);
        grad.addColorStop(0, "#fff");
        grad.addColorStop(0.4, color);
        grad.addColorStop(1, this._darken(color, 0.4));
        ctx.fillStyle = grad;
        ctx.beginPath(); ctx.arc(px, py, r, 0, Math.PI * 2); ctx.fill();
        ctx.strokeStyle = this._darken(color, 0.6); ctx.lineWidth = 1.5;
        ctx.stroke();

        // 眼睛（两个小白圆）
        const eyeR = r * 0.18;
        const eyeY = py - r * 0.15;
        ctx.fillStyle = "#fff";
        ctx.beginPath(); ctx.arc(px - r * 0.28, eyeY, eyeR, 0, Math.PI * 2); ctx.fill();
        ctx.beginPath(); ctx.arc(px + r * 0.28, eyeY, eyeR, 0, Math.PI * 2); ctx.fill();
        // 瞳孔
        ctx.fillStyle = "#111";
        ctx.beginPath(); ctx.arc(px - r * 0.3, eyeY, eyeR * 0.5, 0, Math.PI * 2); ctx.fill();
        ctx.beginPath(); ctx.arc(px + r * 0.26, eyeY, eyeR * 0.5, 0, Math.PI * 2); ctx.fill();

        // 嘴巴
        ctx.strokeStyle = "#111"; ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(px, py + r * 0.15, r * 0.15, 0.1, Math.PI - 0.1);
        ctx.stroke();
    }

    // ===== 丘丘人：人形身体 + 面具脸 =====
    _drawHilichurl(ctx, px, py, r, color, cs, eid) {
        const isFighter = eid === "hilichurl_fighter";
        // 身体（椭圆）
        const bodyH = r * 1.4;
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.ellipse(px, py, r * 0.85, bodyH * 0.7, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = this._darken(color, 0.5); ctx.lineWidth = 1.5;
        ctx.stroke();

        // 头部（上方小圆）
        const headR = r * 0.55;
        ctx.fillStyle = this._darken(color, 0.3);
        ctx.beginPath(); ctx.arc(px, py - bodyH * 0.55, headR, 0, Math.PI * 2); ctx.fill();
        ctx.strokeStyle = this._darken(color, 0.6); ctx.lineWidth = 1;
        ctx.stroke();

        // 面具
        ctx.fillStyle = "#fff";
        ctx.beginPath();
        ctx.ellipse(px, py - bodyH * 0.55, headR * 0.7, headR * 0.65, 0, 0, Math.PI * 2);
        ctx.fill();
        // 面具眼孔
        ctx.fillStyle = "#111";
        ctx.beginPath(); ctx.arc(px - headR * 0.25, py - bodyH * 0.58, headR * 0.15, 0, Math.PI * 2); ctx.fill();
        ctx.beginPath(); ctx.arc(px + headR * 0.25, py - bodyH * 0.58, headR * 0.15, 0, Math.PI * 2); ctx.fill();
        // 面具纹路
        ctx.strokeStyle = "#333"; ctx.lineWidth = 0.8;
        ctx.beginPath();
        ctx.moveTo(px - headR * 0.3, py - bodyH * 0.45);
        ctx.lineTo(px + headR * 0.3, py - bodyH * 0.45);
        ctx.stroke();

        // 战士额外标记：盾牌图案
        if (isFighter) {
            ctx.strokeStyle = "#fff"; ctx.lineWidth = 1.2;
            ctx.beginPath();
            ctx.arc(px, py + bodyH * 0.15, r * 0.25, 0, Math.PI * 2);
            ctx.stroke();
            ctx.fillStyle = "#fff";
            ctx.font = `${Math.floor(cs * 0.16)}px Arial`;
            ctx.textAlign = "center"; ctx.textBaseline = "middle";
            ctx.fillText("🛡", px, py + bodyH * 0.15);
        }
    }

    // ===== 丘丘暴徒：大块头 + 斧头 =====
    _drawMitachurl(ctx, px, py, r, color, cs) {
        // 身体
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.ellipse(px, py, r * 0.9, r * 1.1, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = this._darken(color, 0.5); ctx.lineWidth = 2;
        ctx.stroke();

        // 肩甲
        ctx.fillStyle = "#555";
        ctx.fillRect(px - r * 1.1, py - r * 0.5, r * 0.4, r * 0.3);
        ctx.fillRect(px + r * 0.7, py - r * 0.5, r * 0.4, r * 0.3);

        // 头部
        const headR = r * 0.45;
        ctx.fillStyle = this._darken(color, 0.4);
        ctx.beginPath(); ctx.arc(px, py - r * 0.7, headR, 0, Math.PI * 2); ctx.fill();
        ctx.strokeStyle = this._darken(color, 0.6); ctx.lineWidth = 1.2;
        ctx.stroke();

        // 面具
        ctx.fillStyle = "#eee";
        ctx.beginPath();
        ctx.ellipse(px, py - r * 0.7, headR * 0.7, headR * 0.6, 0, 0, Math.PI * 2);
        ctx.fill();
        // 怒眼
        ctx.fillStyle = "#c00";
        ctx.beginPath(); ctx.arc(px - headR * 0.2, py - r * 0.72, headR * 0.12, 0, Math.PI * 2); ctx.fill();
        ctx.beginPath(); ctx.arc(px + headR * 0.2, py - r * 0.72, headR * 0.12, 0, Math.PI * 2); ctx.fill();

        // 斧头标记
        ctx.fillStyle = "#fff";
        ctx.font = `${Math.floor(cs * 0.22)}px Arial`;
        ctx.textAlign = "center"; ctx.textBaseline = "middle";
        ctx.fillText("🪓", px + r * 0.6, py - r * 0.2);
    }

    // ===== 丘丘王：巨型 + 王冠 + 护甲纹 =====
    _drawLawachurl(ctx, px, py, r, color, cs) {
        // 身体
        const grad = ctx.createRadialGradient(px, py - r * 0.2, r * 0.2, px, py, r);
        grad.addColorStop(0, this._lighten(color, 0.2));
        grad.addColorStop(1, this._darken(color, 0.3));
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.ellipse(px, py, r * 0.9, r * 1.2, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = "#000"; ctx.lineWidth = 2.5;
        ctx.stroke();

        // 护甲条纹
        ctx.strokeStyle = "rgba(255,255,255,0.15)"; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.moveTo(px - r * 0.6, py - r * 0.3); ctx.lineTo(px - r * 0.6, py + r * 0.5); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(px + r * 0.6, py - r * 0.3); ctx.lineTo(px + r * 0.6, py + r * 0.5); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(px - r * 0.7, py); ctx.lineTo(px + r * 0.7, py); ctx.stroke();

        // 头部
        const headR = r * 0.5;
        ctx.fillStyle = this._darken(color, 0.5);
        ctx.beginPath(); ctx.arc(px, py - r * 0.85, headR, 0, Math.PI * 2); ctx.fill();
        ctx.strokeStyle = "#000"; ctx.lineWidth = 1.5;
        ctx.stroke();

        // 怒眼
        ctx.fillStyle = "#f00";
        ctx.beginPath(); ctx.arc(px - headR * 0.22, py - r * 0.88, headR * 0.14, 0, Math.PI * 2); ctx.fill();
        ctx.beginPath(); ctx.arc(px + headR * 0.22, py - r * 0.88, headR * 0.14, 0, Math.PI * 2); ctx.fill();

        // 王冠
        ctx.fillStyle = "#fbbf24";
        ctx.beginPath();
        ctx.moveTo(px - headR, py - r * 1.05);
        ctx.lineTo(px - headR * 0.6, py - r * 1.22);
        ctx.lineTo(px - headR * 0.2, py - r * 1.08);
        ctx.lineTo(px + headR * 0.2, py - r * 1.08);
        ctx.lineTo(px + headR * 0.6, py - r * 1.22);
        ctx.lineTo(px + headR, py - r * 1.05);
        ctx.closePath();
        ctx.fill();
        ctx.strokeStyle = "#b45309"; ctx.lineWidth = 1;
        ctx.stroke();
    }

    // ===== 深渊法师：浮空 + 翅膀 =====
    _drawAbyssMage(ctx, px, py, r, color, cs) {
        // 翅膀
        ctx.fillStyle = "rgba(100,100,200,0.4)";
        ctx.beginPath();
        ctx.moveTo(px - r * 0.5, py);
        ctx.quadraticCurveTo(px - r * 1.2, py - r * 0.5, px - r * 0.7, py - r * 0.3);
        ctx.quadraticCurveTo(px - r * 0.3, py - r * 0.6, px - r * 0.5, py);
        ctx.fill();
        ctx.beginPath();
        ctx.moveTo(px + r * 0.5, py);
        ctx.quadraticCurveTo(px + r * 1.2, py - r * 0.5, px + r * 0.7, py - r * 0.3);
        ctx.quadraticCurveTo(px + r * 0.3, py - r * 0.6, px + r * 0.5, py);
        ctx.fill();

        // 身体
        const grad = ctx.createRadialGradient(px, py - r * 0.2, r * 0.1, px, py, r * 0.75);
        grad.addColorStop(0, "#b8c");
        grad.addColorStop(1, color);
        ctx.fillStyle = grad;
        ctx.beginPath(); ctx.arc(px, py, r * 0.7, 0, Math.PI * 2); ctx.fill();
        ctx.strokeStyle = this._darken(color, 0.5); ctx.lineWidth = 1.2;
        ctx.stroke();

        // 面具
        ctx.fillStyle = "#fff";
        ctx.beginPath(); ctx.arc(px, py, r * 0.35, 0, Math.PI * 2); ctx.fill();
        // 眼睛
        ctx.fillStyle = "#f0f";
        ctx.beginPath(); ctx.arc(px - r * 0.1, py - r * 0.05, r * 0.08, 0, Math.PI * 2); ctx.fill();
        ctx.beginPath(); ctx.arc(px + r * 0.1, py - r * 0.05, r * 0.08, 0, Math.PI * 2); ctx.fill();

        // 魔法光环
        ctx.strokeStyle = "rgba(180,130,255,0.5)"; ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.arc(px, py - r * 0.1, r * 0.55, 0, Math.PI * 2); ctx.stroke();
    }

    // ===== 遗迹守卫：机械风格 =====
    _drawRuinGuard(ctx, px, py, r, color, cs) {
        // 身体（矩形 + 圆形混合）
        ctx.fillStyle = "#8a8a9a";
        ctx.beginPath();
        ctx.roundRect(px - r * 0.7, py - r * 0.8, r * 1.4, r * 1.6, r * 0.2);
        ctx.fill();
        ctx.strokeStyle = "#555"; ctx.lineWidth = 2;
        ctx.stroke();

        // 中心发光核心
        const coreGrad = ctx.createRadialGradient(px, py - r * 0.1, 0, px, py - r * 0.1, r * 0.35);
        coreGrad.addColorStop(0, "#ff0");
        coreGrad.addColorStop(0.5, "#f80");
        coreGrad.addColorStop(1, "rgba(255,136,0,0)");
        ctx.fillStyle = coreGrad;
        ctx.beginPath(); ctx.arc(px, py - r * 0.1, r * 0.35, 0, Math.PI * 2); ctx.fill();

        // 核心白点
        ctx.fillStyle = "#fff";
        ctx.beginPath(); ctx.arc(px, py - r * 0.1, r * 0.12, 0, Math.PI * 2); ctx.fill();

        // 机械纹路
        ctx.strokeStyle = "#666"; ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(px - r * 0.5, py - r * 0.5); ctx.lineTo(px + r * 0.5, py - r * 0.5); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(px - r * 0.4, py + r * 0.3); ctx.lineTo(px + r * 0.4, py + r * 0.3); ctx.stroke();

        // 肩部铆钉
        ctx.fillStyle = "#444";
        [{ dx: -0.65, dy: -0.5 }, { dx: 0.65, dy: -0.5 }, { dx: -0.65, dy: 0.5 }, { dx: 0.65, dy: 0.5 }]
            .forEach(({ dx, dy }) => {
                ctx.beginPath();
                ctx.arc(px + r * dx, py + r * dy, r * 0.1, 0, Math.PI * 2);
                ctx.fill();
            });
    }

    // ---- 颜色辅助 ----
    _darken(hex, amount) {
        const num = parseInt(hex.replace("#", ""), 16);
        const r = Math.max(0, (num >> 16) - Math.floor(255 * amount));
        const g = Math.max(0, ((num >> 8) & 0xff) - Math.floor(255 * amount));
        const b = Math.max(0, (num & 0xff) - Math.floor(255 * amount));
        return `rgb(${r},${g},${b})`;
    }
    _lighten(hex, amount) {
        const num = parseInt(hex.replace("#", ""), 16);
        const r = Math.min(255, (num >> 16) + Math.floor(255 * amount));
        const g = Math.min(255, ((num >> 8) & 0xff) + Math.floor(255 * amount));
        const b = Math.min(255, (num & 0xff) + Math.floor(255 * amount));
        return `rgb(${r},${g},${b})`;
    }
    _hexToRGBA(hex, alpha) {
        const num = parseInt(hex.replace("#", ""), 16);
        const r = (num >> 16) & 0xff;
        const g = (num >> 8) & 0xff;
        const b = num & 0xff;
        return `rgba(${r},${g},${b},${alpha})`;
    }
    _drawHex(ctx, cx, cy, r, fill, stroke) {
        ctx.fillStyle = fill;
        ctx.strokeStyle = stroke; ctx.lineWidth = 1;
        ctx.beginPath();
        for (let i = 0; i < 6; i++) {
            const a = Math.PI / 6 + (Math.PI / 3) * i;
            const x = cx + r * Math.cos(a);
            const y = cy + r * Math.sin(a);
            if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
    }

    // ====== 陷阱 3D 形状绘制 ======

    // 通用：绘制球体/圆球（3D 高光渐变）
    _draw3DSphere(ctx, cx, cy, r, color) {
        const grad = ctx.createRadialGradient(cx - r * 0.3, cy - r * 0.4, r * 0.05, cx, cy, r);
        grad.addColorStop(0, "#fff");
        grad.addColorStop(0.25, this._lighten(color, 0.2));
        grad.addColorStop(0.5, color);
        grad.addColorStop(1, this._darken(color, 0.5));
        ctx.fillStyle = grad;
        ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.fill();
        ctx.strokeStyle = this._darken(color, 0.6); ctx.lineWidth = 1.5;
        ctx.stroke();
    }

    // 爆炸陷阱：3D 炸弹球体 + 导火索
    _drawTrap3D_Explode(ctx, px, py, r, color) {
        // 炸弹球体
        this._draw3DSphere(ctx, px, py, r * 0.75, color);
        // 导火索（右侧向上弯曲）
        ctx.strokeStyle = "#8B4513"; ctx.lineWidth = 2.5;
        ctx.lineCap = "round";
        ctx.beginPath();
        ctx.moveTo(px + r * 0.55, py - r * 0.1);
        ctx.quadraticCurveTo(px + r * 0.85, py - r * 0.7, px + r * 0.55, py - r * 0.8);
        ctx.stroke();
        // 火花
        const t = Date.now() / 200;
        const sparkAlpha = 0.6 + Math.sin(t) * 0.4;
        ctx.fillStyle = `rgba(255,200,50,${sparkAlpha})`;
        ctx.beginPath();
        ctx.arc(px + r * 0.55, py - r * 0.82, r * 0.15, 0, Math.PI * 2);
        ctx.fill();
    }

    // 冰冻陷阱：3D 冰柱晶体
    _drawTrap3D_Freeze(ctx, px, py, r, color) {
        // 冰晶底座光晕
        ctx.fillStyle = "rgba(125,211,252,0.15)";
        ctx.beginPath(); ctx.arc(px, py, r * 0.85, 0, Math.PI * 2); ctx.fill();
        // 六角冰晶（分层渐变）
        for (let i = 2; i >= 0; i--) {
            const sr = r * (0.5 + i * 0.2);
            const alpha = 0.6 + i * 0.15;
            this._drawHex(ctx, px, py, sr,
                `rgba(179,230,252,${alpha})`,
                `rgba(255,255,255,${0.4 + i * 0.1})`);
        }
        // 中心闪光冰核
        const grad = ctx.createRadialGradient(px, py, 0, px, py, r * 0.35);
        grad.addColorStop(0, "#fff");
        grad.addColorStop(0.5, "rgba(200,240,255,0.9)");
        grad.addColorStop(1, "rgba(150,220,255,0.2)");
        ctx.fillStyle = grad;
        ctx.beginPath(); ctx.arc(px, py, r * 0.35, 0, Math.PI * 2); ctx.fill();
        // 冰刺
        ctx.strokeStyle = "rgba(200,240,255,0.7)"; ctx.lineWidth = 2;
        for (let i = 0; i < 6; i++) {
            const a = (i / 6) * Math.PI * 2 - Math.PI / 2;
            ctx.beginPath();
            ctx.moveTo(px + Math.cos(a) * r * 0.35, py + Math.sin(a) * r * 0.35);
            ctx.lineTo(px + Math.cos(a) * r * 0.75, py + Math.sin(a) * r * 0.75);
            ctx.stroke();
        }
    }

    // 眩晕陷阱：3D 雷电球体 + 电弧
    _drawTrap3D_Stun(ctx, px, py, r, color) {
        // 雷电球体
        this._draw3DSphere(ctx, px, py, r * 0.7, color);
        // 电弧特效（随机抖动）
        const t = Date.now() / 150;
        ctx.strokeStyle = "rgba(255,255,255,0.7)"; ctx.lineWidth = 1.5;
        for (let i = 0; i < 3; i++) {
            const a = (i / 3) * Math.PI * 2 + Math.sin(t + i) * 0.3;
            ctx.beginPath();
            ctx.moveTo(px + Math.cos(a) * r * 0.55, py + Math.sin(a) * r * 0.55);
            let cx = px + Math.cos(a) * r * 0.65 + Math.sin(t + i * 2) * r * 0.15;
            let cy = py + Math.sin(a) * r * 0.65 + Math.cos(t + i * 2) * r * 0.15;
            let ex = px + Math.cos(a + 0.3) * r * 0.85;
            let ey = py + Math.sin(a + 0.3) * r * 0.85;
            ctx.lineTo(cx, cy);
            ctx.lineTo(ex, ey);
            ctx.stroke();
        }
    }

    // 吹飞陷阱：3D 旋风柱
    _drawTrap3D_Push(ctx, px, py, r, color) {
        // 旋风底部渐变
        const grad = ctx.createRadialGradient(px, py, r * 0.1, px, py, r * 0.7);
        grad.addColorStop(0, "rgba(255,255,255,0.3)");
        grad.addColorStop(0.5, this._lighten(color, 0.1));
        grad.addColorStop(1, color);
        ctx.fillStyle = grad;
        ctx.beginPath(); ctx.arc(px, py, r * 0.7, 0, Math.PI * 2); ctx.fill();
        // 旋风弧线（多层旋转）
        const t = Date.now() / 800;
        for (let layer = 0; layer < 3; layer++) {
            const lr = r * (0.35 + layer * 0.22);
            ctx.strokeStyle = `rgba(255,255,255,${0.3 + layer * 0.2})`;
            ctx.lineWidth = 1.5 + layer * 0.5;
            ctx.beginPath();
            ctx.arc(px, py, lr, t + layer * 0.8, t + layer * 0.8 + Math.PI * 1.6);
            ctx.stroke();
        }
        // 中心眼
        ctx.fillStyle = "#fff";
        ctx.beginPath(); ctx.arc(px, py, r * 0.12, 0, Math.PI * 2); ctx.fill();
    }

    // 缠绕陷阱：3D 藤蔓球
    _drawTrap3D_Root(ctx, px, py, r, color) {
        // 暗色底座
        const grad = ctx.createRadialGradient(px, py, r * 0.3, px, py, r * 0.65);
        grad.addColorStop(0, this._lighten(color, 0.15));
        grad.addColorStop(1, this._darken(color, 0.4));
        ctx.fillStyle = grad;
        ctx.beginPath(); ctx.arc(px, py, r * 0.65, 0, Math.PI * 2); ctx.fill();
        // 藤蔓缠绕带
        const t = Date.now() / 1200;
        ctx.strokeStyle = this._lighten(color, 0.25); ctx.lineWidth = 3;
        ctx.lineCap = "round";
        for (let i = 0; i < 3; i++) {
            const a = t + (i / 3) * Math.PI * 2;
            ctx.beginPath();
            ctx.arc(px, py, r * 0.55, a, a + Math.PI * 0.7);
            ctx.stroke();
        }
        // 刺/叶子
        ctx.fillStyle = this._lighten(color, 0.3);
        for (let i = 0; i < 4; i++) {
            const a = (i / 4) * Math.PI * 2 + t * 0.5;
            const lx = px + Math.cos(a) * r * 0.55;
            const ly = py + Math.sin(a) * r * 0.55;
            ctx.beginPath();
            ctx.ellipse(lx, ly, r * 0.15, r * 0.08, a, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    // 减速陷阱：3D 水池领域
    _drawTrap3D_Slow(ctx, px, py, r, color) {
        // 水池渐变
        const grad = ctx.createRadialGradient(px - r * 0.15, py - r * 0.2, r * 0.05, px, py, r * 0.65);
        grad.addColorStop(0, "rgba(255,255,255,0.5)");
        grad.addColorStop(0.3, this._lighten(color, 0.2));
        grad.addColorStop(0.7, color);
        grad.addColorStop(1, this._darken(color, 0.4));
        ctx.fillStyle = grad;
        ctx.beginPath(); ctx.arc(px, py, r * 0.65, 0, Math.PI * 2); ctx.fill();
        ctx.strokeStyle = this._darken(color, 0.5); ctx.lineWidth = 1.5;
        ctx.stroke();
        // 水面波纹（动态）
        const t = Date.now() / 600;
        for (let i = 0; i < 2; i++) {
            const wr = r * (0.25 + i * 0.2) + Math.sin(t + i * 2) * 0.05;
            ctx.strokeStyle = `rgba(255,255,255,${0.3 - i * 0.1})`;
            ctx.lineWidth = 1;
            ctx.beginPath(); ctx.arc(px, py, wr, 0, Math.PI * 2); ctx.stroke();
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

    _drawProjectiles(ctx) {
        if (!this.battle) return;
        for (const proj of this.battle.projectiles) {
            if (proj.hit) continue;
            // 箭矢线条
            ctx.strokeStyle = proj.color;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(proj.px, proj.py);

            // 计算箭头方向
            const dx = proj.target.px - proj.px;
            const dy = proj.target.py - proj.py;
            const dist = Math.hypot(dx, dy);
            if (dist < 1) continue;
            const nx = dx / dist;
            const ny = dy / dist;

            // 箭头尖端（比当前位置稍微前移一点）
            const tipX = proj.px + nx * 6;
            const tipY = proj.py + ny * 6;
            ctx.lineTo(tipX, tipY);
            ctx.stroke();

            // 三角形箭头
            const size = 4;
            ctx.fillStyle = proj.color;
            ctx.beginPath();
            ctx.moveTo(tipX, tipY);
            ctx.lineTo(tipX - nx * size + ny * size * 0.5, tipY - ny * size - nx * size * 0.5);
            ctx.lineTo(tipX - nx * size - ny * size * 0.5, tipY - ny * size + nx * size * 0.5);
            ctx.closePath();
            ctx.fill();

            // 发光效果
            ctx.strokeStyle = "rgba(255,255,255,0.6)";
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(tipX, tipY);
            ctx.lineTo(tipX - nx * 8, tipY - ny * 8);
            ctx.stroke();
        }
    }
}