const { log } = require('console');
const { JSDOM, VirtualConsole } = require('jsdom');
const fs = require('node:fs');
const dom = new JSDOM('', {
    url: "https://example.com/",
    pretendToBeVisual: true,
    virtualConsole: new VirtualConsole(),
    // runScripts: "outside-only"
});
const window = dom.window;

const logConfig = {
    common: true,
    opCode: true
}

let __seq = 0
let __logSeq = 0
let __pendingConcat = null;

function flushPendingConcat() {
    if (!__pendingConcat) return;
    const pending = __pendingConcat;
    __pendingConcat = null;
    log("seq:", ++__logSeq, "id:", pending.id, "运算符:", "+=", "args:", JSON.stringify(pending.args), "res:", JSON.stringify(pending.res));
}

function prevLog(func, t, args) {
    flushPendingConcat();
    if (!logConfig.common) return;
    const id = ++__seq;
    t = t === window ? "window" : t && t.constructor && t.constructor.name || typeof t;
    log("seq:", ++__logSeq, "id:", id, "func:", func, "this:", t, "args:", args);
    return {id, func};
}

function nextLog(id, func, res) {
    flushPendingConcat();
    if (!logConfig.common) return;
    log("seq:", ++__logSeq, "id:", id, "func:", func, "res:", res);
}

function prevOpCode(opcode, args) {
    if (!logConfig.opCode) return;
    if (opcode !== "+=") flushPendingConcat();
    const id = ++__seq;
    return { id, opcode, args };
}

function nextOpCode(ctx, res) {
    if (!logConfig.opCode) return res;
    if (ctx.opcode === "+=") {
        if (__pendingConcat && __pendingConcat.res === ctx.args[0]) {
            __pendingConcat.args[1] += ctx.args[1];
            __pendingConcat.res = res;
            __pendingConcat.count++;
        } else {
            flushPendingConcat();
            __pendingConcat = {
                id: ctx.id,
                args: [ctx.args[0], ctx.args[1]],
                res,
                count: 1,
            };
        }
        return res;
    }
    flushPendingConcat();
    log("seq:", ++__logSeq, "id:", ctx.id, "运算符:", ctx.opcode, "args:", JSON.stringify(ctx.args), "res:", JSON.stringify(res));
    return res;
}
