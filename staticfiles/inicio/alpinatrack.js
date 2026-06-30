/* ═══════════════════════════════════════════════════════════════
   ALPINATRACK — Core Scripts v3 (FINAL - CON NAVEGACIÓN)
═══════════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', function () {

    /* ── 1. SIDEBAR ───────────────────────────────────────────── */
    const sidebar = document.getElementById('alpSidebar');
    const toggleBtn = document.getElementById('alpToggle');
    const overlay = document.getElementById('sidebarOverlay');
    const main = document.querySelector('.alp-main');

    // Verificar que los elementos existan
    if (!sidebar) console.warn('Sidebar no encontrado');
    if (!toggleBtn) console.warn('Toggle button no encontrado');

    function isMobile() {
        return window.innerWidth <= 768;
    }

    function updateSidebar() {
        if (!sidebar) return;

        if (isMobile()) {
            // MODO MÓVIL - overlay solo aquí
            sidebar.classList.remove('collapsed');
            document.body.classList.remove('alp-collapsed');

            if (sidebar.classList.contains('mobile-open')) {
                if (overlay) {
                    overlay.classList.add('active');
                    overlay.style.display = 'block';
                }
                document.body.style.overflow = 'hidden';
            } else {
                if (overlay) {
                    overlay.classList.remove('active');
                    overlay.style.display = 'none';
                }
                document.body.style.overflow = '';
            }
            if (main) main.style.marginLeft = '0';

        } else {
            // MODO DESKTOP/TABLET - NUNCA mostrar overlay
            sidebar.classList.remove('mobile-open');

            // FORZAR REMOVER OVERLAY SIEMPRE
            if (overlay) {
                overlay.classList.remove('active');
                overlay.style.display = 'none';
            }
            document.body.style.overflow = '';

            // Restaurar estado guardado
            const saved = localStorage.getItem('alp_sidebar_collapsed') === '1';
            if (saved) {
                sidebar.classList.add('collapsed');
                document.body.classList.add('alp-collapsed');
                if (main) main.style.marginLeft = '58px';
            } else {
                sidebar.classList.remove('collapsed');
                document.body.classList.remove('alp-collapsed');
                if (main) main.style.marginLeft = 'var(--sidebar-w)';
            }
        }
    }

    function toggleSidebar() {
        if (!sidebar) return;

        if (isMobile()) {
            // Móvil: toggle mobile-open
            sidebar.classList.toggle('mobile-open');
            updateSidebar();
        } else {
            // Desktop: toggle collapsed
            const isCollapsed = sidebar.classList.contains('collapsed');
            if (isCollapsed) {
                sidebar.classList.remove('collapsed');
                document.body.classList.remove('alp-collapsed');
                if (main) main.style.marginLeft = 'var(--sidebar-w)';
                localStorage.setItem('alp_sidebar_collapsed', '0');
            } else {
                sidebar.classList.add('collapsed');
                document.body.classList.add('alp-collapsed');
                if (main) main.style.marginLeft = '58px';
                localStorage.setItem('alp_sidebar_collapsed', '1');
            }
            // Asegurar que el overlay NO esté activo en desktop
            if (overlay) {
                overlay.classList.remove('active');
                overlay.style.display = 'none';
            }
        }
    }

    function closeSidebar() {
        if (isMobile() && sidebar && sidebar.classList.contains('mobile-open')) {
            sidebar.classList.remove('mobile-open');
            updateSidebar();
        }
    }

    // ─── CERRAR SIDEBAR ANTES DE NAVEGAR ──────────────────────
    function closeSidebarBeforeNavigate() {
        if (isMobile() && sidebar && sidebar.classList.contains('mobile-open')) {
            sidebar.classList.remove('mobile-open');
            if (overlay) {
                overlay.classList.remove('active');
                overlay.style.display = 'none';
            }
            document.body.style.overflow = '';
        }
    }

    /* ── Event Listeners ────────────────────────────────────── */
    if (toggleBtn) {
        toggleBtn.addEventListener('click', toggleSidebar);
    }

    if (overlay) {
        overlay.addEventListener('click', closeSidebar);
    }

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeSidebar();
    });

    // ─── CAPTURAR CLICS EN ENLACES DEL SIDEBAR ────────────────
    document.querySelectorAll('.alp-nav-item, .alp-sub-item').forEach(function(link) {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            // Si es un enlace interno (no #) y está en móvil
            if (href && href !== '#' && isMobile()) {
                // Cerrar el sidebar antes de navegar
                closeSidebarBeforeNavigate();
            }
        });
    });

    // ─── CAPTURAR NAVEGACIÓN CON BEFOREUNLOAD ──────────────────
    window.addEventListener('beforeunload', function() {
        // Limpiar overlay antes de salir
        if (overlay) {
            overlay.classList.remove('active');
            overlay.style.display = 'none';
        }
        document.body.style.overflow = '';
    });

    /* ── Resize ──────────────────────────────────────────────── */
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            // Si no es móvil, forzar overlay oculto
            if (!isMobile() && overlay) {
                overlay.classList.remove('active');
                overlay.style.display = 'none';
            }
            updateSidebar();
        }, 200);
    });

    /* ── Inicializar ──────────────────────────────────────────── */
    // Forzar overlay oculto al cargar si no es móvil
    if (!isMobile() && overlay) {
        overlay.classList.remove('active');
        overlay.style.display = 'none';
    }

    // Forzar overlay oculto en móvil al cargar
    if (isMobile() && overlay) {
        overlay.classList.remove('active');
        overlay.style.display = 'none';
        if (sidebar) sidebar.classList.remove('mobile-open');
    }

    updateSidebar();

    /* ── 2. SUBMENÚS ──────────────────────────────────────────── */
    window.alpToggleSub = function(subId, trigger) {
        const sub = document.getElementById(subId);
        if (!sub) return;
        const isOpen = sub.classList.contains('open');

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
    const themeIcon = document.getElementById('alpThemeIcon');

    function applyDarkMode(isDark) {
        document.documentElement.classList.toggle('dark', isDark);
        if (darkToggle) darkToggle.classList.toggle('on', isDark);
        if (themeIcon) themeIcon.className = isDark ? 'fa-regular fa-sun' : 'fa-regular fa-moon';
        localStorage.setItem('alp_dark', isDark ? '1' : '0');
    }

    applyDarkMode(localStorage.getItem('alp_dark') === '1');

    if (darkToggle) {
        darkToggle.addEventListener('click', () =>
            applyDarkMode(!document.documentElement.classList.contains('dark'))
        );
    }
    if (modeToggle) {
        modeToggle.addEventListener('click', () =>
            applyDarkMode(!document.documentElement.classList.contains('dark'))
        );
    }

    /* ── 7. FAB SELECTOR DE TEMA ─────────────────────────────── */
    const themeFab = document.getElementById('alpThemeFab');
    const themeOpts = document.getElementById('alpThemeOpts');
    if (themeFab && themeOpts) {
        themeFab.addEventListener('click', e => {
            e.stopPropagation();
            themeOpts.classList.toggle('open');
        });
        document.addEventListener('click', () => themeOpts.classList.remove('open'));
        themeOpts.addEventListener('click', e => e.stopPropagation());
    }

    /* ── 8. TOASTS ────────────────────────────────────────────── */
    let _toastStyle = document.getElementById('alp-toast-style');
    if (!_toastStyle) {
        _toastStyle = document.createElement('style');
        _toastStyle.id = 'alp-toast-style';
        document.head.appendChild(_toastStyle);
    }

    window.alpShowAlert = function(msg, type) {
        if (typeof Swal === 'undefined') return;

        const cs = getComputedStyle(document.documentElement);
        const bgCard = cs.getPropertyValue('--bg-card').trim() || '#fff';
        const bdrMid = cs.getPropertyValue('--border-mid').trim() || 'rgba(0,0,0,.14)';
        const txt1 = cs.getPropertyValue('--text-1').trim() || '#1A2332';
        const accent = cs.getPropertyValue('--accent').trim() || '#1E5CDB';

        const iconMap = {
            success: '#00A86B',
            error: '#EF4444',
            danger: '#EF4444',
            warning: '#F59E0B',
            info: accent,
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
            .alp-toast .swal2-success-ring { border-color: ${ic}40 !important; }
            .alp-toast .swal2-success-line-tip,
            .alp-toast .swal2-success-line-long { background: ${ic} !important; }
            .alp-toast .swal2-x-mark-line-left,
            .alp-toast .swal2-x-mark-line-right { background: ${ic} !important; }
            .alp-toast .swal2-timer-progress-bar { background: ${ic} !important; height: 3px !important; }
            .alp-toast .swal2-timer-progress-bar-container {
                border-radius: 0 0 10px 10px !important;
                overflow: hidden !important;
            }
        `;

        Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3500,
            timerProgressBar: true,
            scrollbarPadding: false,
            customClass: { popup: 'alp-toast' },
            didOpen: toast => {
                toast.addEventListener('mouseenter', Swal.stopTimer);
                toast.addEventListener('mouseleave', Swal.resumeTimer);
            }
        }).fire({
            icon: ({ success: 'success', error: 'error', danger: 'error', warning: 'warning', info: 'info' })[type] || 'info',
            title: msg
        });
    };

    /* ── 9. DISPARAR MENSAJES DJANGO ──────────────────────────── */
    if (Array.isArray(window.alpDjangoMessages)) {
        window.alpDjangoMessages.forEach(function(m) {
            alpShowAlert(m.msg, m.tags);
        });
    }

    /* ── 10. DIAGNÓSTICO ──────────────────────────────────────── */
    console.log('✅ AlpinaTrack JS cargado correctamente');
    console.log('📱 Modo móvil:', isMobile());
    console.log('📐 Ancho de pantalla:', window.innerWidth);

}); /* fin DOMContentLoaded */
