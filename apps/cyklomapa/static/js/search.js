var geoCodeURL = "http://nominatim.openstreetmap.org/search";
search_options = {
       source: function ( request, response ) {
           $.ajax({
                  url: geoCodeURL,
                  dataType: "jsonp",
                  jsonp: 'json_callback',
                  data: {
                      format: "json",
                      viewbox: mapconfig.address_search_area,
                      bounded: 1,
                      q: request.term
                  },
                  success: function ( data ) {
                      response ( $.map( data, function( item ) {
                          return {
                              label: item.display_name,
                              value: item.display_name,
                              lat: item.lat,
                              lon: item.lon
                          }}));

                      }
                  })
        },
        minLength: 2,
        delay: 200,
        select: function (e, ui) {
            ga('send', 'event', 'search', 'select', e.target.id);
            lonlat = new OpenLayers.LonLat( ui.item.lon, ui.item.lat).transform(
                  new OpenLayers.Projection("EPSG:4326"),
                  map.getProjectionObject()
            );
            map_move_by_code = true;
            map.setCenter(lonlat, 16);
            map_move_by_code = false;
            if (appMode != 'routing') {
                return false;
            }
            if (e.target.id == "jpStartStreetSearch") {
                marker = startMarker;
            } else {
                marker = endMarker;
            };
            curpos = marker.geometry;
            marker.geometry.move(lonlat.lon - curpos.x, lonlat.lat - curpos.y);
            setWaypoint(marker);
            return false;
        },
        open: function (e) {
            ga('send', 'event', 'search', 'open', e.target.id);
            $( this ).removeClass( "ui-corner-all" ).addClass( "ui-corner-top");
        },
        close: function (e) {
            ga('send', 'event', 'search', 'close', e.target.id);
            $( this ).removeClass( "ui-corner-top").addClass("ui-corner-all");
        },
        focus: function (e) {
            ga('send', 'event', 'search', 'focus', e.target.id);
        },
        //selectFirst: true,
        autoFocus: true 
};

/*
* jQuery UI Autocomplete Select First Extension
*
* Copyright 2010, Scott González (http://scottgonzalez.com)
* Dual licensed under the MIT or GPL Version 2 licenses.
*
* http://github.com/scottgonzalez/jquery-ui-extensions
*/
/*
(function( $ ) {

$( ".ui-autocomplete-input" ).live( "autocompleteopen", function() {
var autocomplete = $( this ).data( "autocomplete" ),
menu = autocomplete.menu;

if ( !autocomplete.options.selectFirst ) {
return;
}

menu.activate( $.Event({ type: "mouseenter" }), menu.element.children().first() );
});

}( jQuery ));
*/
