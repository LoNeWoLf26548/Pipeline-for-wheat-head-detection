import json
from ultralytics import YOLO

with open('config.json', 'r') as f:
    config = json.load(f)

def load_models():
    plot_extraction_model_path = config['PLOT EXTRACTION MODEL PATH']
    wheat_head_model_path = config['WHEAT HEAD DETECTION PATH']
    plot_extraction_model = YOLO(plot_extraction_model_path)
    wheat_head_model = YOLO(wheat_head_model_path)
    return plot_extraction_model, wheat_head_model

def predict_plots(model, image_path):
    model.predict(source=image_path, conf=0.4, save=True, show_labels=False, show_conf=False, save_txt=True)

def predict_wheat_heads(model, folder_path):
    model.predict(source=folder_path, conf=0.2, save=True, show_labels=False, show_conf=False, save_txt=True)