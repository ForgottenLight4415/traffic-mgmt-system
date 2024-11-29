import cv2
import numpy as np
from ultralytics import YOLO

# Load the YOLO model
model = YOLO('../best.pt')  # Replace with the path to your trained YOLOv8 model

# Load the input image
image_path = "test4.jpeg"
image = cv2.imread(image_path)

# Run YOLOv8 inference
results = model(image)
detections = results[0].boxes.data.tolist()  # List of bounding boxes: [x1, y1, x2, y2, confidence, class_id]

# Define lane areas as polygons (manually adjusted based on camera angle)
lanes = {
    "north": np.array([(262, 320), (459, 360), (477, 154), (419, 161), (259, 319)]),  # Top center lane
    "south": np.array([(7, 435), (375, 423), (316, 633), (12, 630), (4, 438)]),  # Bottom center lane
    "east": np.array([(481, 279), (594, 469), (634, 467), (635, 287), (483, 278)]),  # Right lane
    "west": np.array([(44, 406), (178, 312), (38, 222), (4, 264), (43, 407)]),  # Left lane
}
# lanes = {
#     "north": np.array([(214, 266), (391, 260), (247, 15), (186, 26), (215, 266)]),  # Top center lane
#     "south": np.array([(7, 435), (375, 423), (316, 633), (12, 630), (4, 438)]),  # Bottom center lane
#     "east": np.array([(481, 279), (594, 469), (634, 467), (635, 287), (483, 278)]),  # Right lane
#     "west": np.array([(3, 421), (36, 279), (4, 270), (4, 421)]),  # Left lane
# }
# Count vehicles in each lane
vehicle_counts = {lane: 0 for lane in lanes}

for detection in detections:
    x1, y1, x2, y2, conf, cls = detection
    # Calculate the center of the bounding box
    center_x = int((x1 + x2) / 2)
    center_y = int((y1 + y2) / 2)

    # Check which lane the vehicle belongs to
    for lane, polygon in lanes.items():
        if cv2.pointPolygonTest(polygon, (center_x, center_y), False) >= 0:
            vehicle_counts[lane] += 1
            break

# Decide the green signal based on vehicle counts
signal_colors = {lane: (0, 0, 255) for lane in lanes}  # Default to red
most_cars_lane = max(vehicle_counts, key=vehicle_counts.get)
signal_colors[most_cars_lane] = (0, 255, 0)  # Set the lane with the most cars to green


# Draw the lane polygons and signals on the image
def draw_lanes_and_signals(image, lanes, signal_colors):
    for lane, polygon in lanes.items():
        # Draw lane boundaries
        cv2.polylines(image, [polygon], isClosed=True, color=(255, 255, 255), thickness=2)
        # Draw the signal
        position = tuple(polygon.mean(axis=0).astype(int))  # Center of the polygon
        cv2.circle(image, position, 20, signal_colors[lane], -1)


draw_lanes_and_signals(image, lanes, signal_colors)

# Save the output image
output_path = "output_lane_signals.jpg"
cv2.imwrite(output_path, image)

# Print the lane with the green signal and vehicle counts
print(f"Lane with green signal: {most_cars_lane}")
print(f"Vehicle counts: {vehicle_counts}")
