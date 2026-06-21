/* ═══════════════════════════════════════════════════════════════
   ALPINATRACK — Core Scripts v3
   Archivo : static/inicio/alpinatrack.js
   NOTA    : Este archivo NO puede contener tags {% %} de Django.
             Los mensajes Django se inyectan desde base.html
             mediante window.alpDjangoMessages (ver base.html).
═══════════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', function () {

    /* ── 1. SIDEBAR COLLAPSE ─────────────────────────────────── */
    const sidebar   = document.getElementById('alpSidebar');
    const toggleBtn = document.getElementById('alpToggle');

    function setSidebarState(collapsed) {
        document.body.classList.toggle('alp-collapsed', collapsed);
        if (sidebar) sidebar.classList.toggle('collapsed', collapsed);
        localStorage.setItem('alp_sidebar_collapsed', collapsed ? '1' : '0');
    }

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            const isCollapsed = sidebar.classList.contains('collapsed');

            /* Móvil: overlay en lugar de colapso */
            if (window.innerWidth <= 768) {
                sidebar.classList.toggle('mobile-open');
                return;
            }
            setSidebarState(!isCollapsed);
        });
    }

    /* Restaurar estado guardado al cargar */
    if (localStorage.getItem('alp_sidebar_collapsed') === '1' && window.innerWidth > 768) {
        setSidebarState(true);
    }

    /* ── 2. SUBMENÚS (animación max-height) ─────────────────── */
    window.alpToggleSub = function (subId, trigger) {
        const sub = document.getElementById(subId);
        if (!sub) return;
        const isOpen = sub.classList.contains('open');

        /* Cierra los demás submenús abiertos */
        document.querySelectorAll('.alp-sub.open').forEach(s => {
            if (s.id !== subId) s.classList.remove('open');
        });
        document.querySelectorAll('.alp-nav-item.sub-open').forEach(n => {
            if (n !== trigger) n.classList.remove('sub-open');
        });

        sub.classList.toggle('open', !isOpen);
        trigger.classList.toggle('sub-open', !isOpen);
    };

    /* ── 3. MARCADO AUTOMÁTICO DE ACTIVOS ───────────────────── */
    const currentPath = window.location.pathname;

    document.querySelectorAll('.alp-sub-item').forEach(item => {
        const href = item.getAttribute('href');
        if (href && href !== '#' && currentPath.startsWith(href)) {
            item.classList.add('active');
            const parentSub = item.closest('.alp-sub');
            if (parentSub) {
                parentSub.classList.add('open');
                const trigger = parentSub.previousElementSibling;
                if (trigger) trigger.classList.add('sub-open');
            }
        }
    });

    document.querySelectorAll('.alp-nav-item[href]').forEach(item => {
        const href = item.getAttribute('href');
        if (href && href !== '#' && currentPath === href) {
            item.classList.add('active');
        }
    });

    /* ── 4. PANTALLA COMPLETA ───────────────────────────────── */
    const fsBtn = document.getElementById('alpFsBtn');
    if (fsBtn) {
        fsBtn.addEventListener('click', () => {
            const icon = fsBtn.querySelector('i');
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch(() => {});
                if (icon) icon.className = 'fa-solid fa-compress';
            } else {
                document.exitFullscreen();
                if (icon) icon.className = 'fa-solid fa-expand';
            }
        });
    }

    /* ── 5. SELECTOR DE COLOR DE TEMA ───────────────────────── */
    const savedTheme = localStorage.getItem('alp_theme') || 'cobalt';
    document.documentElement.setAttribute('data-theme', savedTheme);

    document.querySelectorAll('.alp-tc').forEach(tc => {
        if (tc.dataset.t === savedTheme) tc.classList.add('sel');
        tc.addEventListener('click', () => {
            document.querySelectorAll('.alp-tc').forEach(t => t.classList.remove('sel'));
            tc.classList.add('sel');
            document.documentElement.setAttribute('data-theme', tc.dataset.t);
            localStorage.setItem('alp_theme', tc.dataset.t);
        });
    });

    /* ── 6. MODO OSCURO / CLARO ─────────────────────────────── */
    const darkToggle = document.getElementById('alpDarkToggle');
    const modeToggle = document.getElementById('alpModeToggle');
    const themeIcon  = document.getElementById('alpThemeIcon');

    function applyDarkMode(isDark) {
        document.documentElement.classList.toggle('dark', isDark);
        if (darkToggle) darkToggle.classList.toggle('on', isDark);
        if (themeIcon)  themeIcon.className = isDark ? 'fa-regular fa-sun' : 'fa-regular fa-moon';
        localStorage.setItem('alp_dark', isDark ? '1' : '0');
    }

    applyDarkMode(localStorage.getItem('alp_dark') === '1');

    if (darkToggle) darkToggle.addEventListener('click', () =>
        applyDarkMode(!document.documentElement.classList.contains('dark'))
    );
    if (modeToggle) modeToggle.addEventListener('click', () =>
        applyDarkMode(!document.documentElement.classList.contains('dark'))
    );

    /* ── 7. FAB SELECTOR DE TEMA ─────────────────────────────── */
    const themeFab  = document.getElementById('alpThemeFab');
    const themeOpts = document.getElementById('alpThemeOpts');
    if (themeFab && themeOpts) {
        themeFab.addEventListener('click', e => {
            e.stopPropagation();
            themeOpts.classList.toggle('open');
        });
        document.addEventListener('click', () => themeOpts.classList.remove('open'));
        themeOpts.addEventListener('click', e => e.stopPropagation());
    }

    /* ── 8. TOASTS — SWEETALERT2 ────────────────────────────── */
    /*
     * Este bloque crea el sistema de toasts.
     * Los mensajes Django se procesan DESPUÉS de que este script
     * cargó, leyendo window.alpDjangoMessages inyectado en base.html.
     */
    let _toastStyle = document.getElementById('alp-toast-style');
    if (!_toastStyle) {
        _toastStyle = document.createElement('style');
        _toastStyle.id = 'alp-toast-style';
        document.head.appendChild(_toastStyle);
    }

    window.alpShowAlert = function (msg, type) {
        if (typeof Swal === 'undefined') return;

        const cs     = getComputedStyle(document.documentElement);
        const bgCard = cs.getPropertyValue('--bg-card').trim()    || '#fff';
        const bdrMid = cs.getPropertyValue('--border-mid').trim() || 'rgba(0,0,0,.14)';
        const txt1   = cs.getPropertyValue('--text-1').trim()     || '#1A2332';
        const accent = cs.getPropertyValue('--accent').trim()     || '#1E5CDB';

        const iconMap = {
            success : '#00A86B',
            error   : '#EF4444',
            danger  : '#EF4444',
            warning : '#F59E0B',
            info    : accent,
        };
        const ic = iconMap[type] || iconMap.info;

        _toastStyle.textContent = `
            .swal2-container.swal2-top-end {
                filter: drop-shadow(0 4px 20px rgba(0,0,0,.18)) !important;
                overflow: visible !important;
                padding: 14px 14px 0 0 !important;
            }
            .alp-toast.swal2-popup {
                background: ${bgCard} !important;
                border: 1px solid ${bdrMid} !important;
                border-radius: 10px !important;
                box-shadow: none !important;
                padding: 12px 16px !important;
                min-width: 270px !important;
                overflow: hidden !important;
            }
            .alp-toast .swal2-title {
                color: ${txt1} !important;
                font-size: 13.5px !important;
                font-family: 'Inter', sans-serif !important;
                font-weight: 600 !important;
                margin: 0 !important;
                padding: 0 !important;
            }
            .alp-toast .swal2-icon {
                border-color: ${ic} !important;
                color: ${ic} !important;
                width: 28px !important;
                height: 28px !important;
                margin: 0 10px 0 0 !important;
                font-size: 14px !important;
            }
            .alp-toast .swal2-icon .swal2-icon-content { color: ${ic} !important; font-size: 18px !important; }
            .alp-toast .swal2-success-ring            { border-color: ${ic}40 !important; }
            .alp-toast .swal2-success-line-tip,
            .alp-toast .swal2-success-line-long       { background: ${ic} !important; }
            .alp-toast .swal2-x-mark-line-left,
            .alp-toast .swal2-x-mark-line-right       { background: ${ic} !important; }
            .alp-toast .swal2-timer-progress-bar      { background: ${ic} !important; height: 3px !important; }
            .alp-toast .swal2-timer-progress-bar-container {
                border-radius: 0 0 10px 10px !important;
                overflow: hidden !important;
            }
        `;

        Swal.mixin({
            toast             : true,
            position          : 'top-end',
            showConfirmButton : false,
            timer             : 3500,
            timerProgressBar  : true,
            scrollbarPadding  : false,
            customClass       : { popup: 'alp-toast' },
            didOpen: toast => {
                toast.addEventListener('mouseenter', Swal.stopTimer);
                toast.addEventListener('mouseleave', Swal.resumeTimer);
            }
        }).fire({
            icon  : ({ success:'success', error:'error', danger:'error', warning:'warning', info:'info' })[type] || 'info',
            title : msg
        });
    };

    /* ── 9. DISPARAR MENSAJES DJANGO ────────────────────────────
     * base.html inyecta window.alpDjangoMessages antes de este
     * script. Aquí los consumimos y mostramos como toasts.
     * ────────────────────────────────────────────────────────── */
    if (Array.isArray(window.alpDjangoMessages)) {
        window.alpDjangoMessages.forEach(function (m) {
            alpShowAlert(m.msg, m.tags);
        });
    }

}); /* fin DOMContentLoaded */
