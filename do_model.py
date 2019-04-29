
import sys
import os
import pathlib
import argparse

import pickle

import torch

import numpy as np

import tqdm

import gzip

import matplotlib as mpl

import skimage.io

import subprocess


def wind_kernel( direction, bone ):

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


def main( argv ):

	me_path = pathlib.Path( __file__ ).parent.resolve()

	ap = argparse.ArgumentParser()

	ap.add_argument( '--cuda', action='store_true', default=False )

	ap.add_argument( '--emission-map', type=pathlib.Path, default=( me_path / 'emission.pkl' ) )

	ap.add_argument( '--steps', type=int, default=1000 )

	ap.add_argument( '--mix-angle', type=float, default=130 )

	ap.add_argument( '--mix-ratio', type=float, default=0.6 )

	ap.add_argument( '--output-video', type=pathlib.Path, default=None )

	ap.add_argument( '--output-epochs', type=pathlib.Path, default=None )

	ap.add_argument( '--output-result', type=pathlib.Path, default=None )

	args = ap.parse_args( argv )

	print( 'initializing...' )

	if args.output_video:
		os.makedirs( args.output_video.parent, exist_ok=True )

	if args.output_result:
		os.makedirs( args.output_result.parent, exist_ok=True )

	if args.output_epochs:
		os.makedirs( args.output_epochs, exist_ok=True )

	output_frames = args.output_epochs or args.output_video

	if args.cuda:
		print( 'using CUDA' )
		device = torch.device( 'cuda' )
	else:
		print( 'using CPU' )
		device = torch.device( 'cpu' )

	print( 'loading emission map...' )

	emission = pickle.loads( args.emission_map.read_bytes() )
	emission = torch.tensor( emission, dtype=torch.float32 ).to( device )

	print( 'building field...' )

	field = torch.zeros( 1, 1, emission.size( 0 ), emission.size( 1 ), dtype=torch.float32 ).to( device )

	print( 'building kernel...' )

	kernel = wind_kernel( np.deg2rad( args.mix_angle ), args.mix_ratio )
	kernel = torch.tensor( kernel.reshape( 1, 1, 3, 3 ), dtype=torch.float32 ).to( device )

	cm = mpl.cm.get_cmap( 'jet' )

	if args.output_video:

		video_proc = subprocess.Popen( [
			'ffmpeg',
		#	'-v', 'debug',
			'-loglevel', 'panic',
			'-f', 'rawvideo',
			'-framerate', '24',
			'-pixel_format', 'rgb24',
			'-video_size', f'{field.size(2)}x{field.size(3)}',
			'-i', '-',
			'-vcodec', 'h264',
			'-y',
			str( args.output_video ),
			], stdin=subprocess.PIPE )

	field_max = 0.0

	print( 'processing...' )

	for epoch_n in tqdm.tqdm( range( args.steps ) ):

		field += emission
		torch.clamp( field, min=0, out=field )

		field = torch.nn.functional.conv2d( field, kernel, padding=1 )

		if output_frames:

			cur_frame = field.cpu().numpy()
			cur_frame.resize( cur_frame.shape[2:] )

			if args.output_epochs:

				dst_fn = args.output_epochs / f'epoch-{epoch_n:06d}.pkl.gz'
				with gzip.open( dst_fn, 'wb', compresslevel=6 ) as dst_f:
					pickle.dump( cur_frame, dst_f, -1 )

			if args.output_video:

				cur_field_max = cur_frame.max()

				if field_max < cur_field_max:
					field_max = cur_field_max

				cur_field = cur_frame / field_max

				cur_field_cm = ( cm( cur_field ) * 255.0 )[:,:,:3].astype( np.uint8 )

				video_proc.stdin.write( cur_field_cm.tobytes() )

	if args.output_video:

		video_proc.stdin.close()

		video_proc.communicate()

	if args.output_result:

		print( 'saving result...' )

		if not output_frames:

			cur_frame = field.cpu().numpy()
			cur_frame.resize( cur_frame.shape[2:] )

		cur_field = cur_frame.copy()

		args.output_result.write_bytes( pickle.dumps( cur_field, -1 ) )

		cur_field /= cur_field.max()

		cur_field_cm = ( cm( cur_field ) * 255.0 )[:,:,:3].astype( np.uint8 )

		skimage.io.imsave( str( args.output_result.with_suffix( '.tiff' ) ), cur_field_cm, compress=6 )

	print( 'done...' )

	return 0


if __name__ == '__main__':
	sys.exit( main( sys.argv[1:] ) )
