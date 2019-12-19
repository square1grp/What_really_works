$(document).ready(function () {
    var func_checkBoxesStatesCheck = function () {
        $.each($("select#user_symptom_id option"), function (idx, selector) {
            var user_symptom_id = $(selector).val();

            var start_symptom_severity_id = $("input.start_symptom_severity_id[symptom-id=" + user_symptom_id + "]").val();
            var today_symptom_severity_id = $("input.today_symptom_severity_id[symptom-id=" + user_symptom_id + "]").val();

            if (start_symptom_severity_id && start_symptom_severity_id != -1) {

                if (
                    !$("#is_ended").prop("checked") ||
                    $("#is_ended").prop("checked") && (today_symptom_severity_id && today_symptom_severity_id != -1)
                ) {
                    $("input.filled-out-" + user_symptom_id).prop("checked", true);

                    return true;
                }
            }

            $("input.filled-out-" + user_symptom_id).prop("checked", false);
        });
    };

    var checkOffSymptomInterval = setInterval(func_checkBoxesStatesCheck, 500);

    var checkOffSymptom = function () {
        clearInterval(checkOffSymptomInterval);

        if ($("form#new_treatment.was-validated .form-control:invalid").length > 0) {
            $("input[class*=filled-out-]").prop("checked", false);
            return false;
        }

        checkOffSymptomInterval = setInterval(func_checkBoxesStatesCheck, 500);

        var user_symptom_id = $("select#user_symptom_id").val();
        var start_symptom_severity_id = $("select#start_symptom_severity_id").val();
        var today_symptom_severity_id = $("select#today_symptom_severity_id").val();

        $("input.start_symptom_severity_id[symptom-id=" + user_symptom_id + "]").val(start_symptom_severity_id);
        $("input.today_symptom_severity_id[symptom-id=" + user_symptom_id + "]").val(today_symptom_severity_id);
    };

    $("#is_ended").change(function () {
        if ($(this).prop("checked")) {
            $(".form-group.end .form-control").prop("required", true);
        } else {
            $(".form-group.end .form-control").prop("required", false);
        }

        $(".form-group.end").slideToggle("fast");
        checkOffSymptom()
    });

    $("select#user_symptom_id").change(function () {
        $("select#start_symptom_severity_id").val("");
        $("select#today_symptom_severity_id").val("");
        $("form#new_treatment").removeClass("was-validated").addClass("needs-validation");
    });

    $("select#start_symptom_severity_id").change(function () {
        $("form#new_treatment").removeClass("needs-validation").addClass("was-validated");

        checkOffSymptom();
    });

    $("form#new_treatment .form-control").change(function () {
        checkOffSymptom();
    }).keyup(function () {
        checkOffSymptom();
    });

    setInterval(function () {
        $.each($("input[class*=filled-out-]"), function (idx, selector) {
            if (!$(selector).prop("checked")) {
                $("form#new_treatment button").prop("disabled", true);
            } else {
                $("form#new_treatment button").prop("disabled", false);
            }
        });
    }, 500);

    $(".added-treatment-form a").click(function () {
        var action = "";

        if ($(this).hasClass("edit")) {
            action = "edit";
        } else if ($(this).hasClass("delete")) {
            action = "delete";
        }

        $(this).siblings("input[name=action]").val(action);
        $(this).parent("form.added-treatment-form").submit();
    });
});


// start/end date validation
$(document).ready(function () {
    $.each(mdfv, function () {
        for (var i = 0; i < this.length; i++) {
            this[i].started_at = new Date(this[i].started_at);
            this[i].ended_at = new Date(this[i].ended_at);
        }
    });

    var init_date_pickers = function () {
        var id = $("select#method_id").val();

        $("#started_at").datepicker({
            autoclose: true,
            maxDate: new Date(),
            changeMonth: true,
            changeYear: true,
            beforeShowDay: function (date) {
                var dates_list = mdfv['method_' + id];

                if (!dates_list)
                    return [true]

                for (var i = 0; i < dates_list.length; i++) {
                    if ((date >= dates_list[i].started_at) && (date <= dates_list[i].ended_at)) {
                        return [false];
                    }
                }

                return [true];
            }
        });

        $("#started_at").datepicker("setDate", started_at_date);

        $("#ended_at").datepicker({
            autoclose: true,
            maxDate: new Date(),
            changeMonth: true,
            changeYear: true,
            beforeShowDay: function (date) {
                var dates_list = mdfv['method_' + id];

                if (!dates_list)
                    return [true]

                for (var i = 0; i < dates_list.length; i++) {
                    if ((date >= dates_list[i].started_at) && (date <= dates_list[i].ended_at)) {
                        return [false];
                    }
                }

                return [true];
            }
        });

        $("#ended_at").datepicker("setDate", ended_at_date);
    };

    init_date_pickers();

    $("select#method_id").change(function () {
        $("#started_at").datepicker("destroy");
        $("#ended_at").datepicker("destroy");

        init_date_pickers();
    });

    $("#started_at").change(function () {
        var start_date = $(this).datepicker("getDate");
        var id = $("select#method_id").val();
        var dates_list = mdfv['method_' + id];

        if (!dates_list) {
            return;
        }

        var max_date = undefined;

        for (var i = 0; i < dates_list.length; i++) {
            if (start_date < dates_list[i].started_at) {
                if (!max_date) {
                    max_date = dates_list[i].started_at
                } else if (dates_list[i].started_at < max_date) {
                    max_date = dates_list[i].started_at
                }
            }
        }

        if (max_date) {
            $("#ended_at").datepicker("option", "maxDate", new Date(max_date.getTime() - (1000 * 60 * 60 * 24)));
        } else {
            $("#ended_at").datepicker("option", "maxDate", new Date());
        }
    });
});