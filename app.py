import os
import cv2
import numpy as np
from flask import Flask, request, jsonify
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

### 1. Endpoint: Upload and Process Video ###
@app.route('/upload', methods=['POST'])
def upload_and_process_video():
    """
    Endpoint to upload a video, process it using YOLOv8, and save the processed video.
    """
    try:
        # Check if the file is provided
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Save the uploaded file
        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(input_path)

        # Define the output path
        output_path = os.path.join(PROCESSED_FOLDER, f"processed_{file.filename}")

        # Process the video
        process_video_with_yolo(input_path, output_path)

        return jsonify({
            "message": "Video uploaded and processed successfully!",
            "processed_video_url": f"http://127.0.0.1:5001/processed/processed_{file.filename}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def process_video_with_yolo(input_path, output_path):
    """
    Process the video frame-by-frame using YOLOv8 and save the output.
    """
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Run YOLOv8 on the frame
        results = model(frame)
        annotated_frame = results[0].plot()  # Annotate frame with detections
        out.write(annotated_frame)

    cap.release()
    out.release()

### 2. Endpoint: Process Image and Get Lane Signal ###
@app.route('/process-image', methods=['POST'])
def process_image_and_get_signal():
    """
    Endpoint to process an image, determine lane signals, and return results as JSON.
    """
    try:
        # Check if the image is provided
        if 'file' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No image selected"}), 400

        # Save the uploaded image
        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(input_path)

        # Process the image
        image = cv2.imread(input_path)
        response = calculate_signals(image)

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def calculate_signals(image):
    """
    Analyze an image to determine lane signals and vehicle counts.
    """
    # Define lane polygons
    lanes = {
        "north": np.array([(258, 329), (421, 152), (463, 149), (454, 350), (259, 331)]),  # Top center lane
        "south": np.array([(7, 435), (375, 423), (316, 633), (12, 630), (4, 438)]),  # Bottom center lane
        "east": np.array([(630, 366), (565, 561), (634, 582), (632, 371)]),  # Right lane
        "west": np.array([(42, 427), (184, 306), (18, 221), (3, 234), (41, 425)]),  # Left lane
    }

    # Run YOLOv8 inference
    results = model(image)
    detections = results[0].boxes.data.tolist()  # List of bounding boxes

    # Count vehicles in each lane
    vehicle_counts = {lane: 0 for lane in lanes}
    for detection in detections:
        x1, y1, x2, y2, conf, cls = detection
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)

        for lane, polygon in lanes.items():
            if cv2.pointPolygonTest(polygon, (center_x, center_y), False) >= 0:
                vehicle_counts[lane] += 1
                break

    # Determine the lane with the green signal
    most_cars_lane = max(vehicle_counts, key=vehicle_counts.get)

    # Prepare response
    response = {
        "lane_with_green_signal": most_cars_lane,
        "vehicle_counts": vehicle_counts
    }
    return response

from flask import send_from_directory
@app.route('/processed/<filename>')
def serve_processed_video(filename):
    """
    Serve the processed video file for playback in the browser.
    """
    return send_from_directory(PROCESSED_FOLDER, filename)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
#curl -X POST -F "file=@test/images/test_image_screen_2.jpeg" http://127.0.0.1:5001/process-image
# curl -X POST -F "file=@test/test1.mp4" http://127.0.0.1:5001/upload
