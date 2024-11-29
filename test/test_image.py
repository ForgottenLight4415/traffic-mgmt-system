import cv2
from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO('../best.pt')  # Replace 'best.pt' with the path to your YOLOv8 model

# Path to the test image
image_path = "test4.jpeg"  # Replace with your image file path

# Read the image
image = cv2.imread(image_path)

# Run YOLOv8 inference
results = model(image)

# Print detection results
print("Detections:")
for box in results[0].boxes.data.tolist():  # Iterate through detected objects
    x1, y1, x2, y2, conf, cls = box
    print(f"Class: {model.names[int(cls)]}, Confidence: {conf:.2f}, Box: [{x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f}]")

# Draw the results on the image
annotated_image = results[0].plot()

# Show the annotated image
cv2.imshow("YOLOv8 Detection", annotated_image)
cv2.waitKey(0)  # Wait for a key press to close the image window
cv2.destroyAllWindows()

# Optional: Save the annotated image
cv2.imwrite("annotated_image.jpg", annotated_image)
