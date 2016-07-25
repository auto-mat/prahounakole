var map, layer_osm, layerPNK, kml, filter_rule, nofilter_rule, zoomFilter;
var layerSwitcher;
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
var drag = null;
var isRoutingSet = false;
var selectControl;
var lastSelectedFeature;
var criteria = {};
var criteriaCnt = 0;
var selectedItinerary = null;
var selectedPlan;
var dragInAction = false;
var ignoreHashChange = false;
var touchMoved = false;
var lastActions = "";

var EPSG4326 = new OpenLayers.Projection("EPSG:4326");
var EPSG900913 = new OpenLayers.Projection("EPSG:900913"); 

var bounds = new OpenLayers.Bounds(12,48.5,19,51.1);
var extent = new OpenLayers.Bounds(-180.0,-90.0,180.0,90.0);
bounds.transform(EPSG4326, EPSG900913);
extent.transform(EPSG4326, EPSG900913);

function getTileURL(bounds) {
    var res = this.map.getResolution();
    var x = Math.round((bounds.left - this.maxExtent.left) / (res * this.tileSize.w));
    var y = Math.round((this.maxExtent.top - bounds.top) / (res * this.tileSize.h));
    var z = this.map.getZoom();
    return this.url + z + "/" + x + "/" + y + "." + this.type;
}

//Hack, který vylepší scaffold přepínače vrstev
function polishLayersSwitcherScaffold(){
    $("#layer_switcher").prepend("<div id='dataLayers' class='col-md-6'></div>")
    $(".dataLbl").appendTo("#dataLayers");
    $(".dataLayersDiv").appendTo("#dataLayers");
    $("#layer_switcher").prepend("<div id='baseLayers' class='col-md-6'></div>")
    $(".baseLbl").appendTo("#baseLayers");
    $(".baseLayersDiv").appendTo("#baseLayers");
    $("#layer_toggles").appendTo('#dataLayers');
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

    var controls;
    layerSwitcher = new OpenLayers.Control.LayerSwitcher({'div':OpenLayers.Util.getElement('layer_switcher')});
    controls = [
        //new OpenLayers.Control.TouchNavigation(), // Tohle je zvláštní, pinchZoom mi funguje i bez toho a když to zapnu, tak to blokuje parametr xy pro touchend akci
        new OpenLayers.Control.ArgParser({configureLayers: configureLayers}),
        new OpenLayers.Control.Attribution(),
        layerSwitcher,
        new OpenLayers.Control.Navigation(),
        new OpenLayers.Control.Permalink({createParams: createParams}),
        new OpenLayers.Control.ScaleLine({maxWidth: 300, bottomOutUnits: ''}),
    ];

    var options = { 
        controls: controls,
        maxExtent: extent.clone(),
        restrictedExtent: bounds.clone(),
        projection: EPSG4326,
        displayProjection : EPSG4326,
        eventListeners: {
            "changelayer": mapLayerChanged,
            "changebaselayer": mapBaseLayerChanged,
        } ,
		// fallThrough : false,
        theme: null
    };

    map = new OpenLayers.Map('map', options);

    polishLayersSwitcherScaffold();

    layer_osm = new OpenLayers.Layer.OSM.Mapnik(
        "OpenStreetMap", { 
        slug: "O",
        displayOutsideMaxExtent: false,
    });
    var layerCycle  = new OpenLayers.Layer.OSM.CycleMap(
        "Cycle map", {
        slug: "C",
    });
    layerPNK = new OpenLayers.Layer.OSM(
        "Prahou na kole",
        "http://tiles.prahounakole.cz/", {
        slug:"P",
        type: 'png',
        numZoomLevels: mapconfig.maxzoom + 1,
        getURL: getTileURL,
        tileOptions : {crossOriginKeyword: null} 
    });
    layerIPR = new OpenLayers.Layer.WMS(
        "Ortofoto IPR mimovegetační",
        "http://mpp.praha.eu/arcgis/services/MAP/mimovegetacni_snimkovani_cache/MapServer/WmsServer",
        {
            layers: '0',
            format: 'image/jpeg',
            transparent: true,
            srs: "EPSG:3857",
        },
        {
            isBaseLayer: true,
            slug:"I",
            numZoomLevels: 22,
            displayInLayerSwitcher: true,
            attribution:"<a href='http://www.geoportalpraha.cz/cs/clanek/276/licencni-podminky-pro-otevrena-data' target='_new' title='link opens in new window'>IPR Praha CC BY-SA 4.0</a>",
            projection : new OpenLayers.Projection("EPSG:3857")
        });
    layerBW = new OpenLayers.Layer.OSM(
        "Černobílá",
        "http://tiles.prahounakole.cz/", {
        slug:"W",
        type: 'png',
        numZoomLevels: mapconfig.maxzoom + 1,
        getURL: getTileURL,
        className: "cb-tiles",
        transitionEffect: null,
        zoomMethod: null,
        tileOptions : {crossOriginKeyword: null}
    });

     map.addLayers([layerPNK, layer_osm, layerCycle, layerBW, layerIPR]);
     if(google.maps.MapTypeId !== undefined){
        var layerGoogle = new OpenLayers.Layer.Google(
           "Satelitní mapa Google", {
           slug:"G",
           type: google.maps.MapTypeId.SATELLITE,
           numZoomLevels: 21
        });
        map.addLayer(layerGoogle);
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

     $('.close_poi').live("click",function(){
        if(selectControl){
           selectControl.unselectAll();
        }
     });

     position_layer = new OpenLayers.Layer.Vector("Poloha", {});
     map.addLayer(position_layer);

     geocontrol = new OpenLayers.Control.Geolocate({
         watch: true,
         bind: true,
         geolocationOptions: {
             enableHighAccuracy: true,
             maximumAge: 0,
             timeout: 7000 }
      });
      map.addControl(geocontrol);
      geocontrol.events.register("locationupdated", geocontrol, onLocationUpdate);

      $("#geolocate").click(function(){
          if(!geocontrol.active) {
              geocontrol.activate();
          }
          if(position_layer.getDataExtent()){
              map.setCenter(position_layer.getDataExtent().getCenterLonLat());
          }
          geocontrol.bind = true;
          $("#geolocate").addClass("geobind_active");
      });
      $("#map").children().bind("touchstart click", function(){
          geocontrol.bind = false;
          $("#geolocate").removeClass("geobind_active");
          hidePanelOnMobile();
      });

      hidePanelOnMobile();
} // init

function mapLayerChanged(event) {
    reportAction('send', 'event', event.type, event.layer.name, event.property);
}

function mapBaseLayerChanged(event) {
    reportAction('send', 'event', event.type, event.layer.name);
}

function showPanel(slug) {
    // highlight active mode icon
    $('.mode-btn').parent().removeClass('active');
    $('.mode-btn.' + slug).parent().addClass('active');

    $('.panel').hide();
    $('#' + slug + '.panel').show();
};

function showPanel_closeBox(slug) {
   showPanel(slug);
   closePoiBox();
   if(selectControl){
      selectControl.unselectAll();
   }
   $(".print").show();
}

function updatePermalink(){
    permalink = map.getControlsBy("displayClass", "olControlPermalink")[0]
    permalink.updateLink()
}

function setupPnkMap() {
    if (appMode == 'pnkmap') {
        // uz jsme v rezimu pnkmap, neni co delat
        return;
    }
    if (appMode == 'routing') {
        destroyRouting();
    }

    $('.olControlLayerSwitcher').show();

    kmlvrstvy = mapconfig.vrstvy;
    if(vectors.length == 0){
       for (var i in kmlvrstvy) {
           name = kmlvrstvy[i][0];
           url = mapconfig.root_url + kmlvrstvy[i][1];
           slug = kmlvrstvy[i][3];
           enabled = kmlvrstvy[i][2] == 'True' || mapconfig.center_feature_slug == slug;
           switch(slug) {
               case 'a':
                   addCSLayer(name, enabled, slug);
                   break;
               case 'r':
                   addRekola(name, enabled, slug);
                   break;
               case 'g':
                   addDPNK1(name, enabled, slug);
                   break;
               case 't':
                   addDPNK2(name, enabled, slug);
                   break;
               default:
                   addPoiLayer(name, url, enabled, slug);
           }
       }
    } else {
       for (var i=0; i < vectors.length; i++) {
          vectors[i].setVisibility(vectors[i].was_visible);
       };
    };

    if(!selectControl){
       selectControl = new OpenLayers.Control.SelectFeature(
           vectors, {
           toggle: true,
           clickout: true,
           multiple: false,
           onUnselect: onFeatureUnselect,
           onSelect: onFeatureSelect
       });
    };

    map.addControl(selectControl);
    selectControl.activate();

     $('#mapStreetSearch').autocomplete(search_options);

     appMode = 'pnkmap';
     updatePermalink();
} // setupPnkMap

function destroyPnkMap() {
    map.removeControl(selectControl);
    selectControl.deactivate();
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

    CSApi.init(map, 'ad9beeeff0afb15e');

    if(isRoutingSet){
       markerLayer.setVisibility(true);
    } else {
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
    }

    if(!isRoutingSet){
       drag = new OpenLayers.Control.DragFeature(markerLayer, {
           onStart: onDragStart,
           onComplete: onDragComplete
       });

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
       $(document).on("submit", '#jpForm', onPlanButtonClick);
       $('.jpPlanType').click(onPlanSelect);
       $('.jpPlanType').hover(previewPlanIn, previewPlanOut);
       selectedPlan = null;
       $('#jpStartStreetSearch').focus();
    }

    toggleButtons();
    map.events.register("click", map, onMapClick);

    //Takhle zachycujeme kliknutí ma mobilu:
    map.events.register("touchmove", map, onTouchMove);
    map.events.register("touchend", map, onTouchEnd);

    appMode = 'routing';
    addJourneyLayer();
    map.addControl(drag);
    drag.activate();

    map.events.register('mousemove', map, onMouseMove);
} // setupRouting

function destroyRouting() {
    if (appMode != 'routing') {
        // mapa neni v routing modu, nemame co delat
        return;
    }
    isRoutingSet = true;
    drag.deactivate();
    markerLayer.setVisibility(false);
    if (journeyLayer) {
        journeyLayer.setVisibility(false);
    }
    map.events.unregister("click", map, onMapClick);
    map.events.unregister("touchend", map, onTouchEnd);
    map.events.unregister("touchmove", map, onTouchMove);
    map.events.unregister('mousemove', map, onMouseMove);
    $('.olMap').css("cursor", "auto");
    appMode = 'normal';
}

function initRoutingPanel() {
    if(!isRoutingSet){
       $('#jpDetails').hide();
       $('#jpPlanTypeSelector').hide();
       $('#jpPlanMessage').hide();
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
    routeHash();
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
        reportAction('send', 'event', 'drag', 'start', feature.attributes.newWpSequenceId);
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
    if (waypoints.length >= 2 && waypoints[0] && waypoints[1])
       planJourney();
}

function hidePanelOnMobile() {
    var vw = $('body').width();
    // kdyz je panel oteveny a sire stranky je mensi, nebo rovna 400px
    if(vw <= 400) {
       panel_action('minimize');
    }
}

function onTouchMove(e){
    touchMoved = true;
}
function onTouchEnd(e){
    if(!touchMoved){
        onMapClick(e);
    };
    touchMoved = false;
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

    hidePanelOnMobile();
}

function toggleButtons() {
    if(!waypoints[0]){
         $('#jpStartStreetSearch').removeClass('wp_set');
    } else {
         $('#jpStartStreetSearch').addClass('wp_set');
    }
    if(!waypoints[1]){
         $('#jpFinishStreetSearch').removeClass('wp_set');
    } else {
         $('#jpFinishStreetSearch').addClass('wp_set');
    }

    if(!waypoints[0]){
         // IE nepodporuje hotspot pres souradnice, ale jen zakodovany v .cur
         $('.olMap').css("cursor", "url('/static/img/route-start.cur'), crosshair");
         $('.olMap').css("cursor", "url('/static/img/route-start.cur') 17 41, crosshair");
         $('#jpPlanButton').hide();
         routingState = 'start';
    } else if(!waypoints[1]) {
         $('.olMap').css("cursor", "url('/static/img/route-stop.cur'), crosshair");
         $('.olMap').css("cursor", "url('/static/img/route-stop.cur') 17 41, crosshair");
         $('#jpPlanButton').hide();
         routingState = 'stop';
    } else {
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
    if(waypoints.length >= 2 && waypoints[0] && waypoints[1]){
        clearWaypoints();
        planJourney();
    } else {
        alert("Zadejte start i cíl trasy a vyberte ho z rozbalovací nabídky");
    }
    return false;
}

function planJourney() {
    $('#jpPlanButton').hide();
    $('#jpPlanMessage').show();
    if (selectedPlan)
        reqPlan = selectedPlan;
    else
        reqPlan = 'balanced';
    reportAction('send', 'event', 'plan', 'selected', selectedPlan);
    selectedPlan = null;
    CSApi.journey(null, waypoints, 'balanced', addPlannedJourney, { select: reqPlan });
}

function routeHash(){
   if(selectedPlan){
      setHashParameter('trasa', selectedItinerary, false);
      setHashParameter('plan', selectedPlan, false);
   }
}

// callback to process route returned by server
function addPlannedJourney(itinerary, plan, route, options) {
    reportAction('send', 'event', 'route', 'planned', plan, itinerary);
    CSApi.routeInfo(route);
    if (plan == 'balanced') {
        CSApi.journey(itinerary, null, 'fastest', addPlannedJourney, options);
        CSApi.journey(itinerary, null, 'quietest', addPlannedJourney, options);
    }
    if (options && options.select && options.select == plan) {
        selectedItinerary = itinerary;
        selectPlan(plan);
        if (options['zoomToPlan']){
            map.zoomToExtent(journeyLayer.getDataExtent());
        }
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
            strokeWidth: 12,
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

    if(journeyLayer) {
       journeyLayer.setVisibility(true);
    } else {
       journeyLayer = new OpenLayers.Layer.Vector("Trasa", {
           styleMap: styleMap,
           displayInLayerSwitcher: false
       });
       map.addLayer(journeyLayer);
    }
}

function onPlanSelect() {
    selectPlan($(this).data('plan'));
    map.zoomToExtent(journeyLayer.getDataExtent());
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
    $('.selected').removeClass('selected');
    $('#' + plan).addClass('selected');
    $('#needle').attr('class', plan);
    selectedPlan = plan;
    $('#jpInstructions').html(CSApi.getRouteInstructions(plan));
    $('#jpInstructions').find('tr').click(zoomToSegment);
    $('#jpDetails').show();
    $('#gpxLink').attr('href', CSApi.gpxLink(plan));
    routeHash();
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

function selectFeatureById(layer_slug, poi_id) {
   layer = map.getLayersBy("slug", layer_slug)[0];
   layer.setVisibility(true);
   feat = layer.getFeatureByFid(poi_id);
   if(feat) {
      map.zoomToExtent(feat.geometry.getBounds());
      selectControl.unselectAll();
      selectControl.select(feat);
   }
   mapconfig.center_feature_slug = layer_slug
   mapconfig.center_feature = poi_id
}

function parseHash() {
    var hash = location.hash;
    hash = hash.replace(/^#/, '');
    var args = {};
    if (hash.length == 0) {
        return args;
    }
    var parts = hash.split('@');
    for (var i=0; i < parts.length; i++) {
        var a = parts[i].split('=');
        args[a[0]] = a[1];
    }
    return args;
}

// if trigger=True, fires the hashchange event
function setHash(newhash, trigger) {
    if (!trigger && (location.hash.replace(/^#/, '') != newhash)) {
        ignoreHashChange = true;
    }
    location.hash = newhash;
}

function encodeHash(args) {
    var newhash = '';
    for (var i in args) {
        if (args[i]) {
            newhash += '@' + i + '=' + args[i];
        } else {
            newhash += '@' + i;
        }
    }
    if (newhash !== '') {
        newhash = newhash.substr(1);
    }
    return newhash;
}

// encode the param into hash url
function setHashParameter(param, value, trigger) {
    args = parseHash();
    args[param] = value;
    var newhash = encodeHash(args);
    setHash(newhash, trigger);
}

function removeHashParameter(param, trigger) {
    args = parseHash();
    delete args[param];
    var newhash = encodeHash(args);
    setHash(newhash, trigger);
}

function loadPanelContent(slug, func, onload) {
    div_class = '#' + slug;
    if($(div_class).children().length == 0){
       $(div_class).load($(div_class).data("src"), function(){
          func();
          if(onload !== undefined){
             onload();
          }
       });
    } else {
       func();
    }
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
        reportAction('send', 'event', 'left-panel-tab', 'switch', 'mapa');
        loadPanelContent('mapa', function(){
           setupPnkMap();
           showPanel_closeBox('mapa');
        });
    }
    if (hash == 'hledani') {
        reportAction('send', 'event', 'left-panel-tab', 'switch', 'hledani');
        loadPanelContent('hledani', function(){
           setupRouting();
           initRoutingPanel();
           showPanel_closeBox('hledani');
        });
    }
    if (args['trasa']) {
        reportAction('send', 'event', 'left-panel-tab', 'switch', 'trasa');
        loadPanelContent('hledani', function(){
           setupRouting();
           showPanel_closeBox('hledani');
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
           CSApi.journey(args['trasa'], null, 'balanced', addPlannedJourney, { select: plan, zoomToPlan: true });
        });
    }
    if (args['misto']) {
        var poi_array = args['misto'].split("_");
        mapconfig.center_feature = parseInt(poi_array[poi_array.length-1]);
        mapconfig.center_feature_slug = poi_array[poi_array.length-2];

        setupPnkMap();
        showPanel('mapa');
    }
    if (hash == 'informace') {
        reportAction('send', 'event', 'left-panel-tab', 'switch', 'informace');
        loadPanelContent('informace', function(){
           setupPnkMap();
           showPanel_closeBox('informace');
        }, function(){
           $('.harmonika .txt').not('.active').hide();
        });
    }
}

function onLoadEnd(evt) {
    if (mapconfig.center_feature) {
       var feature = this.getFeatureByFid(mapconfig.center_feature);
       if ((!mapconfig.center_feature_slug || mapconfig.center_feature_slug == this.slug) && feature) {
           map.zoomToExtent(feature.geometry.getBounds());
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
                extractStyles: false,
                extractAttributes: true})
        })
    });
    kml.setVisibility(enabled);
    kml.styleMap.styles["default"].addRules([filter_rule]);
    kml.styleMap.styles["default"].defaultStyle.cursor = 'pointer';
    kml.styleMap.styles["default"].defaultStyle.cursor = 'pointer';
    kml.events.register('loadend', kml, onLoadEnd);
    vectors.push(kml);
    map.addLayer(kml);
}

function removePoiLayers() {
    for (var i=0; i < vectors.length; i++) {
        vectors[i].was_visible = vectors[i].getVisibility();
        vectors[i].setVisibility(false);
    }
}

function onFeatureSelect(feature) {
    setHashParameter('misto', feature.layer.slug + "_" + feature.fid, false);
    var components = "";
    if(feature.geometry.components){
        components = feature.geometry.components;
    } else {
        components = [feature.geometry];
    }
    for(var i = 0; i < components.length; i++){
        $("#" + components[i].id).attr("class", "selected");
    }

    // Trochu hackovita podpora pro specialni vrstvu ReKola
    // obsah popup se netaha ze serveru, ale vyrabi se z KML
    if (feature.layer.slug == "r") {
        var response = {};
        response.responseText =
            '<div> <div class="trc"> <h4>' +
            feature.attributes.name +
            '</h4> <div class="row controls"> <div class="col-md-2 col-md-offset-10 centred"> <a class="sprite btn close close_poi" title="Zavřít popis místa"></a> </div> </div> </div> <div class="rc"><p>' +
            feature.attributes.description +
            '<p><a href="http://www.rekola.cz/" target="_blank">ReKola - komunitní bikesharing (zatím) v Praze</a>' +
            '</div></div>';
        feature.attributes.width = 32;
        feature.attributes.height = 20;
        createPopup.call(feature, response);
        return;
    }
    if (feature.layer.slug == "a") {
        var response = {};
        var photo = ""
        if(feature.attributes.photo_thumb_url){
            photo = "<img src='http://www.cyklistesobe.cz/" + feature.attributes.photo_thumb_url + "'>";
        }
        response.responseText =
            '<div> <div class="trc"> <h4>' +
            feature.attributes.title +
            '</h4> <div class="row controls"> <div class="col-md-2 col-md-offset-10 centred"> <a class="sprite btn close close_poi" title="Zavřít popis místa"></a> </div> </div> </div> <div class="rc"><p>' +
            photo +
            feature.attributes.description +
            '<p><a href="' +
            feature.attributes.cyclescape_url +
            '" target="_blank">Stránka podnětu Cyklisté sobě</a>' +
            '</div></div>';
        createPopup.call(feature, response);
        return;
    }
    showPoiDetail(feature.fid);
}

function reportAction(a, b="", c="", d="", e="", f=""){
   ga(a, b, c, d, e, f);
   lastActions += a + " " + b + " " + c + " " + d + " " + e + " " + f + "\n";
   Raven.setExtraContext({
      last_actions: lastActions,
   });
}

function onFeatureUnselect(feature) {
    reportAction('send', 'event', 'poi', 'close', feature.fid);
    var components = "";
    if(feature.geometry.components){
        components = feature.geometry.components;
    } else {
        components = [feature.geometry];
    }
    for(var i = 0; i < components.length; i++){
        $("#" + components[i].id).removeAttr("class");
    }
    closePoiBox();
}

function showPoiDetail(poi_id) {
    reportAction('send', 'event', 'poi', 'show', poi_id);
    var url = mapconfig.root_url + "/popup/" + poi_id + "/";

    var requestFailed = function(response) {
        alert(response.responseText);
    };

    var request = OpenLayers.Request.GET({
        url: url,
        success: createPopup,
        failure: requestFailed,
        //scope: feature
    });
}

function createPopup(response) {
    panel_action('maximize');
    $('#poi_text').html(response.responseText);
    jQuery('.textinput,.emailinput,#id_url,#id_comment').persist();
    $('#poi_box').slideDown(400).show(400);
    $('#panel-content').hide();
};

function closePoiBox() {
    $('#poi_box').slideUp(400).hide(400)
    $('#panel-content').show(400);
    removeHashParameter('misto', false);    
}

function zoomToSegment() {
    feature = journeyLayer.getFeatureById($(this).attr('data-fid'));
    map.zoomToExtent(feature.geometry.getBounds(), closest=true);
    //setHashParameter('rnd', feature.id.split('_')[1]);
}

function ZoomToLonLat(obj, lon, lat, zoom) {
    lonlat = new OpenLayers.LonLat(lon,lat);
    lonlat.transform(EPSG4326, map.getProjectionObject());
    map.setCenter(lonlat,zoom);
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
}

function addDPNK1(name, enabled, slug) {
  var dpnk_gpxfile = new OpenLayers.Layer.WMS(name,
     "http://www.auto-mat.cz:8080/geoserver/dpnk/wms?tiled=true",
     {
        layers: 'dpnk:the_gpx_geom_anonymous',
        format: 'image/png',
        transparent: true,
  });
  dpnk_gpxfile.slug = slug
  dpnk_gpxfile.setVisibility(enabled);
  map.addLayers([dpnk_gpxfile]);
}

function addDPNK2(name, enabled, slug) {
  var dpnk_tracks = new OpenLayers.Layer.WMS(name,
     "http://www.auto-mat.cz:8080/geoserver/dpnk/wms?tiled=true",
     {
        layers: 'dpnk:tracks_anonymous',
        format: 'image/png',
        transparent: true,
  });
  dpnk_tracks.slug = slug
  dpnk_tracks.setVisibility(enabled);
  map.addLayers([dpnk_tracks]);
}

function addCSLayer(name, enabled, slug) {
     var cs_layer = new OpenLayers.Layer.Vector(name, {
         slug: slug,
         strategies: [new OpenLayers.Strategy.Fixed()],
         protocol: new OpenLayers.Protocol.HTTP({
            url: "http://prahounakole.cz/wp-content/pnk/cs_tracks/list.json",
            format: new OpenLayers.Format.GeoJSON({
                   parseFeature: function(data) {
                       feature = OpenLayers.Format.GeoJSON.prototype.parseFeature(data)
                       if($.inArray("vyresene", feature.attributes.tags) != -1){
                          feature.attributes.feature_color = "#2BBF2B";
                          feature.attributes.select_color = "#135513";
                          feature.attributes.icon = '/static/img/cyklistesobe-done.png';
                       } else {
                          feature.attributes.feature_color = "#BF2B2B";
                          feature.attributes.select_color = "#531313";
                          feature.attributes.icon = '/static/img/cyklistesobe.png';
                       }
                       return feature
                   }
            }),
        }),
     });
     cs_layer.styleMap = new OpenLayers.StyleMap({
        "default": {
           cursor: 'pointer',
           externalGraphic: '${icon}',
           graphicWidth: 20,
           graphicHeight: 20,
           strokeWidth: 3,
           strokeColor: "${feature_color}",
           fillOpacity: 0.6,
           graphicOpacity: 1,
           fillColor: "${feature_color}",
        },
        "select": {
           fillColor: "${select_color}",
           strokeColor: "${select_color}",
           fillOpacity: 0.85,
           graphicOpacity: 1,
        },
     });
     cs_layer.setVisibility(enabled);
     cs_layer.events.register('loadend', cs_layer, onLoadEnd);
     map.addLayers([cs_layer]);
     vectors.push(cs_layer);
}

function addRekola(name, enabled, slug) {
     var rekola = new OpenLayers.Layer.Vector(name, {
         slug: slug,
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
     rekola.styleMap = new OpenLayers.StyleMap({
        "default": {
           cursor: 'pointer',
           externalGraphic: '/static/img/rekola.png',
           graphicWidth: 20,
           graphicHeight: 20,
           fillOpacity: 1,
        },
        "select": {
           fillOpacity: 1,
        },
     });
     rekola.setVisibility(enabled);
     rekola.events.register('loadend', rekola, onLoadEnd);
     map.addLayers([rekola]);
     vectors.push(rekola);
}

function activateLayers(base_layer_slug, overlay_layer_slugs){
   map.setBaseLayer(map.getLayersBy("slug", base_layer_slug)[0]);
   overlay_layer_slugs.push(mapconfig.center_feature_slug);

   for(var layer_id in map.layers){
      layer = map.layers[layer_id]
      if(layer.displayInLayerSwitcher && !layer.isBaseLayer)
        if($.inArray(layer.slug, overlay_layer_slugs) >= 0)
           map.layers[layer_id].setVisibility(true);
        else
           map.layers[layer_id].setVisibility(false);
   }
}

function switchAllLayers(enable){
   for(var layer_id in map.layers){
      layer = map.layers[layer_id]
      if(layer.displayInLayerSwitcher && !layer.isBaseLayer)
        if(enable)
           map.layers[layer_id].setVisibility(true);
        else
           map.layers[layer_id].setVisibility(false);
   }
}
    
