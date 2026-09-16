/* ==================== 主入口 ==================== */

class TiwateApp {
    constructor() {
        this.gs = null;
        this.battle = null;
        this.battleStageId = 1;
        this.playStart = performance.now() / 1000;
        this.gameLoopId = null;
        this.tdLastTime = 0;
        this.tdCellSize = 60;
        this.battleActive = false;

        /* 加载状态 */
        this.gs = loadGame() || createNewGame();
        saveGame(this.gs);

        /* DOM 引用 */
        this.content = document.getElementById("content");

        /* 初始化模块 */
        this.ui = new UIManager(this);
        this.battleScreen = new BattleScreen(this);

        /* 绑定事件 */
        document.getElementById("btn-enter").addEventListener("click", () => this.battleScreen.enterMap());
        document.getElementById("btn-start").addEventListener("click", () => this.battleScreen.startWave());
        document.getElementById("btn-back").addEventListener("click", () => this.battleScreen.returnToStageSelect());
        document.getElementById("battle-canvas").addEventListener("click", (e) => this.battleScreen.onCanvasClick(e));
        document.getElementById("btn-daily").addEventListener("click", () => this.claimDaily());
        document.getElementById("btn-save").addEventListener("click", () => this.saveGameManual());

        /* 初始化界面 */
        this.ui.showStageSelect();
        this.ui.updateResourceBar();
        this.updateTimers();

        /* 检查离线收益 */
        setTimeout(() => this.checkOffline(), 500);
    }

    /* 保存 */
    saveState() {
        this.gs.last_online = performance.now() / 1000;
        saveGame(this.gs);
    }

    saveGameManual() {
        this.saveState();
        this.ui.showToast("💾 游戏已保存！");
    }

    /* 树脂恢复 */
    updateResin() {
        const now = performance.now() / 1000;
        const last = this.gs.resources.resin_last_update || now;
        const elapsed = now - last;
        const gain = Math.floor(elapsed / 480);
        if (gain > 0) {
            this.gs.resources.resin = Math.min(160, this.gs.resources.resin + gain);
            this.gs.resources.resin_last_update = now;
        }
    }

    /* 应用奖励 */
    applyRewards(rewards) {
        const r = this.gs.resources;
        r.mora += rewards.mora || 0;
        r.exp_books += rewards.exp_books || 0;
        r.primogems += rewards.primogems || 0;
        this.gs.adventure_exp += rewards.adventure_exp || 0;
        while (this.gs.adventure_exp >= this.gs.adventure_rank * 100) {
            this.gs.adventure_exp -= this.gs.adventure_rank * 100;
            this.gs.adventure_rank++;
            r.resin = Math.min(160, r.resin + 60);
            r.mora += 500;
        }
    }

    updateResourceBar() { this.ui.updateResourceBar(); }

    /* 定时更新 */
    updateTimers() {
        this.updateResin();
        this.ui.updateResourceBar();
        const elapsed = performance.now() / 1000 - this.playStart;
        const mins = Math.floor(elapsed / 60);
        const hrs = Math.floor(mins / 60);
        const timeStr = hrs > 0 ? `游玩: ${hrs}时${mins % 60}分` : `游玩: ${mins}分`;
        document.getElementById("play-time").textContent = timeStr;
        setTimeout(() => this.updateTimers(), 10000);
    }

    /* 离线收益 */
    checkOffline() {
        const now = performance.now() / 1000;
        const last = this.gs.last_online || now;
        const offlineSec = Math.min(Math.max(0, now - last), 43200);
        if (offlineSec < 60) return;

        const hours = offlineSec / 3600;
        const mora = Math.floor(100 * hours * 0.7);
        const exp = Math.max(0, Math.floor(hours * 0.7 * 2));
        const arExp = Math.floor(hours * 0.7 * 50);

        this.ui.showConfirm("欢迎回来！",
            `你离开了 ${hours.toFixed(1)} 小时\n\n离线收益:\n🪙 摩拉: ${mora}\n📘 经验书: ${exp}\n⭐ 冒险阅历: ${arExp}\n\n领取奖励？`,
            () => {
                this.applyRewards({ mora, exp_books: exp, adventure_exp: arExp, primogems: 0 });
                this.gs.last_online = now;
                this.saveState();
                this.ui.updateResourceBar();
            }
        );
    }

    /* 每日委托 */
    claimDaily() {
        const now = performance.now() / 1000;
        const dailies = this.gs.dailies;
        if (now - dailies.last_daily_reset > 86400) {
            dailies.commissions_done = 0;
            dailies.last_daily_reset = now;
        }
        const done = dailies.commissions_done;
        const remaining = Math.max(0, 4 - done);
        if (remaining <= 0) {
            this.ui.showModal("提示", "今日委托已全部完成！");
            return;
        }
        const actual = Math.min(remaining, 4);
        dailies.commissions_done += actual;
        const rewards = { mora: actual * 5000, exp_books: actual * 3, adventure_exp: actual * 50 };
        this.applyRewards(rewards);
        this.saveState();
        this.ui.updateResourceBar();
        this.ui.showModal("每日委托", `完成${actual}个委托！\n获得 🪙${actual * 5000}摩拉 📘${actual * 3}经验书`);
    }

    /* 代理 */
    showContextMenu(x, y, gx, gy, isPath, existing) {
        this.ui.showContextMenu(x, y, gx, gy, isPath, existing);
    }
    showModal(title, msg, cb) { this.ui.showModal(title, msg, cb); }
    showStageSelect() { this.ui.showStageSelect(); }
}

/* 启动 */
window.addEventListener("DOMContentLoaded", () => {
    new TiwateApp();
});