var gliphy_shape=null;


function start_data_rendering(map_instance){

    var chanSocket = new WebSocket('ws://' + window.location.host +'/ws/model/');

    chanSocket.onopen=function(e){
        chanSocket.send(JSON.stringify({'type':'start'}));
        console.log("onopen");
        
    }
    
    chanSocket.onmessage = function(e) {
        var data = JSON.parse(e.data);
        var msg_text='';
    
        console.log("onmsg");
        
        switch (data.type){
            case 'points':{
                points=data.points;
                colors=data.colors;
                if (gliphy_shape!=null){
                    gliphy_shape.remove();
                }
                gliphy_shape=L.glify.points({
                    map:map_instance,
                    data:points,
                    size : 3,
                    opacity : 0.4,
                    color: function(index, point){
                        return colors[index];
                    }    
                })
            }
            default:{
                console.log(data.type);
                break;
            }
        }
    
    };
    
    chanSocket.onclose = function(e) {
        // $('#container').text('Chat socket closed unexpectedly');
    };

    return chanSocket;
}

function stop_data_rendering(socket){
    chanSocket.send(JSON.stringify({'type':'stop'}));
}


function start_data_tofile(mapInstance,layerControl){
    var map = mapInstance;
    var layerControl = layerControl;
    var velocityLayer=null;
    
    var chanSocket = new WebSocket('ws://' + window.location.host +'/ws/model/');

    chanSocket.onopen=function(e){
        chanSocket.send(JSON.stringify({'type':'tofile','zoom_level':13}));
        console.log("onopen");
        
    }
    
    chanSocket.onmessage = function(e) {
        var msg_text='';
        var data = JSON.parse(e.data);
        switch (data.type){
            case 'points':{
                if (velocityLayer==null){

                    velocityLayer=L.velocityLayer({
                        displayValues:true,
                        displayOptions:{
                            angleConvention:'bearing',
                            emptyString:'No wind here',
                            velocityType:'Wind',
                            displayPosition:'bottomleft',
                            displayEmptyString:'no wind here',
                        },
            
                        data:data.points,
                        maxVelocity:5.0,
                        minVelocity:0.0,
                        velocityScale:0.005,
                    })
                    
                    layerControl.addOverlay(velocityLayer,"Wind")
    

                }else{
                    console.log("ws:",data.points[0].data[100])
                    velocityLayer.setData(data.points)
                }
            }
        }
    


    
    };
    
    chanSocket.onclose = function(e) {
        $('#container').text('Chat socket closed unexpectedly');
        if (velocity_layer!=null){
            layerControl.removeLayer(velocityLayer)
        }
    };

    return chanSocket;
}
