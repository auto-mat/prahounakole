// This allows layer URL parameters to be string encoded
//

function createParams(center, zoom, layers) {
    center = center || this.map.getCenter();
      
    var params = OpenLayers.Util.getParameters(this.base);
    
    // If there's still no center, map is not initialized yet.
    // Break out of this function, and simply return the params from the
    // base link.
    if (center) {

        //zoom
        params.zoom = zoom || this.map.getZoom();

        //lon,lat
        var lat = center.lat;
        var lon = center.lon;
        
        if (this.displayProjection) {
            var mapPosition = OpenLayers.Projection.transform(
              { x: lon, y: lat },
              this.map.getProjectionObject(),
              this.displayProjection );
            lon = mapPosition.x;
            lat = mapPosition.y;
        }
        params.lat = Math.round(lat*100000)/100000;
        params.lon = Math.round(lon*100000)/100000;

        //layers
        layers = layers || this.map.layers;
        params.layers = '_';
        for (var i=0, len=layers.length; i<len; i++) {
            var layer = layers[i];

            if (layer.getVisibility() && layer.slug) {
               params.layers += layer.slug
            }
        }
    }

    return params;
} 

function configureLayers() {
    for(var i=0, len=this.map.layers.length; i<len; i++) {
        layer = this.map.layers[i];

        if(!layer.slug) {
           continue;
        }

        var layer_visible = this.layers.indexOf(layer.slug) != -1 || mapconfig.center_feature_slug == layer.slug;
        if(layer.isBaseLayer) {
           if(layer_visible) {
              this.map.setBaseLayer(layer);
           }
        } else {
           layer.setVisibility(layer_visible);
        }
    }

    if (this.layers.length == this.map.layers.length && this.layers.charAt(0) != "_") {
        this.map.events.unregister('addlayer', this, this.configureLayers);
        for(var i=0, len=this.layers.length; i<len; i++) {
            
            var layer = this.map.layers[i];
            var c = this.layers.charAt(i);
            
            if (c == "B") {
                this.map.setBaseLayer(layer);
            } else if ( (c == "T") || (c == "F") ) {
                layer.setVisibility(c == "T");
            }
        }
    }
   
} 

