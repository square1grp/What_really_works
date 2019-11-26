$(document).ready(function () {
    console.log($("#ended_treatment"))
    $("#ended_treatment").click(function () {
        if ($(this).prop("checked")) {
            $("#end_section .form-control").prop("required", true);
            $("#end_section").show();

            $("#start_severity_on_end_date .form-control").prop("required", true);
            $("#start_severity_on_end_date").show();
        } else {
            $("#end_section .form-control").prop("required", false);
            $("#end_section").hide();

            $("#start_severity_on_end_date .form-control").prop("required", false);
            $("#start_severity_on_end_date").hide();
        }
    });
})