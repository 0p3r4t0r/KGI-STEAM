//https://docs.djangoproject.com/en/3.0/ref/contrib/admin/javascript/
(function($) {
    $(document).on('formset:added', function(event, $row, formsetName) {
        if (formsetName == 'lesson_set') {
            prevNumberFieldVal = parseInt($("#id_" + $row[0].previousElementSibling.id + "-number").val());
            newNumberField = $("#id_" + $row[0].id + "-number");
            newNumberField.val(prevNumberFieldVal + 1);
        }
    });

    $(document).on('formset:removed', function(event, $row, formsetName) {
        // Row removed
    });
})(django.jQuery);
