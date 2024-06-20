$(document).ready(function() {

    $('.payWithRazorpay').click(function(e) {
        e.preventDefault();

        var fname = $("[name='fname']").val();
        var lname = $("[name='lname']").val();
        var email = $("[name='email']").val();
        var phone = $("[name='phone']").val();
        var address = $("[name='address']").val();
        var city = $("[name='city']").val();
        var state = $("[name='state']").val();
        var country = $("[name='country']").val();
        var pincode = $("[name='pincode']").val();
        var token = $("[name='csrfmiddlewaretoken']").val();
        

        if(fname == "" || lname=="" || email == "" || phone == "" || address=="" || city == "" || state == "" || country=="" || pincode == "" )
        {
            //alert("All fields are mandatory!")
            swal("Alert!", "All fields are mandatory!", "error");
            return false;
        }
        else
        {
            $.ajax({
                method: "GET",
                url:"/proceed-to-pay",
                success: function(response){
                    //console.log(response);
                    var options = {
                        "key": "rzp_test_uko136oNjyc4JN", // Enter the Key ID generated from the Dashboard
                        "amount": 100,//response.total_price * 100, // Amount is in currency subunits. Default currency is INR. Hence, 50000 refers to 50000 paise
                        "currency": "INR",
                        "name": "Jawadhu Hills",
                        "description": "Test Transaction",
                        "image": "https://example.com/your_logo",
                        //"order_id": "order_9A33XWu170gUtm", //This is a sample Order ID. Pass the `id` obtained in the response of Step 1
                        "handler": function (responseb){
                            alert(responseb.razorpay_payment_id);

                            data={
                             "fname": fname,
                             "lname":  lname,
                             "email":  email,
                             "phone":  phone,
                             "address":   address,
                             "city":  city,
                             "state":  state,
                             "country":  country,
                             "pincode":   pincode,
                             "payment_mode":"Razorpay",
                             "payment_id":responseb.razorpay_payment_id,
                             csrfmiddlewaretoken: token


                            }


                            $.ajax({
                                method:"POST",
                                url:"/place-order",
                                data:data,
                                success: function(responsec){
                                    swal("Done!", responsec.status, "success").then((value) => {
                                        window.location.href = '/my-orders'
                                      });

                                }
                            })



                        
                        },
                        "prefill": {
                            "name": fname+" "+lname,
                            "email": email,
                            "contact": phone
                        },
                        "notes": {
                            "address": "Razorpay Corporate Office"
                        },
                        "theme": {
                            "color": "#3399cc"
                         }
                    };
                    var rzp1 = new Razorpay(options);
                    
                    rzp1.open();
                }
            });

            

        }
    
    });
});