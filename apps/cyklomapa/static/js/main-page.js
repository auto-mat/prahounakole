function full_screen(){
  var vw = $('body').width();
  if(vw <= 768) {
     var body = document.documentElement;
     if (body.requestFullscreen) {
        body.requestFullscreen();
     } else if (body.webkitRequestFullscreen) {
        body.webkitRequestFullscreen();
     } else if (body.mozRequestFullScreen) {
        body.mozRequestFullScreen();
     } else if (body.msRequestFullscreen) {
        body.msRequestFullscreen();
     }
  }
}

function panel_action(action){
  if(action != undefined){
     maximize = (action == 'maximize');
  } else {
     var Body = $('body');
     maximize = Body.is('.panel_minimized')
  }
  if (maximize) {
    $('body').removeClass('panel_minimized');
    $('#panel').removeClass('minimized');
    $('.dildo').addClass('hide');
    // console.log('minimize')
  }else{
    $('body').addClass('panel_minimized');
    $('#panel').addClass('minimized');
    $('.dildo').removeClass('hide');
    full_screen();
    // console.log('maximaze')
  }

  // change the map container size dinamicaly
  map_width_fix();
  panel_position()
  // update map size
  map.updateSize();
}



function panel_position(){
  var holder = $('.panel_switch_holder')
  var switch_ = $('.panel_switch')
  var panel_w = $('#panel').width()
  var window_height = $('body').height()

  $(holder).css({
    'top' : 0, 
    'left' : (panel_w) + 'px'
  })
  $(switch_).css({
    'top' : (window_height / 2) + 'px',
    'left' : (panel_w) + 'px'
  })

}
// corect the map width on large screens
 // 1445
function map_width_fix(){
  var panel_minimized = $('body').is('.panel_minimized');

  if (!panel_minimized) {
    $('.map_holder').css({
      "position": "fixed"
     });
  }

  W_width = $(window).width();
  if (panel_minimized) {
    $('.map_holder').css({
      "width": '100%',
      "position":"static"
    });
  }else{
    panel_width = $('#panel').width();
    $('.map_holder').css({
      "width": W_width - panel_width,
      "left": panel_width,
     });
   }
   //Fix for Android browser, which doesn't support "vh" units
  W_height = $(window).height();
   $('#map, .panel_switch_holder, .map_holder, body, html').css({
      "height": W_height
   });
}

jQuery(document).ready(function($) {
  

  $('#zoom-in').click( function(event){
      event.preventDefault();
      map.zoomIn()
    });
  $('#zoom-out').click( function(event){
      event.preventDefault();
      map.zoomOut()
    });
  $('#zoom-reset').click( function(event){
      event.preventDefault();
      map.setCenter(new OpenLayers.LonLat(mapconfig.baselon, mapconfig.baselat).transform(EPSG4326, map.getProjectionObject()), mapconfig.basezoom);
      // Prosim doplnit
      // map.zoom....()
    });
  $('#feedback-btn, #print-btn, #layers-switch, #layers-switch, #city-switch, #zoom-reset, #geolocate, #zoom-in, #zoom-out, #advanced_switch').on('click', function (e) {
    ga('send', 'event', 'button', 'clicked', e.target.id);
  });
  $('.print').on('click', function (e) {
    e.preventDefault();
    window.print()
  });

  // --------  PANEL SWITCH ---------
  $('.panel_switch').click( function(event){
      // prevent default a (link) behavior
      event.preventDefault();
      // close | open panel
      panel_action();
  });


  map_width_fix();
  panel_position()


 $(window).on({
    resize:function(){
      /* Act on the event */
      map_width_fix()
      panel_position()
      }
  });
  // advanced menu in layers layer
  $('#advanced_switch').on('click', function (e) {
    e.preventDefault();
    $('#layer_switcher').toggle();
    $('#modal-layer').animate({scrollTop: $("#baseLayers").offset().top},'slow');
  });

  $(".change-layer").click(function(event) {
     ga('send', 'event', 'layer', 'change', event.currentTarget.dataset['name']);
     base_layer = event.currentTarget.dataset['baselayer'];
     overlayers = JSON.parse(event.currentTarget.dataset['overlayers']);
     activateLayers(base_layer, overlayers);
  });

 

  // akordeon (panel-informace )
  $(document).on("click", '.open_txt', function(event) {
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
});
