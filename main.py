import json, os
from scripts.image_processing import tile_image, stitch_images, overlap_plots, save_stitched_image, extract_bounding_box_images
from scripts.model_utils import load_models, predict_plots, predict_wheat_heads
from scripts.data_utils import read_output_images, count_rows_in_txt_files, create_excel_file
from scripts.file_utils import get_latest_folder, delete_non_empty_directory, move_directory, get_coords_path

with open('config.json', 'r') as f:
    config = json.load(f)

def main(input_orthomosaic_image_path, output_path):
    # Load models
    plot_extraction_model, wheat_head_model = load_models()

    # Extract image name
    image_name = os.path.splitext(os.path.basename(input_orthomosaic_image_path))[0]

    # Create necessary folders
    cropped_plots_folder = 'extracted_plots'
    output_folder_for_stitched_images = 'stitched_images'
    output_folder_for_ortho = 'Output_with_detected_plots'
    os.makedirs(cropped_plots_folder, exist_ok=True)
    os.makedirs(output_folder_for_stitched_images, exist_ok=True)
    os.makedirs(output_folder_for_ortho, exist_ok=True)

    # Predict plots
    predict_plots(plot_extraction_model, input_orthomosaic_image_path)
    
    # Store the labels of the first orthomosaic image
    path_to_coords = get_coords_path(image_name)
    with open(path_to_coords, 'r') as f:
        stored_labels = f.read()

    # Extract bounding box images
    extract_bounding_box_images(input_orthomosaic_image_path, cropped_plots_folder)

# preprocessing the plots 
    

    # Process each extracted plot
    input_image_folder = "extracted_plots"
    data = process_plots(input_image_folder, wheat_head_model, output_folder_for_stitched_images)

    # Create Excel file
    excel_file = os.path.join(output_path, "data.xlsx")
    create_excel_file(excel_file, data)

    # Recreate the labels file for overlapping plots
    temp_labels_path = 'temp_labels.txt'
    with open(temp_labels_path, 'w') as f:
        f.write(stored_labels)

    # Overlap plots on orthomosaic
    path_to_plots_folder = 'stitched_images'
    output_for_ortho = os.path.join(output_folder_for_ortho, f"{image_name}.jpg")
    overlap_plots(input_orthomosaic_image_path, temp_labels_path, path_to_plots_folder, output_for_ortho)

    # Clean up temporary directories and files
    cleanup(temp_labels_path)

    # Move output to desired location
    move_directory(output_folder_for_ortho, output_path)

    print(f"ORIGINAL ORTHO_IMAGE: {input_orthomosaic_image_path}")
    print(f"EXCEL FILE SAVED AS: {excel_file}")
    print(f"RESULT ON ORTHOMOSAIC IMAGE: {os.path.basename(output_for_ortho)}")

def process_plots(input_image_folder, model, output_folder):
    data = []
    input_image_files = sorted(os.listdir(input_image_folder), key=lambda x: os.path.getctime(os.path.join(input_image_folder, x)))

    for idx, input_image_file in enumerate(input_image_files, 1):
        input_image_path = os.path.join(input_image_folder, input_image_file)
        tiled_folder = os.path.join("DATA", "Plot_tiled", os.path.basename(input_image_path))
        tile_image(input_image_path, tiled_folder)

        predict_wheat_heads(model, tiled_folder)

        folder_for_stitching_back = get_latest_folder('runs/detect')
        if folder_for_stitching_back:
            labels_folder = os.path.join(folder_for_stitching_back, "labels")
            total_rows = count_rows_in_txt_files(labels_folder)  # This is now the wheat head count for this plot

            images = read_output_images(folder_for_stitching_back)
            stitched_image = stitch_images(images)

            if stitched_image is not None:
                output_path = os.path.join(output_folder, f"stitched_image_{input_image_file}")
                save_stitched_image(stitched_image, output_path, idx, total_rows)
                data.append([f"P_{idx}", total_rows])
            else:
                print(f"No stitched image for {input_image_file} to save.")
        else:
            print(f"No folders found in 'runs/detect' for {input_image_file}.")

        # Delete the 'runs/detect' folder after processing each plot
        delete_non_empty_directory('runs/detect')

    return data

def cleanup(temp_labels_path):
    delete_non_empty_directory("DATA/Plot_tiled")
    delete_non_empty_directory("DATA")
    delete_non_empty_directory("extracted_plots")
    delete_non_empty_directory("runs")
    delete_non_empty_directory("stitched_images")
    if os.path.exists(temp_labels_path):
        os.remove(temp_labels_path)

if __name__ == "__main__":
    input_orthomosaic_image_path = config['INPUT ORTHOMOSAIC IMAGE PATH']
    output_path = config['FINAL OUTPUT ORTHOMOSAIC IMAGE + XLXS FILE']
    main(input_orthomosaic_image_path, output_path)
