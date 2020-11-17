$(document).ready(function(){
var percent = page+"%";
$('#progressBar').attr('aria-valuenow', percent).css('width', percent).text(percent);
});