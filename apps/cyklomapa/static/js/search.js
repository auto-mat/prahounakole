var geoCodeURL = "https://api.mapbox.com/geocoding/v5/mapbox.places/";
search_options = {
       source: function ( request, response ) {
           $.ajax({
                  url: geoCodeURL + request.term + ".json",
                  data: {
                      format: "json",
                      // Focus pointy nefungují dobře, protože se tam pak nenabízejí ulice a města, ale spousta adresních bodů.
                      "proximity": map.getCenter().transform(EPSG900913, EPSG4326).lat + "," + map.getCenter().transform(EPSG900913, EPSG4326).lon,
                      access_token: "pk.eyJ1IjoicGV0cmRsb3VoeSIsImEiOiJjajhvbHE0OGQwNHFnMnhxY252NDYzaHRjIn0.Xn34k0Fd0zzjvfJku892aw",
                      "country": "cz",
                      "language": "CS_cz",
                      text: request.term
                  },
                  success: function ( data ) {
                      item_map = $.map( data.features, function( item ) {
                          return {
                              label: item.place_name,
                              value: item.place_name,
                              lat: String(item.center[1]),
                              lon: String(item.center[0])
                          };
                      });
                      response(item_map);
                      }
                  });
        },
        minLength: 2,
        delay: 200,
        select: function (e, ui) {
            ga('send', 'event', 'search', 'select', e.target.id);
            $(e.target).val(ui.item.label);
            lonlat = new OpenLayers.LonLat( ui.item.lon, ui.item.lat).transform(
                  new OpenLayers.Projection("EPSG:4326"),
                  map.getProjectionObject()
            );
            map_move_by_code = true;
            if (e.target.id == "mapStreetSearch")
               zoom_to_level = 16; // Můžeme zvýšit na 18, pokud bude vše vyrenderováno
            else
               zoom_to_level = 16;
            map.setCenter(lonlat, zoom_to_level);
            map_move_by_code = false;
            if (appMode != 'routing') {
                return false;
            }
            if (e.target.id == "jpStartStreetSearch") {
                marker = startMarker;
            } else {
                marker = endMarker;
            }
            curpos = marker.geometry;
            marker.geometry.move(lonlat.lon - curpos.x, lonlat.lat - curpos.y);
            setWaypoint(marker);
            if (e.target.id == "jpFinishStreetSearch" && waypoints[0] != undefined) {
                planJourney();
            }
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
