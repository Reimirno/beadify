import csv
from colormath.color_objects import sRGBColor, LabColor
from color import hex_to_lab

def prepare_repository(csv_file_path) -> list[tuple[LabColor, dict]]:
    repository = []
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            repository.append((hex_to_lab(row['hex']), row))
    return repository