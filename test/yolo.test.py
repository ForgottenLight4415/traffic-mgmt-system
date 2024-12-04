import cv2
from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO('../best.pt')  # Replace 'best.pt' with the path to your trained YOLOv8 model

# Define a confidence threshold
CONFIDENCE_THRESHOLD = 0.91

# Open the input video file
video_path = 'emergency_test.mp4'  # Replace with the path to your input video file
cap = cv2.VideoCapture(video_path)

# Get video properties
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4 output
out = cv2.VideoWriter('emergency_test_output.mp4', fourcc, fps, (width, height))

# Process the video frame by frame
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLOv8 inference on the frame
    results = model(frame)

    # Filter detections based on confidence threshold
    filtered_boxes = []
    for box in results[0].boxes.data:  # YOLOv8 boxes data
        if box[4] >= CONFIDENCE_THRESHOLD:  # Confidence threshold check
            filtered_boxes.append(box)

    # Replace the original boxes with the filtered ones
    results[0].boxes.data = filtered_boxes

    # Annotate the frame with detection results using YOLO's `plot()`
    annotated_frame = results[0].plot()

    # Write the annotated frame to the output video
    out.write(annotated_frame)

    # Display the frame (optional for debugging)
    cv2.imshow('YOLOv8 Inference', annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit early
        break

# Release resources
cap.release()
out.release()
cv2.destroyAllWindows()

print("Processing complete. The output video is saved as 'output_video.mp4'")
