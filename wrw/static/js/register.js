$(document).ready(function () {
    $("#first_name").change(function () {
        var first_name = $("#first_name").val();
        $("#first_name").val(first_name.charAt(0).toUpperCase() + first_name.slice(1));
    });

    $("#last_name").change(function () {
        var last_name = $("#last_name").val();
        $("#last_name").val(last_name.charAt(0).toUpperCase() + last_name.slice(1));
    });

    $("#register-form").submit(function () {
        $.each($("#password, #confirm_password"), function () {
            var password = $(this).val();

            if (password.length == 0)
                return false;

            var is_valid = true;

            if (!/\d/.test(password)) {
                is_valid = false;
            }

            if (!/[a-zA-Z]/.test(password)) {
                is_valid = false;
            }

            if (!/[(@!#\$%\^\&*\)\(+=._-]/.test(password)) {
                is_valid = false;
            }

            if (is_valid) {
                this.setCustomValidity("")
            } else {
                this.setCustomValidity("invalid")
            }

            if ($("#password").val() != $("#confirm_password").val()) {
                $.each($("#password, #confirm_password"), function () {
                    this.setCustomValidity("invalid")
                });
            } else {
                $.each($("#password, #confirm_password"), function () {
                    this.setCustomValidity("")
                });
            }

        })
    });
});


$(function () {
    window.verifyRecaptchaCallback = function (response) {
        $('input[data-recaptcha]').val(response).trigger('change');
    }

    window.expiredRecaptchaCallback = function () {
        $('input[data-recaptcha]').val("").trigger('change');
    }

    $('#register-form').validator();
});