
window.dsgovbrAdminFiltersInit = function() {
    var filterBar = document.getElementById('filter-bar');
    var tagsContainer = document.getElementById('filter-tags');
    var form = document.getElementById('changelist-form'); // Corrigido para o form correto

    // Evita múltiplos event listeners
    if (filterBar && !filterBar._dsgovbrFilterListenerAdded) {
        filterBar.addEventListener('click', function(e) {
            var el = e.target;
            while (el && !el.classList.contains('filter_choice')) {
                if (el === filterBar) return;
                el = el.parentElement;
            }
            if (!el || !el.classList.contains('filter_choice')) return;
            e.preventDefault();
            var fieldName = el.getAttribute('data-field-name');
            var fieldTitle = el.getAttribute('data-field-title');
            var value = el.getAttribute('data-value');
            var display = el.getAttribute('data-display');
            if (!fieldName || !value) {
                return;
            }

            // Remove tag/input antigos para o mesmo filtro
            if (tagsContainer) {
                var oldTag = tagsContainer.querySelector('[data-field-name="' + fieldName + '"]');
                if (oldTag) oldTag.remove();
            }
            if (form) {
                var oldInput = form.querySelector('input[name="' + fieldName + '"]');
                if (oldInput) oldInput.remove();
            }

            var tag = document.createElement('span');
            tag.className = 'badge text-bg-primary d-inline-flex align-items-center gap-2';
            tag.setAttribute('data-field-name', fieldName);
            tag.appendChild(document.createTextNode(fieldTitle + ': ' + display));

            var closeButton = document.createElement('button');
            closeButton.className = 'btn-close btn-close-white';
            closeButton.type = 'button';
            closeButton.setAttribute('aria-label', 'Remover o filtro ' + fieldTitle);
            tag.appendChild(closeButton);

            if (tagsContainer) tagsContainer.appendChild(tag);

            var input = document.createElement('input');
            input.type = 'hidden';
            input.name = fieldName;
            input.value = value;
            if (form) form.appendChild(input);

            closeButton.addEventListener('click', function() {
                tag.remove();
                input.remove();
            });
        });
        filterBar._dsgovbrFilterListenerAdded = true;
    }
}

// Inicializa automaticamente ao carregar o script
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.dsgovbrAdminFiltersInit);
} else {
    window.dsgovbrAdminFiltersInit();
}
