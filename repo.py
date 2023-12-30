import csv
from colormath.color_objects import sRGBColor, LabColor
from color import hex_to_lab, hex_to_rgb, hex_to_srgb
from model import ColorEntry

def prepare_repository(csv_file_path) -> list[ColorEntry]:
    repository = []
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            repository.append(_row_to_colorentry(row))
    return repository

def _row_to_colorentry(row) -> ColorEntry:
    hex_str, coco, mard, available = row['hex'].lstrip('#'), row['coco'], row['mard'], row['available'].lower() == 'true'
    rgb_tuple, srgb_color, lab_color = hex_to_rgb(hex_str), hex_to_srgb(hex_str), hex_to_lab(hex_str)
    return ColorEntry(hex_str, coco, mard, available, rgb_tuple, srgb_color, lab_color)