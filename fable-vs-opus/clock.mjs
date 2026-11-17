// Virtual clock injected before page scripts: frame N always shows t = N/fps (see record.mjs).
export const VIRTUAL_CLOCK = `(() => {
  let now = 0;
  const epoch = 1767225600000; // fixed wall clock: 2026-01-01, so Date-based animations are repeatable
  const rafs = new Map(); let rafId = 0;
  const timers = []; let tid = 0;
  performance.now = () => now;
  Date.now = () => epoch + now;
  window.requestAnimationFrame = (cb) => { rafs.set(++rafId, cb); return rafId; };
  window.cancelAnimationFrame = (id) => { rafs.delete(id); };
  window.setTimeout = (cb, ms = 0, ...a) => { timers.push({ id: ++tid, at: now + Math.max(0, +ms || 0), cb, a }); return tid; };
  window.setInterval = (cb, ms = 0, ...a) => { const every = Math.max(1, +ms || 0); timers.push({ id: ++tid, at: now + every, cb, a, every }); return tid; };
  window.clearTimeout = window.clearInterval = (id) => { const i = timers.findIndex((t) => t.id === id); if (i >= 0) timers.splice(i, 1); };
  window.__vt = {
    advance(dt) {
      const target = now + dt;
      for (let guard = 0; guard < 10000; guard++) {
        timers.sort((x, y) => x.at - y.at);
        const t = timers[0];
        if (!t || t.at > target) break;
        now = t.at;
        if (t.every) t.at += t.every; else timers.shift();
        try { if (typeof t.cb === "function") t.cb(...t.a); } catch (e) { console.error(e); }
      }
      now = target;
      const cbs = [...rafs.values()]; rafs.clear();
      for (const cb of cbs) { try { cb(now); } catch (e) { console.error(e); } }
      for (const a of document.getAnimations()) { try { a.pause(); a.currentTime = now; } catch (e) {} }
    },
    get now() { return now; },
  };
})();`;
