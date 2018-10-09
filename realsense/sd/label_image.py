# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import numpy as np
import tensorflow as tf
import os
import cv2
import time

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
model_file_under = "/Users/sho/PycharmProjects/PathPlanning/realsense/sd/green/retrained_graph_green_under.pb"
label_file_under = "/Users/sho/PycharmProjects/PathPlanning/realsense/sd/green/retrained_labels_under.txt"
model_file_middle = "/Users/sho/PycharmProjects/PathPlanning/realsense/sd/green/retrained_graph_green_middle.pb"
label_file_middle = "/Users/sho/PycharmProjects/PathPlanning/realsense/sd/green/retrained_labels_middle.txt"
model_file_up= "/Users/sho/PycharmProjects/PathPlanning/realsense/sd/green/retrained_graph_green_up.pb"
label_file_up = "/Users/sho/PycharmProjects/PathPlanning/realsense/sd/green/retrained_labels_up.txt"
input_height = 299
input_width = 299
input_mean = 0
input_std = 200
input_layer = "Placeholder"
output_layer = "final_result"


class StandingDetection:
    def __init__(self):
        pass

    def load_graph(self, model_file):
        graph = tf.Graph()
        graph_def = tf.GraphDef()

        with open(model_file, "rb") as f:
            graph_def.ParseFromString(f.read())
        with graph.as_default():
            tf.import_graph_def(graph_def)

        return graph

    def read_tensor_from_image_file(self, file_name,
                                    input_height=299,
                                    input_width=299,
                                    input_mean=0,
                                    input_std=255):
        input_name = "file_reader"
        output_name = "normalized"
        file_reader = tf.read_file(file_name, input_name)
        if file_name.endswith(".png"):
            image_reader = tf.image.decode_png(
                file_reader, channels=3, name="png_reader")
        elif file_name.endswith(".gif"):
            image_reader = tf.squeeze(
                tf.image.decode_gif(file_reader, name="gif_reader"))
        elif file_name.endswith(".bmp"):
            image_reader = tf.image.decode_bmp(file_reader, name="bmp_reader")
        else:
            image_reader = tf.image.decode_jpeg(
                file_reader, channels=3, name="jpeg_reader")
        float_caster = tf.cast(image_reader, tf.float32)
        dims_expander = tf.expand_dims(float_caster, 0)
        resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
        normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
        sess = tf.Session()
        result = sess.run(normalized)

        return result

    def load_labels(self, label_file):
        label = []
        proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
        for l in proto_as_ascii_lines:
            label.append(l.rstrip())
        return label

    def read_tensor_from_numpy_image(self, image):
        tfImage = np.array(image)[:, :, 0:3]
        float_caster = tf.cast(tfImage, tf.float32)
        dims_expander = tf.expand_dims(float_caster, 0)
        resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
        normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
        sess = tf.Session()
        result = sess.run(normalized)
        return result

    def detect(self, image):
        try:
            type = image[1]
            if type == 0:
                model_file = model_file_under
                label_file = label_file_under
            elif type == 1:
                model_file = model_file_middle
                label_file = label_file_middle
            else:
                model_file = model_file_up
                label_file = label_file_up
            sd = StandingDetection()
            graph = sd.load_graph(model_file)
            t = self.read_tensor_from_numpy_image(image[0])
            input_name = "import/" + input_layer
            output_name = "import/" + output_layer
            input_operation = graph.get_operation_by_name(input_name)
            output_operation = graph.get_operation_by_name(output_name)
            with tf.Session(graph=graph) as sess:
                results = sess.run(output_operation.outputs[0], {
                    input_operation.outputs[0]: t
                })
            results = np.squeeze(results)
            top_k = results.argsort()[-5:][::-1]
            labels = sd.load_labels(label_file)

            ret = []
            for i in top_k:
                ret.append((labels[i], results[i]))
                print(type, (labels[i], results[i]))
            ret.sort(key=lambda x: x[1], reverse=True)
            return ret[0][0]
        except Exception as error:
            print(str(error))
            return 'fallendown'


if __name__ == "__main__":
    path = input()
    img = cv2.imread(path)
    orgHeight, orgWidth = img.shape[:2]
    size = (int(orgHeight * 0.9), int(orgWidth * 0.9))
    halfImg = cv2.resize(img, size)
    sd = StandingDetection()
    print(sd.detect(halfImg))
