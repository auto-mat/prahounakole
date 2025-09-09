search_options = {
  source: function (request, response) {
    $.ajax({
      url: window.geoapifyAutocompleteApiUrl,
      data: {
        format: "json",
        filter: "countrycode:cz",
        lang: "cs",
        apiKey: window.geoapifyApiKey,
        text: request.term,
      },
      success: function (data) {
        var item_map = $.map(data["results"], function (item) {
          if ("formatted" in item) {
            return {
              label: item.formatted,
              value: item.formatted,
              item: item,
              locationid: item.place_id,
            };
          }
        });
        response(item_map);
      },
    });
  },
  minLength: 2,
  delay: 200,
  select: function (e, ui) {
    ga("send", "event", "search", "select", e.target.id);
    $(e.target).val(ui.item.label);
    var lonlat = new OpenLayers.LonLat(
      ui.item.item.lon,
      ui.item.item.lat
    ).transform(
      new OpenLayers.Projection("EPSG:4326"),
      map.getProjectionObject()
    );
    var map_move_by_code = true;
    if (e.target.id == "mapStreetSearch") zoom_to_level = 16;
    // Můžeme zvýšit na 18, pokud bude vše vyrenderováno
    else var zoom_to_level = 16;
    map.setCenter(lonlat, zoom_to_level);
    map_move_by_code = false;
    if (appMode != "routing") {
      return false;
    }
    if (e.target.id == "jpStartStreetSearch") {
      var marker = startMarker;
    } else {
      var marker = endMarker;
    }
    var curpos = marker.geometry;
    marker.geometry.move(lonlat.lon - curpos.x, lonlat.lat - curpos.y);
    setWaypoint(marker);
    if (e.target.id == "jpFinishStreetSearch" && waypoints[0] != undefined) {
      planJourney();
    }
  },
  open: function (e) {
    ga("send", "event", "search", "open", e.target.id);
    $(this).removeClass("ui-corner-all").addClass("ui-corner-top");
  },
  close: function (e) {
    ga("send", "event", "search", "close", e.target.id);
    $(this).removeClass("ui-corner-top").addClass("ui-corner-all");
  },
  focus: function (e) {
    ga("send", "event", "search", "focus", e.target.id);
  },
  //selectFirst: true,
  autoFocus: true,
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
