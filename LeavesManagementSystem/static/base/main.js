/*Set the width of the side navigation to 200px and If window-width is greater-than or equal 960, left margin the page content to 200px */
function maximizeNav()
{
  document.getElementById("mySidenav").style.width = "200px";
  $('.menueBtn').css("padding-left", "20%")
  if ($(window).width() >= 960) {
    document.getElementById("main").style.marginLeft = "200px";
  }
}
  
  /* Set the width of the side navigation to 35 and the left margin of the page content to 35 */
function minimizeNav() 
{
    document.getElementById("mySidenav").style.width = "35px";
    document.getElementById("main").style.marginLeft = "35px";
    $('.menueBtn').css("padding-left", "3%");
}

function toggleDashboardBtns()
{
  $('.dashboard-menueBtn').toggle();
}

function toggleRequestBtns()
{
  $('.request-menueBtn').toggle();
}

$(window).on('load', function(){
  $('.dashboard-menueBtn').hide();
  $('.request-menueBtn').hide();
});
