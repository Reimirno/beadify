import tkinter as tk
from PIL import Image
import color as clr
import repo as repo
from model import ColorEntry, ColorEntryMatch

K = 5
CELL_SIZE = 20
AVAIALABLE_ONLY = True

class ImageFixture:
    def __init__(self, width: int, height: int, pixels: list[list[str]], 
                 color_map: dict[str, list[ColorEntryMatch]]):
        self.width = width
        self.height = height
        self.pixels = pixels
        self.color_map = color_map

class ColorMapChoice:
    def __init__(self, image_fixture: ImageFixture):
        self.color_map = image_fixture.color_map
        self.color_map_choice = {hex_str: 0 for hex_str in image_fixture.color_map}

    @property
    def count(self):
        return len(self.color_map_choice)
    
    def set_mapped_color_for(self, hex_str, new_choice_idx):
        self.color_map_choice[hex_str] = new_choice_idx
    
    def reset_all_map_choice(self):
        for hex_str in self.color_map_choice:
            self.color_map_choice[hex_str] = 0
    
    def get_mapped_color_for(self, hex_str) -> ColorEntryMatch:
        return self.color_map[hex_str][self.color_map_choice[hex_str]]
    
    def get_all_mapped_colors_for(self, hex_str) -> list[ColorEntryMatch]:
        return self.color_map[hex_str]
    
    def get_complete_map(self) -> dict[str, ColorEntryMatch]:
        return {orig_hex_str: self.get_mapped_color_for(orig_hex_str) for orig_hex_str in self.color_map}

    def get_unique_mapped_colors(self) -> set[ColorEntryMatch]:
        return {self.get_mapped_color_for(orig_hex_str) for orig_hex_str in self.color_map}

class SrcImgCanvas(tk.Canvas):
    def __init__(self, root, image_fixture: ImageFixture, **kwargs):
        self.image_fixture = image_fixture
        width, height = image_fixture.width, image_fixture.height
        super().__init__(root, width=width*CELL_SIZE, height=height*CELL_SIZE, **kwargs)
        for x in range(width):
            for y in range(height):
                position = x * CELL_SIZE, y * CELL_SIZE, (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE
                self.create_rectangle(position, fill=image_fixture.pixels[x][y], tags=f"rect_{x}_{y}")
    
    def update(self, var_outline):
        width, height = self.image_fixture.width, self.image_fixture.height
        for x in range(width):
            for y in range(height):
                self.itemconfig(f"rect_{x}_{y}", outline='grey' if var_outline else '')

class RltImgCanvas(tk.Canvas):
    def __init__(self, root, image_fixture: ImageFixture, **kwargs):
        self.image_fixture = image_fixture
        self.change_focus_lambda = lambda x, y: None
        width, height = image_fixture.width, image_fixture.height
        super().__init__(root, width=width*CELL_SIZE, height=height*CELL_SIZE, **kwargs)
        for x in range(width):
            for y in range(height):
                position = x * CELL_SIZE, y * CELL_SIZE, (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE
                cell = self.create_rectangle(position, tags=f"rect_{x}_{y}")
                text = self.create_text((x + 0.5) * CELL_SIZE, (y + 0.5) * CELL_SIZE, text='', tags=f"text_{x}_{y}")
                self.tag_bind(text, '<Button-1>', lambda event, x=x, y=y: self.change_focus_lambda(x, y))
                self.tag_bind(cell, '<Button-1>', lambda event, x=x, y=y: self.change_focus_lambda(x, y))
    
    def assign_event(self, change_focus_lambda):
        self.change_focus_lambda = change_focus_lambda

    def update(self, var_map_choice: ColorMapChoice, var_label:  bool, var_outline: bool):
        width, height = self.image_fixture.width, self.image_fixture.height
        for x in range(width):
            for y in range(height):
                chosen_mapped_color = var_map_choice.get_mapped_color_for(self.image_fixture.pixels[x][y])
                self.itemconfig(f"rect_{x}_{y}", fill='#' + chosen_mapped_color.color.hex,
                                    outline='grey' if var_outline else '')
                self.itemconfig(f"text_{x}_{y}", text=chosen_mapped_color.color.coco if var_label else '',
                                    fill=get_contrasting_text_color_hex_str(chosen_mapped_color.color.hex))

class FocusPalette(tk.Canvas):
    def __init__(self, root, image_fixture: ImageFixture, **kwargs):
        self.image_fixture = image_fixture
        self.change_map_choice_lambda = lambda x: None
        big_cell_size = 200
        medium_cell_size = 100
        spacing_big = 50
        spacing_medium = 5
        canvas_width = max(2 * big_cell_size + spacing_big, K * medium_cell_size + (K - 1) * spacing_medium)
        canvas_height = big_cell_size + medium_cell_size + spacing_medium
        super().__init__(root, width=canvas_width, height=canvas_height, **kwargs)

        x = (canvas_width - 2 * big_cell_size - spacing_big) / 2
        y = 0
        self.create_rectangle(x, y, x + big_cell_size, y + big_cell_size, tags='target_color')
        self.create_text(x + big_cell_size / 2, y + big_cell_size / 2, text='', tags='target_text')

        x += big_cell_size + spacing_big
        self.create_rectangle(x, y, x + big_cell_size, y + big_cell_size, tags='current_color')
        self.create_text(x + big_cell_size / 2, y + big_cell_size / 2, text='', tags='current_text')

        y = big_cell_size + spacing_medium
        for i in range(K):
            x = i * (medium_cell_size + spacing_medium)
            x += (canvas_width - K * medium_cell_size - (K - 1) * spacing_medium) / 2
            cell = self.create_rectangle(x, y, x + medium_cell_size, y + medium_cell_size, tags=f'option_color_{i}')
            text = self.create_text(x + medium_cell_size / 2, y + medium_cell_size / 2, text='', tags=f'option_text_{i}')
            self.tag_bind(text, '<Button-1>', lambda event, i=i: self.change_map_choice_lambda(i))
            self.tag_bind(cell, '<Button-1>', lambda event, i=i: self.change_map_choice_lambda(i))
    
    def assign_event(self, change_map_choice_lambda):
        self.change_map_choice_lambda = change_map_choice_lambda

    def update(self, var_map_choice: ColorMapChoice, var_fx: int, var_fy: int):
        orig_hex_str = self.image_fixture.pixels[var_fx][var_fy]
        chosen_mapped_color = var_map_choice.get_mapped_color_for(orig_hex_str)
        all_mapped_colors = var_map_choice.get_all_mapped_colors_for(orig_hex_str)

        self.itemconfig('target_color', fill=orig_hex_str)
        self.itemconfig('target_text', text="TARGET-" + orig_hex_str,
                        fill=get_contrasting_text_color_hex_str(orig_hex_str))

        self.itemconfig('current_color', fill='#' + chosen_mapped_color.color.hex)
        self.itemconfig('current_text', text="CURRENT-" + chosen_mapped_color.color.coco,
                        fill=get_contrasting_text_color_hex_str(chosen_mapped_color.color.hex))

        for i in range(K):
            cur_option_color = all_mapped_colors[i]
            self.itemconfig(f'option_color_{i}', fill='#' + cur_option_color.color.hex)
            self.itemconfig(f'option_text_{i}', text=cur_option_color.color.coco,
                            fill=get_contrasting_text_color_hex_str(cur_option_color.color.hex))

class ButtonGroup(tk.Frame):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
    
    def add_button(self, text, command):
        button = tk.Button(self, text=text, command=command)
        button.pack(side='left')

class ColorSummary(tk.Canvas):
    def __init__(self, root, image_fixture: ImageFixture, **kwargs):
        self.image_fixture = image_fixture
        super().__init__(root, width=150, height=600, **kwargs)

        self.scrollbar = tk.Scrollbar(root, orient="vertical", command=self.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.configure(yscrollcommand=self.scrollbar.set) # let scrollbar control the canvas

        self.cell_size = 40
        self.interval = 5

        x = 10
        for i, orig_hex in enumerate(image_fixture.color_map):
            y0 = i * (self.cell_size + self.interval) + 10 
            x1 = x + self.cell_size 
            y1 = y0 + self.cell_size
            self.create_rectangle(x, y0, x1, y1, fill=orig_hex, outline='grey')
        
        x += self.cell_size + self.interval
        for i, orig_hex in enumerate(image_fixture.color_map):
            y0 = i * (self.cell_size + self.interval) + 10 
            x1 = x + self.cell_size 
            y1 = y0 + self.cell_size
            self.create_rectangle(x, y0, x1, y1, fill='#000000', outline='grey', tags=f"mappped_color_{i}")
            self.create_text(x + self.cell_size / 2, y0 + self.cell_size / 2, text='', tags=f"mappped_text_{i}")
        
        self.config(scrollregion=self.bbox("all")) # let canvas know the scrollable region
    
    def update(self, var_map_choice: ColorMapChoice):
        for i, orig_hex in enumerate(self.image_fixture.color_map):
            chosen_mapped_color = var_map_choice.get_mapped_color_for(orig_hex)
            self.itemconfig(f"mappped_color_{i}", fill='#' + chosen_mapped_color.color.hex)
            self.itemconfig(f"mappped_text_{i}", text=chosen_mapped_color.color.coco,
                            fill=get_contrasting_text_color_hex_str(chosen_mapped_color.color.hex))
        
        self.delete(*self.find_withtag("unique_*"))
        uniques = list(var_map_choice.get_unique_mapped_colors())
        uniques.sort(key=lambda cem:cem.color.coco)
        x = 10 + 2 * (self.cell_size + self.interval) + self.interval * 2
        for i, cem in enumerate(uniques):
            y0 = i * (self.cell_size + self.interval) + 10 
            x1 = x + self.cell_size 
            y1 = y0 + self.cell_size
            self.create_rectangle(x, y0, x1, y1, fill='#' + cem.color.hex, outline='grey', tags=f"unique_color_{i}")
            self.create_text(x + self.cell_size / 2, y0 + self.cell_size / 2, text=cem.color.coco,
                             fill=get_contrasting_text_color_hex_str(cem.color.hex),
                              tags=f"unique_text_{i}")
        

def load_src_img(repository: list[ColorEntry], src_img_path) -> ImageFixture:
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
    for hex_str in uniq_src_pxls:
        lab_color = clr.hex_to_lab(hex_str)
        closest_colors = clr.find_closest_colors(repository, lab_color, k=K, available_only=AVAIALABLE_ONLY)
        uniq_src_pxls[hex_str] = closest_colors
    image_fixture = ImageFixture(width, height, src_pxls, uniq_src_pxls)
    return image_fixture

def get_contrasting_text_color_hex_str(bg_hex_str: str) -> str:
    return '#FFFFFF' if clr.calculate_luminance(bg_hex_str) < 0.5 else '#000000'

def export_canvas(canvas):
    canvas.postscript(file="output.ps", colormode='color')
    img = Image.open("output.ps")
    img.save("output.png", "png")

def main():
    cur_img_path = None

    if not cur_img_path:
        from tkinter import filedialog
        cur_img_path = filedialog.askopenfilename(
            initialdir = ".",
            title = "Select file",
            filetypes = (("png files","*.png"),("jpeg files","*.jpg"),("all files","*.*")))

    if not cur_img_path:
        print("No image selected. Exiting.")
        exit(0)
    
    root = tk.Tk()
    root.title("Beadify")

    repository = repo.prepare_repository("colors.csv")
    image_fixture = load_src_img(repository, cur_img_path)

    var_map_choice = ColorMapChoice(image_fixture)
    var_fx, var_fy = 0, 0
    var_label, var_outline = True, True

    left_pane = tk.Frame(root)
    right_pane = tk.Frame(root)

    src_canvas = SrcImgCanvas(left_pane, image_fixture=image_fixture)
    src_canvas.update(var_outline)
    src_canvas.grid(row=0, column=0)

    rlt_canvas = RltImgCanvas(left_pane, image_fixture=image_fixture)
    rlt_canvas.update(var_map_choice, var_label, var_outline)
    rlt_canvas.grid(row=0, column=1)

    focus_palette = FocusPalette(left_pane, image_fixture=image_fixture)
    focus_palette.update(var_map_choice, var_fx, var_fy)
    focus_palette.grid(row=1, column=0, columnspan=2)

    def change_focus_lambda(x, y):
        nonlocal var_fx, var_fy
        var_fx, var_fy = x, y
        focus_palette.update(var_map_choice, var_fx, var_fy)
    rlt_canvas.assign_event(change_focus_lambda)

    def change_map_choice_lambda(new_val):
        nonlocal var_map_choice, var_fx, var_fy, var_label, var_outline
        orig_hex_str = image_fixture.pixels[var_fx][var_fy]
        var_map_choice.set_mapped_color_for(orig_hex_str, new_val)
        color_summary.update(var_map_choice)
        rlt_canvas.update(var_map_choice, var_label, var_outline)
        focus_palette.update(var_map_choice, var_fx, var_fy)
    focus_palette.assign_event(change_map_choice_lambda)

    def reset_all_map_choice():
        nonlocal var_map_choice, var_fx, var_fy, var_label, var_outline
        var_map_choice.reset_all_map_choice()
        color_summary.update(var_map_choice)
        rlt_canvas.update(var_map_choice, var_label, var_outline)
        focus_palette.update(var_map_choice, var_fx, var_fy)
    
    def change_label_lambda():
        nonlocal var_label, var_outline
        var_label = not var_label
        src_canvas.update(var_outline)
        rlt_canvas.update(var_map_choice, var_label, var_outline)
    
    def change_outline_lambda():
        nonlocal var_label, var_outline
        var_outline = not var_outline
        src_canvas.update(var_outline)
        rlt_canvas.update(var_map_choice, var_label, var_outline)

    btn_group = ButtonGroup(left_pane)
    btn_group.add_button("Label", change_label_lambda)
    btn_group.add_button("Outline", change_outline_lambda)
    btn_group.add_button("Reset", reset_all_map_choice)
    btn_group.add_button("Save", lambda: export_canvas(rlt_canvas))
    btn_group.add_button("Exit", root.destroy)
    btn_group.grid(row=3, column=0, columnspan=2)

    color_summary = ColorSummary(right_pane, image_fixture=image_fixture)
    color_summary.update(var_map_choice)
    color_summary.pack(side="left", fill="both", expand=True)

    left_pane.pack(side='left')
    right_pane.pack(side='right', fill='y')

    root.mainloop()

if __name__ == "__main__":
    main()
