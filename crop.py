import numpy as np
from PIL import Image, ImageDraw
from util import BBox, V2
from math import floor, ceil


def calculate_composite_bbox_and_dimensions(tiles):
    """
    calculate the geographic bounding box and the required
    composite image dimensions for the given tiles.
    """
    bbox = None
    for i, tile in enumerate(tiles):
        if i == 0:
            bbox = BBox(tile['bbox'].min, tile['bbox'].max)
        else:
            bbox.expand(tile['bbox'].min)
            bbox.expand(tile['bbox'].max)

    # Use the first tile bounding box and dimensions - the assumption here is
    # that all the tile are of the same size, but this is not checked
    # The fucntion should really assert this assumption.
    tile_image_width = tiles[0]['img'].size[0]
    tile_image_height = tiles[0]['img'].size[1]
    width = round(bbox.width / tiles[0]['bbox'].width) * tile_image_width
    height = round(bbox.height / tiles[0]['bbox'].height) * tile_image_height
    return (bbox, (width, height))


def create_composite_image(tiles, bbox, dims):
    """
    With the given tileset, create a new image with the given
    bounding box and dimensions. Returns a PIL image.
    """
    (width, height) = dims

    # Default is black with 0 opacity
    composite_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))

    for i, tile in enumerate(tiles):
        offset_x = round(
            (tile['bbox'].min.x - bbox.min.x) / bbox.width * width)
        offset_y = round(
            -(tile['bbox'].max.y - bbox.max.y) / bbox.height * height)
        composite_img.paste(tile['img'], (offset_x, offset_y))
    return composite_img


def geo_json_bbox(coordinates):
    """
    Calculate the bounding box from the GeoJSON coordinates.
    """
    bbox = None
    for i, coordinate in enumerate(coordinates):
        vec = V2(coordinate[0], coordinate[1])
        if i == 0:
            bbox = BBox(vec, vec)
        else:
            bbox.expand(vec)
    return bbox


def calculate_crop(image, uncropped_bbox, boundary_bbox):
    """
    Crop an image with a given geographic bounding to the new bounding box.
    As we round up the pixel size of the new image, the geographic bounding
    box of new image will be potentially slightly larger then the required one,
    so also calculate the correct bounding box for the result.
    """
    pixel_min_x = floor(
        (boundary_bbox.min.x - uncropped_bbox.min.x) /
        uncropped_bbox.width * image.size[0])
    pixel_min_y = floor(
        (uncropped_bbox.max.y - boundary_bbox.max.y) /
        uncropped_bbox.height * image.size[1])
    pixel_max_x = ceil(
        (boundary_bbox.max.x - uncropped_bbox.min.x) /
        uncropped_bbox.width * image.size[0])
    pixel_max_y = ceil(
        (uncropped_bbox.max.y - boundary_bbox.min.y) /
        uncropped_bbox.height * image.size[1])
    cropped_pixels = (pixel_min_x, pixel_min_y, pixel_max_x, pixel_max_y)

    cropped_bbox = BBox(
        V2(
            uncropped_bbox.min.x + pixel_min_x /
            image.size[0] * uncropped_bbox.width,
            uncropped_bbox.max.y - pixel_max_y /
            image.size[1] * uncropped_bbox.height),
        V2(
            uncropped_bbox.min.x + pixel_max_x /
            image.size[0] * uncropped_bbox.width,
            uncropped_bbox.max.y - pixel_min_y /
            image.size[1] * uncropped_bbox.height))
    return (cropped_pixels, cropped_bbox)


def crop_to_boundary(boundary_coordinates, composite_img, composite_bbox):
    """
    Crop an image to the given GeoJSON boundary.
    """
    boundary_bbox = geo_json_bbox(boundary_coordinates)
    (cropped_pixels, cropped_bbox) = calculate_crop(
        composite_img, composite_bbox, boundary_bbox)
    return (composite_img.crop(cropped_pixels), cropped_bbox)


def create_boundary_pixels(coordinates, bbox, image_dims):
    """
    For the given GeoJSON coordinates, map to a list
    of pixel positions.
    """
    (image_width, image_height) = image_dims

    def coordinate_to_pixels(coordinate):
        return (
            round(
                (coordinate[0] - bbox.min.x) / bbox.width * image_width),
            round(
                (bbox.max.y - coordinate[1]) / bbox.height * image_height))

    pixels = map(coordinate_to_pixels, coordinates)
    return list(pixels)


def mask_pixels_outside_boundary(cropped_to_boundary_image,
                                 boundary_coordinates,
                                 cropped_bbox):
    """
    Mask the image to only include pixels inside the GeoJSON boundary.
    """
    polygon_pixels = create_boundary_pixels(
        boundary_coordinates,
        cropped_bbox,
        cropped_to_boundary_image.size)
    mask_image = Image.new('L', cropped_to_boundary_image.size, 0)
    ImageDraw.Draw(mask_image).polygon(polygon_pixels, outline=0, fill=1)
    mask_raw = np.array(mask_image)

    cropped_to_bbox_raw = np.asarray(cropped_to_boundary_image)
    masked_raw = np.empty(cropped_to_bbox_raw.shape, dtype='uint8')
    # Mask all channels to reduce file size.
    # How to do RGB in one step?
    masked_raw[:, :, 0] = mask_raw * cropped_to_bbox_raw[:, :, 0]
    masked_raw[:, :, 1] = mask_raw * cropped_to_bbox_raw[:, :, 1]
    masked_raw[:, :, 2] = mask_raw * cropped_to_bbox_raw[:, :, 2]
    masked_raw[:, :, 3] = mask_raw * 255
    masked_image = Image.fromarray(masked_raw, 'RGBA')
    return masked_image
