$( document ).ready(function() {
  $("#labeltarget").hide();
  $("#texttarget").hide();
  $("#checked").hide();
  $("#tabs").tabs();

  $("#multicastradio").click(function() {
    if($(this).is(":checked")){
        $("#labeltarget").show();
        $("#texttarget").show();
        $('#texttarget').prop('required','true');
        }

       })
  $("#broadcastradio").click(function() {
    if($(this).is(":checked")){
        $("#labeltarget").hide();
        $("#texttarget").hide();
        $("#texttarget").val("")
        $('#texttarget').prop('required','false');
        }
    })
    $( "#adduserform" ).autocomplete({
       source: function( request, response ) {
        $.ajax({
          crossDomain: true,
          url: "http://10.1.20.175:8000/ajax/" + $("#adduserform").val(),
          dataType: "json",
          data: {

          },
          success: function( data ) {
            response( data );
          }
        })
      },
      minLength: 2,
      select: function( event, ui ) {
        $("#checked").show();
        console.log(ui);
      }
    })
});
