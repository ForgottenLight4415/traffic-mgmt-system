import os
import cv2
import numpy as np
import yaml
from flask import Flask, request, jsonify, send_from_directory
from ultralytics import YOLO
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['http://localhost:4200'])

# Directories for storing uploaded files
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Load YOLO model
model = YOLO('best.pt')  # Replace with your trained YOLOv8 model path

### Endpoint to Process Images with AOI ###
import os
import cv2
import numpy as np
import yaml
from flask import Flask, request, jsonify, send_from_directory
from ultralytics import YOLO
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['http://localhost:4200'])

# Directories for storing uploaded files
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Load YOLO model
model = YOLO('best.pt')  # Replace with your trained YOLOv8 model path

### Endpoint to Process Images with AOI ###
@app.route('/upload-images', methods=['POST'])
def upload_images_and_process_aoi():
    """
    Process multiple images with AOI and return vehicle counts and the lane with the highest count.
    """
    try:
        # Check if required files are provided
        required_keys = ['north', 'south', 'east', 'west', 'config']
        for key in required_keys:
            if key not in request.files:
                return jsonify({"error": f"Missing file for {key}"}), 400

        # Save and load the AOI configuration
        aoi_file = request.files['config']
        aoi_path = os.path.join(UPLOAD_FOLDER, 'config.yaml')
        aoi_file.save(aoi_path)

        with open(aoi_path, 'r') as f:
            aoi_data = yaml.safe_load(f)

        aoi_polygon = np.array(aoi_data['config'], dtype=np.int32)

        processed_images = []
        vehicle_counts = {}

        # Process each direction
        for direction in ['north', 'south', 'east', 'west']:
            image_file = request.files[direction]
            if image_file.filename == '':
                return jsonify({"error": f"Empty file for {direction}"}), 400

            input_path = os.path.join(UPLOAD_FOLDER, f"{direction}.jpg")
            image_file.save(input_path)

            # Process the image
            processed_path, vehicle_count = process_image_with_aoi(input_path, aoi_polygon)
            vehicle_counts[direction] = vehicle_count

            processed_images.append({
                "direction": direction,
                "processed_image": f"http://127.0.0.1:5001/processed/{os.path.basename(processed_path)}",
                "vehicle_count": vehicle_count
            })

        # Find the direction with the highest vehicle count
        highest_vehicle_direction = max(vehicle_counts, key=vehicle_counts.get)

        return jsonify({
            "message": "Images processed successfully!",
            "processed_images": processed_images,
            "lane_with_highest_vehicles": highest_vehicle_direction
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def process_image_with_aoi(image_path, aoi_polygon):
    """
    Process a single image, annotate it, and count vehicles within the AOI.
    """
    image = cv2.imread(image_path)
    results = model(image)
    detections = results[0].boxes.data.tolist()
    vehicle_count = 0

    for detection in detections:
        x1, y1, x2, y2, conf, cls = detection
        cls_name = model.names[int(cls)]

        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)

        # Check if the detection is within the AOI
        if cv2.pointPolygonTest(aoi_polygon, (center_x, center_y), False) >= 0:
            vehicle_count += 1
            cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 255), 2)
            label = f"{cls_name} {conf:.2f}"
            (label_width, label_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(image, (int(x1), int(y1) - label_height - baseline), (int(x1) + label_width, int(y1)),
                          (0, 0, 255), -1)
            cv2.putText(image, label, (int(x1), int(y1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Save the annotated image
    processed_path = os.path.join(PROCESSED_FOLDER, f"processed_{os.path.basename(image_path)}")
    cv2.imwrite(processed_path, image)

    return processed_path, vehicle_count


### Serve Processed Files ###
@app.route('/processed/<filename>')
def serve_processed_file(filename):
    """
    Serve the processed image file for playback in the browser.
    """
    return send_from_directory(PROCESSED_FOLDER, filename)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)



### Serve Processed Files ###
@app.route('/processed/<filename>')
def serve_processed_file(filename):
    """
    Serve the processed image file for playback in the browser.
    """
    return send_from_directory(PROCESSED_FOLDER, filename)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
