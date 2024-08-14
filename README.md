# Wheat Head Detection Pipeline

This project implements an automated system for detecting and counting wheat heads in orthomosaic images of wheat fields. It uses advanced computer vision and machine learning techniques to process large-scale aerial imagery and provide accurate wheat head counts for each plot in the field.

## Prerequisites

- Python 3.8 or higher
- CUDA-capable GPU (recommended for faster processing)

## Installation


1. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv   # For Linux
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Configuration

Before running the system, you need to configure the input and output paths in the `config.json` file. Open `config.json` and modify the following fields:

```json
{
  "INPUT ORTHOMOSAIC IMAGE PATH": "/path/to/your/input/orthomosaic.jpg",
  "FINAL OUTPUT ORTHOMOSAIC IMAGE + XLXS FILE": "/path/to/your/output/directory",
  "PLOT EXTRACTION MODEL PATH": "/path/to/your/plot detection model.pt",
  "WHEAT HEAD DETECTION PATH": "/path/to/your/wheathead detection model.pt"
}
```

Ensure that all paths are absolute and correctly point to your input image, desired output directory, and model files.

## Usage

To run the wheat head detection system, execute the following command from the project root directory:

```
python main.py
```

The system will process the input orthomosaic image, detect wheat heads, and generate the following outputs in the specified output directory:

1. An annotated orthomosaic image with detected plots
2. An Excel file (`data.xlsx`) containing wheat head counts for each plot
3. Individual images of each detected plot with wheat heads highlighted

## Output

After successful execution, you will see output messages indicating:

- The path to the original orthomosaic image
- The path to the generated Excel file
- The filename of the result orthomosaic image with detected plots

## Troubleshooting

If you encounter any issues:

1. Ensure all dependencies are correctly installed by re-running `pip install -r requirements.txt`
2. Verify that the paths in `config.json` are correct and accessible
3. Check that your input orthomosaic image is in a supported format (e.g., JPG, PNG)
4. If using a GPU, ensure that your CUDA drivers are up to date
