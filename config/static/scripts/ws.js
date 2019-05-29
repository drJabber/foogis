var gliphy_shape=null;


function start_data_rendering(map_instance){

    var chanSocket = new WebSocket('ws://' + window.location.host +'/ws/model/');

    chanSocket.onopen=function(e){
        chanSocket.send(JSON.stringify({'type':'start'}));
    }
    
    chanSocket.onmessage = function(e) {
        var data = JSON.parse(e.data);
        var msg_text='';
    
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
                    size : 2,
                    opacity : 0.4,
                    color: function(index, point){
                        // col2=L.glify.color.random();
                        col=colors[index];
                        return col;
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

