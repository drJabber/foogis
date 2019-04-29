import torch
import numpy as np
import pickle
import pathlib
import tqdm
import itertools

class ModelContext:
    def __init__(self, emission_path, angle, ratio,steps):
        print( 'initializing...' )
        
        self.queue=[]
        self.steps=steps
        self.iter=itertools.count(1)

        self.emission = pickle.loads( pathlib.Path(emission_path).read_bytes() )

        device = torch.device( 'cuda' )

        print( 'loading emission map...' )

        self.emission = torch.tensor( self.emission, dtype=torch.float32 ).to( device )

        print( 'building field...' )

        self.field = torch.zeros( 1, 1, self.emission.size( 0 ), self.emission.size( 1 ), dtype=torch.float32 ).to( device )

        print( 'building kernel...' )

        self.kernel = self.wind_kernel( np.deg2rad( angle ), ratio )
        self.kernel = torch.tensor( self.kernel.reshape( 1, 1, 3, 3 ), dtype=torch.float32 ).to( device )
        
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
        for epoch_n in range( self.steps +1) :
            self.field += self.emission
            torch.clamp( self.field, min=0, out=self.field )
            self.field = torch.nn.functional.conv2d( self.field, self.kernel, padding=1 )

        cur_frame = self.field.cpu().numpy()
        cur_frame.resize( cur_frame.shape[2:] )
        cur_field = cur_frame.copy()
        
        self.queue.append(cur_field)

        return cur_field


