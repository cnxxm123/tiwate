/* ==================== 存档系统（localStorage） ==================== */

const SAVE_KEY = "tiwate_td_save";

function createNewGame() {
    return {
        player_name: "旅行者",
        adventure_rank: 1,
        adventure_exp: 0,
        play_time: 0,
        last_online: Date.now() / 1000,
        resources: {
            mora: 10000,
            primogems: 0,
            resin: 160,
            exp_books: 5,
            resin_last_update: Date.now() / 1000,
        },
        stage_progress: {
            highest_stage_unlocked: 1,
            completed_stages: [],
        },
        dailies: {
            commissions_done: 0,
            last_daily_reset: Date.now() / 1000,
        },
    };
}

function saveGame(gs) {
    gs.last_save_time = Date.now() / 1000;
    gs.save_version = 1;
    localStorage.setItem(SAVE_KEY, JSON.stringify(gs));
}

function loadGame() {
    const raw = localStorage.getItem(SAVE_KEY);
    if (!raw) return null;
    try {
        return JSON.parse(raw);
    } catch (e) {
        return null;
    }
}

function deleteSave() {
    localStorage.removeItem(SAVE_KEY);
}