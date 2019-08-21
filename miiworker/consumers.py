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
from copy import deepcopy

from PIL import Image 
from io import BytesIO

from . import periodic
from . import model_context
from .projection import Projection


class BackgroundTaskConsumer(AsyncConsumer):
    
    def __init__(self, arg):
        self.counter=0
        self.periods=0

        self.context=model_context.ModelContext(emission_path='./data/emission.pkl',angle=60,ratio=1,steps=1,zoom_level=-1,start_lat=55.9146, start_lon=37.3151)
        
        self.cm = mplcm.get_cmap( 'jet' )
        
        self.periodic=periodic.Periodic(self, self.call_payload,1)
        self.periodic2=periodic.Periodic(self, self.call_payload2,5)
        self.projection=Projection(geod=pyproj.Geod(ellps='WGS84'),start_lat=self.context['start_lat'],start_lon=self.context['start_lon'],scale=50)

    async def call_payload(self):
        await self.payload(self.context,self.cm)

    async def call_payload2(self):
        await self.payload2(self.context,self.cm)

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
                if (c0>0.000001) and (c1>0.000001) and (c2>0.000001):
                    # pixel=f'#{c2:02x}{c1:02x}{c0:02x}'
                    colors_list.append({'r':1-c2,'b':1-c1,'g':1-c0})

                    point_list.append(list(self.projection.to_latlon(j,i)))
                if (c0<0 or c1<0 or c2<0):
                    print('************************************************************************')    

        return result

    def get_step_for_zoom(self):
        # STEPS={0:1,1:3,4:5,5:10,8:20,11:50,13:80,15:100}
        STEPS={0:1,1:3,4:5,5:8,8:13,11:16,13:20,15:25}
        print('.')
        return list(filter(lambda it: it[0]>=self.context['zoom_level'],STEPS.items()))[0][1]

    def make_points2(self,cur_field):

        step=self.get_step_for_zoom()
        print(f'zoom:{self.context["zoom_level"]}, step:{step}')
        nx=cur_field.shape[0]
        ny=cur_field.shape[1]
        item={'header':{'parameterUnit':'m.s-1','parameterNumber':0,'nx':0,'ny':0,'dx':0,'dy':0,'la1':0,'la2':0,'lo1':0,'lo2':0}, 'data':[]}       
        result=[deepcopy(item),deepcopy(item)]

        r=result[0]['header']
        r['parameterCategory']=2
        r['parameterNumber']=2
        r['parameterNumberName']='1'
        r['refTime']= "2019-09-01 23:00:00"

        r['nx']=nx//step
        r['ny']=ny//step
        r['dx']=0.1
        r['dy']=0.1
        r['la1']=self.context['start_lat']
        r['lo1']=self.context['start_lon']
        r['la2']=list(self.projection.to_latlon(nx-1,ny-1))[0]
        r['lo2']=list(self.projection.to_latlon(nx-1,ny-1))[1]

        r=result[1]['header']               
        r['parameterCategory']=2
        r['parameterNumber']=3
        r['parameterNumberName']='2'
        r['refTime']= "2019-09-01 23:00:00"

        r['nx']=nx//step
        r['ny']=ny//step
        r['dx']=0.1
        r['dy']=0.1
        r['la1']=self.context['start_lat']
        r['lo1']=self.context['start_lon']
        r['la2']=list(self.projection.to_latlon(nx-1,ny-1))[0]
        r['lo2']=list(self.projection.to_latlon(nx-1,ny-1))[1]

        cos_a=np.cos(np.deg2rad( self.context['angle'] ))
        sin_a=np.sin(np.deg2rad( self.context['angle'] ))
        result[0]['data']=(cur_field[0:nx:step,0:ny:step]*sin_a).flatten().tolist()
        result[1]['data']=(cur_field[0:nx:step,0:ny:step]*cos_a).flatten().tolist()

        return result

    async def payload(self, context, cm):
        index=self.context.get_current_index()
        print(f'step: {index}')

        cur_field=self.context.run()
        # print(f'ndim:{cur_field.ndim}\nsize:{cur_field.size}\nflags:{cur_field.flags}\ndtype:{cur_field.dtype}\nitemsize:{cur_field.itemsize}\nshape:{cur_field.shape}\n')

        cur_field_cm = ( cm( cur_field/cur_field.max() ))[:,:,:3].astype( np.float )

        result=self.make_points(cur_field_cm)

        message= {
                  'type':'process_points_data',
                  'index':index,
                  'points':result,
                  'colors': result['colors'],
              }

        print('points size ', len (result['points']))
        # print(self.channel_layer.groups)  
        await self.channel_layer.group_send("mii-group",message)

        print(f'step: {index} after send')


    async def payload2(self, context, cm):
        index=self.context.get_current_index()
        cur_field=self.context.run()
        result=self.make_points2(cur_field)

        message= {
                  'type':'process_scalar_points_data',
                  'index':index,
                #   'direction':self.context['angle'],
                  'points':result,
              }

        print('points size ', len (result[0]['data']))   
        await self.channel_layer.group_send("mii-group",message)
        print(f'step: {index} after send')


    async def start(self, message):
        self.counter+=1
        await self.periodic.start()


    async def tofile(self, message):
        self.counter+=1
        self.context['zoom_level']=message['zoom_level']

        await self.periodic2.start()



