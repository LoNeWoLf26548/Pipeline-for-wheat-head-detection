import os
import glob
import shutil

 
def get_latest_folder(path):
    folders = glob.glob(os.path.join(path, '*'))
    folders.sort(key=os.path.getctime)
    return folders[-1] if folders else None

def delete_non_empty_directory(directory):
    try:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                delete_non_empty_directory(item_path)
            else:
                os.unlink(item_path)
        os.rmdir(directory)
        print(f"Directory '{directory}' and its contents have been successfully deleted.")
    except OSError as e:
        print(f"Error: {directory} : {e.strerror}")

def move_directory(source_dir, destination_dir):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    
    for item in os.listdir(source_dir):
        source_item_path = os.path.join(source_dir, item)
        destination_item_path = os.path.join(destination_dir, item)
        if os.path.isdir(source_item_path):
            move_directory(source_item_path, destination_item_path)
        else:
            shutil.move(source_item_path, destination_item_path)
    
    os.rmdir(source_dir)
    print(f"Directory '{source_dir}' moved to '{destination_dir}' successfully.")



def get_coords_path(image_name):
    
    latest_folder_path = get_latest_folder("runs/detect")

    if latest_folder_path is None:
        return None
    
        
    labels_folder_path = os.path.join(latest_folder_path, "labels")
    coords_path = os.path.join(labels_folder_path, image_name + ".txt")
    
    if os.path.exists(coords_path):
        with open(coords_path, 'r') as file:
            lines = file.readlines()
        
        coordinates = []
        for idx, line in enumerate(lines):
            coords = map(float, line.strip().split())
            coordinates.append((idx,) + tuple(coords))
        
        sorted_coordinates = sorted(coordinates, key=lambda x: (x[1], x[2]))
        
        with open(coords_path, 'w') as file:
            for coord in sorted_coordinates:
                file.write(' '.join(map(str, coord[1:])) + '\n')
        
        return coords_path
    
    else:
        return None