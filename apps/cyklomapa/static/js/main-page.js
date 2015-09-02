// function togglePanel(event, minimalized){
//     // prevent default a (link) behavior
//     if(event){
//        event.preventDefault();
//     }
//     // let tthe body know the change .. for next possible visual changes
//    $('body').toggleClass('panel_minimized', minimalized);
//       var not_minimalized = undefined;
//       if(minimalized != undefined){
//          not_minimalized = !minimalized;
//       }
//       // stretch - extend panel container
//        // $('#panel').toggleClass('minimized col-sm-2', minimalized);
//        // $('#panel').toggleClass('col-md-3 col-sm-10', not_minimalized);
//        // stretch - extend map container
//       // $('.map_holder').toggleClass('col-md-12 col-sm-12', minimalized);
//       // $('.map_holder').toggleClass('col-md-9 col-sm-12', not_minimalized);
//       // show/hide panel content
//       $('.dildo').toggleClass('hide', not_minimalized);
//       $('.gold').toggleClass('hide', minimalized);
//     // update map size
//     setTimeout(function(){map.updateSize();},500);
// }

function panel_action(){
  var Body = $('body');
  if (Body.is('.panel_minimized')) {
    $('body').removeClass('panel_minimized');
    $('#panel').removeClass('minimized');
    $('.dildo').addClass('hide');
    // console.log('minimize')
  }else{
    $('body').addClass('panel_minimized');
    $('#panel').addClass('minimized');
    $('.dildo').removeClass('hide');
    // console.log('maximaze')
  }

  // change the map container size dinamicaly
  map_width_fix();
  // update map size
  map_move_by_code = true;
  map.updateSize();
  map_move_by_code = false;

  
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
  W_width = $(window).width();
  var Body = $('body');
  if (Body.is('.panel_minimized')) {
    $('.map_holder').css({
      "width": '100%',
      "position":"static"
    });
  }else{
    panel_width = $('#panel').width();
    $('.map_holder').css({
      "width": W_width - panel_width,
      "left": panel_width,
      "position": "fixed"
     });
   }
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
  $('#feedback-btn, #print-btn, #layers-switch, #layers-switch, #city-switch, #zoom-reset, #geolocate, #zoom-in, #zoom-out').on('click', function (e) {
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
  });

  $(".change-layer").click(function(event) {
     ga('send', 'event', 'layer', 'change', event.currentTarget.dataset['name']);
     base_layer = event.currentTarget.dataset['baselayer']
     overlayers = event.currentTarget.dataset['overlayers']
     activateLayers(base_layer, overlayers)
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
