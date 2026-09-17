// ==================== 主控制器 ====================
class GameApp {
    constructor() {
        this.ui = new UIManager();
        this.renderer = new MapRenderer(document.getElementById("td-canvas"));
        this.battle = null;
        this.loopId = null;
        this.selectedMapData = null;

        this._bindEvents();
        this._loadProgress();
    }

    _bindEvents() {
        // 返回按钮
        document.getElementById("btn-return").addEventListener("click", () => this.ui.showSelect());

        // 开始出怪
        document.getElementById("btn-start-wave").addEventListener("click", () => this._startWave());

        // 点击 canvas 建造
        const canvas = document.getElementById("td-canvas");
        canvas.addEventListener("click", (e) => this._onCanvasClick(e));

        // 点击其他区域关闭弹窗
        document.addEventListener("click", (e) => {
            if (!e.target.closest("#popup-menu") && !e.target.closest("#td-canvas")) {
                this.ui.hidePopup();
            }
        });

        // UI callbacks
        this.ui.onStartWave = () => this._startWave();
        this.ui.onPlaceBuilding = (bid, gx, gy) => this._placeBuilding(bid, gx, gy);
        this.ui.onSellBuilding = (gx, gy) => this._sellBuilding(gx, gy);
        this.ui.onEnterBattle = () => this.showBattle();
        this.ui.onReturnSelect = () => this._cleanupBattle();
    }

    // ---- 选关逻辑 ----
    get selectedMap() {
        return this.ui.selectedMap;
    }

    set selectedMap(v) {
        this.ui.selectedMap = v;
        this.selectedMapData = v;
    }

    // ---- 战斗逻辑 ----
    showBattle() {
        const map = this.ui.selectedMap;
        if (!map) return;
        this.selectedMapData = map;

        // 初始化战斗引擎
        const mapData = { ...this.selectedMapData, cell_size: 66 };
        this.battle = new TDEngine(mapData);
        this.renderer.setBattle(this.battle);
        this.renderer.render();
        this._updateInfo();

        // 隐藏开始按钮（战斗未开始）
        document.getElementById("btn-start-wave").style.display = "block";
    }

    _startWave() {
        if (!this.battle) return;
        this.battle.start();
        document.getElementById("btn-start-wave").style.display = "none";
        this._startLoop();
    }

    _startLoop() {
        if (this.loopId) return;
        const loop = () => {
            if (!this.battle || this.battle.gameOver) {
                this._handleEnd();
                return;
            }
            this.battle.update();
            this.renderer.render();
            this._updateInfo();
            this.loopId = requestAnimationFrame(loop);
        };
        this.loopId = requestAnimationFrame(loop);
    }

    _handleEnd() {
        if (this.loopId) {
            cancelAnimationFrame(this.loopId);
            this.loopId = null;
        }
        this.renderer.render();
        this.ui.showResult(
            this.battle.victory,
            this.battle.killCount,
            this.battle.goldEarned
        );
        this._saveProgress();
    }

    _cleanupBattle() {
        if (this.loopId) {
            cancelAnimationFrame(this.loopId);
            this.loopId = null;
        }
        this.battle = null;
        this.renderer.setBattle(null);
    }

    _updateInfo() {
        if (!this.battle) return;
        this.ui.updateInfo(
            this.battle.gold,
            this.battle.lives,
            this.battle.maxLives,
            Math.min(this.battle.waveIndex + 1, this.battle.waves.length),
            this.battle.waves.length,
            this.battle.killCount
        );
    }

    _onCanvasClick(e) {
        if (!this.battle) return;
        const canvas = document.getElementById("td-canvas");
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;
        const mx = (e.clientX - rect.left) * scaleX;
        const my = (e.clientY - rect.top) * scaleY;
        const gx = Math.floor(mx / this.battle.cellSize);
        const gy = Math.floor(my / this.battle.cellSize);

        if (gx < 0 || gx >= this.battle.width || gy < 0 || gy >= this.battle.height) return;

        const canPlaceTower = this.battle.canPlaceTower(gx, gy);
        const canPlaceTrap = this.battle.canPlaceTrap(gx, gy);

        // 检查是否有建筑
        const hasBuilding = this.battle.towers.some(t => t.gridX === gx && t.gridY === gy)
            || this.battle.traps.some(t => t.gridX === gx && t.gridY === gy);

        if (!canPlaceTower && !canPlaceTrap && !hasBuilding) return;

        this.ui.showPopupMenu(gx, gy, canPlaceTower, canPlaceTrap, hasBuilding);
    }

    _placeBuilding(bid, gx, gy) {
        if (!this.battle) return;
        const bdef = BUILDING_DEFS[bid];
        if (!bdef) return;

        if (bdef.type === "tower") {
            this.battle.placeTower(bid, gx, gy);
        } else if (bdef.type === "trap") {
            this.battle.placeTrap(bid, gx, gy);
        }
        this.renderer.render();
        this._updateInfo();
    }

    _sellBuilding(gx, gy) {
        if (!this.battle) return;
        this.battle.sellBuilding(gx, gy);
        this.renderer.render();
        this._updateInfo();
    }

    // ---- 存档 ----
    async _saveProgress() {
        try {
            await fetch("/api/stage-progress", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ lastMap: this.selectedMapData?.id || 1 }),
            });
        } catch (e) {
            // 忽略存档错误
        }
    }

    async _loadProgress() {
        try {
            const resp = await fetch("/api/stage-progress");
            const data = await resp.json();
            // 预选最后玩的地图
            if (data.lastMap) {
                const map = TD_MAPS.find(m => m.id === data.lastMap);
                if (map) this.selectedMap = map;
            }
        } catch (e) {
            // 忽略
        }
    }
}

// ---- 启动 ----
let app;
document.addEventListener("DOMContentLoaded", () => {
    app = new GameApp();
});