$(document).ready(function () {
    console.log($("#ended_treatment"))
    $("#ended_treatment").click(function () {
        if ($(this).prop("checked")) {
            $("#end_section").show();
            $("#end_severity").prop("disabled", false);
        } else {
            $("#end_section").hide();
            $("#end_severity").prop("disabled", true);
        }
    });
})