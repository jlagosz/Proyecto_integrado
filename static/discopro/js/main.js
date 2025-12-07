document.addEventListener('DOMContentLoaded', function() {

    //  SIDEBAR TOGGLE
    const sidebarToggle = document.getElementById("sidebarToggle");
    const wrapper = document.getElementById("wrapper");

    if (sidebarToggle && wrapper) {
        sidebarToggle.addEventListener("click", function(e) {
            e.preventDefault();
            wrapper.classList.toggle("toggled");
        });
    }

    //  AUTO-CIERRE DE ALERTAS
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


    // 3. BUSCADOR CON X
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