import cv2
from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO('../best.pt')  # Replace 'best.pt' with the path to your downloaded model file

# Open the video file
video_path = 'atrium_video.avi'  # Replace with the path to your input video file
cap = cv2.VideoCapture(video_path)

# Get video properties
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec for .avi output
out = cv2.VideoWriter('output_video.avi', fourcc, fps, (width, height))

# Process the video frame by frame
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLOv8 inference on the frame
    results = model(frame)

    # Annotate the frame with detection results
    annotated_frame = results[0].plot()  # Add bounding boxes and labels to the frame

    # Write the annotated frame to the output video
    out.write(annotated_frame)

    # Display the frame (optional for debugging, can be commented out)
    cv2.imshow('YOLOv8 Inference', annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit early
        break

# Release resources
cap.release()
out.release()
cv2.destroyAllWindows()

print("Processing complete. The output video is saved as 'output_video.avi'")
