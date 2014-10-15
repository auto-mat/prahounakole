var map, layer_osm, layerPNK, layerPNK_BW,  kml, filter_rule, nofilter_rule, zoomFilter;
var simpleSwitcher, layerSwitcher;
var appMode = ''; // pnkmap nebo routing
// jakou cast zadani prave resime - slouzi hlavne pro obsluhu kurzoru
// * start, stop - vychozi a cilovy bod
// * go - muzeme spustit vyhledavani
var routingState = 'start';
var vectors = [];
var journeyLayer, markerLayer, startMarker, endMarker, middleMarker, wpAttrs;
var previewedRoute;
var waypoints = [];
var startFeature = null;
var endFeature = null;
var draggedFeature = null;
var lastSelectedFeature;
var criteria = {};
var criteriaCnt = 0;
var selectedItinerary = null;
var selectedPlan;
var dragInAction = false;
var ignoreHashChange = false;

var EPSG4326 = new OpenLayers.Projection("EPSG:4326");
var EPSG900913 = new OpenLayers.Projection("EPSG:900913"); 

var bounds = new OpenLayers.Bounds(12,48.5,19,51.1);
bounds.transform(EPSG4326, EPSG900913);

function defaultPanZoom() {
    var newPanZoom = new OpenLayers.Control.ZoomPanel();

    OpenLayers.Util.extend(newPanZoom, {
        activateControl: function(evt) {
            switch (evt.displayClass) {
                case "olControlZoomIn": 
                    this.map.zoomIn(); 
                    break;
                case "olControlZoomOut": 
                    this.map.zoomOut(); 
                    break;
                case "olControlZoomToMaxExtent": 
                    map.setCenter(new OpenLayers.LonLat(mapconfig.baselon, mapconfig.baselat).transform(EPSG4326, map.getProjectionObject()), mapconfig.basezoom);
                    break;
                }
            }
   });
   return newPanZoom;
}

function getTileURL(bounds) {
    var res = this.map.getResolution();
    var x = Math.round((bounds.left - this.maxExtent.left) / (res * this.tileSize.w));
    var y = Math.round((this.maxExtent.top - bounds.top) / (res * this.tileSize.h));
    var z = this.map.getZoom();
    return this.url + z + "/" + x + "/" + y + "." + this.type;
}

function init(mapconfig) {
    OpenLayers.ImgPath = "/static/css/img/";
    OpenLayers.Lang.setCode("cs-CZ");
    mainFilter = new OpenLayers.Filter.Logical({
        type: OpenLayers.Filter.Logical.AND
    });
            
    filter_rule = new OpenLayers.Rule({
        filter: mainFilter,
        symbolizer: {
            'externalGraphic': '${ikona}',
            'graphicWidth': 20,
            'graphicHeight': 20,
            'graphicZIndex': '${zindex}',
            'strokeWidth': '${line_width}',
            'strokeColor': '${line_color}',
            'fillColor': '${line_color}',
            graphicXOffset: -10,
            graphicYOffset: -10,
            'graphicOpacity': 1,
            'graphicTitle': '${name}',
            'fillOpacity': 0.5
        }
    });

    nofilter_rule = new OpenLayers.Rule({
        symbolizer: {
            'externalGraphic': '${ikona}',
            'graphicWidth': 20,
            'graphicHeight': 20,
            'graphicZIndex': '${zindex}',
            'strokeWidth': '${line_width}',
            'strokeColor': '${line_color}',
            'fillColor': '${line_color}',
            graphicXOffset: -10,
            graphicYOffset: -10,
            'graphicOpacity': 1,
            'graphicTitle': '${name}',
            'fillOpacity': 0.5
        }
    });

    // Filtr, ktery na nejnizsich zoomlevelech skryje nektere znacky.
    // Hodnotu kriteria je nutne aktualizovat pri zmene zoom levelu.
    // Alternativni postup by byl dynamicky filtr, kde by se poustela nejaka funkce
    // porovnavajici minZoom s aktualnim zoomem, ale takto je to primocarejsi.
    zoomFilter = new OpenLayers.Filter.Comparison({
        type: OpenLayers.Filter.Comparison.LESS_THAN_OR_EQUAL_TO,
        property: "minZoom",
        value: mapconfig.zoom
    });
    mainFilter.filters.push(zoomFilter);

    simpleSwitcher = new SimpleLayerSwitcher();
    var controls;
    if(mapconfig.mobilni) {
        controls = [
            new OpenLayers.Control.ArgParser({configureLayers: configureLayers}),
            new OpenLayers.Control.Attribution(),
            new OpenLayers.Control.Navigation(),
            defaultPanZoom()
        ];
    } else {
        layerSwitcher = new OpenLayers.Control.LayerSwitcher({roundedCornerColor:'#cb541c', ascending:0});
        controls = [
            new OpenLayers.Control.ArgParser({configureLayers: configureLayers}),
            new OpenLayers.Control.Attribution(),
            layerSwitcher,
            simpleSwitcher,
            new OpenLayers.Control.Navigation(),
            new OpenLayers.Control.Permalink({createParams: createParams}),
            new OpenLayers.Control.ScaleLine({maxWidth: 300}),
            defaultPanZoom()
        ];
    }

    var options = { 
        controls: controls,
        maxExtent: bounds.clone(),
        restrictedExtent: bounds.clone(),
        projection: EPSG4326,
        displayProjection : EPSG4326,
		// fallThrough : false,
        theme: null
    };

    map = new OpenLayers.Map('map', options);

    if(!mapconfig.mobilni) {
        if (mapconfig.minimize_layerswitcher) {
            layerSwitcher.minimizeControl();
        } else {
            layerSwitcher.maximizeControl();
        }
    }

    layer_osm = new OpenLayers.Layer.OSM.Mapnik(
        "OpenStreetMap", { 
        slug: "O",
        displayOutsideMaxExtent: false,
        displayInLayerSwitcher: false
    });
    var layerCycle  = new OpenLayers.Layer.OSM.CycleMap(
        "Cycle map", {
        slug: "C",
        displayInLayerSwitcher: false
    });
    layerPNK = new OpenLayers.Layer.OSM(
        "Prahou na kole",
        "http://tiles.prahounakole.cz/", {
        displayInLayerSwitcher: false,
        slug:"P",
        type: 'png',
        numZoomLevels: 19,
        getURL: getTileURL,
        tileOptions : {crossOriginKeyword: null} 
    });
    // tlumena verze mapy pro vyhledavac
    layerPNK_BW = new OpenLayers.Layer.OSM(
        "Vyhledávač PNK",
        "http://tilesbw.prahounakole.cz/", {
        displayInLayerSwitcher: false,
        slug:"H",
        type: 'png',
        numZoomLevels: 19,
        getURL: getTileURL,
        tileOptions : {crossOriginKeyword: null}
    });
    var layerGoogle = new OpenLayers.Layer.Google(
        "Satelitní mapa Google", {
        displayInLayerSwitcher: false,
        slug:"G",
        type: google.maps.MapTypeId.SATELLITE,
        numZoomLevels: 22
     });

     map.addLayers([layerPNK]);
     if(!mapconfig.mobilni) {
         map.addLayers([layerPNK_BW, layer_osm, layerCycle, layerGoogle]);
         layerGoogle.mapObject.setTilt(0);
     }

     // zabranime odzoomovani na nizsi level nez 8 
     map.isValidZoomLevel = function(zoomLevel) {
         var valid = ( (zoomLevel !== null) &&
                       (zoomLevel >= 8) &&
                       (zoomLevel < this.getNumZoomLevels()) );
         if (valid && zoomFilter.value != 999) {
             // Toto je trochu hack, ale jinak (napr. pomoci eventu) nelze zajistit
             // aby se aktualizovalo kriterium filtru pri zmene zoom levelu.
             zoomFilter.value = zoomLevel;
         }
         return valid;
     };
     // pokud byl zoomlevel nastaven z url, musime aktualizovat filter
     zoomFilter.value = map.getZoom();

     $(window).hashchange(onHashChange);
     $(window).hashchange();
     if (!map.getCenter()) {
         map.setCenter(new OpenLayers.LonLat(mapconfig.lon, mapconfig.lat).transform(EPSG4326, map.getProjectionObject()), mapconfig.zoom);
     }
} // init

function setupPnkMap() {
    if (appMode == 'pnkmap') {
        // uz jsme v rezimu routing, neni co delat
        return;
    }
    if (appMode == 'routing') {
        destroyRouting();
    }

    map.setBaseLayer(layerPNK);
    $('.olControlLayerSwitcher').show();

    if(!mapconfig.mobilni) {
        kmlvrstvy = mapconfig.vrstvy;
        for (var i in kmlvrstvy) {
            addPoiLayer(kmlvrstvy[i][0], mapconfig.root_url + kmlvrstvy[i][1], kmlvrstvy[i][2] == 'True', kmlvrstvy[i][3]);
        }
        addRekola();

        selectControl = new OpenLayers.Control.SelectFeature(
            vectors, {
            toggle: true,
            clickout: true,
            multiple: false,
            onUnselect: onFeatureUnselect,
            onSelect: onFeatureSelect
        });

        map.addControl(selectControl);
        selectControl.activate();
    }

    if(mapconfig.mobilni) {
        position_layer = new OpenLayers.Layer.Vector("Poloha", {});
        map.addLayer(position_layer);
             
        geocontrol = new OpenLayers.Control.Geolocate({
            watch: true,
            bind: false,
            geolocationOptions: {
                enableHighAccuracy: true,
                maximumAge: 0,
                timeout: 7000 }
         });
         map.addControl(geocontrol);
         geocontrol.activate();
         geocontrol.events.register("locationupdated", geocontrol, onLocationUpdate);
     }

     appMode = 'pnkmap';
     $('.panel').hide();
     $('#uvod').show();
} // setupPnkMap

function destroyPnkMap() {
    map.removeControl(selectControl);
    selectControl.destroy();
    removePoiLayers();
}

function setupRouting() {
    if (appMode == 'routing') {
        // uz jsme v rezimu routing, neni co delat
        return;
    }
    if (appMode == 'pnkmap') {
       destroyPnkMap();
    }

    map.setBaseLayer(layerPNK_BW);
    $('.olControlLayerSwitcher').hide(); // jinak zustane po LS prouzek zpusobeny marginem
    CSApi.init(map, 'ad9beeeff0afb15e');

    markerLayer = new OpenLayers.Layer.Vector("Start/cil", {
        styleMap: new OpenLayers.StyleMap({
            externalGraphic: "${icon}",
            pointRadius: 15,
            graphicWidth: '${w}',
            graphicHeight: '${h}',
            graphicXOffset: '${xof}',
            graphicYOffset: '${yof}',
            graphicTitle: "Přetažením změníte trasu"
        }),
        displayInLayerSwitcher: false
    });
    map.addLayer(markerLayer);
    drag = new OpenLayers.Control.DragFeature(markerLayer, {
        onStart: onDragStart,
        onComplete: onDragComplete
    });
    map.addControl(drag);
    drag.activate();
    startMarker = new OpenLayers.Feature.Vector(
        new OpenLayers.Geometry.Point(0,0), {
            icon: "/static/img/route-start.png",
            w: 34, h: 42, xof: -17, yof: -42 }
    );
    endMarker = new OpenLayers.Feature.Vector(
        new OpenLayers.Geometry.Point(0,0),
            { icon: "/static/img/route-stop.png",
            w:34, h:42, xof: -17, yof: -42 }
    );
    wpAttrs = { icon: "/static/img/waypoint.png", w:26, h:35, xof: -8, yof: -32 };
    middleMarker = new OpenLayers.Feature.Vector(
        new OpenLayers.Geometry.Point(0,0), 
        wpAttrs
    );

    // zabranime odeslani formu, kdyz uzivatel zmackne enter v okamziku,
    // kdy neni vybrana polozka autocompletu 
    $(".jpSearch").keypress(function(e) {
        var code = (e.keyCode ? e.keyCode : e.which);
        if(code == 13) { //Enter keycode
            return false;
        }
    });
    $('#jpStartStreetSearch').autocomplete(search_options);
    $('#jpFinishStreetSearch').autocomplete(search_options);
    addJourneyLayer();
    toggleButtons();
    map.events.register("click", map, onMapClick);
    $('#jpPlanButton').click(onPlanButtonClick);
    $('.jpPlanType').click(onPlanSelect);
    $('.jpPlanType').hover(previewPlanIn, previewPlanOut);
    appMode = 'routing';
    selectedPlan = null;
    $('.panel').hide();
    $('#hledani').show();
    $('#jpStartStreetSearch').focus();
    $('#jpFeedbackForm').dialog({
        autoOpen: false,
        modal: true,
        buttons: {
            //"Poslat": function() {
            //},
            "Zrušit": function() { $(this).dialog("close"); }
        },
        title: "Připomínka k nalezené trase",
        width: "350px"
    });
    $('#jpFeedbackButton')
        .click(function() {
            //$('#jpFeedbackForm #trasa').val(CSApi.itinerary);
            //$('#jpFeedbackForm #varianta').val(selectedPlan);
            $('#jpFeedbackMailto').attr('href',
                'mailto:redakce@prahounakole.cz?subject=Připomínka k trase ' + CSApi.itinerary + ', varianta ' + selectedPlan);
            $('#jpFeedbackForm').dialog("open");
        });

    map.events.register('mousemove', map, onMouseMove);
} // setupRouting

function destroyRouting() {
    if (appMode != 'routing') {
        // mapa neni v routing modu, nemame co delat
        return;
    }
    drag.destroy(); 
    markerLayer.destroy();
    if (journeyLayer) {
        journeyLayer.destroy();
    }
    map.events.unregister("click", map, onMapClick);
    map.events.unregister('mousemove', map, onMouseMove);
    $('.olMap').css("cursor", "auto");
    appMode = 'normal';
}

function initRoutingPanel() {
    $('#jpDetails').hide();
    $('#jpPlanTypeSelector').hide();
    waypoints = [];
    selectedItinerary = null;
    selectedPlan = null;
    startFeature = null;
    endFeature = null;
    markerLayer.removeAllFeatures();
    if (journeyLayer) {
        journeyLayer.destroyFeatures();
    }
    $('#jpStartStreetSearch').val('');
    $('#jpFinishStreetSearch').val('');
    $('#jpStartStreetSearch').focus();
    toggleButtons();
}

function setWaypoint(feature) {
    // called either on selection of result from search box,
    // mouse click or dragging of a marker
    if (!feature.layer) {
        markerLayer.addFeatures(feature);
    }
    var lonlat = feature.geometry.clone().transform(map.getProjectionObject(), EPSG4326);
    if (feature == startMarker) {
        waypoints[0] = lonlat;
    } else if (feature == endMarker) {
        waypoints[1] = lonlat;
    } else {
        if (feature.attributes.sequenceId) {
            waypoints[parseInt(feature.attributes.sequenceId)] = lonlat;
        } else {
            waypoints.splice(parseInt(feature.attributes.newWpSequenceId) + 1, 0, lonlat);
        }
    }
    markerLayer.redraw();
    toggleButtons();
}

function onDragStart(feature, pixel) {
    dragInAction = true;
    if (! feature.attributes.sequenceId) {
        // jde o novy waypoint, nikoliv posun stavajiciho
        // dohledame posledni wp v poradi pred menenym segmentem
        var segment = findNearestSegment(feature.geometry);
        var wp = CSApi.getWaypointBySegment(selectedPlan, segment);
        // a jeho pozici si docasne ulozime na feature dragovaci ikony
        feature.attributes.newWpSequenceId = wp.attributes.sequenceId;
    }
}

function onDragComplete(feature) {
    dragInAction = false;
    if (feature == startMarker) {
        CSApi.nearestPoint(startMarker, updateStartLabel);
    } else if (feature == endMarker) {
        CSApi.nearestPoint(endMarker, updateEndLabel);
    }
    setWaypoint(feature);
    // po umisteni cile nebo pretazeni prvku uz nalezene trasy muzeme rovnou vyhledat
    if (waypoints.length >= 2)
       planJourney();
}

function onMapClick(e) {
    var marker;
    switch (routingState) {
        case 'start':
            marker = startMarker;
            $('#jpFinishStreetSearch').focus();
            break;
        case 'stop':
            marker = endMarker;
            // odebereme focus, jinak po chvili vybehne autocomplete
            $('#jpFinishStreetSearch').blur();
            break;
        default:
            return;
    }
    var position = map.getLonLatFromPixel(e.xy);
    movePointToLonLat(marker.geometry, position);
    onDragComplete(marker, position);
}

function toggleButtons() {
    switch (waypoints.length) {
        case 0:
            // IE nepodporuje hotspot pres souradnice, ale jen zakodovany v .cur
            $('.olMap').css("cursor", "url('/static/img/route-start.cur'), crosshair"); 
            $('.olMap').css("cursor", "url('/static/img/route-start.cur') 17 41, crosshair"); 
            routingState = 'start';
            break;
        case 1:
            $('.olMap').css("cursor", "url('/static/img/route-stop.cur'), crosshair"); 
            $('.olMap').css("cursor", "url('/static/img/route-stop.cur') 17 41, crosshair"); 
            routingState = 'stop';
            break;
        default:
            $('.olMap').css("cursor", "auto");
            // odebereme focus, jinak po chvili vybehne autocomplete
            $('#jpFinishStreetSearch').blur();
            $('#jpPlanButton').show();
            routingState = 'go';
    }
}

function updateStartLabel(features) {
    if (features && features.length > 0) {
        $('#jpStartStreetSearch').val(features[0].attributes.name);
    } 
}

function updateEndLabel(features) {
    if (features && features.length > 0) {
        $('#jpFinishStreetSearch').val(features[0].attributes.name);
    } 
}

// move the start and finish markers according to the route
// this is necessary if route was loaded directly by ID in URL hash
function updateMarkersAndLabels(route) {
    var startfinish = CSApi.getStartAndFinish(route);
    $('#jpStartStreetSearch').val(startfinish.start_label);
    $('#jpFinishStreetSearch').val(startfinish.finish_label);
    var lonlat = startfinish.start.clone().transform(EPSG4326, map.getProjectionObject());
    movePointToLonLat(startMarker.geometry, lonlat);
    setWaypoint(startMarker);
    lonlat = startfinish.finish.clone().transform(EPSG4326, map.getProjectionObject());
    movePointToLonLat(endMarker.geometry, lonlat);
    setWaypoint(endMarker);
    removeWaypointMarkers();
    var wps = CSApi.getWaypoints(route);
    for (var i=1; i < wps.length - 1; i++) {
        var marker = new OpenLayers.Feature.Vector(
            wps[i].geometry.clone(),
            wpAttrs
        );
        marker.attributes.sequenceId = wps[i].attributes.sequenceId;
        setWaypoint(marker);
     }
     markerLayer.redraw();
}

function removeWaypointMarkers() {
    // clear waypoints
    remove = [];
    for (var i=0; i < markerLayer.features.length; i++) {
        feature = markerLayer.features[i];
        if (feature != startMarker && feature != endMarker && feature != middleMarker) {
            remove.push(feature);
        }
    }
    markerLayer.destroyFeatures(remove);
}

function clearWaypoints() {
    waypoints.splice(2, waypoints.length - 2);
}

function onPlanButtonClick() {
    clearWaypoints();
    planJourney();
    return false;
}

function planJourney() {
    $('#jpPlanButton').hide();
    $('#jpPlanMessage').show();
    if (selectedPlan)
        reqPlan = selectedPlan;
    else
        reqPlan = 'balanced';
    selectedPlan = null;
    CSApi.journey(null, waypoints, 'balanced', addPlannedJourney, { select: reqPlan });
}

// callback to process route returned by server
function addPlannedJourney(itinerary, plan, route, options) {
    CSApi.routeInfo(route);
    if (plan == 'balanced') {
        CSApi.journey(itinerary, null, 'fastest', addPlannedJourney, options);
        CSApi.journey(itinerary, null, 'quietest', addPlannedJourney, options);
    }
    if (options && options.select && options.select == plan) {
        selectedItinerary = itinerary;
        setHash('trasa=' + itinerary, false);
        $('#' + plan).click();
        updateMarkersAndLabels(route);
    }
    $('#jpPlanTypeSelector').show();
    $('#jpPlanButton').show();
    $('#jpPlanMessage').hide();
}

function addJourneyLayer() {
    // create a styleMap with a custom default symbolizer
    var styleMap = new OpenLayers.StyleMap({
        "default": new OpenLayers.Style({
            strokeOpacity: 0.42,
            // strokeDashstyle: "dashdot",
            strokeWidth: 9,
            strokeColor: "yellow"
        }),
        "select": new OpenLayers.Style({
            strokeOpacity: 0.42,
            strokeWidth: 16
        })
    });
                   
    // create a lookup table with different symbolizers
    var lookup = {
        'balanced': {
            strokeColor: "yellow",
        },
        'fastest': {
            strokeColor: "red",
        },
        'quietest': {
            strokeColor: "green",
        }
    };
                   
    // Add a rule from the above lookup table, with the keys mapped to the "type" property of the features, for the "default" intent.
    styleMap.addUniqueValueRules("default", "plan", lookup);

    journeyLayer = new OpenLayers.Layer.Vector("Trasa", {
        styleMap: styleMap,
        displayInLayerSwitcher: false
    });
    map.addLayer(journeyLayer);
}

function onPlanSelect() {
    selectPlan($(this).data('plan'));
}

function selectPlan(plan) {
    if (plan == selectedPlan) {
        // kliknuti na selector planu zazoomuje zpet na celou trasu
        map.zoomToExtent(journeyLayer.getDataExtent());
        return true;
    }
    if (! CSApi.routeFeatures || ! CSApi.routeFeatures[plan]) {
        return false;
    }
    journeyLayer.removeAllFeatures();
    journeyLayer.addFeatures(CSApi.routeFeatures[plan]);
    map.zoomToExtent(journeyLayer.getDataExtent());
    $('.selected').removeClass('selected');
    $('#' + plan).addClass('selected');
    $('#needle').attr('class', plan);
    selectedPlan = plan;
    $('#jpInstructions').html(CSApi.getRouteInstructions(plan));
    $('#jpInstructions').find('tr').click(zoomToSegment);
    $('#jpDetails').show();
    $('#gpxLink').attr('href', CSApi.gpxLink(plan));
    setHashParameter('plan', plan, false);
}
        
function previewPlanIn() {
    var plan = $(this).data('plan');
    if (! CSApi.routeFeatures || ! CSApi.routeFeatures[plan]) {
        return false;
    }
    if ($('#' + plan).hasClass('selected')) {
        return false;
    }
    previewedRoute = CSApi.routeFeatures[plan];
    journeyLayer.addFeatures(previewedRoute);
}

function previewPlanOut() {
    var plan = $(this).data('plan');
    if (!previewedRoute) {
        return false;
    }
    if ($('#' + plan).hasClass('selected')) {
        return false;
    }
    journeyLayer.removeFeatures(previewedRoute);
    previewedRoute = null;
}

function closeToWaypoints(pt, limit) {
    // check if given point is close to any waypoint
    for (var i=0; i < waypoints.length; i++) {
        if (pt.distanceTo(waypoints[i].clone().transform(EPSG4326, map.getProjectionObject())) < limit)
            return true;
    }
    return false;
}

function findNearestSegment(pt) {
    var segments = CSApi.segments[selectedPlan];
    var feat = null;
    var featDist = Number.MAX_VALUE;
    for (var i=0; i < segments.length; i++) {
        curDist = pt.distanceTo(segments[i].geometry);
        if (curDist < featDist) {
            featDist = curDist;
            feat = segments[i];
        }
    }
    return feat; 
}

function onMouseMove(e) {
    // Podle vzdalenosti kurzoru od trasy umozni preroutovani
    // pridanim markeru pro dalsi waypoint.
    // Po jeho pretazeni se pusti onDragComplete, jako u ostatnich markeru.
    if (!selectedPlan || dragInAction)
        return;
    var cur = map.getLonLatFromPixel(e.xy);
    var curPt = new OpenLayers.Geometry.Point(cur.lon, cur.lat);
    var line = CSApi.route[selectedPlan];
    var dist = line.geometry.distanceTo(curPt, { details: true});
    // vzdalenost kurzoru od cary v pixelech prepoctena dle aktualniho zoomu
    var LIMIT = 20 * map.getResolution();
    if (dist.distance < LIMIT && !closeToWaypoints(curPt, 2*LIMIT)) {
        movePointToLonLat(middleMarker.geometry, {lon: dist.x0, lat: dist.y0});
        markerLayer.addFeatures(middleMarker);
        markerLayer.redraw();
    } else {
        // Pokud se kurzor nachazi nad ikonou, ale daleko od trasy
        // musime explicitne rict DragControlu, ze uz neni nad feature,
        // pred tim, nez ji zrusime. Jinak zustane kurzor v rezimu drag
        // a pri kliknuti kamkoliv do mapy ve snaze o posun se vytvory waypoint.
        if (drag.feature && drag.feature == middleMarker) {
            drag.outFeature(drag.feature);
        }
        if (middleMarker.layer) {
            markerLayer.removeFeatures(middleMarker);
            markerLayer.redraw();
        }
    }
}

function parseHash() {
    var hash = location.hash;
    hash = hash.replace(/^#/, '');
    var parts = hash.split('@');
    var args = {};
    for (var i=0; i < parts.length; i++) {
        var a = parts[i].split('=');
        args[a[0]] = a[1];
    }
    return args;
}

function onHashChange(e) {
    if (ignoreHashChange) {
        ignoreHashChange = false;
        return;
    }

    var hash = location.hash;
    hash = hash.replace(/^#/, '');
    var args = parseHash();
    if (hash === '') {
        setupPnkMap();
    }
    if (hash == 'hledani') {
        setupRouting();
        initRoutingPanel();
    }
    if (args['trasa']) {
        setupRouting();
        var plan = args['plan'];
        if ($.inArray(plan, ['balanced', 'quietest', 'fastest']) < 0) {
            plan = 'balanced';
        }
        if (selectedItinerary == args['trasa']) {
            if (selectedPlan != plan) {
                selectPlan(plan);
            }
            return;
        }
        // odebereme focus nastaveny v setupRouting, jinak po chvili vybehne autocomplete
        $('.ui-autocomplete-input').blur();
        selectedPlan = null;
        CSApi.journey(args['trasa'], null, 'balanced', addPlannedJourney, { select: plan });
    }
}

// if trigger=True, fires the hashchange event
function setHash(newhash, trigger) {
    if (!trigger && (location.hash.replace(/^#/, '') != newhash)) {
        ignoreHashChange = true;
    }
    location.hash = newhash;
}

// encode the param into hash url
function setHashParameter(param, value, trigger) {
    args = parseHash();
    args[param] = value;
    var newhash = '';
    for (var i in args) {
        newhash += '@' + i + '=' + args[i];
    }
    if (newhash !== '') {
        newhash = newhash.substr(1);
    }
    setHash(newhash, trigger);
}

function getPoi(id) {
    var feat;
    for(var i=0; i<map.layers.length; i++) {
        if (map.layers[i].isBaseLayer)
            continue;
        feat = map.layers[i].getFeatureByFid(id);
        if (feat) {
            return feat;
        }
    }
}
        
function onLoadEnd(evt) {
    if (mapconfig.center_feature) {
       var feature = this.getFeatureByFid(mapconfig.center_feature);
       if (feature) {
	       ZoomToLonLat(this, mapconfig.lon, mapconfig.lat, 17);
           selectControl.select(feature);
       }
    }
}

function addPoiLayer(nazev, url, enabled, id) {
    for (var i=0; i < vectors.length; i++) {
        if (vectors[i].name == nazev) {
            map.addLayer(vectors[i]);
            return;
        }
    }
    kml = new OpenLayers.Layer.Vector(nazev, {
        projection: EPSG4326,
        slug: id,
        strategies: [new OpenLayers.Strategy.Fixed()],
        rendererOptions: {yOrdering: true, zIndexing: true},
        protocol: new OpenLayers.Protocol.HTTP({
            url: url,
            format: new OpenLayers.Format.KML({
                extractStyles: true,
                extractAttributes: true})
        })
    });
    kml.setVisibility(enabled);
    kml.styleMap.styles["default"].addRules([filter_rule]);
    kml.styleMap.styles["default"].defaultStyle.cursor = 'pointer';
    kml.events.register('loadend', kml, onLoadEnd);
    vectors.push(kml);
    map.addLayer(kml);
}

function removePoiLayers() {
    for (var i=0; i < vectors.length; i++) {
        map.removeLayer(vectors[i]);
    }
}

function removePopup(popup) {
    map.removePopup(popup);
    popup.destroy();
}
     
function onPopupClose(evt) {
    removePopup(this);
}

function onFeatureSelect(feature) {
    var url = mapconfig.root_url + "/popup/" + feature.fid + "/";
    lastSelectedFeature = feature.fid;
    for (var i in map.popups) {
        removePopup(map.popups[i]);
    }

    // Trochu hackovita podpora pro specialni vrstvu ReKola
    // obsah popup se netaha ze serveru, ale vyrabi se z KML
    if (feature.layer.name == "ReKola") {
        var response = {};
        response.responseText =
            '<div> <div class="trc"> <h4>' +
            feature.attributes.name +
            '</h4> </div><div class="rc"><p>' + 
            feature.attributes.description +
            '<p><a href="http://www.rekola.cz/" target="_blank">ReKola - komunitní bikesharing (zatím) v Praze</a>' +
            '</div></div>';
        feature.attributes.width = 32;
        feature.attributes.height = 20;
        createPopup.call(feature, response);
        return;
    }

    var requestFailed = function(response) {
        alert(response.responseText);
    };

    var request = OpenLayers.Request.GET({
        url: url,
        success: createPopup,
        failure: requestFailed,
        scope: feature
    });
}

var createPopup = function(response) {
    if (this.fid != lastSelectedFeature) {
        // Pokud uzivatel klika moc rychle, dobehne nacitani popupu az po vybrani
        // jineho POI. V tom pripade popup vyrabet nebudeme.
        return false;
    }
    var anchor;
    if (this.geometry.CLASS_NAME == 'OpenLayers.Geometry.Point') {
        anchor = {
            'size': new OpenLayers.Size(this.attributes.width,this.attributes.height),
            'offset': new OpenLayers.Pixel(-this.attributes.width/2,-this.attributes.height/2)
        };
    } else {
        anchor = null;
    }
    popup = new OpenLayers.Popup.FramedCloud(
        "chicken", 
        this.geometry.getCentroid(true).getBounds().getCenterLonLat(),
        new OpenLayers.Size(300,300),
        response.responseText,
        anchor,
        true,
        null
    );
    popup.keepInMap = true;
    popup.panMapIfOutOfView = true;
    popup.maxSize = new OpenLayers.Size(320,500);
    this.popup = popup;
    popup.feature = this;
    map.addPopup(popup);
};

function onFeatureUnselect(feature) {
    if (feature.popup)
        removePopup(feature.popup);
}

function zoomToSegment() {
    feature = journeyLayer.getFeatureById($(this).attr('data-fid'));
    map.zoomToExtent(feature.geometry.getBounds(), closest=true);
    //setHashParameter('rnd', feature.id.split('_')[1]);
}

function ZoomToLonLat( obj, lon, lat, zoom) {
    lonlat = new OpenLayers.LonLat(lon,lat);
	lonlat.transform(EPSG4326, map.getProjectionObject());
	map.setCenter(lonlat,zoom);
	   
	// Test on displayed left overlay - move right to be visible.
	var overlay_left = $('#overlay_left');
	if(overlay_left.css('display') != 'none') {
	    //alert("Overlay, musime posutnout!");
	    map.pan(-130,0);
	}
}

// utility funciton to move OpenLayers point
function movePointToLonLat(point, ll) {
    point.move(ll.lon - point.x, ll.lat - point.y);
} 

var accuracy_style = {
    fillOpacity: 0.1,
    fillColor: '#000',
    strokeColor: '#00f',
    strokeOpacity: 0.4
};

function onLocationUpdate(evt) {
    var coords = evt.position.coords;
    position_layer.removeAllFeatures();
    position_layer.addFeatures([
        new OpenLayers.Feature.Vector(
            evt.point,
            {}, {
                graphicName: 'cross',
                strokeColor: '#00f',
                strokeWidth: 2,
                fillOpacity: 0,
                pointRadius: 10
         }),
         new OpenLayers.Feature.Vector(
             OpenLayers.Geometry.Polygon.createRegularPolygon(
                 new OpenLayers.Geometry.Point(
                    evt.point.x, evt.point.y),
                    evt.position.coords.accuracy / 2,
                    50,
                    0
             ),
             {},
             accuracy_style
         )
    ]);
    map.zoomToExtent(position_layer.getDataExtent());
}

function addRekola() {
    for (var i=0; i < vectors.length; i++) {
        if (vectors[i].slug == 'r') {
            map.addLayer(vectors[i]);
            return;
        }
     }
     var rekola = new OpenLayers.Layer.Vector("ReKola", {
         slug: "r",
         strategies: [new OpenLayers.Strategy.Fixed()],
         protocol: new OpenLayers.Protocol.Script({
            // pomoci Yahoo obchazime crossdomain bezpecnostni politiku
            // http://openlayers.org/dev/examples/cross-origin-xml.html
            url: "http://query.yahooapis.com/v1/public/yql",
            params: {
                q: "select * from xml where url='http://moje.rekola.cz/api/bikes/kml'"
            },
            //url: "http://app.rekola.cz/server/api/bikes/kml",
            format: new OpenLayers.Format.KML({
                //extractStyles: true, 
                extractAttributes: true,
                maxDepth: 2
            }),
            parseFeatures: function(data) {
                return this.format.read(data.results[0]);
            }
        })
     });
     rekola.styleMap.styles["default"].defaultStyle.cursor = 'pointer';
     rekola.styleMap.styles["default"].defaultStyle.externalGraphic = '/static/img/rekola.png';
     rekola.styleMap.styles["default"].defaultStyle.graphicWidth = 20;
     rekola.styleMap.styles["default"].defaultStyle.graphicHeight = 20;
     rekola.styleMap.styles["default"].defaultStyle.fillOpacity = 1;
     map.addLayers([rekola]);
     vectors.push(rekola);
}
