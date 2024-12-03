import cv2
from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO('../best.pt')  # Replace 'best.pt' with the path to your YOLOv8 model

# Path to the test image
image_path = "images/east.jpeg"  # Replace with your image file path

# Read the image
image = cv2.imread(image_path)

# Run YOLOv8 inference
results = model(image)

# Vehicle classes (modify as needed)
vehicle_classes = ['car', 'bus', 'truck', 'motorbike']
vehicle_count = {vehicle: 0 for vehicle in vehicle_classes}

# Annotate and count detections
for box in results[0].boxes.data.tolist():  # Iterate through detected objects
    x1, y1, x2, y2, conf, cls = box
    conf = float(conf)
    cls_name = model.names[int(cls)]

    if conf > 0.6:  # Only consider detections with confidence > 60%
        if cls_name in vehicle_classes:  # Count only specified vehicle classes
            vehicle_count[cls_name] += 1

        # Draw bounding box and label on the image
        cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(image, f"{cls_name} {conf:.2f}", (int(x1), int(y1) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Print detection results
print("Detections:")
for vehicle, count in vehicle_count.items():
    print(f"{vehicle}: {count}")

# Show the annotated image
cv2.imshow("YOLOv8 Detection", image)
cv2.waitKey(0)  # Wait for a key press to close the image window
cv2.destroyAllWindows()

# Optional: Save the annotated image
cv2.imwrite("images/final/model_image.jpg", image)
