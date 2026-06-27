// contar_cuvetas.js
document.addEventListener('DOMContentLoaded', function () {
    const grandes  = document.getElementById('id_cuvetas_grandes');
    const pequenas = document.getElementById('id_cuvetas_pequenas');
    const total    = document.getElementById('total-cuvetas');

    function actualizarTotal() {
        const g = parseInt(grandes.value)  || 0;
        const p = parseInt(pequenas.value) || 0;
        total.textContent = g + p;
    }

    if (grandes && pequenas) {
        grandes.addEventListener('input', actualizarTotal);
        pequenas.addEventListener('input', actualizarTotal);
        actualizarTotal();
    }
});