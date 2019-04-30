var globOverlay = null; 
var stopPic = 0;

function getPic(map){
    var imgUrl;
    $.ajax({
        url: '/dynomap/getimg/',
        // type: 'get', // This is the default though, you don't actually need to always mention it
        cache: false,
        xhrFields:{
            responseType:'blob'
        },
        success: function(data) {
            var img = document.getElementById('my404img');
            var url = window.URL || window.webkitURL;
            
            imgUrl = url.createObjectURL(data);
            img.src = imgUrl;
            
            oldOverlay=globOverlay;
            globOverlay = L.imageOverlay(imgUrl, map.getBounds()).addTo(map);  
            $(globOverlay._image).fadeIn(100, function(){
            });
            if (oldOverlay!=null) {
                $(oldOverlay._image).fadeOut(100, function(){
                    map.removeLayer(oldOverlay);
                });
            }

            if (stopPic == true){
                return
            };
        
            setTimeout(function(){
                getPic(map);
            }, 1000);
        
        },
        failure: function(data) { 
            console.log('Got an error dude')
        }       
    });
    return imgUrl
}
