var suggestionsURL = "https://autocomplete.geocoder.api.here.com/6.2/suggest.json";
var geocodeURL = "https://geocoder.api.here.com/6.2/geocode.json";
var app_id = "HPfz15EtL6weSct5rbvJ";
var app_code = "Bm2A0SrXWE0xZ3nhtTQVfg";
search_options = {
       source: function ( request, response ) {
           $.ajax({
                  url: suggestionsURL,
                  data: {
                      format: "json",
                      // Focus pointy nefungují dobře, protože se tam pak nenabízejí ulice a města, ale spousta adresních bodů.
                      "prox": map.getCenter().transform(EPSG900913, EPSG4326).lat + "," + map.getCenter().transform(EPSG900913, EPSG4326).lon,
                      app_id: app_id,
                      app_code: app_code,
                      "country": "CZE",
                      "language": "cs",
                      query: request.term
                  },
                  success: function ( data ) {
                      item_map = $.map( data.suggestions, function( item ) {
                          return {
                              label: item.label,
                              value: item.label,
                              locationid: item.locationId
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

            $.ajax({
                  url: geocodeURL,
                  data: {
                      format: "json",
                      // Focus pointy nefungují dobře, protože se tam pak nenabízejí ulice a města, ale spousta adresních bodů.
                      app_id: app_id,
                      app_code: app_code,
                      locationid: ui.item.locationid
                  },
                  success: function ( data ) {
                      lonlatdict = data.Response.View[0].Result[0].Location.DisplayPosition
                      lonlat = new OpenLayers.LonLat(lonlatdict.Longitude , lonlatdict.Latitude).transform(
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
                  }
            });
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
