
$(document).ready(function()
{
  $("#selected_parameter").change(function(){

      debugger
      let parameter=$(this).val();

      // Set the hidden parameter by the user's email whose BMI is logged
      var hiddenElement = document.getElementById("user_email");
      hiddenElement.setAttribute("value", parameter) 

  })
}
)
