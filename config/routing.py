from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
#import progress.routing
import miiworker.routing
import miisite.routing

application = ProtocolTypeRouter({
   'websocket': AuthMiddlewareStack(
       URLRouter(
           miisite.routing.public_routing
       )
   ),

    'channel': ChannelNameRouter(
        miiworker.routing.internal_routing
    ),
})

