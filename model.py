from colormath.color_objects import sRGBColor, LabColor

class ColorEntry:
    def __init__(self, hex_str: str, coco: str, mard: str, available: bool, 
                 rgb_tuple: tuple[int, int, int], srgb_color: sRGBColor, lab_color: LabColor):
        self.hex = hex_str.lstrip('#').lower()
        self.coco = coco
        self.mard = mard
        self.available = available
        self.rgb_tuple = rgb_tuple
        self.srgb_color = srgb_color
        self.lab_color = lab_color
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, ColorEntry):
            return False
        return self.hex.lower() == __value.hex.lower()
    
    def __hash__(self) -> int:
        return hash(self.hex.lower())
    
    def __repr__(self):
        return f"ColorEntry({self.hex}, {self.coco}, {self.mard}, {self.available}, {self.rgb_tuple}, {self.srgb_color}, {self.lab_color})"

class ColorEntryMatch:
    def __init__(self, color: ColorEntry, distance: float):
        self.color = color
        self.distance = distance
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, ColorEntryMatch):
            return False
        return self.color == __value.color and self.distance == __value.distance
    
    def __hash__(self) -> int:
        return hash((self.color, self.distance))
