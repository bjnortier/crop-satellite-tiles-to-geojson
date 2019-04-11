#!/usr/bin/env python
import sys
import numpy as np
from PIL import Image, ImageDraw
from math import inf, floor, ceil
from knp import boundary
import timeit

def calculate_uncropped_bbox_and_dimensions(tiles):
    min_x = inf
    max_x = -inf
    min_y = inf
    max_y = -inf
    for i, tile in enumerate(tiles):
        min_x = min(min_x, tile['bbox'][0][0])
        max_x = max(max_x, tile['bbox'][1][0])
        min_y = min(min_y, tile['bbox'][0][1])
        max_y = max(max_y, tile['bbox'][1][1])
    tile_width_coords = tile['bbox'][1][0] - tile['bbox'][0][0]
    tile_height_coords = tile['bbox'][1][1] - tile['bbox'][0][1]
    tile_width_px = tile['img'].size[0]
    tile_height_px = tile['img'].size[1]

    uncropped_width = round((max_x - min_x) / tile_width_coords) * tile_width_px
    uncropped_height = round((max_y - min_y) / tile_height_coords) * tile_height_px
    return (((min_x, min_y), (max_x, max_y)), (uncropped_width, uncropped_height))

def create_boundary_pixels(boundary, bbox, image_dims):
    (image_width, image_height) = image_dims
    (bbox_min, bbox_max) = bbox
    def coordinate_to_pixels(coordinate):
        return (round((coordinate[0] - bbox_min[0]) / (bbox_max[0] - bbox_min[0]) * image_width),
                round((bbox_max[1] - coordinate[1]) / (bbox_max[1] - bbox_min[1]) * image_height))

    pixels = map(coordinate_to_pixels, boundary)
    return list(pixels)

def calculate_boundary_bbox(boundary):
    min_x = inf
    max_x = -inf
    min_y = inf
    max_y = -inf
    for coordinate in boundary:
        min_x = min(min_x, coordinate[0])
        max_x = max(max_x, coordinate[0])
        min_y = min(min_y, coordinate[1])
        max_y = max(max_y, coordinate[1])
    return ((min_x, min_y), (max_x, max_y))

def create_cropped_image(boundary, tiles, uncropped_bbox, uncropped_dims):
    (uncropped_bbox_min, uncropped_bbox_max) = uncropped_bbox
    (uncropped_pixel_width, uncropped_pixel_height) = uncropped_dims
    output_image = Image.new('RGBA', (uncropped_pixel_width, uncropped_pixel_height), (255, 0, 0, 255))

    for i, tile in enumerate(tiles):
        offset_x = round((tile['bbox'][0][0] - uncropped_bbox_min[0]) / (uncropped_bbox_max[0] - uncropped_bbox_min[0]) * uncropped_pixel_width)
        offset_y = round(-(tile['bbox'][1][1] - uncropped_bbox_max[1]) / (uncropped_bbox_max[1] - uncropped_bbox_min[1]) * uncropped_pixel_height)
        output_image.paste(tile['img'], (offset_x, offset_y))

    (boundary_bbox_min, boundary_bbox_max) = calculate_boundary_bbox(boundary)

    cropped_min_x = floor((boundary_bbox_min[0] - uncropped_bbox_min[0]) / (uncropped_bbox_max[0] - uncropped_bbox_min[0]) * output_image.size[0])
    cropped_max_x = ceil((boundary_bbox_max[0] - uncropped_bbox_min[0]) / (uncropped_bbox_max[0] - uncropped_bbox_min[0]) * output_image.size[0])
    cropped_min_y = floor((uncropped_bbox_max[1] - boundary_bbox_max[1]) / (uncropped_bbox_max[1] - uncropped_bbox_min[1]) * output_image.size[1])
    cropped_max_y = floor((uncropped_bbox_max[1] - boundary_bbox_min[1]) / (uncropped_bbox_max[1] - uncropped_bbox_min[1]) * output_image.size[1])

    cropped_dims = (cropped_max_x - cropped_min_x, cropped_max_y - cropped_min_y)
    cropped_bbox_min = (
        uncropped_bbox_min[0] + cropped_min_x / output_image.size[0] * (uncropped_bbox_max[0] - uncropped_bbox_min[0]),
        uncropped_bbox_max[1] - cropped_max_y / output_image.size[1] * (uncropped_bbox_max[1] - uncropped_bbox_min[1]))
    cropped_bbox_max = (
        uncropped_bbox_min[0] + cropped_max_x / output_image.size[0] * (uncropped_bbox_max[0] - uncropped_bbox_min[0]),
        uncropped_bbox_max[1] - cropped_min_y / output_image.size[1] * (uncropped_bbox_max[1] - uncropped_bbox_min[1]))

    output_image = output_image.crop((cropped_min_x, cropped_min_y, cropped_max_x, cropped_max_y))
    output_raw = np.asarray(output_image)

    polygon = create_boundary_pixels(boundary, (cropped_bbox_min, cropped_bbox_max), cropped_dims)

    mask_image = Image.new('L', (output_image.size[0], output_image.size[1]), 0)
    ImageDraw.Draw(mask_image).polygon(polygon, outline=1, fill=1)
    mask_raw = np.array(mask_image)

    cropped_raw = np.empty(output_raw.shape, dtype='uint8')
    cropped_raw[:,:,:] = output_raw[:,:,:]
    cropped_raw[:,:,3] = mask_raw * 255
    cropped_image = Image.fromarray(cropped_raw, 'RGBA')
    return cropped_image


tiles = [
    {
        'bbox': ((30, -25), (40, -15)),
        'img': Image.open('./resources/X21Y09.png').convert('RGBA')
    },
    {
        'bbox': ((30, -35), (40, -25)),
        'img': Image.open('./resources/X21Y10.png').convert('RGBA')
    }
]

def iterate():
    N = 100
    for i in range(N):
        (bbox, dims) = calculate_uncropped_bbox_and_dimensions(tiles)
        img = create_cropped_image(boundary, tiles, bbox, dims)
        img.save('/tmp/{0}.png'.format(i))
        sys.stdout.write('\r[{0}/{1}]'.format(i + 1, N))
        sys.stdout.flush()

print(timeit.timeit(iterate, number=1))
