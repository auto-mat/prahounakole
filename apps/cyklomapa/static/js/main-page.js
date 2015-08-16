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

function activateHarmonika(){
  // akordeon (panel-informace )
  $('.harmonika .txt').not('.active').hide();

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
  $('.print').on('click', function (e) {
    e.preventDefault();
    window.print()
  });

  // --------  PANEL SWITCH ---------
  $('.panel_switch').click( function(event){
      // prevent default a (link) behavior
      event.preventDefault();
      // let tthe body know the change .. for next possible visual changes
     $('body').toggleClass('panel_minimized');
        // stretch - extend panel container
         $('#panel').toggleClass('minimized col-md-3 col-smd-4 col-sm-2 col-sm-10');
         // stretch - extend map container
        $('.map_holder').toggleClass('col-md-12 col-md-9 col-smd-8 col-sm-12 col-sm-2');
        // show/hide panel content
        $('.dildo, .gold').toggleClass('hide');
      // update map size
      // Not needed anymnore ;)
      // setTimeout(function(){map.updateSize();},500);
      map_width_fix();
  });
  // ------ CLOSE POI -----
  $('.close').live("click",function(){
    $('#poi_box').slideUp(400).hide(400)
    $('#panel-content').show(400);
  });
  // corect the map width on large screens
   // 1445
  function map_width_fix(){
    W_width = $(window).width();
    // console.log(W_width);
    // if(W_width > 1444){
    var Body = $('body');
    if (Body.is('.panel_minimized')) {
      $('.map_holder').css("width", '100%');
      console.log('minimized');
    }else{
      panel_width = $('#panel').width();
      $('.map_holder').css("width", W_width - panel_width);
     }
  }
  map_width_fix();

 $(window).on({
    resize:function(){
      /* Act on the event */
      map_width_fix()
      }
  });
  // advanced menu in layers layer
  $('#advanced_switch').on('click', function (e) {
    e.preventDefault();
    $('#layer_switcher').toggle();
  });

  $(".change-layer").click(function(event) {
     base_layer = event.currentTarget.dataset['baselayer']
     overlayers = event.currentTarget.dataset['overlayers']
     activateLayers(base_layer, overlayers)
  });


});
