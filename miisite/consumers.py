# from channels import Cahnnel
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import AsyncConsumer
import json
from time import sleep
from asgiref.sync import sync_to_async
import asyncio
from PIL import Image 
from io import BytesIO
from base64 import b64encode
import numpy as np

class WSConsumer(AsyncWebsocketConsumer):

    # def __init__():
    #     self.started=False
    #     # self.queue=

    async def connect(self):
        print('try connect WS')
        await self.accept()


    async def disconnect(self, code ):
        print('try disconnect')


    async def receive(self, text_data=None, bytes_data=None):
        data=json.loads(text_data)
        if (data['type']=='start'):
            # if self.started:
            #     self.started=True
            await self.channel_layer.group_add("mii-png-group", self.channel_name)
            await self.channel_layer.send('mii-worker',{'type':'start'})

    async def process_png_data(self, message):
        print('received ',message['index'])
        index=message['index']
        buffer=message['field_data']
        dtype=message['field_dtype']
        shape=message['field_shape']
        cur_field=np.frombuffer(buffer,dtype).reshape(shape)

        
        buff=BytesIO()
        im=Image.fromarray(np.asarray(cur_field)).convert('RGBA')
        alfa=Image.new('L',im.size,64)
        im.putalpha(alfa)
        im.save(buff,'png')

        # skimage.io.imsave( str( pathlib.Path(f'./data/data{index:02d}').with_suffix( '.png' ) ), cur_field_cm)
        await self.send(text_data=json.dumps({
            'type':'png-data',
            'index':index,
            'shape':shape,
            'data':b64encode(buff.getvalue()).decode('utf-8'),
        }))