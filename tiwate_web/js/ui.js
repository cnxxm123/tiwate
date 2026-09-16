/* ==================== UI 管理模块 ==================== */

class UIManager {
    constructor(app) {
        this.app = app;
    }

    /* 格式化数字 */
    static formatNum(n) {
        if (n >= 10000) return (n / 10000).toFixed(1) + "万";
        if (n >= 1000) return (n / 1000).toFixed(1) + "k";
        return String(n);
    }

    /* 更新顶部资源栏 */
    updateResourceBar() {
        const gs = this.app.gs;
        const r = gs.resources;
        document.getElementById("res-mora").textContent = `🪙 ${UIManager.formatNum(r.mora)}`;
        document.getElementById("res-gems").textContent = `💎 ${UIManager.formatNum(r.primogems)}`;
        document.getElementById("res-books").textContent = `📘 ${r.exp_books}`;
        document.getElementById("res-resin").textContent = `⚗️ ${r.resin}/160`;
        document.getElementById("res-ar").textContent = `⭐ Lv.${gs.adventure_rank}`;
    }

    /* 显示关卡选择 */
    showStageSelect() {
        const panel = document.getElementById("stage-panel");
        panel.style.display = "flex";
        document.getElementById("battle-panel").classList.add("hidden");

        const grid = document.getElementById("stage-grid");
        grid.innerHTML = "";

        const progress = this.app.gs.stage_progress;
        const unlocked = progress.highest_stage_unlocked;
        const completed = progress.completed_stages;

        for (const tdm of TD_MAPS) {
            const sid = tdm.id;
            const isLocked = sid > unlocked;
            const isDone = completed.includes(sid);

            const card = document.createElement("div");
            card.className = "stage-card" + (isLocked ? " locked" : "");
            if (sid === this.app.battleStageId && !isLocked) card.classList.add("selected");
            card.innerHTML = `
                <div class="name">${tdm.name} ${isDone ? "✓" : isLocked ? "🔒" : ""}</div>
                <div class="info">🗺️ ${tdm.width}×${tdm.height} | ${tdm.waves.length}波</div>
                <div class="gold-info">初始 💰${tdm.starting_gold} | ❤️${tdm.lives}</div>
            `;
            if (!isLocked) {
                card.addEventListener("click", () => {
                    this.app.battleStageId = sid;
                    document.querySelectorAll(".stage-card").forEach(c => c.classList.remove("selected"));
                    card.classList.add("selected");
                });
            }
            grid.appendChild(card);
        }
    }

    /* 右键菜单 */
    showContextMenu(x, y, gx, gy, isPath, existing) {
        this.hideContextMenu();
        const menu = document.createElement("div");
        menu.className = "context-menu";
        menu.style.left = x + "px";
        menu.style.top = y + "px";
        menu.id = "context-menu";

        if (existing) {
            const item = document.createElement("div");
            item.className = "menu-item";
            item.textContent = `🏚 出售 ${existing.name} (返还${Math.floor(existing.cost / 2)}💰)`;
            item.addEventListener("click", () => {
                this.app.battle.sellTrapOrTower(gx, gy);
                this.app.battleScreen.renderMap();
                this.app.battleScreen.updateTopBar();
                this.hideContextMenu();
            });
            menu.appendChild(item);
        } else {
            for (const [bid, bdef] of Object.entries(BUILDING_DEFS)) {
                if (bdef.type === "trap" && !isPath) continue;
                if (bdef.type === "tower" && isPath) continue;
                const item = document.createElement("div");
                item.className = "menu-item";
                item.textContent = `${bdef.icon} ${bdef.name}  [${bdef.cost}💰]`;
                item.addEventListener("click", () => {
                    if (bdef.type === "tower") {
                        this.app.battle.placeTower(bid, gx, gy);
                    } else {
                        this.app.battle.placeTrap(bid, gx, gy);
                    }
                    this.app.battleScreen.renderMap();
                    this.app.battleScreen.updateTopBar();
                    this.hideContextMenu();
                });
                menu.appendChild(item);
            }
        }
        document.body.appendChild(menu);

        const closeMenu = (e) => {
            if (!menu.contains(e.target)) { this.hideContextMenu(); document.removeEventListener("click", closeMenu); }
        };
        setTimeout(() => document.addEventListener("click", closeMenu), 0);
    }

    hideContextMenu() {
        const m = document.getElementById("context-menu");
        if (m) m.remove();
    }

    /* 弹窗 */
    showModal(title, message, callback = null) {
        const overlay = document.createElement("div");
        overlay.className = "modal-overlay";
        overlay.innerHTML = `
            <div class="modal-box">
                <h3>${title}</h3>
                <p>${message.replace(/\n/g, "<br>")}</p>
                <button id="modal-ok">确定</button>
            </div>
        `;
        document.body.appendChild(overlay);
        overlay.querySelector("#modal-ok").addEventListener("click", () => {
            overlay.remove();
            if (callback) callback();
        });
    }

    showConfirm(title, message, onOk, onCancel) {
        const overlay = document.createElement("div");
        overlay.className = "modal-overlay";
        overlay.innerHTML = `
            <div class="modal-box">
                <h3>${title}</h3>
                <p>${message.replace(/\n/g, "<br>")}</p>
                <button id="modal-ok">确定</button>
                <button class="cancel" id="modal-cancel">取消</button>
            </div>
        `;
        document.body.appendChild(overlay);
        overlay.querySelector("#modal-ok").addEventListener("click", () => { overlay.remove(); if (onOk) onOk(); });
        overlay.querySelector("#modal-cancel").addEventListener("click", () => { overlay.remove(); if (onCancel) onCancel(); });
    }

    /* Toast 消息 */
    showToast(message, duration = 2000) {
        const toast = document.createElement("div");
        toast.className = "toast";
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), duration);
    }
}