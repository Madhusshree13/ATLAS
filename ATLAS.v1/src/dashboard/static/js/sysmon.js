/* sysmon.js — System monitor with live polling */

(function () {
  let _pollTimer = null;
  let _prevNet   = null;

  window.sysmonInit = function () {
    poll();
    _pollTimer = setInterval(poll, 2000);
  };

  window.sysmonStop = function () {
    clearInterval(_pollTimer);
    _pollTimer = null;
  };

  async function poll() {
    try {
      const d = await fetch('/api/system').then(r => r.json());
      if (d.error) return;

      setBar('sysbar-cpu',  d.cpu_percent);
      setVal('sysval-cpu',  d.cpu_percent + '%');
      colorBar('sysbar-cpu', d.cpu_percent);

      setBar('sysbar-ram',  d.ram_percent);
      setVal('sysval-ram',  d.ram_percent + '%');
      colorBar('sysbar-ram', d.ram_percent);
      setText('sysval-ram-detail', `${d.ram_used_gb} GB / ${d.ram_total_gb} GB`);

      setBar('sysbar-disk', d.disk_percent);
      setVal('sysval-disk', d.disk_percent + '%');
      colorBar('sysbar-disk', d.disk_percent);
      setText('sysval-disk-detail', `${d.disk_used_gb} GB / ${d.disk_total_gb} GB`);

      if (_prevNet) {
        const recvDelta = Math.max(0, d.net_recv_mb - _prevNet.recv);
        const sentDelta = Math.max(0, d.net_sent_mb - _prevNet.sent);
        setText('sysval-recv', fmtNet(recvDelta) + '/s');
        setText('sysval-sent', fmtNet(sentDelta) + '/s');
      } else {
        setText('sysval-recv', fmtNet(d.net_recv_mb) + ' total');
        setText('sysval-sent', fmtNet(d.net_sent_mb) + ' total');
      }
      _prevNet = { recv: d.net_recv_mb, sent: d.net_sent_mb };

      setText('sysmon-updated', 'Updated ' + new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',second:'2-digit'}));
    } catch (_) {}
  }

  function setBar(id, pct) {
    const el = document.getElementById(id);
    if (el) el.style.width = Math.min(100, pct).toFixed(1) + '%';
  }

  function setVal(id, val) {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  }

  function setText(id, val) { setVal(id, val); }

  function colorBar(id, pct) {
    const el = document.getElementById(id);
    if (!el) return;
    if (pct > 85)      el.style.background = 'var(--danger)';
    else if (pct > 65) el.style.background = 'var(--warn)';
    else               el.style.background = el.style.background || '#3b82f6';
  }

  function fmtNet(mb) {
    if (mb >= 1000) return (mb / 1000).toFixed(2) + ' GB';
    if (mb >= 1)    return mb.toFixed(1) + ' MB';
    return (mb * 1024).toFixed(0) + ' KB';
  }
})();
