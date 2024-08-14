import os
import cv2
import re
from openpyxl import Workbook
from openpyxl.styles import Alignment

def read_output_images(folder_path):
    images = {}
    for filename in os.listdir(folder_path):
        if filename.endswith('.png'):
            match = re.match(r"tile_(\d+)_(\d+)\.png", filename)
            if match:
                row = int(match.group(1))
                col = int(match.group(2))
                img_path = cv2.imread(os.path.join(folder_path, filename))
                images[(row, col)] = img_path
    return images

def count_rows_in_txt_files(labels_folder):
    total_rows = 0
    for txt_file in os.listdir(labels_folder):
        if txt_file.endswith('.txt'):
            with open(os.path.join(labels_folder, txt_file), 'r') as file:
                total_rows += sum(1 for line in file)
    return total_rows

def create_excel_file(file_name, data):
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "Data"

    headers = ["PLOT_ID", "COUNT"]
    ws.append(headers)

    for row in data:
        ws.append(row)

    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        ws.column_dimensions[column].width = adjusted_width
        for cell in col:
            cell.alignment = Alignment(horizontal='center', vertical='center')

    wb.save(file_name)
    print(f"EXCEL FILE SAVED AS: {file_name}")