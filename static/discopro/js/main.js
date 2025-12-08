document.addEventListener('DOMContentLoaded', function() {

    const wrapper = document.getElementById("wrapper");
    const sidebarToggle = document.getElementById("sidebarToggle");
    const storageKey = 'discopro_sidebar_state';

    // =========================================================
    // 1. REACTIVAR ANIMACIONES (SOLUCIÓN FINAL AL PARPADEO)
    // =========================================================
    if (wrapper) {
        // Usamos requestAnimationFrame para asegurar que el navegador 
        // ya pintó el estado inicial antes de reactivar las transiciones.
        requestAnimationFrame(() => {
            setTimeout(() => {
                wrapper.classList.remove('no-transition');
            }, 50); // Un retraso mínimo imperceptible
        });
    }

    // =========================================================
    // 2. TOGGLE DEL SIDEBAR (CLICK)
    // =========================================================
    if (sidebarToggle && wrapper) {
        sidebarToggle.addEventListener("click", function(e) {
            e.preventDefault();
            wrapper.classList.toggle("toggled");

            // Guardar estado en memoria
            if (wrapper.classList.contains("toggled")) {
                localStorage.setItem(storageKey, 'hidden');
            } else {
                localStorage.setItem(storageKey, 'visible');
            }
        });
    }

    // =========================================================
    // 3. AUTO-CIERRE DE ALERTAS
    // =========================================================
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        setTimeout(function() {
            alerts.forEach(function(alert) {
                if (typeof bootstrap !== 'undefined') {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                } else {
                    alert.style.transition = "opacity 0.5s ease";
                    alert.style.opacity = 0;
                    setTimeout(() => alert.remove(), 500);
                }
            });
        }, 3000);
    }

    // =========================================================
    // 4. BUSCADOR CON BOTÓN 'X'
    // =========================================================
    const searchInputs = document.querySelectorAll('input[name="q"]');

    searchInputs.forEach(input => {
        const group = input.closest('.input-group');
        
        if (group) {
            const clearBtn = document.createElement('button');
            clearBtn.type = 'button'; 
            clearBtn.className = 'btn btn-secondary btn-clear-search'; 
            clearBtn.innerHTML = '<i class="bi bi-x-lg"></i>';
            clearBtn.title = 'Limpiar filtro';
            group.appendChild(clearBtn);

            const toggleClearBtn = () => {
                if (input.value.length > 0) {
                    clearBtn.style.display = 'inline-block'; 
                } else {
                    clearBtn.style.display = 'none';
                }
            };

            input.addEventListener('input', toggleClearBtn);
            toggleClearBtn();

            clearBtn.addEventListener('click', function() {
                input.value = '';  
                if (input.form) {
                    input.form.submit(); 
                }
            });
        }
    });

});