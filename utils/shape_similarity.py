import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def find_bounding_rect(image):
    # Convert to grayscale
    

    # Apply thresholding
    _, thresh = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)

    # Find the coordinates of non-zero points
    points = np.column_stack(np.where(thresh.transpose() == 0))

    # Compute the bounding rectangle
    x, y, w, h = cv2.boundingRect(points)

# Draw rectangle on the image (for visualization)
    return x, y, w, h



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



def resize_to_match(image1, image2):
    _, thresholded1 = cv2.threshold(image1, 200, 255, cv2.THRESH_BINARY_INV)
    _, thresholded2 = cv2.threshold(image2, 200, 255, cv2.THRESH_BINARY_INV)

    # Get bounding box for cropping
    x1, y1, w1, h1 = find_bounding_rect(image1)
    x2, y2, w2, h2 = find_bounding_rect(image2)

    # Crop images
    cropped1 = thresholded1[y1:y1+h1, x1:x1+w1]
    cropped2 = thresholded2[y2:y2+h2, x2:x2+w2]
    
    # Resize second image to match first
    resized_cropped1 = cv2.resize(cropped1, (w2, h2))
    return resized_cropped1, cropped2

def compare_shapes(shape1, shape2):
    
    # Calculate similarity
    total_shape_pixels = np.count_nonzero(shape1 | shape2)
    similarity = (np.count_nonzero(shape1 & shape2)) / total_shape_pixels

    return similarity


def calculate_accuracy(task_name, source_path, response_path):
  image_path_source = source_path + '/' + task_name + '.jpg'
  image_path_response = response_path + '/' + task_name + '.jpg'
  print(image_path_response, image_path_source)
  assert os.path.exists(image_path_source) and os.path.exists(image_path_response)


  image1 = cv2.imread(image_path_source, cv2.IMREAD_GRAYSCALE)
  image2 = cv2.imread(image_path_response, cv2.IMREAD_GRAYSCALE)
  try:
    shape1_1, shape2_1 = resize_to_match(image1, image2)
    shape2_2, shape1_2 = resize_to_match(image2, image1)
  except:
    print('Error for', task_name)

  similarity_score = max(compare_shapes(shape1_1, shape2_1), compare_shapes(shape2_2, shape1_2))
  if similarity_score > 0.9:
    return True
  else:
    return None