import cv2
import numpy as np

def iou(boxA, boxB):
    # Compute Intersection over Union (IoU) between two bounding boxes
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[0] + boxA[2], boxB[0] + boxB[2])
    yB = min(boxA[1] + boxA[3], boxB[1] + boxB[3])
    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = boxA[2] * boxA[3]
    boxBArea = boxB[2] * boxB[3]
    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou

# Load and preprocess the image
image = cv2.imread('house_car_image.jpg')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale for edge detection

detected_boxes = []  # List to store detected window boxes
window_count = 0  # Counter for the number of detected windows

# Iterate over different aperture sizes for edge detection
# This allows testing various settings to find the best edge detection results
for aperture in [3, 5]:
    # Apply edge detection to find boundaries
    edges = cv2.Canny(gray, 70, 80, apertureSize=aperture)
    
    # Find contours in the edge-detected image
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        area = cv2.contourArea(contour)
        # Filter contours based on area size to identify potential windows
        if area < 500 or area > 2000:
            continue

        approx = cv2.approxPolyDP(contour, 0.05 * cv2.arcLength(contour, True), True)

        # Check if the shape is roughly rectangular
        if len(approx) < 4:
            continue

        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h

        # Check if the aspect ratio is within a reasonable range for windows
        if aspect_ratio < 0.1 or aspect_ratio > 1.5:
            continue

        new_box = (x, y, w, h)

        # Ensure the new box does not overlap significantly with existing boxes
        if any(iou(new_box, box) > 0.1 for box in detected_boxes):
            continue

        window_count += 1
        detected_boxes.append(new_box)
        
        # Draw rectangle around the detected window
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # Label the window with its count
        cv2.putText(image, str(window_count), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Print the total number of detected windows
print("Number of windows:", window_count)

# Save and display the result
cv2.imwrite('windows_detected.jpg', image)  # Save the final image with detected windows
cv2.imshow("Detected Windows", image)  # Show the image
cv2.waitKey(0)  # Wait for a key press
cv2.destroyAllWindows()  # Close all OpenCV windows
