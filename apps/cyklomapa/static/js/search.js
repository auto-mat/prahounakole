var geoCodeURL = "https://search.mapzen.com/v1/autocomplete";
search_options = {
       source: function ( request, response ) {
           $.ajax({
                  url: geoCodeURL,
                  data: {
                      format: "json",
                      "focus.point.lat": map.getCenter().transform(EPSG900913, EPSG4326).lat,
                      "focus.point.lon": map.getCenter().transform(EPSG900913, EPSG4326).lon,
                      api_key: "mapzen-dsCsXWh",
                      "boundary.country": "CZE",
                      text: request.term
                  },
                  success: function ( data ) {
                      item_map = $.map( data.features, function( item ) {
                          return {
                              label: item.properties.label,
                              value: item.properties.label,
                              lat: String(item.geometry.coordinates[1]),
                              lon: String(item.geometry.coordinates[0])
                          }}
                      )
                      response(item_map);
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
