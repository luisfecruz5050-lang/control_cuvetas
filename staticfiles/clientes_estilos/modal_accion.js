// ============================================================
// FUNCIONES PARA EL MODAL DE EXCEL
// ============================================================

function abrirModalExcel() {
    const modal = document.getElementById('modal-excel');
    modal.style.display = 'flex';
    // Pequeño delay para activar la animación
    setTimeout(function() {
        modal.classList.add('open');
    }, 10);
}

function cerrarModalExcel() {
    const modal = document.getElementById('modal-excel');
    modal.classList.remove('open');
    // Restaurar scroll del body después de la animación
    setTimeout(function() {
        modal.style.display = 'none';
    }, 250);
}

// Mostrar nombre del archivo seleccionado
document.addEventListener('DOMContentLoaded', function() {
    const inputArchivo = document.getElementById('archivo_excel');
    if (inputArchivo) {
        inputArchivo.addEventListener('change', function () {
            const label = document.getElementById('nombre-archivo');
            if (this.files.length > 0) {
                label.textContent = '📄 ' + this.files[0].name;
                label.style.display = 'block';
            } else {
                label.style.display = 'none';
            }
        });
    }

    // Cerrar modal de Excel con Escape
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            const modal = document.getElementById('modal-excel');
            if (modal && modal.classList.contains('open')) {
                cerrarModalExcel();
            }
        }
    });

    // Cerrar modal al hacer clic fuera del contenido
    const modalBackdrop = document.getElementById('modal-excel');
    if (modalBackdrop) {
        modalBackdrop.addEventListener('click', function(e) {
            if (e.target === this) {
                cerrarModalExcel();
            }
        });
    }

    // Asegurar que el modal NO se abra automáticamente
    const modal = document.getElementById('modal-excel');
    if (modal) {
        modal.classList.remove('open');
        modal.style.display = 'none';
    }
});
