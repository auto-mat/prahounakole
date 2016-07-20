var CSApi = {
  //apiKey: 'ad9beeeff0afb15e',
  apiKey: '',
  v2baseUrl: 'https://api.cyclestreets.net',
  baseUrl: '',

  // dict of GML returned from CS server indexed by plan name
  routeFeatures: {},

  // just the linestring of the route returned from CS server indexed by plan name
  route: {},
 
  // dict of route segments returned from CS server indexed by plan name
  segments: {},

  // dict of route waypoints returned from CS server indexed by plan name
  waypoints: {},
 
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
    CSApi.formatJSON =  new OpenLayers.Format.GeoJSON({
      internalProjection: map.getProjectionObject(),
      externalProjection: new OpenLayers.Projection("EPSG:4326")
    });
  },

  nearestPoint: function (feature, callback) {
    var pos = feature.geometry.clone();
    pos.transform(map.getProjectionObject(), new OpenLayers.Projection("EPSG:4326"));
    longitude = pos.x;
    latitude = pos.y;
    var url =  this.v2baseUrl + '/v2/nearestpoint?key=' + this.apiKey + '&lonlat=' + this.r6(longitude) + ',' + this.r6(latitude);
    $.ajax({
      url: url,
      dataType: "text",
      success: function (data) {
        var features = CSApi.formatJSON.read(data);
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
        if (i == 1)
            // the end point will be added later on
            continue;
        itinerarypoints += this.r6(waypoints[i].x) + ',' + this.r6(waypoints[i].y) + '|';
      }
      itinerarypoints += this.r6(waypoints[1].x) + ',' + this.r6(waypoints[1].y);
      url =  this.baseUrl + '/api/journey.xml?key=' + this.apiKey + '&useDom=1&itinerarypoints=' + itinerarypoints + '&plan=' + plan;
    }
    $.ajax({
      url: url,
      dataType: "text",
      success: function (data) {
        var features = CSApi.formatGML.read(data);
        var route = CSApi.getFeature(features, 'route');
        if(route.attributes){
        var plan = route.attributes.plan;
           CSApi.routeFeatures[plan] = features;
           CSApi.segments[plan] = CSApi.getSegments(features);
           CSApi.waypoints[plan] = CSApi.getWaypoints(features);
           CSApi.route[plan] = route;
           CSApi.itinerary = route.attributes.itinerary;
           callback(route.attributes.itinerary, plan, features, options);
        } else {
           Raven.setUserContext({
              journey_url: url,
              journey_data: data,
              journey_route: route,
           });
           Raven.captureMessage('CS API returned empty route');
        };
      }
    });
  },

  routeInfo: function (features) {
    var route = this.getFeature(features, 'route');
    var km = Math.round(route.attributes.length / 100) / 10.0;
    var timeStr = CSApi.secondsToTime(route.attributes.time);
    map.zoomToExtent(journeyLayer.getDataExtent());
    var html =  km + ' km<br>' + timeStr;
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

  localize: function(text) {
    var dict = {
      "Alongside": "podél ul.",
      "Regional cycle network": "cyklotrasa",
      Tunnel: "tunel",
      Bridge: "most"
    };

    var re = new RegExp(Object.keys(dict).join("|"),"gi");
    return text.replace(re, function(matched){
      return dict[matched];
    });
  },

  getRouteInstructions: function (plan) {
    var features = this.routeFeatures[plan];
    var output = $('<table class="instructions"></table>');
    var totalDst = 0;
    for (var i=0; i < features.length; i++) {
      feature = features[i];
      var item = $('<tr></tr>');
      item.attr('data-fid', feature.id);
      if (feature.attributes.type == 'segment') {
        if (feature.attributes.turn) {
          item.append('<td class="turn"><i class="' + feature.attributes.turn.replace(' ','_') + '"></i></td>');
        } else {
          item.append('<td class="turn"></td>');
        };
        item.append('<td>'+ this.localize(feature.attributes.name) + '</td>');
        if (feature.attributes.provisionName && feature.attributes.provisionName == 'Steps') {
          item.append('<td><i class="stairs"></i></td>');
        } else {
          if (feature.attributes.walk && feature.attributes.walk == 1) {
            item.append('<td><i class="walk"></i></td>');
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

  getWaypoints: function (features) {
    var waypoints = [];
    for (var i=0; i < features.length; i++) {
      feature = features[i];
      if (feature.gml.featureType == 'waypoint') {
        waypoints.push(feature);
      }
    }
    return waypoints;
  },

  getSegments: function (features) {
    var segments = [];
    for (var i=0; i < features.length; i++) {
      feature = features[i];
      if (feature.gml.featureType == 'segment') {
        segments.push(feature);
      }
    }
    return segments;
  },

  getWaypointBySegment : function (plan, segment) {
    // Podle zadaneho segmentu nalezene nejblizsi predchozi waypoint.
    // Pri hledani se vychazi z predpokladu, ze waypoint vzdy tvori
    // pocatecni bod nejakeho segementu. Kvuli zaokrouhlovacim chybam
    // nelze porovnavat souradnice presne, ale jen s urcenou toleranci.
    var segments = CSApi.segments[plan];
    var waypoints = CSApi.waypoints[plan];
    var xy;
    var idx;
    // jak blizko musi byt waypoint k zacatku segementu, abychom je
    // povazovali za identicke body
    // seste desetinne misto ve WGS je cca 11m
    var tolerance = 0.000003;

    // najdeme poradi prislusneho segmentu
    for (idx=0; idx < segments.length; idx++) {
      if (segments[idx].id == segment.id)
        break;
    }

    // projdeme vsechny waypointy a porovname se segmenty smerem ke startu trasy
    for (var i=idx; i >= 0; i--) {
      // points obsahuje mezerou oddelene jednotlive body segmentu s WGS84 souradnicemi
      // x a y oddelenymi carkou
      xy = CSApi.segments[plan][i].attributes.points.split(' ')[0].split(',');
      for (var j=0; j < waypoints.length; j++) {
        if ((Math.abs(parseFloat(waypoints[j].attributes.longitude) - xy[0]) < tolerance) &&
            (Math.abs(parseFloat(waypoints[j].attributes.latitude) - xy[1]) < tolerance))
          return waypoints[j];
      }
    } 
    // nenasli jsme zadny waypoint, vratime start
    return waypoints[0];
  },

  gpxLink: function (plan) {
    return 'http://praha.cyclestreets.net/journey/' + CSApi.itinerary + '/cyclestreets' + CSApi.itinerary + plan + '.gpx';
  },

  secondsToTime: function (secs) {
    // hack pro realistictejsi casy, dokud cyclestreets
    // nezohledni nase pripominky ohledne rychlosti na highway=track
    // a dalsi pesimisticke rychlosti
    secs = 0.8 * secs;

    var hours = Math.floor(secs / (60 * 60));
    
    var divisor_for_minutes = secs % (60 * 60);
    var minutes = Math.floor(divisor_for_minutes / 60);
        
    var timeStr;
    if (hours > 0) {
        if (minutes > 9) {
            timeStr = hours + ':' + minutes + ' hod';
        } else {
            timeStr = hours + ':0' + minutes + ' hod';
        }
    } else {
        timeStr = minutes + ' min';
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
