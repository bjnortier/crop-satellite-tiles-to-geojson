#!/usr/bin/env python
from PIL import Image
import json

from util import BBox, V2
from crop import calculate_composite_bbox_and_dimensions
from crop import create_composite_image
from crop import geo_json_bbox, calculate_crop
from crop import create_boundary_pixels
from crop import crop_to_boundary
from crop import mask_pixels_outside_boundary

tiles = [
    {
        'bbox': BBox(V2(30, -25), V2(40, -15)),
        'img': Image.open('./input/X21Y09.png').convert('RGBA')
    },
    {
        'bbox': BBox(V2(30, -35), V2(40, -25)),
        'img': Image.open('./input/X21Y10.png').convert('RGBA')
    }
]

# 1. Calculate the composite bounding box and dimensions:
(composite_bbox, composite_dims) = calculate_composite_bbox_and_dimensions(
    tiles)
print('composite image bounding box:', composite_bbox)
print('composite image dimensions:', composite_dims)

# 2. Create a simple composite image:
composite_img = create_composite_image(tiles, composite_bbox, composite_dims)
composite_img.save('./output/composite.png')

# 3. Crop it to the GeoJSON boundary boundingbox
with open('./input/knp_boundary.geojson', 'r') as f:
    knp = json.load(f)
coordinates = knp['features'][0]['geometry']['coordinates'][0]
(cropped_to_boundary_image, cropped_bbox) = crop_to_boundary(
    coordinates,
    composite_img,
    composite_bbox)
cropped_to_boundary_image.save('./output/cropped_to_boundary.png')
print('cropped to boundary size: {0}'.format(cropped_to_boundary_image.size))
print('cropped to boundary bbox: \n\t{0}\n\t{1}'.format(
    cropped_bbox.min,
    cropped_bbox.max))

# 4. Remove pixels outside boundary
masked_image = mask_pixels_outside_boundary(
    cropped_to_boundary_image,
    coordinates,
    cropped_bbox)
masked_image.save('./output/masked_to_boundary.png')
