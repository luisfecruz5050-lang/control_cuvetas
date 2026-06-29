/* ================================================================
   alp_confirm.js
   Modal de confirmación unificado — Sistema AlpinaTrack
   Compatible con el tema principal (variables CSS, modo oscuro)
   Soporta:
     · confirmDelete(event)        → GET  (eliminar)
     · confirmAction(event, título, texto) → POST (rechazar, etc.)
   Sin SweetAlert2, totalmente nativo y adaptado al tema activo
================================================================ */

document.addEventListener('DOMContentLoaded', function () {

    /* ── 1. Crear el modal una sola vez en el DOM ──────────── */
    const modal = document.createElement('div');
    modal.id        = 'alp-confirm-modal';
    modal.className = 'alp-modal-backdrop';
    modal.innerHTML = `
        <div class="alp-confirm-panel" role="dialog" aria-modal="true" aria-labelledby="ac-title">
            <div class="alp-confirm-icon">
                <i class="fa-solid fa-triangle-exclamation"></i>
            </div>
            <h3 id="ac-title" class="alp-confirm-title">¿Estás seguro?</h3>
            <p id="ac-text" class="alp-confirm-text">Esta acción no se puede revertir.</p>
            <div class="alp-confirm-actions">
                <button id="ac-cancel" class="alp-btn alp-btn-ghost">Cancelar</button>
                <button id="ac-confirm" class="alp-btn alp-btn-danger">Sí, eliminar</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);

    /* ── 2. Estilos del panel (inyectados una sola vez) ─────── */
    const style = document.createElement('style');
    style.textContent = `
        /* Backdrop - Fondo semitransparente con blur */
        #alp-confirm-modal.alp-modal-backdrop {
            position        : fixed;
            inset           : 0;
            background      : rgba(0, 0, 0, 0.65);
            backdrop-filter : blur(4px);
            display         : flex;
            align-items     : center;
            justify-content : center;
            z-index         : 10000;
            opacity         : 0;
            visibility      : hidden;
            transition      : opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1),
                              visibility 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }

        #alp-confirm-modal.alp-modal-backdrop.open {
            opacity    : 1;
            visibility : visible;
        }

        /* Panel central - Estilo AlpinaTrack */
        .alp-confirm-panel {
            background    : var(--bg-card);
            border        : 1px solid var(--border-mid);
            border-radius : 20px;
            padding       : 32px 28px 28px;
            width         : 100%;
            max-width     : 380px;
            text-align    : center;
            box-shadow    : var(--shadow-lg);
            transform     : scale(0.94) translateY(8px);
            transition    : transform 0.22s cubic-bezier(0.4, 0, 0.2, 1);
        }

        #alp-confirm-modal.alp-modal-backdrop.open .alp-confirm-panel {
            transform : scale(1) translateY(0);
        }

        /* Ícono de advertencia */
        .alp-confirm-icon {
            width          : 64px;
            height         : 64px;
            border-radius  : 50%;
            background     : var(--clr-red-soft);
            border         : 2px solid rgba(239, 68, 68, 0.3);
            display        : flex;
            align-items    : center;
            justify-content: center;
            margin         : 0 auto 20px;
            font-size      : 28px;
            color          : var(--clr-red);
            box-shadow     : 0 0 0 4px rgba(239, 68, 68, 0.1);
        }

        /* Título */
        .alp-confirm-title {
            font-family   : 'Space Grotesk', sans-serif;
            font-size     : 20px;
            font-weight   : 700;
            color         : var(--text-1);
            margin        : 0 0 10px;
            letter-spacing: -0.3px;
        }

        /* Texto descriptivo */
        .alp-confirm-text {
            font-family   : 'Inter', sans-serif;
            font-size     : 13px;
            color         : var(--text-3);
            margin        : 0 0 28px;
            line-height   : 1.6;
        }

        /* Contenedor de botones */
        .alp-confirm-actions {
            display : flex;
            gap     : 12px;
        }

        .alp-confirm-actions .alp-btn {
            flex           : 1;
            justify-content: center;
            padding        : 10px 16px;
            font-weight    : 600;
        }

        /* Botón peligro (rojo AlpinaTrack) */
        .alp-btn-danger {
            background : var(--clr-red-soft);
            color      : var(--clr-red);
            border     : 1px solid rgba(239, 68, 68, 0.3);
        }

        .alp-btn-danger:hover {
            background   : rgba(239, 68, 68, 0.22);
            border-color : rgba(239, 68, 68, 0.5);
            color        : var(--clr-red);
            transform    : translateY(-1px);
            box-shadow   : 0 4px 12px rgba(239, 68, 68, 0.2);
        }

        /* Botón ghost personalizado para el modal */
        .alp-confirm-actions .alp-btn-ghost {
            background : var(--bg-root);
            border     : 1px solid var(--border-mid);
            color      : var(--text-2);
        }

        .alp-confirm-actions .alp-btn-ghost:hover {
            background : var(--bg-hover);
            color      : var(--text-1);
            border-color: var(--accent-border);
            transform  : translateY(-1px);
        }

        /* Animación de entrada para el ícono */
        @keyframes alpShake {
            0%, 100% { transform: scale(1); }
            25% { transform: scale(1.1); }
            75% { transform: scale(0.95); }
        }

        #alp-confirm-modal.alp-modal-backdrop.open .alp-confirm-icon {
            animation: alpShake 0.3s ease-out;
        }

        /* Responsive */
        @media (max-width: 480px) {
            .alp-confirm-panel {
                margin: 20px;
                padding: 24px 20px 20px;
                max-width: 90%;
            }

            .alp-confirm-title {
                font-size: 18px;
            }

            .alp-confirm-actions {
                flex-direction: column;
            }

            .alp-confirm-actions .alp-btn {
                width: 100%;
            }
        }
    `;
    document.head.appendChild(style);

    /* ── 3. Referencias a elementos del DOM ─────────────────── */
    const btnCancel  = document.getElementById('ac-cancel');
    const btnConfirm = document.getElementById('ac-confirm');
    const titleEl    = document.getElementById('ac-title');
    const textEl     = document.getElementById('ac-text');

    /* Estado interno: modo GET (url) o modo POST (form) */
    let pendingUrl  = null;
    let pendingForm = null;

    /* ── 4. Funciones para abrir/cerrar el modal ────────────── */
    function openModal(opts) {
        titleEl.textContent    = opts.titulo  || '¿Estás seguro?';
        textEl.textContent     = opts.texto   || 'Esta acción no se puede revertir.';
        btnConfirm.textContent = opts.btnText || 'Sí, eliminar';
        modal.classList.add('open');

    }

    function closeModal() {
        modal.classList.remove('open');
        pendingUrl  = null;
        pendingForm = null;

    }

    /* Cerrar al hacer click fuera del panel */
    modal.addEventListener('click', function (e) {
        if (e.target === modal) closeModal();
    });

    /* Cerrar con tecla ESC */
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && modal.classList.contains('open')) closeModal();
    });

    /* Botón Cancelar */
    btnCancel.addEventListener('click', closeModal);

    /* Botón Confirmar - ejecuta la acción según el modo */
    btnConfirm.addEventListener('click', function () {
        if (pendingUrl) {
            window.location.href = pendingUrl;   // GET → eliminar
        }
        if (pendingForm) {
            pendingForm.submit();                 // POST → rechazar, etc.
        }
        closeModal();
    });

    /* ── 5. Funciones globales para usar en los templates ──────── */

    /**
     * confirmDelete(event)
     * Usar en: <a href="{% url 'eliminar_cliente' pk %}" onclick="return confirmDelete(event)">
     * Intercepta la navegación GET y muestra el modal.
     */
    window.confirmDelete = function (event) {
        event.preventDefault();
        pendingUrl  = event.currentTarget.href;
        pendingForm = null;
        openModal({
            titulo  : '¿Eliminar registro?',
            texto   : 'Esta acción no se puede deshacer. El registro será eliminado permanentemente.',
            btnText : 'Sí, eliminar'
        });
        return false;
    };

    /**
     * confirmAction(event, titulo, texto, btnText)
     * Usar en: <form onsubmit="return confirmAction(event, 'Título', 'Mensaje descriptivo', 'Confirmar')">
     * Intercepta el submit POST y muestra el modal.
     *
     * @param {Event} event - Evento del formulario
     * @param {string} titulo - Título del modal (opcional)
     * @param {string} texto - Texto descriptivo (opcional)
     * @param {string} btnText - Texto del botón confirmar (opcional)
     */
    window.confirmAction = function (event, titulo, texto, btnText) {
        event.preventDefault();
        pendingForm = event.currentTarget;
        pendingUrl  = null;
        openModal({
            titulo  : titulo  || '¿Estás seguro?',
            texto   : texto   || 'Esta acción no se puede revertir.',
            btnText : btnText || 'Sí, confirmar'
        });
        return false;
    };

    /**
     * confirmCustom(event, options)
     * Versión avanzada con opciones personalizadas
     *
     * @param {Event} event - Evento del elemento
     * @param {Object} options - { titulo, texto, btnText, tipo }
     * tipo: 'danger' (rojo), 'warning' (ámbar), 'info' (azul)
     */
    window.confirmCustom = function (event, options) {
        event.preventDefault();

        const tipo = options.tipo || 'danger';
        let iconColor, bgColor, btnColor;

        if (tipo === 'warning') {
            iconColor = 'var(--clr-amber)';
            bgColor = 'var(--clr-amber-soft)';
            btnColor = 'var(--clr-amber)';
        } else if (tipo === 'info') {
            iconColor = 'var(--accent)';
            bgColor = 'var(--accent-soft)';
            btnColor = 'var(--accent)';
        } else {
            iconColor = 'var(--clr-red)';
            bgColor = 'var(--clr-red-soft)';
            btnColor = 'var(--clr-red)';
        }

        // Cambiar dinámicamente los colores del ícono
        const iconDiv = document.querySelector('.alp-confirm-icon');
        if (iconDiv) {
            iconDiv.style.background = bgColor;
            iconDiv.style.color = iconColor;
        }

        // Cambiar color del botón de confirmación
        btnConfirm.style.background = bgColor;
        btnConfirm.style.color = iconColor;
        btnConfirm.style.borderColor = `rgba(${tipo === 'danger' ? '239,68,68' : tipo === 'warning' ? '245,158,11' : '30,92,219'}, 0.3)`;

        pendingForm = event.currentTarget;
        pendingUrl = event.currentTarget.href || null;

        openModal({
            titulo  : options.titulo || '¿Estás seguro?',
            texto   : options.texto || 'Esta acción no se puede revertir.',
            btnText : options.btnText || 'Confirmar'
        });

        return false;
    };

});
