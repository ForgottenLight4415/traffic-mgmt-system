import cv2
import numpy as np

# Initialize global variables
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

# Example usage
image_path = "test4.jpeg"  # Replace with your image path
polygon_coordinates = interactive_polygon_tool(image_path)

# Output the polygon coordinates
print("Polygon Coordinates:", polygon_coordinates)
