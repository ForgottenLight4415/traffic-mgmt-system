import cv2
import numpy as np
from ultralytics import YOLO

# Global variables for AOI selection
drawing = False  # True when the mouse is pressed
polygon_points = []  # Store the polygon points
image = None  # Placeholder for the image


def draw_polygon(event, x, y, flags, param):
    """
    Mouse callback function to capture points and draw the polygon interactively.
    """
    global drawing, polygon_points, image

    if event == cv2.EVENT_LBUTTONDOWN:  # Start drawing the polygon
        drawing = True
        polygon_points.append((x, y))  # Add point
        cv2.circle(image, (x, y), 5, (0, 0, 255), -1)  # Mark the point
        if len(polygon_points) > 1:
            cv2.line(image, polygon_points[-2], polygon_points[-1], (255, 255, 255), 2)  # Draw line
        cv2.imshow("Draw Polygon", image)

    elif event == cv2.EVENT_RBUTTONDOWN:  # Finish polygon (Right mouse button)
        if len(polygon_points) > 2:  # Ensure a valid polygon
            cv2.line(image, polygon_points[-1], polygon_points[0], (255, 255, 255), 2)  # Close the polygon
            cv2.imshow("Draw Polygon", image)
        print("Polygon completed!")
        drawing = False


def interactive_polygon_tool(image_path):
    """
    Allow the user to draw a polygon on an image interactively.
    Returns the coordinates of the polygon points.
    """
    global polygon_points, image
    image = cv2.imread(image_path)  # Load the image
    polygon_points = []  # Reset points

    cv2.imshow("Draw Polygon", image)
    cv2.setMouseCallback("Draw Polygon", draw_polygon)

    print("Left-click to add points. Right-click to close the polygon.")
    print("Press 'q' to save and exit.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return polygon_points


def is_inside_polygon(point, polygon):
    """
    Check if a point is inside a polygon.
    """
    polygon_array = np.array(polygon, dtype=np.int32)
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [polygon_array], 255)
    return mask[point[1], point[0]] == 255


# Load the YOLOv8 model
model = YOLO('../best.pt')  # Replace 'best.pt' with the path to your YOLOv8 model

# Path to the test image
image_path = "test3.jpg"  # Replace with your image path

# Step 1: Select AOI using the interactive tool
polygon_coordinates = interactive_polygon_tool(image_path)
print("Polygon Coordinates:", polygon_coordinates)

# Step 2: Detect objects with YOLO
image = cv2.imread(image_path)
results = model(image)

# Vehicle classes (modify as needed)
vehicle_classes = ['car', 'bus', 'truck', 'motorbike']
vehicle_count = {vehicle: 0 for vehicle in vehicle_classes}

# Step 3: Annotate and count detections within AOI
for box in results[0].boxes.data.tolist():  # Iterate through detected objects
    x1, y1, x2, y2, conf, cls = box
    conf = float(conf)
    cls_name = model.names[int(cls)]

    center_x = int((x1 + x2) / 2)
    center_y = int((y1 + y2) / 2)

    # Check if the detection is inside the AOI
    if is_inside_polygon((center_x, center_y), polygon_coordinates):
        if cls_name in vehicle_classes:  # Count only specified vehicle classes
            vehicle_count[cls_name] += 1

            # Draw bounding box and label for objects inside AOI
            cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 255), 2)  # White bounding box
            label = f"{cls_name} {conf:.2f}"
            (label_width, label_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(
                image,
                (int(x1), int(y1) - label_height - baseline),
                (int(x1) + label_width, int(y1)),
                (0, 0, 255),  # Red background for label
                -1,
            )
            cv2.putText(
                image,
                label,
                (int(x1), int(y1) - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),  # White text
                2,
            )

# Step 4: Draw AOI on the image
cv2.polylines(image, [np.array(polygon_coordinates, dtype=np.int32)], isClosed=True, color=(0, 255, 0), thickness=3)

# Step 5: Print detection results within AOI
print("Detections within AOI:")
for vehicle, count in vehicle_count.items():
    print(f"{vehicle}: {count}")

# Step 6: Display the results
cv2.imshow("YOLOv8 Detection with AOI", image)
cv2.waitKey(0)  # Wait for a key press to close the image window
cv2.destroyAllWindows()

# Optional: Save the annotated image
cv2.imwrite("images/final/north_op.jpg", image)
