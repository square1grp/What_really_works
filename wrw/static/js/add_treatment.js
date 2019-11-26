var clearTreatmentForm = function () {
    $("form#new_treatment .form-control:not(#symptom_id)").prop("disabled", false);
    $("form#new_treatment .form-check-input:not(.filled-out)").prop("disabled", false);
    $("form#new_treatment button").prop("disabled", false);

    $("select#method_id").val("");
    $("#started_at").datepicker("setDate", new Date());
    $("select[name=start_severity_id]").val("");
    $("select[name=start_drawback_id]").val("");
    $("#ended_at").datepicker("setDate", new Date());
    $("select[name=end_severity_id]").val("");
    $("select[name=end_drawback_id]").val("");

    $("input[name=start_title]").val("");
    $("textarea[name=start_description]").val("");

    $("input[name=end_title]").val("");
    $("textarea[name=end_description]").val("");

    $("#ended_treatment").prop("checked", false);
    $("#end_section .form-control").prop("required", false);
    $("#end_section").hide();
    $("#start_severity_on_end_date .form-control").prop("required", false);
    $("#start_severity_on_end_date").hide();
};

var fillTreatmentForm = function (user_treatment) {
    $("form#new_treatment .form-control:not(#symptom_id)").prop("disabled", true);
    $("form#new_treatment .form-check-input").prop("disabled", true);
    $("form#new_treatment button").prop("disabled", true);

    $("select#method_id").val(user_treatment.method_id);

    if (user_treatment.started_at_str)
        $("#started_at").datepicker("setDate", user_treatment.started_at_str);

    $("select[name=start_severity_id]").val(user_treatment.started_severity_id);
    $("select[name=start_drawback_id]").val(user_treatment.started_drawback_id);

    if (user_treatment.ended_at_str)
        $("#ended_at").datepicker("setDate", user_treatment.ended_at_str);

    if (user_treatment.ended_severity_id)
        $("select[name=end_severity_id]").val(user_treatment.ended_severity_id);

    if (user_treatment.ended_drawback_id)
        $("select[name=end_drawback_id]").val(user_treatment.ended_drawback_id);

    if (user_treatment.ended_at_str || user_treatment.ended_severity_id || user_treatment.ended_drawback_id) {
        $("#ended_treatment").prop("checked", true);

        $("#end_section .form-control").prop("required", true);
        $("#end_section").show();

        $("#start_severity_on_end_date .form-control").prop("required", true);
        $("#start_severity_on_end_date").show();
    } else {
        $("#ended_treatment").prop("checked", false);

        $("#end_section .form-control").prop("required", false);
        $("#end_section").hide();

        $("#start_severity_on_end_date .form-control").prop("required", false);
        $("#start_severity_on_end_date").hide();
    }
};

var initTreatmentForm = function (user_treatments) {
    $.each(user_treatments, function (idx, user_treatment) {
        var user_symptom_id = $("select[name=user_symptom_id]").val();

        if (user_symptom_id != user_treatment.user_symptom_id)
            return true;

        fillTreatmentForm(user_treatment);
    });
};

$(document).ready(function () {
    var user_treatments = JSON.parse(document.getElementById('user-treatments').textContent);
    var last_formdata = JSON.parse(document.getElementById('last-formdata').textContent);

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

    if (last_formdata) {
        $("select[name=user_symptom_id]").val(last_formdata.user_symptom_id);

        last_formdata['started_severity_id'] = last_formdata.start_severity_id;
        last_formdata['started_drawback_id'] = last_formdata.start_drawback_id;
        last_formdata['started_at_str'] = last_formdata.started_at;

        last_formdata['ended_severity_id'] = last_formdata.end_severity_id;
        last_formdata['ended_drawback_id'] = last_formdata.end_drawback_id;
        last_formdata['ended_at_str'] = last_formdata.ended_at;

        fillTreatmentForm(last_formdata);

        if (last_formdata['ended_treatment'] != 'on') {
            $("#ended_treatment").prop("checked", false);

            $("#end_section .form-control").prop("required", false);
            $("#end_section").hide();

            $("#start_severity_on_end_date .form-control").prop("required", false);
            $("#start_severity_on_end_date").hide();
        }

        $("input[name=start_title]").val(last_formdata.start_title);
        $("textarea[name=start_description]").val(last_formdata.start_description);

        $("input[name=end_title]").val(last_formdata.end_title);
        $("textarea[name=end_description]").val(last_formdata.end_description);
    }

    $("select[name=user_symptom_id]").change(function () {
        $("form#new_treatment").removeClass("was-validated").addClass("needs-validation");
        clearTreatmentForm();
        initTreatmentForm(user_treatments)
    });
})