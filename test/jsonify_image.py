import cv2
import numpy as np
from flask import Flask, request, jsonify
from ultralytics import YOLO

app = Flask(__name__)
model = YOLO('best.pt')  # Path to your YOLOv8 model

# Signal timing logic (initial timing for signals)
signal_timings = {"north": 30, "south": 30, "east": 30, "west": 30}

@app.route('/detect', methods=['POST'])
def detect_vehicles():
    """
    Detect vehicles from an input video frame.
    """
    try:
        # Get the uploaded frame
        file = request.files['frame']
        if not file:
            return jsonify({"error": "No frame provided"}), 400

        # Read the frame
        file_bytes = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # Run YOLOv8 inference
        results = model(frame)

        # Count vehicles in each direction (mock example based on bounding box positions)
        counts = {"north": 0, "south": 0, "east": 0, "west": 0}
        for box in results[0].boxes.data.tolist():
            x1, y1, x2, y2, _, _ = box
            if y1 < frame.shape[0] // 2:  # Example logic for vehicle positions
                counts["north"] += 1
            else:
                counts["south"] += 1

        # Adjust signal timings based on vehicle counts
        adjust_signal_timings(counts)

        # Return vehicle counts and bounding boxes
        return jsonify({"counts": counts, "signal_timings": signal_timings})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def adjust_signal_timings(counts):
    """
    Adjust signal timings based on vehicle counts.
    """
    total_cars = sum(counts.values())
    for direction in counts:
        signal_timings[direction] = int((counts[direction] / total_cars) * 120)  # 120 seconds total

@app.route('/signal-status', methods=['GET'])
def get_signal_status():
    """
    Get the current signal timings.
    """
    return jsonify({"signal_timings": signal_timings})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
