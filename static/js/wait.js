var wait = setInterval(getfile, 10000);




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
         $("#img").html("Done!")
         $("#img").append("<img src=\"/static/"+waitfile + "\"></img>")
         clearInterval(wait);
     }
  }
);
}
