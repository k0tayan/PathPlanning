from datetime import datetime

import tensorflow as tf

import numpy as np
import os

path = os.path.dirname(os.path.abspath(__file__))
filename = path + '/model2.pb'  # model1.pb 水増しなし model2.pb 水増しあり
labels_filename = path + '/labels.txt'

network_input_size = 227

output_layer = 'loss:0'
input_node = 'Placeholder:0'

graph_def = tf.GraphDef()
labels = []


def initialize():
    print('Loading model...', end=''),
    with tf.gfile.FastGFile(filename, 'rb') as f:
        graph_def.ParseFromString(f.read())
        tf.import_graph_def(graph_def, name='')
    print('Success!')
    print('Loading labels...', end='')
    with open(labels_filename, 'rt') as lf:
        global labels
        labels = [l.strip() for l in lf.readlines()]
    print(len(labels), 'found. Success!')


def log_msg(msg):
    # print("{}: {}".format(datetime.now(),msg))
    pass


def extract_bilinear_pixel(img, x, y, ratio, xOrigin, yOrigin):
    xDelta = (x + 0.5) * ratio - 0.5
    x0 = int(xDelta)
    xDelta -= x0
    x0 += xOrigin
    if x0 < 0:
        x0 = 0
        x1 = 0
        xDelta = 0.0
    elif x0 >= img.shape[1] - 1:
        x0 = img.shape[1] - 1
        x1 = img.shape[1] - 1
        xDelta = 0.0
    else:
        x1 = x0 + 1

    yDelta = (y + 0.5) * ratio - 0.5
    y0 = int(yDelta)
    yDelta -= y0
    y0 += yOrigin
    if y0 < 0:
        y0 = 0
        y1 = 0
        yDelta = 0.0
    elif y0 >= img.shape[0] - 1:
        y0 = img.shape[0] - 1
        y1 = img.shape[0] - 1
        yDelta = 0.0
    else:
        y1 = y0 + 1

    # Get pixels in four corners
    bl = img[y0, x0]
    br = img[y0, x1]
    tl = img[y1, x0]
    tr = img[y1, x1]
    # Calculate interpolation
    b = xDelta * br + (1. - xDelta) * bl
    t = xDelta * tr + (1. - xDelta) * tl
    pixel = yDelta * t + (1. - yDelta) * b
    return pixel.astype(np.uint8)


def extract_and_resize(img, targetSize):
    determinant = img.shape[1] * targetSize[0] - img.shape[0] * targetSize[1]
    if determinant < 0:
        ratio = float(img.shape[1]) / float(targetSize[1])
        xOrigin = 0
        yOrigin = int(0.5 * (img.shape[0] - ratio * targetSize[0]))
    elif determinant > 0:
        ratio = float(img.shape[0]) / float(targetSize[0])
        xOrigin = int(0.5 * (img.shape[1] - ratio * targetSize[1]))
        yOrigin = 0
    else:
        ratio = float(img.shape[0]) / float(targetSize[0])
        xOrigin = 0
        yOrigin = 0
    resize_image = np.empty((targetSize[0], targetSize[1], img.shape[2]), dtype=np.uint8)
    for y in range(targetSize[0]):
        for x in range(targetSize[1]):
            resize_image[y, x] = extract_bilinear_pixel(img, x, y, ratio, xOrigin, yOrigin)
    return resize_image


def extract_and_resize_to_256_square(image):
    h, w = image.shape[:2]
    log_msg("crop_center: " + str(w) + "x" + str(h) + " and resize to " + str(256) + "x" + str(256))
    return extract_and_resize(image, (256, 256))


def crop_center(img, cropx, cropy):
    h, w = img.shape[:2]
    startx = max(0, w // 2 - (cropx // 2) - 1)
    starty = max(0, h // 2 - (cropy // 2) - 1)
    log_msg("crop_center: " + str(w) + "x" + str(h) + " to " + str(cropx) + "x" + str(cropy))
    return img[starty:starty + cropy, startx:startx + cropx]


def convert_to_nparray(image):
    # RGB -> BGR
    log_msg("Convert to numpy array")
    image = np.array(image)
    return image[:, :, (2, 1, 0)]


def predict_image(image):
    log_msg('Predicting image')
    try:
        # Convert image to numpy array
        image = convert_to_nparray(image)

        # Crop the center square and resize that square down to 256x256
        resized_image = extract_and_resize_to_256_square(image)

        # Crop the center for the specified network_input_Size
        cropped_image = crop_center(resized_image, network_input_size, network_input_size)

        tf.reset_default_graph()
        tf.import_graph_def(graph_def, name='')

        with tf.Session() as sess:
            prob_tensor = sess.graph.get_tensor_by_name(output_layer)
            predictions, = sess.run(prob_tensor, {input_node: [cropped_image]})

            result = []
            for p, label in zip(predictions, labels):
                truncated_probablity = np.float64(round(p, 8))
                if truncated_probablity > 1e-8:
                    result.append({
                        'tagName': label,
                        'probability': truncated_probablity,
                        'tagId': '',
                        'boundingBox': None})

            response = {
                'id': '',
                'project': '',
                'iteration': '',
                'created': datetime.utcnow().isoformat(),
                'predictions': result
            }

            log_msg("Results: " + str(response))
            return response

    except Exception as e:
        log_msg(str(e))
        return 'Error: Could not preprocess image for prediction. ' + str(e)
