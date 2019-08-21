function mapInit() {
    var mymap = L.map('map-target').setView([55.763826, 37.662312], 13);

    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        maxZoom: 18,
        id: 'mapbox.streets',
        accessToken: 'pk.eyJ1Ijoic2hpenpnYXIiLCJhIjoiY2pxa3p0bHg1MW9oejN4bWJobWZpZDNpOSJ9.q3iuyK04zDch7wRAHp48dg'
    }).addTo(mymap);

    start_data_rendering(mymap);                

    mymap.on('dragend', function() {
        var width = mymap.latLngToLayerPoint(mymap.getBounds().getNorthEast()).x- mymap.latLngToLayerPoint(mymap.getBounds().getSouthWest()).x; 
        var height = mymap.latLngToLayerPoint(mymap.getBounds().getNorthEast()).y- mymap.latLngToLayerPoint(mymap.getBounds().getSouthWest()).y;              

        console.log('center:' + mymap.getCenter() +'\n'+
        'width:' + width +'\n'+
        'height:' + height +'\n'+
        'size in pixels:' + mymap.getSize())
    });

    return mymap

}

function mapInit2() {
    var MapBox_layer = L.tileLayer(
        'https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
            maxZoom: 18,
            id: 'mapbox.streets',
            accessToken: 'pk.eyJ1Ijoic2hpenpnYXIiLCJhIjoiY2pxa3p0bHg1MW9oejN4bWJobWZpZDNpOSJ9.q3iuyK04zDch7wRAHp48dg'
        });

        var Esri_WorldImagery = L.tileLayer(
            "http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            {
              maxZoom:18,  
              id: 'arcgis.world',
              attribution:
                "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, " +
                "AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
            }
          );
        
    
    var baseLayers = {
        "MapBox": MapBox_layer,
        // "Satellite": Esri_WorldImagery,
      };

    var mymap = L.map('map-target',{layers:[MapBox_layer]})
    var layerControl = L.control.layers(baseLayers);
    layerControl.addTo(mymap);
    
    mymap.setView([55.763826, 37.662312], 13);

    start_data_tofile(mymap,layerControl);                

    mymap.on('mouseover', function (e){
        console.log(e.latlng)

    })
    return {map:mymap, layerControl:layerControl};

}