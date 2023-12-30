import matplotlib.pyplot as plt
import matplotlib.patches as patches
import repo as repo
import color as clr
from model import ColorEntryMatch

def display_color_swatches(target_hex_str: str, closest_colors: list[ColorEntryMatch]):
    fig, ax = plt.subplots()
    swatch_width = 1  # Width of each color swatch
    interval = 0.1    # Interval between swatches

    # Display target color
    ax.add_patch(patches.Rectangle((0, 1), len(closest_colors) * (swatch_width + interval) - interval, 1, color=f"#{target_hex_str}"))
    ax.annotate(f"Target: {target_hex_str}", (len(closest_colors) * (swatch_width + interval) / 2, 1.05), color='black', weight='bold', 
                fontsize=9, ha='center', va='center')

    # Display closest colors
    for i, cem in enumerate(closest_colors):
        position = i * (swatch_width + interval)
        ax.add_patch(patches.Rectangle((position, 0), swatch_width, 1, color=f"#{cem.color.hex}"))
        ax.annotate(f"{cem.color.hex} {cem.color.coco}", (position + swatch_width / 2, -0.05), color='black', weight='bold', 
                    fontsize=8, ha='center', va='center')

    total_width = len(closest_colors) * (swatch_width + interval)
    plt.xlim(0, total_width)
    plt.ylim(-0.1, 2)
    ax.set_aspect('equal', adjustable='box')
    plt.axis('off')
    plt.show()

def main():
    csv_file_path = 'colors.csv'
    repository = repo.prepare_repository(csv_file_path)
   
    while True:
        target_hex_str = input("Enter a hex color (or type 'exit' to quit): ").strip()
        if target_hex_str.lower() in ['exit', 'quit']:
            break

        if len(target_hex_str) != 6 or not all(c in '0123456789ABCDEFabcdef' for c in target_hex_str):
            print("Invalid hex color format. Please enter a 6-digit hex color.")
            continue
        
        target_hex = clr.hex_to_lab(target_hex_str)
        closest_colors = clr.find_closest_colors(repository, target_hex)

        print()
        print(" === BEST MATCH FOR COLOR " + target_hex_str.upper() + " === ")
        for cem in closest_colors:
            print(f"{cem.color.hex} {cem.color.coco}  - Distance: {cem.distance}")
        print()

        display_color_swatches(target_hex_str, closest_colors)
            

if __name__ == "__main__":
    main()
