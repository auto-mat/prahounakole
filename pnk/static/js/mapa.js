        var map, base_layer, kml, filter_rule, nofilter_rule, zoomFilter;
        var appMode = ''; // pnkmap nebo routing
        // jakou cast zadani prave resime - slouzi hlavne pro obsluhu kurzoru
        // * start, stop - vychozi a cilovy bod
        // * go - muzeme spustit vyhledavani
        var routingState = 'start';
        var vectors = [];
        var searchLayer;
        var searchLayerIdx;
        var journeyLayer, markerLayer, startMarker, endMarker;
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

        var bounds = new OpenLayers.Bounds(14.018,49.762,14.897,50.318);

        var EPSG4326 = new OpenLayers.Projection("EPSG:4326");
        var EPSG900913 = new OpenLayers.Projection("EPSG:900913"); 

        bounds.transform(EPSG4326, EPSG900913)

function defaultPanZoom() {
    var newPanZoom = new OpenLayers.Control.PanZoom();

    OpenLayers.Util.extend(newPanZoom, {
           onButtonClick: function(evt) {
               var btn = evt.buttonElement;
               switch (btn.action) {
                   case "panup": 
                       this.map.pan(0, -this.getSlideFactor("h"));
                       break;
                   case "pandown": 
                       this.map.pan(0, this.getSlideFactor("h"));
                       break;
                   case "panleft": 
                       this.map.pan(-this.getSlideFactor("w"), 0);
                       break;
                   case "panright": 
                       this.map.pan(this.getSlideFactor("w"), 0);
                       break;
                   case "zoomin": 
                       this.map.zoomIn(); 
                       break;
                   case "zoomout": 
                       this.map.zoomOut(); 
                       break;
                   case "zoomworld": 
                       map.setCenter(new OpenLayers.LonLat(mapconfig.baselon, mapconfig.baselat).transform(EPSG4326, map.getProjectionObject()), mapconfig.basezoom);
                       break;
                   }
           }
       });
       return newPanZoom;
      }

       function getTileURL(bounds)
       {
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
                //type: OpenLayers.Filter.Logical.OR // not good
                type: OpenLayers.Filter.Logical.AND
            });
            
            filter_rule = new OpenLayers.Rule({
                filter: mainFilter,
                symbolizer: {'externalGraphic': '${ikona}', 'graphicWidth': 20, 'graphicHeight': 20,
                graphicXOffset: -10, graphicYOffset: -10, 'graphicOpacity': 1, 'graphicTitle': '${name}' }
            });
            nofilter_rule = new OpenLayers.Rule({
                symbolizer: {'externalGraphic': '${ikona}', 'graphicWidth': 20, 'graphicHeight': 20,
                graphicXOffset: -10, graphicYOffset: -10, 'graphicOpacity': 1, 'graphicTitle': '${name}' }
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

            var options = { 
                controls: [
                    new OpenLayers.Control.ArgParser(),
                    new OpenLayers.Control.Attribution(),
                    new OpenLayers.Control.LayerSwitcher({roundedCornerColor:'#cb541c', ascending:0}),
                    new OpenLayers.Control.Navigation(),
                    new OpenLayers.Control.Permalink(),
                    new OpenLayers.Control.ScaleLine({maxWidth: 300}),
                    defaultPanZoom()
                    //  new OpenLayers.Control.PanZoomBar(),
                    //  new OpenLayers.Control.MousePosition() 
                ],
                maxExtent: bounds.clone(),
                restrictedExtent: bounds.clone(),
                projection: EPSG4326,
                displayProjection : EPSG4326,
		// fallThrough : false,
                theme: null
            };

            map = new OpenLayers.Map('map', options);

	   var ls = map.getControlsByClass('OpenLayers.Control.LayerSwitcher')[0];
           if (mapconfig.minimize_layerswitcher)
	       ls.minimizeControl();
           else
	       ls.maximizeControl();

            base_layer = new OpenLayers.Layer.OSM.Mapnik("OpenStreetMap", { 
                displayOutsideMaxExtent: false,
                displayInLayerSwitcher: true
            });

            //var layerTah    = new OpenLayers.Layer.OSM.Osmarender("Osmarender");
            var layerCycle  = new OpenLayers.Layer.OSM.CycleMap("Cycle map");
            var layerOPNKM = new OpenLayers.Layer.OSM(
                        "Prahou na kole",
                        "http://tiles.prahounakole.cz/",
                        { type: 'png', numZoomLevels: 19, getURL: getTileURL, tileOptions : {crossOriginKeyword: null} }
            );
            var layerGoogle = new OpenLayers.Layer.Google(
                "Satelitní mapa Google",
                {type: google.maps.MapTypeId.SATELLITE, numZoomLevels: 22}
            );

            map.addLayers([layerOPNKM, base_layer, layerCycle, layerGoogle]);
            layerGoogle.mapObject.setTilt(0);


            // zabranime odzoomovani na nizsi level nez 11 
            map.isValidZoomLevel = function(zoomLevel) {
                var valid = ( (zoomLevel != null) &&
                    (zoomLevel >= 11) &&
                    (zoomLevel < this.getNumZoomLevels()) );
                if (valid && zoomFilter.value != 999) {
                    // Toto je trochu hack, ale jinak (napr. pomoci eventu) nelze zajistit
                    // aby se aktualizovalo kriterium filtru pri zmene zoom levelu.
                    zoomFilter.value = zoomLevel;
                }
                return valid;
            }
            if (!map.getCenter()) {
                map.setCenter(new OpenLayers.LonLat(mapconfig.lon, mapconfig.lat).transform(EPSG4326, map.getProjectionObject()), mapconfig.zoom);
            }
            // pokud byl zoomlevel nastaven z url, musime aktualizovat filter
            zoomFilter.value = map.getZoom();

            $(window).hashchange(onHashChange);
            $(window).hashchange();
        } // init

        function setupPnkMap() {
            if (appMode == 'pnkmap') {
                // uz jsme v rezimu routing, neni co delat
                return;
            };
            if (appMode == 'routing') {
                destroyRouting();
            };

            kmlvrstvy = mapconfig.vrstvy
            for (i in kmlvrstvy) {
                addPoiLayer(kmlvrstvy[i][0], mapconfig.root_url + kmlvrstvy[i][1], kmlvrstvy[i][2] == 'True');
            };

            selectControl = new OpenLayers.Control.SelectFeature(
                vectors, {
                    toggle: true,
                    clickout: true,
                    multiple: false,
                    onUnselect: onFeatureUnselect,
                    onSelect: onFeatureSelect
                }
            );

            map.addControl(selectControl);
            selectControl.activate();
            appMode = 'pnkmap';
            $('.panel').hide();
            $('#uvod').show();
        };
        function destroyPnkMap() {
            map.removeControl(selectControl);
            selectControl.destroy();
            removePoiLayers();
        };

        function setupRouting() {
            if (appMode == 'routing') {
                // uz jsme v rezimu routing, neni co delat
                return;
            };
            if (appMode == 'pnkmap') {
                destroyPnkMap();
            };

            CSApi.init(map, 'ad9beeeff0afb15e');

            markerLayer = new OpenLayers.Layer.Vector("Start/cil", {
                 styleMap: new OpenLayers.StyleMap({
                     externalGraphic: "${icon}",
                     pointRadius: 15,
                     graphicYOffset: -30 // melo by byt 34, ale ikona je resizovana na 30
                })
            });
            map.addLayer(markerLayer);
            drag = new OpenLayers.Control.DragFeature(markerLayer, {
                onComplete: onDragComplete
            });
            map.addControl(drag);
            drag.activate();
            startMarker = new OpenLayers.Feature.Vector(
                    new OpenLayers.Geometry.Point(
                          map.getCenter().lon,
                          map.getCenter().lat
                    ),
                    { icon: "/static/img/route-start.png" }
            );
            endMarker = new OpenLayers.Feature.Vector(
                    new OpenLayers.Geometry.Point(
                        1608999.3765555094,
                        6460357.3778253645
                    ),
                    { icon: "/static/img/route-stop.png" }
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
            addRouteLayer();
            toggleButtons();
            map.events.register("click", map, onMapClick);
            $('#jpPlanButton').click(planJourney);
            $('.jpPlanType').click(selectPlan);
            $('.jpPlanType').hover(previewPlanIn, previewPlanOut);
            appMode = 'routing';
            $('.panel').hide();
            $('#hledani').show();
            $('#jpStartStreetSearch').focus();
        }
        function destroyRouting() {
            if (appMode != 'routing') {
                // mapa neni v routing modu, nemame co delat
                return;
            };
            drag.destroy(); 
            markerLayer.destroy();
            if (journeyLayer) {
                journeyLayer.destroy();
            };
            appMode = 'normal';
        }
        function initRoutingPanel() {
            $('#jpInstructions').hide();
            $('#jpPlanTypeSelector').hide();
            waypoints = [];
            selectedItinerary = null;
            startFeature = null;
            endFeature = null;
            markerLayer.destroyFeatures();
            if (journeyLayer) {
                journeyLayer.destroyFeatures();
            };
            $('#jpStartStreetSearch').val('');
            $('#jpFinishStreetSearch').val('');
            $('#jpStartStreetSearch').focus();
            toggleButtons();
        }
        function setWaypoint(feature) {
            // called either on selection of result from search box
            // or in dragging of marker
            var lonlat;
            if (feature == startMarker) {
                lonlat = startMarker.geometry.clone();
                waypoints[0] = lonlat.transform(map.getProjectionObject(), EPSG4326);
            }
            if (feature == endMarker) {
                lonlat = endMarker.geometry.clone();
                waypoints[1] = lonlat.transform(map.getProjectionObject(), EPSG4326);
            }
            toggleButtons();
        };
        function onDragComplete(feature) {
            if (feature == startMarker) {
                CSApi.nearestPoint(startMarker, updateStartLabel);
            }
            if (feature == endMarker) {
                CSApi.nearestPoint(endMarker, updateEndLabel);
            }
            setWaypoint(feature);
        };
        function onMapClick(e) {
            if (routingState == 'start')
                marker = startMarker;
            else if (routingState == 'stop')
                marker = endMarker;
            else
                return;
            var position = map.getLonLatFromPixel(e.xy);
            movePointToLonLat(marker.geometry, position)
            if (!marker.layer) {
                markerLayer.addFeatures(marker);
            };
            markerLayer.redraw();
            onDragComplete(marker, position);
            // po umisteni cile muzeme rovnou vyhledat
            if (marker == endMarker)
                $('#jpPlanButton').click();
        };
        function toggleButtons() {
            switch (waypoints.length) {
                case 0:
                    $('.olMap').css("cursor", "url('/static/img/route-start.png') 10 34, auto"); 
                    routingState = 'start';
                    break;
                case 1:
                    $('.olMap').css("cursor", "url('/static/img/route-stop.png') 10 34, auto");
                    routingState = 'stop';
                    break;
                default:
                    $('.olMap').css("cursor", "auto");
                    routingState = 'go';
                    $('#jpPlanButton').show();
            }
        };
        function updateStartLabel(features) {
            if (features && features.length > 0) {
                $('#jpStartStreetSearch').val(features[0].attributes.name);
            } 
        };
        function updateEndLabel(features) {
            if (features && features.length > 0) {
                $('#jpFinishStreetSearch').val(features[0].attributes.name);
            } 
        };
        // move the start and finish markers according to the route
        // this is necessary if route was loaded directly by ID in URL hash
        function updateMarkersAndLabels(route) {
            var startfinish = CSApi.getStartAndFinish(route);
            $('#jpStartStreetSearch').val(startfinish.start_label);
            $('#jpFinishStreetSearch').val(startfinish.finish_label);
            var lonlat = startfinish.start.clone().transform(EPSG4326, map.getProjectionObject());
            movePointToLonLat(startMarker.geometry, lonlat);
            lonlat = startfinish.finish.clone().transform(EPSG4326, map.getProjectionObject());
            movePointToLonLat(endMarker.geometry, lonlat);
            markerLayer.redraw();
        };
        function planJourney() {
            $('#jpPlanButton').hide();
            $('#jpPlanMessage').show();
            CSApi.journey(null, waypoints, 'balanced', addPlannedJourney, { select: true });
        };
        // callback to process route returned by server
        function addPlannedJourney(itinerary, route, options) {
            CSApi.routeInfo(route);
            if (options && options.select) {
                selectedItinerary = itinerary;
                CSApi.journey(itinerary, null, 'fastest', addPlannedJourney);
                CSApi.journey(itinerary, null, 'quietest', addPlannedJourney);
                location.hash = 'trasa=' + itinerary;
                $('#balanced').click();
                updateMarkersAndLabels(route);
            }
            $('#jpPlanTypeSelector').show();
            $('#jpPlanButton').show();
            $('#jpPlanMessage').hide();
        }
        function addRouteLayer() {
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
            });
            map.addLayer(journeyLayer);
        }
        function selectPlan() {
            var plan = this.id;
            if (plan == selectedPlan) {
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
            selectedPlan = plan;
            $('#jpInstructions').html(CSApi.getRouteInstructions(plan)).show();
        }
        function previewPlanIn() {
            var plan = this.id;
            if (! CSApi.routeFeatures || ! CSApi.routeFeatures[plan]) {
                return false;
            }
            if ($(this).hasClass('selected')) {
                return false;
            }
            previewedRoute = CSApi.routeFeatures[plan];
            journeyLayer.addFeatures(previewedRoute);
        }
        function previewPlanOut() {
            if (!previewedRoute) {
                return false 
            };
            if ($(this).hasClass('selected')) {
                return false;
            }
            journeyLayer.removeFeatures(previewedRoute);
            previewedRoute = null;
        }
        function onHashChange() {
                var hash = location.hash;
                hash = hash.replace(/^#/, '');
                var parts = hash.split('@');
                var args = {};
                for (var i=0; i < parts.length; i++) {
                        var a = parts[i].split('=');
                        args[a[0]] = a[1];
                }
                if (hash == '') {
                        setupPnkMap();
                };
                if (hash == 'hledani') {
                        setupRouting();
                        initRoutingPanel();
                };
                if (args['trasa']) {
                        setupRouting();
                        if (selectedItinerary == args['trasa']) {
                                return;
                        }
                        selectedPlan = null;
                        CSApi.journey(args['trasa'], null, args['plan'], addPlannedJourney, { select: true });
                };
        };

        function getPoi(id) {
            var feat;
            for(var i=0; i<map.layers.length; i++) {
                if (map.layers[i].isBaseLayer)
                        continue
                feat = map.layers[i].getFeatureByFid(id);
                if (feat) {
                    return feat;
                }
            }
        };
        
        function onLoadEnd(evt) {
	   if (mapconfig.center_feature) {
                var feature = this.getFeatureByFid(mapconfig.center_feature);
                if (feature) {
	            ZoomToLonLat(this, mapconfig.lon, mapconfig.lat, 17);
                    selectControl.select(feature);
                }
            }
        };

        function addPoiLayer(nazev, url, enabled) {
            for (var i=0; i < vectors.length; i++) {
                if (vectors[i].name == nazev) {
                    map.addLayer(vectors[i]);
                    return;
                }
            }
            kml = new OpenLayers.Layer.Vector(nazev, {
                    projection: EPSG4326,
                    strategies: [new OpenLayers.Strategy.Fixed()],
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
        };

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
        };

        function onFeatureSelect(feature) {
            var url = mapconfig.root_url + "/popup/" + feature.fid + "/";
            lastSelectedFeature = feature.fid;
            for (var i in map.popups) {
               removePopup(map.popups[i]);
            }

            var request = OpenLayers.Request.GET({
               url: url,
               success: createPopup,
               failure: requestFailed,
               scope: feature
            });
        };

        var requestFailed = function(response) {
           alert(response.responseText);
        }

        var createPopup = function(response) {
            if (this.fid != lastSelectedFeature) {
               // Pokud uzivatel klika moc rychle, dobehne nacitani popupu az po vybrani
               // jineho POI. V tom pripade popup vyrabet nebudeme.
               return false;
            }
            var anchor = {'size': new OpenLayers.Size(this.attributes.width,this.attributes.height), 'offset': new OpenLayers.Pixel(-this.attributes.width/2,-this.attributes.height/2)}
            popup = new OpenLayers.Popup.FramedCloud(
                "chicken", 
                this.geometry.getBounds().getCenterLonLat(),
                new OpenLayers.Size(300,300),
                response.responseText,
                anchor, true, null
            );
            popup.keepInMap = true;
            popup.panMapIfOutOfView = false;
            popup.maxSize = new OpenLayers.Size(320,500);
            this.popup = popup;
            popup.feature = this;
            map.addPopup(popup);
        };

        function onFeatureUnselect(feature) {
            if (feature.popup)
                removePopup(feature.popup)
        };

        function hoverResult(id) {
            var feature = searchLayer.getFeatureByFid(id);
            selectControl.unselectAll();
            selectControl.select(feature);
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
	};

        // utility funciton to move OpenLayers point
        function movePointToLonLat(point, ll) {
            point.move(ll.lon - point.x, ll.lat - point.y);
        } 
