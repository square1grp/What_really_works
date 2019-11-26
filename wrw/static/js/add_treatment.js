var func_checkBoxesStatesCheck = function () {
    $.each($("select#user_symptom_id option"), function (idx, selector) {
        var user_symptom_id = $(selector).val();

        var start_severity_id = $("input.start_severity_id[symptom-id=" + user_symptom_id + "]").val();
        var end_severity_id = $("input.end_severity_id[symptom-id=" + user_symptom_id + "]").val();

        if ((start_severity_id && start_severity_id != -1) || (end_severity_id && end_severity_id != -1)) {
            $("input.filled-out-" + user_symptom_id).prop("checked", true);

            return true;
        }

        $("input.filled-out-" + user_symptom_id).prop("checked", false);
    });
};

$(document).ready(function () {
    var checkOffSymptomInterval = setInterval(func_checkBoxesStatesCheck, 500);

    var checkOffSymptom = function () {
        clearInterval(checkOffSymptomInterval);

        if ($("form#new_treatment.was-validated .form-control:invalid").length > 0) {
            $("input[class*=filled-out-]").prop("checked", false);
            return false;
        }

        checkOffSymptomInterval = setInterval(func_checkBoxesStatesCheck, 500);

        var user_symptom_id = $("select#user_symptom_id").val();
        var start_severity_id = $("select#start_severity_id").val();
        var end_severity_id = $("select#end_severity_id").val();

        $("input.start_severity_id[symptom-id=" + user_symptom_id + "]").val(start_severity_id);
        $("input.end_severity_id[symptom-id=" + user_symptom_id + "]").val(end_severity_id);
    };

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

        checkOffSymptom();
    });

    $("select#user_symptom_id").change(function () {
        $("select#start_severity_id").val("");
        $("form#new_treatment").removeClass("was-validated").addClass("needs-validation");
    });

    $("select#start_severity_id").change(function () {
        $("form#new_treatment").removeClass("needs-validation").addClass("was-validated");

        checkOffSymptom();
    });

    $("form#new_treatment .form-control").change(function () {
        checkOffSymptom();
    });

    setInterval(function () {
        $.each($("input[class*=filled-out-]"), function (idx, selector) {
            if (!$(selector).prop("checked")) {
                $("form#new_treatment button").prop("disabled", true);
                return false;
            }

            $("form#new_treatment button").prop("disabled", false);
        });
    }, 500);
});