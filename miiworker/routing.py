from . import consumers

    
internal_routing={
    'mii-worker': consumers.BackgroundTaskConsumer,
}

