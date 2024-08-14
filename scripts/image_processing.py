import cv2
from PIL import Image
import os

def tile_image(input_path, output_folder, tile_size=640):
    os.makedirs(output_folder, exist_ok=True)
    original_image = Image.open(input_path)
    width, height = original_image.size
    num_horizontal_tiles = width // tile_size
    num_vertical_tiles = height // tile_size

    for j in range(num_vertical_tiles):
        for i in range(num_horizontal_tiles):
            left = i * tile_size
            upper = j * tile_size
            right = min((i + 1) * tile_size, width)
            lower = min((j + 1) * tile_size, height)

            tile = original_image.crop((left, upper, right, lower))
            tile_filename = f"tile_{j}_{i}.png"
            tile_path = os.path.join(output_folder, tile_filename)
            tile.save(tile_path)

    # Handle remainder tiles
    if width % tile_size != 0:
        for j in range(num_vertical_tiles):
            left = num_horizontal_tiles * tile_size
            upper = j * tile_size
            right = width
            lower = min((j + 1) * tile_size, height)
            tile = original_image.crop((left, upper, right, lower))
            tile_filename = f"tile_{j}_{num_horizontal_tiles}.png"
            tile_path = os.path.join(output_folder, tile_filename)
            tile.save(tile_path)

    if height % tile_size != 0:
        for i in range(num_horizontal_tiles):
            left = i * tile_size
            upper = num_vertical_tiles * tile_size
            right = min((i + 1) * tile_size, width)
            lower = height
            tile = original_image.crop((left, upper, right, lower))
            tile_filename = f"tile_{num_vertical_tiles}_{i}.png"
            tile_path = os.path.join(output_folder, tile_filename)
            tile.save(tile_path)

    if width % tile_size != 0 and height % tile_size != 0:
        left = num_horizontal_tiles * tile_size
        upper = num_vertical_tiles * tile_size
        right = width
        lower = height
        tile = original_image.crop((left, upper, right, lower))
        tile_filename = f"tile_{num_vertical_tiles}_{num_horizontal_tiles}.png"
        tile_path = os.path.join(output_folder, tile_filename)
        tile.save(tile_path)

def stitch_images(images):
    max_row = max(row for (row, col) in images.keys())
    max_col = max(col for (row, col) in images.keys())
    stitched_image = None

    for row in range(max_row + 1):
        row_images = [images.get((row, col), None) for col in range(max_col + 1)]
        row_images = [img for img in row_images if img is not None]
        
        if not row_images:
            continue

        # Ensure all images in the row have the same height and type
        base_height = row_images[0].shape[0]
        base_type = row_images[0].dtype
        row_images = [cv2.resize(img, (img.shape[1], base_height)) if img.shape[0] != base_height else img for img in row_images]
        row_images = [img.astype(base_type) if img.dtype != base_type else img for img in row_images]

        try:
            stitched_row = cv2.hconcat(row_images)
        except cv2.error:
            print(f"Error stitching row {row}. Skipping this row.")
            continue

        if stitched_image is None:
            stitched_image = stitched_row
        else:
            # Ensure the stitched row has the same width as the existing stitched image
            if stitched_row.shape[1] != stitched_image.shape[1]:
                stitched_row = cv2.resize(stitched_row, (stitched_image.shape[1], stitched_row.shape[0]))
            stitched_image = cv2.vconcat([stitched_image, stitched_row])

    return stitched_image

def overlap_plots(ortho_image_path, coords_txt_path, plots_folder_path, output_path):
    ortho_image = cv2.imread(ortho_image_path)

    with open(coords_txt_path, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        _, x_center, y_center, width, height = map(float, line.strip().split())
        abs_x_center = int(x_center * ortho_image.shape[1])
        abs_y_center = int(y_center * ortho_image.shape[0])
        abs_width = int(width * ortho_image.shape[1])
        abs_height = int(height * ortho_image.shape[0])

        top_left_x = abs_x_center - abs_width // 2
        top_left_y = abs_y_center - abs_height // 2

        plot_image_path = f"{plots_folder_path}/stitched_image_bounding_box_{i}.jpg"
        plot_image = cv2.imread(plot_image_path)

        plot_image_resized = cv2.resize(plot_image, (abs_width, abs_height))
        ortho_image[top_left_y:top_left_y+abs_height, top_left_x:top_left_x+abs_width] = plot_image_resized

    cv2.imwrite(output_path, ortho_image)

def save_stitched_image(stitched_image, output_path, plot_num, total_rows):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 2.8
    font_color = (255, 255, 255)
    background_color = (0, 0, 0)
    font_thickness = 8
    border_color = (0, 0, 255)
    
    text = f'P_{plot_num} : {total_rows}'
    
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_x = 50
    text_y = 200
    background_x = text_x
    background_y = text_y - text_size[1]
    background_width = text_size[0]
    background_height = text_size[1] + 10
    
    cv2.rectangle(stitched_image, (background_x, background_y), (background_x + background_width, background_y + background_height), background_color, -1)
    
    border_size = 8
    stitched_image_with_border = cv2.copyMakeBorder(stitched_image, border_size, border_size, border_size, border_size, cv2.BORDER_CONSTANT, value=border_color)

    cv2.putText(stitched_image_with_border, text, (text_x, text_y), font, font_scale, font_color, font_thickness)
    cv2.imwrite(output_path, stitched_image_with_border)

def extract_bounding_box_images(input_image_path, output_folder):
    from scripts.file_utils import get_latest_folder
    
    image_name = os.path.splitext(os.path.basename(input_image_path))[0]
    original_image = cv2.imread(input_image_path)
    height, width, _ = original_image.shape

    latest_folder = get_latest_folder('runs/detect')
    txt_file_path = os.path.join(latest_folder, 'labels', f"{image_name}.txt")

    with open(txt_file_path, 'r') as file:
        lines = file.readlines()

    for idx, line in enumerate(lines):
        class_id, x_center_norm, y_center_norm, width_norm, height_norm = map(float, line.split())
        
        x_center = int(x_center_norm * width)
        y_center = int(y_center_norm * height)
        box_width = int(width_norm * width)
        box_height = int(height_norm * height)
        
        x1 = max(0, int(x_center - box_width / 2))
        y1 = max(0, int(y_center - box_height / 2))
        x2 = min(width, int(x_center + box_width / 2))
        y2 = min(height, int(y_center + box_height / 2))
        
        bounding_box_image = original_image[y1:y2, x1:x2]
        
        output_image_path = os.path.join(output_folder, f'bounding_box_{idx}.jpg')
        cv2.imwrite(output_image_path, bounding_box_image)

        print(f"Bounding box {idx} saved at {output_image_path}")