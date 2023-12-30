from colormath.color_objects import sRGBColor, LabColor

class ColorEntry:
    def __init__(self, hex_str: str, coco: str, mard: str, available: bool, 
                 rgb_tuple: tuple[int, int, int], srgb_color: sRGBColor, lab_color: LabColor):
        self.hex = hex_str
        self.coco = coco
        self.mard = mard
        self.available = available
        self.rgb_tuple = rgb_tuple
        self.srgb_color = srgb_color
        self.lab_color = lab_color
    
    def __repr__(self):
        return f"ColorEntry({self.hex}, {self.coco}, {self.mard}, {self.available}, {self.rgb_tuple}, {self.srgb_color}, {self.lab_color})"

class ColorEntryMatch:
    def __init__(self, color: ColorEntry, distance: float):
        self.color = color
        self.distance = distance
