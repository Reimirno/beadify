from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie1976
from model import ColorEntry, ColorEntryMatch

# Patch numpy to allow asscalar() on numpy.float64
import numpy
def patch_asscalar(a):
    return a.item()
setattr(numpy, "asscalar", patch_asscalar)
# End patch

def hex_to_rgb(hex_str) -> tuple[int, int, int]:
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)

def hex_to_srgb(hex_str: str) -> sRGBColor:
    hex_str = hex_str.lstrip('#')
    rgb_tuple = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
    return sRGBColor(*rgb_tuple, is_upscaled=True)

def srgb_to_lab(srgb_color: sRGBColor) -> LabColor:
    return convert_color(srgb_color, LabColor)

def hex_to_lab(hex_str: str) -> LabColor:
    return srgb_to_lab(hex_to_srgb(hex_str))

def calculate_luminance(hex_str: str) -> float:
    r, g, b = hex_to_rgb(hex_str)
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255

def color_distance(lab_color1: LabColor, lab_color2: LabColor) -> float:
    return delta_e_cie1976(lab_color1, lab_color2)

def find_closest_colors(repository: list[ColorEntry], target_lab_color: LabColor, 
                        k=5, available_only=False) -> list[ColorEntryMatch]:
    rlt = []
    for colorentry in repository:
        if available_only and not colorentry.available:
            continue
        dist = color_distance(colorentry.lab_color, target_lab_color)
        rlt.append(ColorEntryMatch(colorentry, dist))
    rlt.sort(key=lambda cem:cem.distance)
    return rlt[:k]
