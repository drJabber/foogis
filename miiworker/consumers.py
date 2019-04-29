import asyncio
from time import sleep
from channels.consumer import AsyncConsumer
import json
from random import randint,seed
from asgiref.sync import sync_to_async
import matplotlib.cm as mplcm 
import skimage.io
import numpy as np
import pathlib

from PIL import Image 
from io import BytesIO

from . import periodic
from . import model_context


class BackgroundTaskConsumer(AsyncConsumer):

    def __init__(self, arg):
        self.counter=0
        self.periods=0

        self.context=model_context.ModelContext('./data/emission.pkl',30,1,1)
        
        self.cm = mplcm.get_cmap( 'jet' )
        
        self.periodic=periodic.Periodic(self, self.call_payload,2)

    async def call_payload(self):
        await self.payload(self.context,self.cm)

    async def payload(self, context, cm):
        index=self.context.get_current_index()
        print(f'step: {index}')

        cur_field=self.context.run()

        cur_field_cm = ( cm( cur_field/cur_field.max() ) * 255.0 )[:,:,:3].astype( np.uint8 )

        message= {
                  'type':'process_png_data',
                  'index':index,
                  'message':'message',
                  'field_dtype':cur_field_cm.dtype.name,
                  'field_shape':cur_field_cm.shape,
                  'field_data':cur_field_cm.tobytes(),
              }

        await self.channel_layer.group_send("mii-png-group",message)

        print(f'step: {index} after send')


    async def start(self, message):
        self.counter+=1
        await self.periodic.start()




