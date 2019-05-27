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
                L.glify.points({
                    map:map_instance,
                    data:points,
                    size : 3,
                    color: function(index, point){
                        // col2=L.glify.color.random();
                        col=colors[index];
                        return col;
                    }    
                })
            }
            default:{
                msg_text=data.message.toString();
                $('#message-span').text(msg_text);
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

