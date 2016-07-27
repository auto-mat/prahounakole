var mapconfig = {};

describe('testMap', function() {

    mapconfig['root_url'] = "";
    mapconfig['vrstvy'] = [];
    enabled = "True";
    mapconfig['vrstvy'].push(["Trasy a informace", "/kml/z/", enabled, "z"]);
    enabled = "False";
    mapconfig['vrstvy'].push(["Cyklisté sobě", "/kml/a/", enabled, "a"]);
    enabled = "False";
    mapconfig['vrstvy'].push(["ReKola", "/kml/r/", enabled, "r"]);
    enabled = "False";
    mapconfig['vrstvy'].push(["Nahrané denní Do práce na kole 2015", "/kml/g/", enabled, "g"]);
    enabled = "False";
    mapconfig['vrstvy'].push(["Zadané trasy Do práce na kole 2015", "/kml/t/", enabled, "t"]);
     
    mapconfig['basezoom'] = 13;
    mapconfig['address_search_area'] = "13.29156813982122,49.461915914600475,15.554751733252246,50.62946741845168";
    mapconfig['maxzoom'] = 18;
    mapconfig['baselon'] = 14.421099999999988;
    mapconfig['baselat'] = 50.08740999999999;
    
    mapconfig['zoom'] = mapconfig['basezoom'];
    mapconfig['lon'] = mapconfig['baselon'];
    mapconfig['lat'] = mapconfig['baselat'];
        
    location.hash = "#";
    document.body.insertAdjacentHTML(
      'afterbegin',
      '<div id="mapa" data-src="/panel-mapa/"/><div id="hledani" data-src="/panel-hledani/"><div>hledani</div></div>'
    );
    init(mapconfig);

    it('Test map', function() {
        expect(map.layers.length).toBe(12);
        expect(map.zoom).toBe(13);
        expect(map.layers[0].slug).toBe("P");
        expect(map.layers[5].slug).toBe("z");
    });

    location.hash = "#hledani";
    location.hash = "#hledani@trasa=53398329@plan=balanced";
});
