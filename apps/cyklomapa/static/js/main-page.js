function togglePanel(event, minimalized){
    // prevent default a (link) behavior
    if(event){
       event.preventDefault();
    }
    // let tthe body know the change .. for next possible visual changes
   $('body').toggleClass('panel_minimized', minimalized);
      var not_minimalized = undefined;
      if(minimalized != undefined){
         not_minimalized = !minimalized;
      }
      // stretch - extend panel container
       $('#panel').toggleClass('minimized col-sm-2', minimalized);
       $('#panel').toggleClass('col-md-3 col-sm-10', not_minimalized);
       // stretch - extend map container
      $('.map_holder').toggleClass('col-md-12 col-sm-12', minimalized);
      $('.map_holder').toggleClass('col-md-9 col-sm-12', not_minimalized);
      // show/hide panel content
      $('.dildo').toggleClass('hide', not_minimalized);
      $('.gold').toggleClass('hide', minimalized);
    // update map size
    setTimeout(function(){map.updateSize();},500);
}

jQuery(document).ready(function($) {

  // --------  PANEL SWITCH ---------
  $('.panel_switch').click(togglePanel);
  // ------ CLOSE POI -----
  $('.close').live("click",function(){
    closePoiBox(true);
    selectControl.unselectAll();
  });
  // corect the map width on large screens
   // 1445
  function map_width_fix(){
    W_width = $(window).width();
    if(W_width > 1444){
      panel_width = $('#panel').width();
      $('.map_holder').css("width", W_width - panel_width);
    }
  }
  map_width_fix();

  $(window).resize(function(event) {
    /* Act on the event */
    map_width_fix()
  });

  // advanced menu in layers layer
  $('#advanced_switch').on('click', function (e) {
    e.preventDefault();
    $('#layer_switcher').toggle();
  });

  // akordeon (panel-informace )
  $('.harmonika .txt').hide();

  $('.open_txt').click(function(event) {
    event.preventDefault()
    /* Act on the event */
    $('.harmonika .txt').slideUp();
    var closest_txt  = $(this).closest('.harmonika').find('.txt');
    if($(closest_txt).is(':visible')){
      $(closest_txt).slideUp();
    }else{
      $(closest_txt).slideDown();
    }
  });

  $(".change-layer").click(function(event) {
     base_layer = event.currentTarget.dataset['baselayer']
     overlayers = event.currentTarget.dataset['overlayers']
     activateLayers(base_layer, overlayers)
  });


});
