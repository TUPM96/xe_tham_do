import tensorflow as tf
import numpy as np
import cv2
import sys

# Load the model
MODEL_PATH = '../models/saved_model'
detect_fn = tf.saved_model.load_model(MODEL_PATH)

# Simple label map
category_index = {1: {'id': 1, 'name': 'person'}}

def load_image_into_numpy_array(path):
    return np.array(cv2.imread(path))

def detect(image_path):
    image_np = load_image_into_numpy_array(image_path)
    input_tensor = tf.convert_to_tensor(image_np)
    input_tensor = input_tensor[tf.newaxis, ...]

    detections = detect_fn(input_tensor)

    boxes = detections['detection_boxes'][0].numpy()
    classes = detections['detection_classes'][0].numpy().astype(np.int32)
    scores = detections['detection_scores'][0].numpy()

    image_np_with_detections = image_np.copy()
    for i in range(min(10, boxes.shape[0])):
        if scores[i] > 0.5:
            box = boxes[i]
            y1, x1, y2, x2 = box
            h, w, _ = image_np.shape
            startY, startX, endY, endX = int(y1 * h), int(x1 * w), int(y2 * h), int(x2 * w)
            cv2.rectangle(image_np_with_detections, (startX, startY), (endX, endY), (0, 255, 255), 2)
            label = category_index[classes[i]]['name']
            cv2.putText(image_np_with_detections, f'{label}: {int(scores[i]*100)}%', 
                        (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

    cv2.imshow('Thermal Detection', image_np_with_detections)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        detect(sys.argv[1])
    else:
        print("Usage: python thermal_detect.py <image_path>")
