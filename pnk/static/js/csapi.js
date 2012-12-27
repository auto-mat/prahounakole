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
        callback(route.attributes.itinerary, features, options);
      }
    });
  },

  routeInfo: function (features) {
    var route = this.getFeature(features, 'route');
    var km = Math.round(route.attributes.length / 100) / 10.0;
    var timeStr = CSApi.secondsToTime(route.attributes.time);
    map.zoomToExtent(journeyLayer.getDataExtent());
    var html =  km + ' km / ' + timeStr;
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
    var features = this.routeFeatures[plan];
    var route = this.getFeature(features, 'route');
    var output = $('<table class="instructions"></table>');
    var totalDst = 0;
    for (var i=0; i < features.length; i++) {
      feature = features[i];
      var item = $('<tr></tr>');
      if (feature.attributes.type == 'segment') {
        if (feature.attributes.turn) {
          item.append('<td class="turn"><i class="' + feature.attributes.turn.replace(' ','_') + '"></i></td>');
        } else {
          item.append('<td class="turn"></td>');
        };
        item.append('<td>'+ feature.attributes.name + '</td>');
        if (feature.attributes.walk && feature.attributes.walk == 1) {
          item.append('<td><i class="walk"></i></td>');
        } else {
          if (feature.attributes.provisionName && feature.attributes.provisionName == 'steps') {
            item.append('<td><i class="stairs"></i></td>');
          } else {
            item.append('<td></td>');
          }
        }

        totalDst += parseInt(feature.attributes.distance);
        item.append('<td class="distance"><span class="dist">' +
                         this.distanceHumanize(totalDst) +
                    '</span><span class="leng">' + 
                        this.distanceHumanize(feature.attributes.distance) +
                    '</span></td>');
        output.append(item);
      }
    }
    return(output);
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
    // hack pro realistictejsi casy, dokud cyclestreets
    // nezohledni nase pripominky ohledne rychlosti na highway=track
    // a dalsi pesimisticke rychlosti
    secs = 0.8 * secs;

    var hours = Math.floor(secs / (60 * 60));
    
    var divisor_for_minutes = secs % (60 * 60);
    var minutes = Math.floor(divisor_for_minutes / 60);
    var m;
    if (minutes > 9) {
        m = '' + minutes;
    } else {
        m = '0' + minutes;
    }
        
    var timeStr;
    if (hours > 0) {
        timeStr = hours + ':' + m + ' hod';
    } else {
        timeStr = m + ' min';
    }
    return timeStr;
  },

  distanceHumanize: function (dist) {
    if (dist < 1000) {
      // do 1km v desitkach metru
      return Math.round(dist /10) * 10 + '&nbsp;m';
    } else {
      // vsechno nad v desetinach km
      return (Math.round(dist / 100) / 10) + '&nbsp;km';
    }
  }
};
