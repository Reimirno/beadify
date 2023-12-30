import tkinter as tk
from PIL import Image
import color as clr
import repo as repo

K = 5
CELL_SIZE = 20
AVAIALABLE_ONLY = True


def load_src_img(src_img_path) -> (Image, list[list[str]], dict[str, any]):
    image = Image.open(src_img_path)
    pixels = image.load()
    width, height = image.size
    src_pxls, uniq_src_pxls = [], {}
    for x in range(width):
        row_pxls = []
        for y in range(height):
            r, g, b, a = pixels[x, y]
            rgb = (r, g, b)
            hex_str = clr.rgb_to_hex(rgb)
            row_pxls.append(hex_str)
            uniq_src_pxls[hex_str] = None
        src_pxls.append(row_pxls)
    return image, src_pxls, uniq_src_pxls

def prepare_pxl_map(uniq_src_pxls: dict[str, any], repository: list[tuple[clr.LabColor, dict[str, any]]]) -> dict[str, any]:
    for hex_str in uniq_src_pxls:
        lab_color = clr.hex_to_lab(hex_str)
        closest_colors = clr.find_closest_colors(repository, lab_color, k=K, available_only=AVAIALABLE_ONLY)
        uniq_src_pxls[hex_str] = closest_colors
    return uniq_src_pxls

def get_mapped_color_row(pxl_map: dict[str, any], orig_hex_str: str, sub_idx: int):
    return pxl_map[orig_hex_str][sub_idx][2]

def get_all_mapped_color_rows(pxl_map: dict[str, any], orig_hex_str: str):
    return [pxl_map[orig_hex_str][i][2] for i in range(len(pxl_map[orig_hex_str]))]

def get_contrasting_text_color_hex_str(bg_hex_str: str) -> str:
    return '#FFFFFF' if clr.calculate_luminance(bg_hex_str) < 0.5 else '#000000'

def export_canvas(canvas):
    canvas.postscript(file="output.ps", colormode='color')
    img = Image.open("output.ps")
    img.save("output.png", "png")

def main():
    cur_img_path = None

    if not cur_img_path:
        # make a file dialog to select an image
        from tkinter import filedialog
        cur_img_path = filedialog.askopenfilename(initialdir = ".",title = "Select file",filetypes = (("png files","*.png"),("jpeg files","*.jpg"),("all files","*.*")))

    if not cur_img_path:
        print("No image selected. Exiting...")
        exit(0)
    
    root = tk.Tk()
    root.title("Beadify")

    img, src_pxls, uniq_src_pxls = load_src_img(cur_img_path)
    repository = repo.prepare_repository("colors.csv")
    pxl_map = prepare_pxl_map(uniq_src_pxls, repository)

    var_map_choice = {hex_str: 0 for hex_str in pxl_map}
    change_map_choice_lambda = lambda new_val: None
    var_fx, var_fy = 0, 0
    change_focus_lambda = lambda x, y: None
    var_label, var_outline = True, True
    change_style_lambda = lambda: None

    def draw_src_img(var_outline):
        width, height = img.size
        canvas = tk.Canvas(root, width=width*CELL_SIZE, height=height*CELL_SIZE)
        for x in range(width):
            for y in range(height):
                position = x * CELL_SIZE, y * CELL_SIZE, (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE
                canvas.create_rectangle(position, fill=src_pxls[x][y], outline='grey' if var_outline else '',
                                        tags=f"rect_{x}_{y}")
        return canvas

    def update_src_img(canvas, new_var_outline):
        width, height = img.size
        for x in range(width):
            for y in range(height):
                canvas.itemconfig(f"rect_{x}_{y}", outline='grey' if new_var_outline else '')

    src_canvas = draw_src_img(var_outline)
    src_canvas.grid(row=0, column=0)

    def draw_rlt_img(map_choice, var_label, var_outline):
        width, height = img.size
        canvas = tk.Canvas(root, width=width*CELL_SIZE, height=height*CELL_SIZE)
        for x in range(width):
            for y in range(height):
                choice_idx = map_choice[src_pxls[x][y]]
                bead_choice = pxl_map[src_pxls[x][y]][choice_idx][2]
                position = x * CELL_SIZE, y * CELL_SIZE, (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE
                cell = canvas.create_rectangle(position, fill='#' + bead_choice['hex'], outline='grey' if var_outline else '', tags=f"rect_{x}_{y}")
                center_x, center_y = (x + 0.5) * CELL_SIZE, (y + 0.5) * CELL_SIZE
                text = canvas.create_text(center_x, center_y, text=bead_choice['coco'] if var_label else '', 
                                          fill=get_contrasting_text_color_hex_str(bead_choice['hex']),
                                          tags=f"text_{x}_{y}")
                nonlocal change_focus_lambda
                canvas.tag_bind(text, '<Button-1>', lambda event, x=x, y=y: change_focus_lambda(x, y))
                canvas.tag_bind(cell, '<Button-1>', lambda event, x=x, y=y: change_focus_lambda(x, y))
        return canvas

    def update_rlt_img(canvas, new_map_choice, new_var_label, new_var_outline):
        width, height = img.size
        for x in range(width):
            for y in range(height):
                choice_idx = new_map_choice[src_pxls[x][y]]
                bead_choice = pxl_map[src_pxls[x][y]][choice_idx][2]
                canvas.itemconfig(f"rect_{x}_{y}", fill='#' + bead_choice['hex'],
                                  outline='grey' if new_var_outline else '')
                canvas.itemconfig(f"text_{x}_{y}", text=bead_choice['coco'] if new_var_label else '',
                                  fill=get_contrasting_text_color_hex_str(bead_choice['hex']))

    rlt_canvas = draw_rlt_img(var_map_choice, var_label, var_outline)
    rlt_canvas.grid(row=0, column=1)

    def draw_focus_palette(map_choice, fx, fy):
        big_cell_size = 200
        medium_cell_size = 100
        spacing_big = 50
        spacing_medium = 5
        canvas_width = max(2 * big_cell_size + spacing_big, K * medium_cell_size + (K - 1) * spacing_medium)
        canvas_height = big_cell_size + medium_cell_size + spacing_medium

        orig_hex_str = src_pxls[fx][fy]
        choice_idx = map_choice[orig_hex_str]
        cur_rlt_color_row = get_mapped_color_row(pxl_map, orig_hex_str, choice_idx)
        all_rlt_color_rows = get_all_mapped_color_rows(pxl_map, orig_hex_str)

        canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)

        x = (canvas_width - 2 * big_cell_size - spacing_big) / 2
        y = 0
        canvas.create_rectangle(x, y, x + big_cell_size, y + big_cell_size, fill=orig_hex_str, tags='target_color')
        canvas.create_text(x + big_cell_size / 2, y + big_cell_size / 2, text="TARGET-" + orig_hex_str, 
                            fill=get_contrasting_text_color_hex_str(orig_hex_str), tags='target_text')

        x += big_cell_size + spacing_big
        canvas.create_rectangle(x, y, x + big_cell_size, y + big_cell_size, fill='#' + cur_rlt_color_row['hex'], tags='current_color')
        canvas.create_text(x + big_cell_size / 2, y + big_cell_size / 2, text="CURRENT-" + cur_rlt_color_row['coco'], 
                           fill=get_contrasting_text_color_hex_str(cur_rlt_color_row['hex']), tags='current_text')

        y = big_cell_size + spacing_medium
        for i in range(K):
            x = i * (medium_cell_size + spacing_medium)
            # Center the second row horizontally
            x += (canvas_width - K * medium_cell_size - (K - 1) * spacing_medium) / 2
            cell = canvas.create_rectangle(x, y, x + medium_cell_size, y + medium_cell_size, fill='#' + all_rlt_color_rows[i]['hex'], tags=f'option_color_{i}')
            text = canvas.create_text(x + medium_cell_size / 2, y + medium_cell_size / 2, text=all_rlt_color_rows[i]['coco'], 
                                      fill=get_contrasting_text_color_hex_str(all_rlt_color_rows[i]['hex']), tags=f'option_text_{i}')
            nonlocal change_map_choice_lambda
            canvas.tag_bind(text, '<Button-1>', lambda event, i=i: change_map_choice_lambda(i))
            canvas.tag_bind(cell, '<Button-1>', lambda event, i=i: change_map_choice_lambda(i))

        return canvas

    def update_focus_palette(canvas, new_map_choice, new_fx, new_fy):
        orig_hex_str = src_pxls[new_fx][new_fy]
        choice_idx = new_map_choice[orig_hex_str]
        cur_rlt_color_row = get_mapped_color_row(pxl_map, orig_hex_str, choice_idx)
        all_rlt_color_rows = get_all_mapped_color_rows(pxl_map, orig_hex_str)

        # Update target color and text
        canvas.itemconfig('target_color', fill=orig_hex_str)
        canvas.itemconfig('target_text', text="TARGET-" + orig_hex_str,
                          fill=get_contrasting_text_color_hex_str(orig_hex_str))

        # Update current color and text
        canvas.itemconfig('current_color', fill='#' + cur_rlt_color_row['hex'])
        canvas.itemconfig('current_text', text="CURRENT-" + cur_rlt_color_row['coco'],
                          fill=get_contrasting_text_color_hex_str(cur_rlt_color_row['hex']))

        # Update option colors and texts
        for i in range(K):
            canvas.itemconfig(f'option_color_{i}', fill='#' + all_rlt_color_rows[i]['hex'])
            canvas.itemconfig(f'option_text_{i}', text=all_rlt_color_rows[i]['coco'],
                              fill=get_contrasting_text_color_hex_str(all_rlt_color_rows[i]['hex']))
            
    focus_canvas = draw_focus_palette(var_map_choice, var_fx, var_fy)
    focus_canvas.grid(row=1, column=0, columnspan=2)

    def draw_color_collection(map_choice):
        color_size = 40
        color_interval = 5
        width = min(800, len(map_choice) * (color_size + color_interval) - color_interval)
        height = color_size
        canvas = tk.Canvas(root, width=width, height=height)
        x, y = 0, 0
        for i, hex_str in enumerate(map_choice):
            mapped_color_row = get_mapped_color_row(pxl_map, hex_str, map_choice[hex_str])
            canvas.create_rectangle(x, y, x + color_size, y + color_size, fill='#' + mapped_color_row['hex'],
                                    outline='grey', tags=f"color_{i}")
            canvas.create_text(x + color_size / 2, y + color_size / 2, text=mapped_color_row['coco'],
                                fill=get_contrasting_text_color_hex_str(mapped_color_row['hex']), tags=f"text_{i}")
            x += color_size
            if x >= width:
                x = 0
                y += CELL_SIZE
        return canvas
    
    def update_color_collection(canvas, new_map_choice):
        for i, hex_str in enumerate(new_map_choice):
            mapped_color_row = get_mapped_color_row(pxl_map, hex_str, new_map_choice[hex_str])
            canvas.itemconfig(f"color_{i}", fill='#' + mapped_color_row['hex'])
            canvas.itemconfig(f"text_{i}", text=mapped_color_row['coco'],
                                fill=get_contrasting_text_color_hex_str(mapped_color_row['hex']))
        

    color_collection_canvas = draw_color_collection(var_map_choice)
    color_collection_canvas.grid(row=2, column=0, columnspan=2)

    def change_focus_lambda(x, y):
        nonlocal var_fx, var_fy
        var_fx, var_fy = x, y
        update_focus_palette(focus_canvas, var_map_choice, var_fx, var_fy)

    def change_map_choice_lambda(new_val):
        nonlocal var_map_choice, var_fx, var_fy, var_label, var_outline
        orig_hex_str = src_pxls[var_fx][var_fy]
        var_map_choice[orig_hex_str] = new_val
        update_rlt_img(rlt_canvas, var_map_choice, var_label, var_outline)
        update_color_collection(color_collection_canvas, var_map_choice)
        update_focus_palette(focus_canvas, var_map_choice, var_fx, var_fy)

    def reset_all_map_choice():
        nonlocal var_map_choice, var_fx, var_fy, var_label, var_outline
        for hex_str in uniq_src_pxls:
            var_map_choice[hex_str] = 0
        update_rlt_img(rlt_canvas, var_map_choice, var_label, var_outline)
        update_color_collection(color_collection_canvas, var_map_choice)
        update_focus_palette(focus_canvas, var_map_choice, var_fx, var_fy)
    
    def change_style_lambda():
        nonlocal var_label, var_outline
        var_label = not var_label
        var_outline = not var_outline
        update_src_img(src_canvas, var_outline)
        update_rlt_img(rlt_canvas, var_map_choice, var_label, var_outline)

    def draw_button_groups():
        button_frame = tk.Frame(root)

        style_button = tk.Button(button_frame, text="Style", command=lambda: change_style_lambda())
        style_button.grid(row=0, column=0)

        reset_button = tk.Button(button_frame, text="Reset", command=reset_all_map_choice)
        reset_button.grid(row=0, column=1)

        save_button = tk.Button(button_frame, text="Save", command=lambda: export_canvas(rlt_canvas))
        save_button.grid(row=0, column=2)

        exit_button = tk.Button(button_frame, text="Exit", command=root.destroy)
        exit_button.grid(row=0, column=3)

        return button_frame
    
    button_frame = draw_button_groups()
    button_frame.grid(row=3, column=0, columnspan=2)

    root.mainloop()

if __name__ == "__main__":
    main()
