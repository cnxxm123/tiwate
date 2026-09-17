// ==================== UI 管理器 ====================
class UIManager {
    constructor() {
        this.currentView = "select"; // "select" | "battle"
        this.selectedMap = null;

        // DOM elements
        this.selectPanel = document.getElementById("stage-select");
        this.battlePanel = document.getElementById("battle-panel");
        this.battleTop = document.getElementById("battle-top");
        this.mapGrid = document.getElementById("map-grid");
        this.btnStartWave = document.getElementById("btn-start-wave");
        this.canvasWrapper = document.getElementById("canvas-wrapper");
        this.popupMenu = document.getElementById("popup-menu");
        this.popupGrid = document.getElementById("popup-grid");
        this.popupName = document.getElementById("popup-name");

        // info elements
        this.spanGold = document.getElementById("info-gold");
        this.spanLives = document.getElementById("info-lives");
        this.spanWave = document.getElementById("info-wave");
        this.spanKills = document.getElementById("info-kills");

        // callback
        this.onStartWave = null;
        this.onPlaceBuilding = null;
        this.onSellBuilding = null;
        this.onReturnSelect = null;
        this.onEnterBattle = null;

        this._initStageSelect();
    }

    _initStageSelect() {
        this.mapGrid.innerHTML = "";
        for (const map of TD_MAPS) {
            const card = document.createElement("div");
            card.className = "map-card";
            card.innerHTML = `
                <div class="map-card-title">🗺️ ${map.name}</div>
                <div class="map-card-info">
                    <span>👾 ${map.waves.length}波</span>
                    <span>💰 ${map.starting_gold}金</span>
                    <span>❤️ ${map.lives}命</span>
                </div>
            `;
            card.addEventListener("click", () => {
                this.selectedMap = map;
                this.showMapPreview(map);
            });
            this.mapGrid.appendChild(card);
        }
    }

    showMapPreview(map) {
        // 移除旧预览
        const old = document.querySelector(".map-preview-overlay");
        if (old) old.remove();

        const overlay = document.createElement("div");
        overlay.className = "map-preview-overlay";
        overlay.innerHTML = `
            <div class="map-preview-card">
                <h2>${map.name}</h2>
                <div class="map-preview-stats">
                    <div>👾 ${map.waves.length} 波怪物</div>
                    <div>💰 初始 ${map.starting_gold} 金币</div>
                    <div>❤️ ${map.lives} 条生命</div>
                    <div>📐 ${map.width}×${map.height} 格子</div>
                </div>
                <div class="map-preview-btns">
                    <button class="btn-enter" id="btn-enter-map">🗺️ 进入地图</button>
                    <button class="btn-cancel" id="btn-cancel-preview">取消</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        overlay.querySelector("#btn-cancel-preview").addEventListener("click", () => overlay.remove());
        overlay.querySelector("#btn-enter-map").addEventListener("click", () => {
            overlay.remove();
            this.showBattle();
            if (this.onEnterBattle) this.onEnterBattle();
        });
    }

    showBattle() {
        this.currentView = "battle";
        this.selectPanel.style.display = "none";
        this.battlePanel.style.display = "flex";
        this.btnStartWave.style.display = "block";
        this.popupMenu.style.display = "none";
    }

    showSelect() {
        this.currentView = "select";
        this.selectPanel.style.display = "flex";
        this.battlePanel.style.display = "none";
        if (this.onReturnSelect) this.onReturnSelect();
    }

    updateInfo(gold, lives, maxLives, wave, maxWave, kills) {
        this.spanGold.textContent = gold;
        this.spanLives.textContent = `${lives}/${maxLives}`;
        this.spanWave.textContent = `${wave}/${maxWave}`;
        this.spanKills.textContent = kills;
    }

    showResult(victory, kills, goldEarned) {
        const overlay = document.createElement("div");
        overlay.className = "map-preview-overlay";
        const title = victory ? "🏆 胜利！" : "💀 失败";
        const color = victory ? "#4ade80" : "#ef4444";
        overlay.innerHTML = `
            <div class="map-preview-card">
                <h2 style="color:${color}">${title}</h2>
                <div class="map-preview-stats">
                    <div>👾 击杀: ${kills}</div>
                    <div>💰 获得金币: ${goldEarned}</div>
                </div>
                <div class="map-preview-btns">
                    <button class="btn-enter" id="btn-result-ok">返回</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);
        overlay.querySelector("#btn-result-ok").addEventListener("click", () => {
            overlay.remove();
            this.showSelect();
        });
    }

    showPopupMenu(gridX, gridY, canPlaceTower, canPlaceTrap, hasBuilding, clickX, clickY, availTowers, availTraps) {
        this.popupGrid.textContent = `(${gridX}, ${gridY})`;

        // 使用鼠标点击位置定位，确保在视口内
        const menuW = 200;
        let left = clickX || 100;
        let top = clickY || 100;
        if (left + menuW > window.innerWidth) left = window.innerWidth - menuW - 10;
        if (left < 10) left = 10;
        if (top < 10) top = 10;
        // 先显示才能获取高度
        this.popupMenu.style.display = "block";
        this.popupMenu.style.left = left + "px";
        this.popupMenu.style.top = top + "px";
        // 如果底部溢出，向上调整
        requestAnimationFrame(() => {
            const h = this.popupMenu.offsetHeight;
            if (top + h > window.innerHeight - 10 && top > h + 10) {
                this.popupMenu.style.top = (window.innerHeight - h - 10) + "px";
            }
        });
        this.popupMenu.dataset.gridX = gridX;
        this.popupMenu.dataset.gridY = gridY;

        // 清空菜单项
        while (this.popupMenu.children.length > 1) {
            this.popupMenu.removeChild(this.popupMenu.lastChild);
        }
        // 移除旧的 btn-sell
        const oldSell = this.popupMenu.querySelector(".popup-btn[data-action='sell']");
        if (oldSell) oldSell.remove();

        if (hasBuilding) {
            const sellBtn = document.createElement("div");
            sellBtn.className = "popup-btn";
            sellBtn.dataset.action = "sell";
            sellBtn.textContent = "💰 出售";
            sellBtn.addEventListener("click", () => {
                this.popupMenu.style.display = "none";
                if (this.onSellBuilding) this.onSellBuilding(gridX, gridY);
            });
            this.popupMenu.appendChild(sellBtn);
        } else {
            if (canPlaceTower) {
                for (const [bid, bdef] of Object.entries(BUILDING_DEFS)) {
                    if (bdef.type !== "tower") continue;
                    if (availTowers && availTowers.length > 0 && !availTowers.includes(bid)) continue;
                    const btn = document.createElement("div");
                    btn.className = "popup-btn";
                    btn.dataset.action = "place";
                    btn.dataset.bid = bid;
                    btn.textContent = `${bdef.icon} ${bdef.name} (${bdef.cost}💰)`;
                    btn.addEventListener("click", () => {
                        this.popupMenu.style.display = "none";
                        if (this.onPlaceBuilding) this.onPlaceBuilding(bid, gridX, gridY);
                    });
                    this.popupMenu.appendChild(btn);
                }
            }
            if (canPlaceTrap) {
                for (const [bid, bdef] of Object.entries(BUILDING_DEFS)) {
                    if (bdef.type !== "trap") continue;
                    if (availTraps && availTraps.length > 0 && !availTraps.includes(bid)) continue;
                    const btn = document.createElement("div");
                    btn.className = "popup-btn";
                    btn.dataset.action = "place";
                    btn.dataset.bid = bid;
                    btn.textContent = `${bdef.icon} ${bdef.name} (${bdef.cost}💰)`;
                    btn.addEventListener("click", () => {
                        this.popupMenu.style.display = "none";
                        if (this.onPlaceBuilding) this.onPlaceBuilding(bid, gridX, gridY);
                    });
                    this.popupMenu.appendChild(btn);
                }
            }
        }
    }

    hidePopup() {
        this.popupMenu.style.display = "none";
    }
}