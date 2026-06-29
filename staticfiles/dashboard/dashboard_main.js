/* ============================================================
   dashboard_main.js  —  versión limpia
   Gráficos basados en: Factura · Clientes · Usuario

   Requiere (definidos ANTES en el template):
     window.DASHBOARD   — datos de series
     window.CONTEOS     — conteos globales
     window.CONTEOS_MES — conteos mes actual
     Chart.js           — cargado antes de este archivo
   ============================================================ */

(function () {
    "use strict";

    /* ── CSS vars ────────────────────────────────────────── */
    function cv(name) {
        return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    }
    const C = {
        accent    : () => cv("--accent"),
        accentSoft: () => cv("--accent-soft"),
        bgCard    : () => cv("--bg-card"),
        border    : () => cv("--border"),
        borderMid : () => cv("--border-mid"),
        t1        : () => cv("--text-1"),
        t2        : () => cv("--text-2"),
        t3        : () => cv("--text-3"),
        grn       : () => cv("--kd-grn"),
        red       : () => cv("--kd-red"),
        blu       : () => cv("--kd-blu"),
    };

    /* ── Formato COP ─────────────────────────────────────── */
    function fmtCOP(n) {
        if (n >= 1_000_000) return "$" + (n / 1_000_000).toFixed(1) + "M";
        if (n >= 1_000)     return "$" + (n / 1_000).toFixed(0)     + "K";
        return "$" + Math.round(n).toLocaleString("es-CO");
    }

    /* ── Rango de fecha en el header ─────────────────────── */
    function buildDateRange() {
        const now  = new Date();
        const from = new Date(now.getFullYear(), now.getMonth(), 1);
        const opts = { day: "numeric", month: "short", year: "numeric" };
        const fmt  = d => d.toLocaleDateString("es-CO", opts);
        const el   = document.getElementById("kdDateRange");
        if (el) el.textContent = fmt(from) + " — " + fmt(now);
    }

    /* ── Modo Mensual / Anual ────────────────────────────── */
    let _barMode = "mensual";

    function getBarData() {
        const ventas = window.DASHBOARD.ventas;
        if (_barMode === "mensual") {
            return { labels: ventas.labels, subtotales: ventas.subtotales };
        }
        const byYear = {};
        ventas.labels.forEach((lbl, i) => {
            const year = (lbl || "").split("-")[0];
            if (!year) return;
            byYear[year] = (byYear[year] || 0) + (ventas.subtotales[i] || 0);
        });
        const years = Object.keys(byYear).sort();
        return { labels: years, subtotales: years.map(y => byYear[y]) };
    }

    /* ── Barras nativas de ventas ────────────────────────── */
    function buildNativeBars() {
        const wrap = document.getElementById("kdNativeBars");
        const labs = document.getElementById("kdNativeBarLabs");
        if (!wrap) return;
        wrap.innerHTML = "";
        if (labs) labs.innerHTML = "";

        const data = getBarData();
        if (!data.subtotales.length) {
            wrap.innerHTML = '<p style="color:var(--text-3);font-size:12px;margin:auto">Sin datos</p>';
            return;
        }

        const max  = Math.max(...data.subtotales, 1);
        const mths = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"];

        data.subtotales.forEach((v, i) => {
            const pct = Math.max(4, (v / max) * 100);

            const bar = document.createElement("div");
            bar.className = "kd-bar";
            bar.setAttribute("data-v", fmtCOP(v));
            bar.style.height     = "0";
            bar.style.background = "var(--accent)";
            wrap.appendChild(bar);

            setTimeout(() => {
                bar.style.transition = "height .55s cubic-bezier(.4,0,.2,1)";
                bar.style.height     = pct + "%";
            }, 200 + i * 35);

            if (labs) {
                const lbl = document.createElement("span");
                if (_barMode === "mensual") {
                    const mm = parseInt((data.labels[i] || "").split("-")[1], 10);
                    lbl.textContent = mths[mm - 1] || data.labels[i] || "";
                } else {
                    lbl.textContent = data.labels[i] || "";
                }
                labs.appendChild(lbl);
            }
        });
    }

    /* ── Trend line (últimos 8 meses de ventas) ──────────── */
    function buildTrend() {
        const vals = window.DASHBOARD.ventas.subtotales.slice(-8);
        if (vals.length < 2) return;
        const max = Math.max(...vals, 1), W = 300, H = 80, P = 10;
        const pts = vals.map((v, i) => [
            P + (i / (vals.length - 1)) * (W - 2 * P),
            H - P - ((v / max) * (H - 2 * P)),
        ]);
        const dL = "M" + pts.map(p => p.join(",")).join(" L");
        const dF = dL + ` L${pts[pts.length - 1][0]},${H} L${pts[0][0]},${H} Z`;
        const tl = document.getElementById("kdTrendLine");
        const tf = document.getElementById("kdTrendFill");
        if (tl) tl.setAttribute("d", dL);
        if (tf) tf.setAttribute("d", dF);
    }

    /* ── KPI cards — variaciones ─────────────────────────── */
    function buildVariaciones() {
        const v = window.VARIACIONES || {};

        function apply(key, upElId, pctElId) {
            const data = v[key];
            if (!data) return;

            const upEl  = document.getElementById(upElId);
            const pctEl = document.getElementById(pctElId);

            if (upEl) {
                upEl.className = data.up ? "kd-var-arrow up" : "kd-var-arrow down";
                upEl.textContent = data.up ? "▲" : "▼";
            }
            if (pctEl) {
                pctEl.textContent = data.pct !== null ? data.pct + "%" : "—";
                pctEl.style.color = data.up ? "var(--kd-grn)" : "var(--kd-red)";
            }
        }

        apply("ventas",   "varVentasArrow",   "varVentasPct");
        apply("ticket",   "varTicketArrow",   "varTicketPct");
        apply("clientes", "varClientesArrow", "varClientesPct");
    }

    /* ── Opciones base Chart.js ──────────────────────────── */
    function chartOpts(yFmt) {
        return {
            responsive          : true,
            maintainAspectRatio : false,
            plugins: {
                legend: { labels: { color: C.t2(), font: { family: "Sora", size: 11 } } },
                tooltip: {
                    backgroundColor: C.bgCard(),
                    borderColor    : C.borderMid(),
                    borderWidth    : 1,
                    titleColor     : C.t1(),
                    bodyColor      : C.t2(),
                },
            },
            scales: {
                x: {
                    ticks: { color: C.t3(), font: { family: "Sora", size: 10 } },
                    grid : { color: C.border() },
                },
                y: {
                    ticks: { color: C.t3(), font: { family: "Sora", size: 10 }, callback: yFmt || fmtCOP },
                    grid : { color: C.border() },
                },
            },
        };
    }

    /* ── Gestión de instancias Chart.js ──────────────────── */
    const charts = {};

    function safeDestroy(canvasId, key) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        const existing = Chart.getChart(ctx);
        if (existing) existing.destroy();
        if (charts[key]) { charts[key].destroy(); charts[key] = null; }
        return ctx;
    }

    function destroyAll() {
        Object.keys(charts).forEach(k => {
            if (charts[k]) { charts[k].destroy(); charts[k] = null; }
        });
    }

    /* ── Gráfico: Ingresos (ventas) por mes ─────────────── */
    function buildIngresosChart() {
        const ctx = safeDestroy("chartVentasMes", "ventasMes");
        if (!ctx) return;
        const o = chartOpts();
        o.plugins.tooltip.callbacks = { label: c => ` ${fmtCOP(c.raw)}` };
        charts.ventasMes = new Chart(ctx, {
            type: "bar",
            data: {
                labels  : window.DASHBOARD.ventas.labels,
                datasets: [{
                    label          : "Ventas",
                    data           : window.DASHBOARD.ventas.subtotales,
                    backgroundColor: C.accent() + "cc",
                    borderColor    : C.accent(),
                    borderWidth    : 1,
                    borderRadius   : 4,
                }],
            },
            options: o,
        });
    }

    /* ── Gráfico: Cantidad de facturas por mes ───────────── */
    function buildCantidadChart() {
        const ctx = safeDestroy("chartVentasCantidad", "cant");
        if (!ctx) return;
        const o = chartOpts(v => v);
        o.plugins.tooltip.callbacks = { label: c => ` ${c.raw} facturas` };
        charts.cant = new Chart(ctx, {
            type: "line",
            data: {
                labels  : window.DASHBOARD.ventas.labels,
                datasets: [{
                    label              : "Facturas emitidas",
                    data               : window.DASHBOARD.ventas.cantidades,
                    borderColor        : C.accent(),
                    backgroundColor    : C.accentSoft(),
                    borderWidth        : 2,
                    fill               : true,
                    tension            : 0.4,
                    pointBackgroundColor: C.accent(),
                    pointRadius        : 3,
                }],
            },
            options: o,
        });
    }

    /* ── Gráfico: Clientes registrados por mes ───────────── */
    function buildClientesChart() {
        const ctx = safeDestroy("chartClientes", "cli");
        if (!ctx) return;
        const o = chartOpts(v => v);
        o.plugins.tooltip.callbacks = { label: c => ` ${c.raw} clientes` };
        charts.cli = new Chart(ctx, {
            type: "line",
            data: {
                labels  : window.DASHBOARD.clientes.labels,
                datasets: [{
                    label              : "Clientes nuevos",
                    data               : window.DASHBOARD.clientes.totales,
                    borderColor        : C.grn(),
                    backgroundColor    : "rgba(16,185,129,.12)",
                    borderWidth        : 2,
                    fill               : true,
                    tension            : 0.4,
                    pointBackgroundColor: C.grn(),
                    pointRadius        : 3,
                }],
            },
            options: o,
        });
    }

    /* ── Gráfico: Usuarios registrados por mes ───────────── */
    function buildUsuariosChart() {
        const ctx = safeDestroy("chartUsuarios", "usr");
        if (!ctx) return;
        const o = chartOpts(v => v);
        o.plugins.tooltip.callbacks = { label: c => ` ${c.raw} usuarios` };
        charts.usr = new Chart(ctx, {
            type: "bar",
            data: {
                labels  : window.DASHBOARD.usuarios.labels,
                datasets: [{
                    label          : "Usuarios registrados",
                    data           : window.DASHBOARD.usuarios.totales,
                    backgroundColor: C.blu() + "bb",
                    borderColor    : C.blu(),
                    borderWidth    : 1,
                    borderRadius   : 4,
                }],
            },
            options: o,
        });
    }

    /* ── Render completo ─────────────────────────────────── */
    function renderAll() {
        buildDateRange();
        buildNativeBars();
        buildTrend();
        buildVariaciones();
        buildIngresosChart();
        buildCantidadChart();
        buildClientesChart();
        buildUsuariosChart();
    }

    /* ── Observer de tema con debounce ──────────────────── */
    let _themeTimer = null;
    new MutationObserver(() => {
        clearTimeout(_themeTimer);
        _themeTimer = setTimeout(() => {
            destroyAll();
            renderAll();
        }, 200);
    }).observe(document.documentElement, {
        attributes     : true,
        attributeFilter: ["data-theme", "class"],
    });

    /* ── Toggle Mensual / Anual ──────────────────────────── */
    function bindToggle() {
        const btnM = document.getElementById("kdBtnMensual");
        const btnA = document.getElementById("kdBtnAnual");
        if (!btnM || !btnA) return;

        btnM.addEventListener("click", () => {
            if (_barMode === "mensual") return;
            _barMode = "mensual";
            btnM.className = "kd-btn kd-btn-p kd-btn-sm"; btnM.style.fontSize = "11px";
            btnA.className = "kd-btn kd-btn-g kd-btn-sm"; btnA.style.fontSize = "11px";
            buildNativeBars();
        });

        btnA.addEventListener("click", () => {
            if (_barMode === "anual") return;
            _barMode = "anual";
            btnA.className = "kd-btn kd-btn-p kd-btn-sm"; btnA.style.fontSize = "11px";
            btnM.className = "kd-btn kd-btn-g kd-btn-sm"; btnM.style.fontSize = "11px";
            buildNativeBars();
        });
    }

    /* ── Arranque ────────────────────────────────────────── */
    function init() {
        renderAll();
        bindToggle();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

})();