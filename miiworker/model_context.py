import torch
import numpy as np
import pickle
import pathlib
import tqdm
import itertools

class ModelContext:
    # def __init__(self, emission_path, angle, ratio,steps,zoom_level):
    def __init__(self, **kwargs):
        print( 'initializing...' )
        
        self.context=dict()
        self.context.update(kwargs)
        self.queue=[]
        # self.steps=steps
        self.iter=itertools.count(1);

        self.emission = pickle.loads( pathlib.Path(self.context['emission_path']).read_bytes() )
        
        # self.angle=angle
        # self.ratio=ratio
        # self.zoom_level=zoom_level

        device = torch.device( 'cuda' )

        print( 'loading emission map...' )

        self.emission = torch.tensor( self.emission, dtype=torch.float32 ).to( device )

        print( 'building field...' )

        self.field = torch.zeros( 1, 1, self.emission.size( 0 ), self.emission.size( 1 ), dtype=torch.float32 ).to( device )

        print( 'building kernel...' )

        self.kernel = self.wind_kernel( np.deg2rad( self.context['angle'] ), self.context['ratio'] )
        self.kernel = torch.tensor( self.kernel.reshape( 1, 1, 3, 3 ), dtype=torch.float32 ).to( device )

    def __getitem__(self, param):
        return self.context[param] 

    def __setitem__(self, param, value):
        self.context[param]=value 

    def wind_kernel(self, direction, bone ):
        t = np.abs( np.tan( direction ) )
        x = 1.0 / ( 1.0 + t )
        y = t / ( 1.0 + t )

        ret = np.zeros( ( 3, 3 ) )

        if 0 < direction <= np.pi*0.5:
            ret[1,0] = x * bone
            ret[2,1] = y * bone

        elif np.pi*0.5 < direction <= np.pi:
            ret[1,2] = x * bone
            ret[2,1] = y * bone

        elif np.pi < direction <= np.pi*1.5:
            ret[1,2] = x * bone
            ret[0,1] = y * bone

        elif np.pi*1.5 < direction <= np.pi*2:
            ret[1,0] = x * bone
            ret[0,1] = y * bone

        ret[1,1] = ( 1.0 - bone )

        return ret

    def get_current_index(self):
        return self.iter.__next__()

    def run(self):
        # for epoch_n in tqdm.tqdm( range( self.steps ) ):
        for epoch_n in range( self.context['steps'] +1) :
            self.field += self.emission
            torch.clamp( self.field, min=0, out=self.field )
            self.field = torch.nn.functional.conv2d( self.field, self.kernel, padding=1 )

        cur_frame = self.field.cpu().numpy()
        cur_frame.resize( cur_frame.shape[2:] )
        cur_field = cur_frame.copy()
        
        self.queue.append(cur_field)

        return cur_field


