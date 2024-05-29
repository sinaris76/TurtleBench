import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def find_bounding_rect(image):

    _, thresh = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)
    points = np.column_stack(np.where(thresh.transpose() == 0))
    x, y, w, h = cv2.boundingRect(points)
    return x, y, w, h

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
  image_path_source = os.path.join(source_path, task_name+'.jpg')
  image_path_response = os.path.join(response_path, task_name + '.jpg')

  assert os.path.exists(image_path_source) and os.path.exists(image_path_response)


  image1 = cv2.imread(image_path_source, cv2.IMREAD_GRAYSCALE)
  image2 = cv2.imread(image_path_response, cv2.IMREAD_GRAYSCALE)
  try:
    shape1_1, shape2_1 = resize_to_match(image1, image2)
    shape2_2, shape1_2 = resize_to_match(image2, image1)
  except:
    print('Error for', task_name)
    return False

  similarity_score = max(compare_shapes(shape1_1, shape2_1), compare_shapes(shape2_2, shape1_2))
  if similarity_score > 0.9:
    return True
  else:
    return False