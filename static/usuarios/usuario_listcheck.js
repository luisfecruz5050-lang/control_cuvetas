document.addEventListener('DOMContentLoaded', function () {

    /* ── Utilidad: abrir/cerrar modal ─────────────────────── */
    function openModal(id)  { document.getElementById(id)?.classList.add('open'); }
    function closeModal(id) { document.getElementById(id)?.classList.remove('open'); }

    /* Cerrar al click fuera del panel */
    document.querySelectorAll('.alp-modal-backdrop').forEach(function (backdrop) {
        backdrop.addEventListener('click', function (e) {
            if (e.target === backdrop) backdrop.classList.remove('open');
        });
    });

    /* ── MODAL ROLES ───────────────────────────────────────── */
    const btnAbrirRoles     = document.getElementById('btnAbrirRoles');
    const btnCerrarRoles    = document.getElementById('cerrarRoles');
    const btnConfirmarRoles = document.getElementById('confirmarRoles');

    if (btnAbrirRoles)     btnAbrirRoles.addEventListener('click',     () => openModal('modalRoles'));
    if (btnCerrarRoles)    btnCerrarRoles.addEventListener('click',    () => closeModal('modalRoles'));
    if (btnConfirmarRoles) btnConfirmarRoles.addEventListener('click', () => closeModal('modalRoles'));

    function updateRolesBadge() {
        const n = document.querySelectorAll('#modalRoles input[type="checkbox"]:checked').length;
        const badgeRoles    = document.getElementById('badgeRoles');
        const rolesSelCount = document.getElementById('rolesSelCount');
        if (badgeRoles)    badgeRoles.textContent    = n;
        if (rolesSelCount) rolesSelCount.textContent = n;
        if (btnAbrirRoles) {
            const span = btnAbrirRoles.querySelector('span:first-child');
            if (span) span.innerHTML =
                n > 0
                ? '<i class="fa-solid fa-users"></i> ' + n + ' rol(es) seleccionado(s)'
                : '<i class="fa-solid fa-users"></i> Seleccionar roles';
        }
    }
    document.querySelectorAll('#modalRoles input[type="checkbox"]')
        .forEach(cb => cb.addEventListener('change', updateRolesBadge));
    updateRolesBadge();

    /* ── MODAL PERMISOS ────────────────────────────────────── */
    const btnAbrirPermisos     = document.getElementById('btnAbrirPermisos');
    const btnCerrarPermisos    = document.getElementById('cerrarPermisos');
    const btnConfirmarPermisos = document.getElementById('confirmarPermisos');

    if (btnAbrirPermisos)     btnAbrirPermisos.addEventListener('click',     () => openModal('modalPermisos'));
    if (btnCerrarPermisos)    btnCerrarPermisos.addEventListener('click',    () => closeModal('modalPermisos'));
    if (btnConfirmarPermisos) btnConfirmarPermisos.addEventListener('click', () => closeModal('modalPermisos'));

    function updatePermsBadge() {
        const n = document.querySelectorAll('#modalPermisos input[name="user_permissions"]:checked').length;
        const badgePermisos = document.getElementById('badgePermisos');
        const permsSelCount = document.getElementById('permsSelCount');
        if (badgePermisos)  badgePermisos.textContent = n;
        if (permsSelCount)  permsSelCount.textContent = n;

        if (btnAbrirPermisos) {
            const span = btnAbrirPermisos.querySelector('span:first-child');
            if (span) span.innerHTML =
                n > 0
                ? '<i class="fa-solid fa-key"></i> ' + n + ' permiso(s) adicional(es)'
                : '<i class="fa-solid fa-key"></i> Administrar permisos';
        }

        /* Contadores por módulo */
        document.querySelectorAll('.select-module-perm').forEach(function (master) {
            const mod = master.dataset.module;
            const all = document.querySelectorAll('.uperm-' + mod);
            const sel = document.querySelectorAll('.uperm-' + mod + ':checked');
            const cnt = document.getElementById('pcnt-' + mod);
            if (cnt) cnt.textContent = sel.length > 0 ? sel.length + '/' + all.length : '';
            master.checked = sel.length === all.length && all.length > 0;
        });
    }

    /* Toggle "seleccionar todos" por módulo en permisos */
    document.querySelectorAll('.select-module-perm').forEach(function (master) {
        master.addEventListener('change', function () {
            const mod = this.dataset.module;
            document.querySelectorAll('.uperm-' + mod)
                .forEach(cb => { cb.checked = master.checked; });
            updatePermsBadge();
        });
    });

    document.querySelectorAll('input[name="user_permissions"]')
        .forEach(cb => cb.addEventListener('change', updatePermsBadge));
    updatePermsBadge();

    /* ❌ ELIMINADO: Ya no necesitamos el código de click en labels
       porque CSS lo maneja con :has() */

    /* ── Cerrar con ESC ────────────────────────────────────── */
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            closeModal('modalRoles');
            closeModal('modalPermisos');
        }
    });

});