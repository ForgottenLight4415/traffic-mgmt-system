import os
import cv2
from flask import Flask, request, jsonify, send_file
from ultralytics import YOLO

app = Flask(__name__)

# Directories for storing uploaded and processed videos
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Load YOLO model
model = YOLO('best.pt')  # Replace with your trained YOLOv8 model path

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
            "processed_file": f"{output_path}"
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
