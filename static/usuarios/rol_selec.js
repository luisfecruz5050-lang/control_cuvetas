document.addEventListener('DOMContentLoaded', function () {

    /* ── Actualiza contadores de permisos seleccionados ── */
    function updateCounters() {
        let total = 0;

        document.querySelectorAll('.alp-modal-perm-module').forEach(module => {
            const checks = module.querySelectorAll('input[type="checkbox"][name="permissions"]');
            const selected = [...checks].filter(c => c.checked).length;
            total += selected;

            const selAll = module.querySelector('.select-module');
            if (!selAll) return;

            const modName = selAll.dataset.module;
            const counter = document.getElementById('pcnt-' + modName);
            if (counter) {
                counter.textContent = selected > 0 ? selected + '/' + checks.length : '';
                counter.classList.toggle('has-selected', selected > 0);
            }

            selAll.checked = selected === checks.length && checks.length > 0;
        });

        const totalEl = document.getElementById('totalCounter');
        if (totalEl) {
            totalEl.textContent = total > 0 ? total + ' seleccionado' + (total !== 1 ? 's' : '') : '0 seleccionados';
            totalEl.classList.toggle('has-selected', total > 0);
        }
    }

    /* ── Toggle "seleccionar todos" del módulo ── */
    document.querySelectorAll('.select-module').forEach(function (master) {
        master.addEventListener('change', function () {
            const modulo = this.dataset.module;
            document.querySelectorAll('.perm-' + modulo).forEach(function (cb) {
                cb.checked = master.checked;
            });
            updateCounters();
        });
    });

    /* ── Actualiza contadores al cambiar cualquier permiso ── */
    document.querySelectorAll('input[name="permissions"]').forEach(function (cb) {
        cb.addEventListener('change', updateCounters);
    });

    /* ── Inicializar contadores al cargar ── */
    updateCounters();

    /* ❌ ELIMINADO: Ya no necesitamos el código de click en labels porque CSS lo maneja */

});