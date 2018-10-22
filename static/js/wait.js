var wait = setInterval(getfile, 5000);




function getfile(){

var waitfile = $("#newfile").html();

$.ajax(
  {
    url:'/static/' + waitfile,
     type:'GET',
     error: function()
     {
         //file not exists
     },
     success: function()
     {
         $("#img").html("Done!<br>")
         $("#img").append("<img src=\"/static/"+waitfile + "\"></img>")
         clearInterval(wait);
     }
  }
);
}
