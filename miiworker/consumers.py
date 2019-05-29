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
import pyproj

from PIL import Image 
from io import BytesIO

from . import periodic
from . import model_context
from .projection import Projection


class BackgroundTaskConsumer(AsyncConsumer):

    def __init__(self, arg):
        self.counter=0
        self.periods=0

        self.context=model_context.ModelContext('./data/emission.pkl',60,1,1)
        
        self.cm = mplcm.get_cmap( 'jet' )
        
        self.periodic=periodic.Periodic(self, self.call_payload,1)
        self.projection=Projection(geod=pyproj.Geod(ellps='WGS84'),start_lat=55.9146,start_lon=37.3151,scale=50)

    async def call_payload(self):
        await self.payload(self.context,self.cm)

    def make_points(self,cur_field):
        result={'points': [],
                'colors': []}

        point_list=result['points']
        colors_list=result['colors']

        for i in range(cur_field.shape[0]):
            for j in range(cur_field.shape[1]):
                c0=cur_field[i,j,0].item()
                c1=cur_field[i,j,1].item()
                c2=cur_field[i,j,2].item()
                if (c0>0.0001) and (c1>0.0001) and (c2>0.0001):
                    # pixel=f'#{c2:02x}{c1:02x}{c0:02x}'
                    colors_list.append({'g':c2,'b':c1,'r':c0})

                    point_list.append(list(self.projection.to_latlon(j,i)))
                if (c0<0 or c1<0 or c2<0):
                    print('************************************************************************')    

        return result

        # for ch in self.channel_layer.groups.get("mii-group",set()):
        #     print(ch)
        #     queue=self.channel_layer.channels.setdefault(ch,asyncio.Queue())
        #     print(f'Queue size is {queue.qsize()}')

    async def payload(self, context, cm):
        index=self.context.get_current_index()
        print(f'step: {index}')

        cur_field=self.context.run()

        cur_field_cm = ( cm( cur_field/cur_field.max() ))[:,:,:3].astype( np.float )

        result=self.make_points(cur_field_cm)

        message= {
                  'type':'process_points_data',
                  'index':index,
                  'points':result['points'],
                  'colors': result['colors'],
              }

        print('points size ', len (result['points']))
        # print(self.channel_layer.groups)  
        await self.channel_layer.group_send("mii-group",message)

        print(f'step: {index} after send')


    async def start(self, message):
        self.counter+=1
        await self.periodic.start()




