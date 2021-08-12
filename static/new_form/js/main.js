(function($) {



    var form = $("#signup-form");
    form.validate({
        errorPlacement: function errorPlacement(error, element) {
             element.before(error);
        },
        rules: {
            first_name : {
                required: true,
            },
            last_name : {
                required: true,
            },
            email : {
                required: true,
            }
        },
        onfocusout: function(element) {
            $(element).valid();
        },
        highlight : function(element, errorClass, validClass) {
            $(element.form).find('.actions').addClass('form-error');
            $(element).parent().find('.form-label').addClass('form-label-error');
            $(element).removeClass('valid');
            $(element).addClass('error');
        },
        unhighlight: function(element, errorClass, validClass) {
            $(element.form).find('.actions').removeClass('form-error');
            $(element).parent().find('.form-label').removeClass('form-label-error');
            $(element).removeClass('error');
            $(element).addClass('valid');
        }
    });
    form.children("div").steps({


        headerTag: "h3",
        bodyTag: "fieldset",
        transitionEffect: "fade",
        labels: {
            previous : '<i class="zmdi zmdi-chevron-left"></i>',
            next : '<i class="zmdi zmdi-chevron-right"></i>',
            finish : '<i class="zmdi zmdi-chevron-right"></i>'
        },
        onStepChanging: function (event, currentIndex, newIndex)
        {
          console.log(currentIndex);
            if(currentIndex === 0) {
                form.parent().parent().parent().append('<div class="footer footer-' + currentIndex + '"></div>');
            }
            if(currentIndex === 1) {
              // alert("hi")

                // Hide and seek of individual and company fields
                form.parent().parent().parent().find('.footer').removeClass('footer-0').addClass('footer-'+ currentIndex + '');
            }
            if(currentIndex === 2) {
                form.parent().parent().parent().find('.footer').removeClass('footer-1').addClass('footer-'+ currentIndex + '');
            }
            if(currentIndex === 3) {
                form.parent().parent().parent().find('.footer').removeClass('footer-2').addClass('footer-'+ currentIndex + '');
            }


            if(currentIndex === 4) {
                form.parent().parent().parent().find('.footer').removeClass('footer-3').addClass('footer-'+ currentIndex + '');
            }
            if(currentIndex === 5) {
                form.parent().parent().parent().find('.footer').removeClass('footer-4').addClass('footer-'+ currentIndex + '');
            }
            if(currentIndex === 6) {
                form.parent().parent().parent().find('.footer').removeClass('footer-5').addClass('footer-'+ currentIndex + '');
            }
            if(currentIndex === 7) {

              document.getElementById('otp_field').style.display = "none";
                form.parent().parent().parent().find('.footer').removeClass('footer-6').addClass('footer-'+ currentIndex + '');
            }
            if(currentIndex === 8) {

                // Ajax call for verification

                var contact_no = $('#id_contact_no').val();
                var alternate_no = $('#id_alternate_no').val();
                var random_number = Math.floor(10000 + Math.random() * 9000);
                var setOtp = sessionStorage.setItem('OTP', random_number);
                var csrf_token = document.getElementById('csrf_token').value;
                $.ajax({
                url: "/create_user/",
                method: "POST",
                headers: {'X-CSRFToken': csrf_token},
                data : {"contact_no":contact_no,'random_number':random_number},
                success: function (data) {
                // document.getElementById('id_otp').style.display = "none";
                //   document.getElementById('btn_otp').style.display = "block";
                  document.getElementById('otp_field').style.display = "block";
                }
                })

                // End of Ajax call for verification
                form.parent().parent().parent().find('.footer').removeClass('footer-7').addClass('footer-'+ currentIndex + '');
                // form.submit()
            }
            if(currentIndex === 9) {

                // OTP comparision

                var message = document.getElementById("otp_field");
                var getOtp = sessionStorage.getItem('OTP');
                var input_otp = message.value;
                if (getOtp == input_otp){
                // document.getElementById('next').style.display = "block";
                $("#error_msg").html("Phone number is verified successfully")
                }
                else {
                $("#error_msg").html("Please Enter Valid OTP")
                // document.getElementById('next').style.display = "none";
                }

                // End of OTP comparision
                form.parent().parent().parent().find('.footer').removeClass('footer-8').addClass('footer-'+ currentIndex + '');

            }
            if(currentIndex === 10) {
                form.parent().parent().parent().find('.footer').removeClass('footer-9').addClass('footer-'+ currentIndex + '');
            }
            if(currentIndex === 11) {

                // form.parent().parent().parent().find('.footer').removeClass('footer-10').addClass('footer-'+ currentIndex + '');
                form.submit();
            }
            if(currentIndex === 12) {
                form.parent().parent().parent().find('.footer').removeClass('footer-11').addClass('footer-'+ currentIndex + '');
            }
            if(currentIndex === 13) {
                form.parent().parent().parent().find('.footer').removeClass('footer-12').addClass('footer-'+ currentIndex + '');
            }


            // if(currentIndex === 4) {
            //     form.parent().parent().parent().append('<div class="footer" style="height:752px;"></div>');
            // }
            form.validate().settings.ignore = ":disabled,:hidden";
            return form.valid();
        },
        onFinishing: function (event, currentIndex)
        {
            form.validate().settings.ignore = ":disabled";
            return form.valid();
        },
        onFinished: function (event, currentIndex)
        {
          // form.parent().parent().append('<h1>Hi , Hoang !</h1>').parent().addClass('finished');
            form.submit();
            return true;
        },
        onStepChanged : function (event, currentIndex, priorIndex) {

            return true;
        }
    });

    jQuery.extend(jQuery.validator.messages, {
        required: "",
        remote: "",
        email: "",
        url: "",
        date: "",
        dateISO: "",
        number: "",
        digits: "",
        creditcard: "",
        equalTo: ""
    });
    $(".toggle-password").on('click', function() {

        $(this).toggleClass("zmdi-eye zmdi-eye-off");
        var input = $($(this).attr("toggle"));
        if (input.attr("type") == "password") {
          input.attr("type", "text");
        } else {
          input.attr("type", "password");
        }
    });
})(jQuery);




// <!-- Ajax call script for phone number verification -->


// $('#next').click(function () {
//   var test =  document.getElementById("id_type").selectedIndex;
//   alert(test);
// })
function div() {

}

// $(document).ready(function(){
// $("#id_otp").click(function(){
//
// });
// });


$("#btn_otp").click(function(){



})



// <!-- End of Ajaxscript for phone number verification -->
