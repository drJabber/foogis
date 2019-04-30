function start_data_rendering(map_instance){

    var chanSocket = new WebSocket('ws://' + window.location.host +'/ws/model/');

    chanSocket.onopen=function(e){
        chanSocket.send(JSON.stringify({'type':'start'}));
    }
    
    chanSocket.onmessage = function(e) {
        var data = JSON.parse(e.data);
        var msg_text='';
    
        switch (data.type){
            case 'png-data':{
                $(function () {
                    var $img = $('#image-target');
                    var index=data.index;
                    msg_text='png #'+index.toString();
                    shape=data.shape;
                    $img.attr("height",shape[0]/2);
                    $img.attr("width",shape[1]/2);
                    $img.attr("opacity",0.1);
                    $img.attr("src", "data:image/png;base64," + data.data);
                    $('#message-span').text(msg_text);
                    console.log('message='+msg_text);
    
                });
                break;
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

