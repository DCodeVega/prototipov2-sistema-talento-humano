// Scripts generales del sistema

document.addEventListener('DOMContentLoaded', function() {
    // Validación de formularios
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let valid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    valid = false;
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!valid) {
                e.preventDefault();
                alert('Por favor complete todos los campos obligatorios.');
            }
        });
    });
    
    // Auto-uppercase para nombres y apellidos
    const textFields = document.querySelectorAll('input[type="text"]');
    textFields.forEach(field => {
        field.addEventListener('blur', function() {
            if (this.name.includes('nombre') || this.name.includes('apellido')) {
                this.value = this.value.toUpperCase();
            }
        });
    });
});