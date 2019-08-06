# from channels import Cahnnel
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import AsyncConsumer
import json
from time import sleep
from asgiref.sync import sync_to_async
import asyncio

import os

# from PIL import Image 
# from io import BytesIO
# from base64 import b64encode
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "data/out")


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
            print(self.channel_name)
            await self.channel_layer.group_add("mii-group", self.channel_name)
            await self.channel_layer.send('mii-worker',{'type':'start'})

    async def process_points_data(self, message):
        print('received ',message['index'])
        index=message['index']

        print('points size ', len (message['colors']))

        json_text=json.dumps({
            'type':'points',
            'index':index,
            'points':message['points'],
            'colors':message['colors'],
        })

        await self.send(text_data=json_text)

        fp=open(os.path.join(OUT_DIR,f'output{index:03d}.json'),'w+')
        fp.write(json_text)
        fp.close()