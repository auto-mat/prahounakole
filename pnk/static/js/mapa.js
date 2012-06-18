        var map, base_layer, kml, filter_rule, nofilter_rule, zoomFilter;
        var vectors = [];
        var searchLayer
        var searchLayerIdx;
        var lastSelectedFeature;
        var criteria = {};
        var criteriaCnt = 0;

        var bounds = new OpenLayers.Bounds(14.018,49.762,14.897,50.318);

        var EPSG4326 = new OpenLayers.Projection("EPSG:4326");
        var EPSG900913 = new OpenLayers.Projection("EPSG:900913"); 

        bounds.transform(EPSG4326, EPSG900913)

       function getTileURL(bounds)
       {
         var res = this.map.getResolution();
         var x = Math.round((bounds.left - this.maxExtent.left) / (res * this.tileSize.w));
         var y = Math.round((this.maxExtent.top - bounds.top) / (res * this.tileSize.h));
         var z = this.map.getZoom();
         return this.url + z + "/" + x + "/" + y + "." + this.type;
       }

        function init(mapconfig) {
            //OpenLayers.ImgPath = "/media/js/img/";
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
                    //new OpenLayers.Control.LayerSwitcher(),
                    new OpenLayers.Control.Navigation(),
                    new OpenLayers.Control.Permalink(),
                    new OpenLayers.Control.ScaleLine({maxWidth: 300}),
                    new OpenLayers.Control.PanZoom()
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


            kmlvrstvy = mapconfig.vrstvy
            for (i in kmlvrstvy) {
                addMapLayer(kmlvrstvy[i][0], mapconfig.root_url + kmlvrstvy[i][1], vectors);
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

            $.tools.overlay.addEffect('namiste',
                // vlastni overlay efekt, ktery narozdil od 'default'
                // nepridava k pozici scrollTop, cili neni zarovnany vuci oknu, ale cele strance
                function(pos, onLoad) {
                    var conf = this.getConf();
                    pos.position = 'absolute';
                    this.getOverlay().css(pos).fadeIn(conf.speed, onLoad); 
                    }, function(onClose) {
                        this.getOverlay().fadeOut(this.getConf().closeSpeed, onClose);                  
                    }
            );

	    var offset = $('#core').offset();
            // XXX V PNK se nepouziva, pozustatek Zelene mapy
            $('#overlay_left').overlay({
                effect: 'namiste',
	        top: 0,
	        left: offset.left,
	        fixed: false,
 	        oneInstance: false, 
	        closeOnClick: false,
                onClose: onLeftOverlayClosed
	    });
            $(window).hashchange(onHashChange);
            $(window).hashchange();
        } // init

        function onHashChange() {
                var hash = location.hash;
                hash = hash.replace(/^#/, '');
                if (hash == '') {
                        //$('#overlay_left').overlay().close();
                        return;
                }
                if (hash == 'doplnit') {
                        OverlayLeft(this, mapconfig.root_url + '/doplnit/');
                        return;
                }
                if (hash == 'vlastnosti') {
                        OverlayLeft(this, mapconfig.root_url + '/vlastnosti/');
                        return;
                }
                var parts = hash.split('@');
                var args = {};
                for (var i=0; i < parts.length; i++) {
                        var a = parts[i].split('=');
                        args[a[0]] = a[1];
                }
                /*
                // toto jeste nefunguje
                if (args['misto']) {
                    var poi = getPoi(args['misto']);
                };
                */
                
                if (args['detail']) {
                        OverlayLeft(this, mapconfig.root_url + '/detail/' + args['detail']);
                };
                if (args['clanek']) {
                        OverlayLeft(this, mapconfig.root_url + '/clanky/' + args['clanek']);
                };
                if (args['doplnit']) {
                        OverlayLeft(this, mapconfig.root_url + '/doplnit/' + args['doplnit']);
                };
        };

        function onLeftOverlayClosed() {
               location.hash = ''; 
        }

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

        function addMapLayer(nazev, url, layers) {
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
            kml.styleMap.styles["default"].addRules([filter_rule]);
            kml.styleMap.styles["default"].defaultStyle.cursor = 'pointer';
            kml.events.register('loadend', kml, onLoadEnd);
            map.addLayer(kml);
            var len = layers.push(kml);
            return (len - 1);
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

        function toggleFilter(obj) {
            str = obj.getAttribute('id');
            if (criteria[str]) {
                unsetFilter(str);
                obj.className='inactive';
            } else {
                setFilter(str);
                obj.className='active';
            }
            // Filtr podle zoom levelu plati jen kdyz neni aktivni
            // zadny filtr dle vlastnosti.
            if (criteriaCnt == 0) {
                zoomFilter.value = map.getZoom();
            } else {
                zoomFilter.value = 999;
            };
            for (var i in vectors)
                vectors[i].redraw();
        };

        function setFilter(str) {
            var filter = new OpenLayers.Filter.Comparison({
                type: OpenLayers.Filter.Comparison.LIKE,
                property: "tag",
                value: str
            });
            criteria[str] = filter;
            mainFilter.filters.push(filter);
            criteriaCnt += 1;
            _gaq.push(['_trackEvent', 'Filtry', str, '', criteriaCnt]);
        };

        function unsetFilter(str) {
            var filter = criteria[str];
            filter.destroy();
            delete criteria[str];
            criteriaCnt -= 1;
            mainFilter.filters.splice(1, mainFilter.filters.length);
            for (var i in criteria)
                mainFilter.filters.push(criteria[i])
        };

        function toggleFiltry_add(obj) 
        {
           var e = document.getElementById('filtry_add');
	          if(e.style.display == 'block') {
		     e.style.display = 'none';
		     obj.innerHTML = 'Další filtry...'; 
		  }
	          else {
	               e.style.display = 'block';
	               obj.innerHTML = 'Méně filtrů...';
		  }
	}

   
        function doSearch(obj) {
                /* tady bychom meli vypnout submit, aby neslo pustit hledani znova */
                var searchField = document.getElementById('search_input');
                if (! searchField.value || (searchField.value.length < 3)) {
                    alert("Zadejte prosím alespoň 3 znaky");
                    return false;
                }
                if (searchLayer) {
                    destroySearchLayer();
                } 
                searchLayerIdx = addMapLayer("Hledání", mapconfig.root_url + '/search/' + encodeURIComponent(searchField.value) + '/', vectors);
                searchLayer = vectors[searchLayerIdx];
                searchLayer.styleMap.styles["default"].addRules([nofilter_rule]);;
                for (var i in vectors) {
                        if (i != searchLayerIdx)
                                vectors[i].setVisibility(false);
                }
                selectControl.setLayer(vectors);
                searchLayer.redraw();
                searchLayer.events.on({
                    "loadend": function() {
                        var features = searchLayer.features;
                        var sr_div = $('#sr_inner');
                        sr_div.html('');
                        for (var i in features) {
                            var content = $('<a class="result_item" onmouseover="hoverResult(' 
					    + features[i].fid + ')" href="#detail=' + features[i].fid + '"></a>');
                            content.html('<img class="sr_img" src="' 
					  + features[i].attributes.ikona + '" />' + features[i].attributes.name);
			    content.appendTo(sr_div);
                            sr_div.append('<br />');
                        }
		        var sr_height = $('.filtry').height() - 25;
		        $('#sr_inner').height(sr_height);
		       
                        var offset = $('.filtry').offset();
                        $('#search_results').overlay({
                            effect: 'namiste',
                            top: offset.top,
                            left: offset.left,
                            fixed: false,
                            closeOnClick: false,
			    oneInstance: false, 
                            onClose: searchClosed
                        });
		       $('#search_results').overlay().load();
		       $('#search_results').css('left', offset.left);
                        map.zoomToExtent(searchLayer.getDataExtent()); 
                    }
                }); 
        };

        function hoverResult(id) {
            var feature = searchLayer.getFeatureByFid(id);
            selectControl.unselectAll();
            selectControl.select(feature);
        }

        function destroySearchLayer() {
            selectControl.deactivate();
            vectors.splice(searchLayerIdx, 1);
            searchLayer.destroy();
            selectControl.setLayer(vectors);
            selectControl.activate();
            searchLayer = null;
        }

        function searchClosed(e) {
	   /*var sr = document.getElementById('search_results'); 
	   sr.style.display = 'none';*/
	   destroySearchLayer();
	   for (var i in vectors)
                vectors[i].setVisibility(true);
         }

        // Popup (version 1) - OBSOLETE!!!!
	function OverlayLeft_old(obj, pageURL)
        {
	   var title = pageURL;
	   var w = 550;
	   var h = 700;
	   var left = (screen.width/2)-(w/2);
	   var top = (screen.height/2)-(h/2);
	   var targetWin = window.open (pageURL, title, 
	       'toolbar=no, location=no, directories=no, status=no, menubar=no, scrollbar-y=yes, resizable=no, copyhistory=no, width='+w+', height='+h+', top='+top+', left='+left);
	};

        // Popup verison 2 - new style
        function OverlayLeft(obj, pageURL)
        {
	   var overlay_left = $('#overlay_left');
           var iframe = $('#left_iframe');
           iframe.html('<iframe id="overlay_src" class="overlay_iframe"  scrolling="auto" frameborder="0" src="'+ pageURL +'">');
           overlay_left.overlay().load();
	   window.scrollTo(0,0);
	   var offset = $('#core').offset();
	   //overlay_left.css('left', offset.left);
	   // Nezdarily pokus o zmenu vysku scrollu
	   // var f = document.getElementById("overlay_src");
	   // alert(f);
	   // f.style.height = f.contentWindow.document.body.scrollHeight + "px";
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
        

