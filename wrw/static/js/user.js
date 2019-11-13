$(document).ready(function () {
    $("a#redirect_to_symptom").click(function (e) {
        e.preventDefault();

        symptom_id = $("select.symptom").val();
        window.location.href = '/symptom/' + symptom_id.toString();
    });
});