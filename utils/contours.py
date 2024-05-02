import cv2
import numpy as np
import matplotlib.pyplot as plt


def preprocess_image(image_path):
    # Load the image in grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    # Apply binary thresholding
    _, thresholded = cv2.threshold(img, 240, 255, cv2.THRESH_BINARY_INV)
    return thresholded

def plot_contour(original_image, contour, name):
  height, width = original_image.shape[:2]
  blank_image = np.zeros((height, width, 3), np.uint8)

# Draw the contour on the blank image
# -1 in the third argument indicates drawing all contours
# (255, 255, 255) is color (white in this case), and 2 is the thickness
  cv2.drawContours(blank_image, [contour], -1, (255, 255, 255), 2)

# Now use plt.imshow to display the image
  plt.imshow(cv2.cvtColor(blank_image, cv2.COLOR_BGR2RGB))
  plt.savefig(f'aacontour_{name}.png')


def find_contour(image):
    # Find contours
    
    contours, _ = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 2 and cv2.contourArea(contours[0]) / cv2.contourArea(contours[1]) < 1.1:
      contours = [contours[0]]  # Keep only the largest contour

    # Assuming the largest contour is the desired shape
    # for i, cr in enumerate(contours):
    #   plot_contour(image, cr, i)
    #   print(cv2.contourArea(cr))
    if not contours:
      return None, 0
    contour = max(contours, key=cv2.contourArea)
    contour_num = len(contours) 
    return contour, contour_num

def compare_shapes(contour1, contour2):
    # Compare two contours
    return cv2.matchShapes(contour1, contour2, cv2.CONTOURS_MATCH_I1, 0.0)

def draw_matches(img1_path, img2_path, kp1, kp2, matches):
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    # Draw the first 10 matches.
    # You can change the number of matches you wish to draw, or remove the slicing to draw all matches
    img_matches = cv2.drawMatches(img1, kp1, img2, kp2, matches[:10], None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

    # Display the image with matches
    cv2.imshow('Matches', img_matches)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


find_contour(preprocess_image('autotest/source/source_40_1.jpg'))[1]