import os
import asyncio
from  periodic import Periodic
from model_context import ModelContext
import matplotlib as mpl
import skimage.io
import numpy as np
import pathlib


def sequence():
	iteration=0
	yield iteration
	iteration+=1

def payload(context,cmap):
	index=context.get_current_index()
	print(f'step: {index}')

	cur_field=context.run()

	cur_field_cm = ( cmap( cur_field/cur_field.max() ) * 255.0 )[:,:,:3].astype( np.uint8 )
	
	skimage.io.imsave( str( pathlib.Path(f'./data/data{index:02d}').with_suffix( '.png' ) ), cur_field_cm)

async def main():

	cm = mpl.cm.get_cmap( 'jet' )
	context = ModelContext('./data/emission.pkl',30,0.9,200)
	p = Periodic(lambda: payload(context,cm), 1)
	try:
		print('Start')
		await p.start()
		await asyncio.sleep(100.1)
		
	finally:
		await p.stop()  # we should stop task finally

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())