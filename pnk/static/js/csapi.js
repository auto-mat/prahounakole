var CSApi = {
  //apiKey: 'ad9beeeff0afb15e',
  apiKey: '',
  //baseUrl: 'http://praha.cyclestreets.net',
  baseUrl: '',

  // dict of GML returned from CS server indexed by plan name
  routeFeatures: {},
  
  // CS itinerary ID of current route
  itinerary: null,

  // Rounds numbers to 6 figures to make them more readable
  r6: function (x) {
    return Math.round(1000000 * x) / 1000000;
  },
  
  planNames: {
    'balanced': 'Optimální',
    'fastest' : 'Rychlá',
    'quietest': 'Klidná'
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

  journey: function (itinerary, waypoints, plan, callback, options) {
    var url;
    if (!plan) {
      plan = 'balanced';
    }
//    if (itinerary && this.itinerary == itinerary) {
//      callback(this.routeFeatures[plan], options);
//    }
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
        var route = CSApi.getFeature(features, 'route');
        CSApi.routeFeatures[route.attributes.plan] = features;
        CSApi.itinerary = route.attributes.itinerary;
        location.hash = 'trasa=' + CSApi.itinerary;
        if (route.attributes.plan == 'balanced') {
            CSApi.journey(route.attributes.itinerary, null, 'fastest', callback);
            CSApi.journey(route.attributes.itinerary, null, 'quietest', callback);
        }
        callback(features, options);
      }
    });
  },

  routeInfo: function (features) {
    var route = this.getFeature(features, 'route');
    var km = Math.round(route.attributes.length / 100) / 10.0;
    var timeStr = CSApi.secondsToTime(route.attributes.time);
    map.zoomToExtent(journeyLayer.getDataExtent());
    var html = this.planNames[route.attributes.plan] + '<br>' + km + ' km<br>' + timeStr + '<br>';
    switch (route.attributes.plan) {
      case 'balanced':
        $('#balanced').html(html);
        break;
      case 'fastest':
        $('#fastest').html(html);
        break;
      case 'quietest':
        $('#quietest').html(html);
        break;
    }
  },

 // Seeks the first feature with the requested featureType.
 getFeature: function (features, featureType) {
    var feature = false;
    for (var i=0; i < features.length; i++) {
      feature = features[i];
      if (feature.attributes.type == featureType) {break;}
      feature = false;
    }
    return feature;
  },

  getRouteInstructions: function (plan) {
    var output = $('<table></table>');
    var features = this.routeFeatures[plan];
    // only for debugging
    var route = this.getFeature(features, 'route');
    output.prepend('<a href="http://praha.cyclestreets.net/journey/' + route.attributes.itinerary + '/">Inspect on CycleStreets</a>');
    for (var i=0; i < features.length; i++) {
      feature = features[i];
      var tr = $('<tr></tr>')
      if (feature.attributes.type == 'segment') {
        if (feature.attributes.turn) {
          tr.append('<td>' + feature.attributes.turn + '</td>');
        } else {
          tr.append('<td></td>');
        }
        tr.append('<td>'+ feature.attributes.name + '</td>');
        output.append(tr);
      }
    }
    return output;
  },

  getStartAndFinish: function (features) {
    var route = this.getFeature(features, 'route');
    var start = new OpenLayers.LonLat(route.attributes.start_longitude, route.attributes.start_latitude)
    var finish = new OpenLayers.LonLat(route.attributes.finish_longitude, route.attributes.finish_latitude)
    return {
        'start': start,
        'finish': finish,
        'start_label': route.attributes.start,
        'finish_label': route.attributes.finish
    };
  },

  secondsToTime: function (secs) {
    var hours = Math.floor(secs / (60 * 60));
    
    var divisor_for_minutes = secs % (60 * 60);
    var minutes = Math.floor(divisor_for_minutes / 60);
    
    var divisor_for_seconds = divisor_for_minutes % 60;
    var seconds = Math.ceil(divisor_for_seconds);
    
    var obj = {
        "h": hours,
        "m": minutes,
        "s": seconds
    };
    
    var timeStr;
    if (obj.h > 0) {
        timeStr = obj.h + ':' + obj.m + ' hod.';
    } else {
        timeStr = obj.m + ' minut';
    }
    return timeStr;
  }
};
