BASECOORDS = [50.431782, 30.516382];

function makeMap() {
    var TILE_URL = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
    var MB_ATTR = 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
    mymap = L.map('llmap').setView(BASECOORDS, 8);
    L.tileLayer(TILE_URL, {attribution: MB_ATTR}).addTo(mymap);
}

var layer = L.layerGroup();

function renderData(districtid) {
    $.getJSON("/district/" + districtid, function(obj) {
        var markers = obj.data.map(
            function(arr) {
                console.log(arr)
                return L.marker([arr[0], arr[1]]).bindPopup(arr[2]).openPopup();

            }
        );
        mymap.removeLayer(layer);
        layer = L.layerGroup(markers);
        mymap.addLayer(layer);
    });
}


$(function() {
    makeMap();
    renderData('0');
    $('#distsel').change(function() {
        var val = $('#distsel option:selected').val();
        renderData(val);
    });
})
