// contar_cuvetas.js

// ── 1. Contador de cuvetas (total en tiempo real) ─────────────
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

// ── 2. Select2 con búsqueda AJAX para el campo Cliente ─────────
document.addEventListener('DOMContentLoaded', function () {
    // Si jQuery o select2 no están cargados en esta página, no truena, solo no hace nada
    if (typeof jQuery === 'undefined' || typeof jQuery.fn.select2 === 'undefined') {
        return;
    }

    const $ = jQuery;
    const $clienteSelect = $('#id_cliente');

    if ($clienteSelect.length === 0) {
        return;
    }

    $clienteSelect.select2({
        placeholder: 'Buscar cliente...',
        minimumInputLength: 2,
        language: {
            inputTooShort: function () {
                return 'Escribe al menos 2 letras...';
            },
            searching: function () {
                return 'Buscando...';
            },
            noResults: function () {
                return 'No se encontraron clientes';
            }
        },
        ajax: {
            url: $clienteSelect.data('ajax-url'),
            dataType: 'json',
            delay: 300,
            data: function (params) {
                return {
                    term: params.term || '',
                    page: params.page || 1
                };
            },
            processResults: function (data, params) {
                params.page = params.page || 1;
                return {
                    results: data.results,
                    pagination: { more: data.pagination.more }
                };
            },
            cache: true
        }
    });
});

// ── 2. Select2 con búsqueda AJAX (reutilizable para cualquier campo) ───
document.addEventListener('DOMContentLoaded', function () {
    if (typeof jQuery === 'undefined' || typeof jQuery.fn.select2 === 'undefined') {
        return;
    }

    const $ = jQuery;

    // Selecciona TODOS los selects que tengan data-ajax-url, no solo #id_cliente
    $('[data-ajax-url]').each(function () {
        const $select = $(this);

        // Evita inicializar dos veces el mismo select
        if ($select.hasClass('select2-hidden-accessible')) {
            return;
        }

        $select.select2({
            placeholder: $select.data('placeholder') || 'Buscar...',
            minimumInputLength: $select.data('min-length') ?? 2,
            allowClear: $select.data('allow-clear') === true,
            language: {
                inputTooShort: function () {
                    return `Escribe al menos ${$select.data('min-length') ?? 2} letras...`;
                },
                searching: function () {
                    return 'Buscando...';
                },
                noResults: function () {
                    return 'Sin resultados';
                }
            },
            ajax: {
                url: $select.data('ajax-url'),
                dataType: 'json',
                delay: 300,
                data: function (params) {
                    return {
                        term: params.term || '',
                        page: params.page || 1
                    };
                },
                processResults: function (data, params) {
                    params.page = params.page || 1;
                    return {
                        results: data.results,
                        pagination: { more: data.pagination.more }
                    };
                },
                cache: true
            }
        });
    });
});
