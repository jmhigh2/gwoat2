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
        document.getElementById("target2").classList.remove('content');
        document.getElementById("target2").classList.add('content2');

         $("#img").html("")
         $("#img").append("<img id='sally' src=\"/static/"+waitfile + "\"></img>")
         clearInterval(wait);
     }
  }
);
}
