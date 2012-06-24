var geoCodeURL = "http://nominatim.openstreetmap.org/search";
search_options = {
       source: function ( request, response ) {
           $.ajax({
                  url: geoCodeURL,
                  dataType: "json",
                  data: {
                      format: "json",
                      viewbox: "14.3081641,50.2,14.5718359,49.9355541",
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
            lonlat = new OpenLayers.LonLat( ui.item.lon, ui.item.lat).transform(
                  new OpenLayers.Projection("EPSG:4326"),
                  map.getProjectionObject()
            );
            if (e.target.id == "jpStartStreetSearch") {
                marker = startMarker;
            } else {
                marker = endMarker;
            };
            map.setCenter(lonlat, 16);
            curpos = marker.geometry;
            marker.geometry.move(lonlat.lon - curpos.x, lonlat.lat - curpos.y);
            if (! startMarker.layer) {
                markerLayer.addFeatures(marker);
            };
            markerLayer.redraw();
            onDragComplete(marker, null);
        },
        open: function () {
            $( this ).removeClass( "ui-corner-all" ).addClass( "ui-corner-top");
        },
        close: function () {
            $( this ).removeClass( "ui-corner-top").addClass("ui-corner-all");
        }
};

