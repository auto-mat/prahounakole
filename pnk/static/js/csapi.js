var CSApi = {
  //apiKey: 'ad9beeeff0afb15e',
  apiKey: '',
  //baseUrl: 'http://praha.cyclestreets.net',
  baseUrl: '',

  // Rounds numbers to 6 figures to make them more readable
  r6: function (x) {
    return Math.round(1000000 * x) / 1000000;
  },

  init: function (map, apiKey) {
    this.map = map;
    this.apiKey = apiKey;
    CSApi.formatGML =  new OpenLayers.Format.GML({
      internalProjection: map.getProjectionObject(),
      externalProjection: new OpenLayers.Projection("EPSG:4326")
    });
  },

  nearestPoint: function (feature, callback) {
    var pos = feature.geometry.clone();
    pos.transform(map.getProjectionObject(), new OpenLayers.Projection("EPSG:4326"));
    longitude = pos.x;
    latitude = pos.y;
    var url =  this.baseUrl + '/api/nearestpoint.xml?key=' + this.apiKey + '&useDom=1&longitude=' + this.r6(longitude) + '&latitude=' + this.r6(latitude);
    $.ajax({
      url: url,
      dataType: "text",
      success: function (data) {
        var features = CSApi.formatGML.read(data);
        callback(features);
      }
    });
  },

  journey: function (itinerary, waypoints, plan, callback) {
    var url;
    if (itinerary) {
      url =  this.baseUrl + '/api/journey.xml?key=' + this.apiKey + '&useDom=1&itinerary=' + itinerary + '&plan=' + plan;
    } else {
      var itinerarypoints = '';
      for(var i=0; i < waypoints.length; i++){
        itinerarypoints += this.r6(waypoints[i].x) + ',' + this.r6(waypoints[i].y) + '|';
      }
      // remove the last '|'
      itinerarypoints = itinerarypoints.substring(0, itinerarypoints.length - 1);
      url =  this.baseUrl + '/api/journey.xml?key=' + this.apiKey + '&useDom=1&itinerarypoints=' + itinerarypoints + '&plan=' + plan;
    }
    $.ajax({
      url: url,
      dataType: "text",
      success: function (data) {
        var features = CSApi.formatGML.read(data);
        callback(features);
      }
    });
  }
};
