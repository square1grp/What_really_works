$(document).ready(function () {
    console.log($("#ended_treatment"))
    $("#ended_treatment").click(function () {
        if ($(this).prop("checked")) {
            $("#end_section").show();
            $("#start_severity_on_end_date").show();
        } else {
            $("#end_section").hide();
            $("#start_severity_on_end_date").hide();
        }
    });
})