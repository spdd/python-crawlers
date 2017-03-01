from if3py.ml.image.torch.stylize import stylize_image_with_torch

import os, glob

work_dir = os.getcwd()
os.chdir('cache/images')
images_names = [m for m in glob.glob("*.jpg")]

os.chdir(work_dir)

for im in images_names:
	name = im.split('_')[0]
	out_name = name + '.jpg'
	stylize_image_with_torch('cache/images/{}'.format(im),
							'cache/images/stylized/{}'.format(out_name),
							img_size = 1002, 
							model = 'mosaic.t7')