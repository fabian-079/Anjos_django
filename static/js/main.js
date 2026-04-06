document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss alerts after 5 seconds
    document.querySelectorAll('.alert.alert-dismissible').forEach(function (alert) {
        setTimeout(function () {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // Confirm on delete forms
    document.querySelectorAll('form[data-confirm]').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            if (!confirm(form.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });

    // Quantity input clamp in cart
    document.querySelectorAll('input[name="quantity"]').forEach(function (input) {
        input.addEventListener('change', function () {
            var val = parseInt(this.value);
            var min = parseInt(this.min) || 1;
            var max = parseInt(this.max) || 9999;
            if (isNaN(val) || val < min) this.value = min;
            if (val > max) this.value = max;
        });
    });
});
