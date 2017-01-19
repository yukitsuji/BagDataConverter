#!/usr/bin/env python

import sys
import os
import rospy
import numpy as np
import cv2
import pcl
import sensor_msgs.point_cloud2 as pc2
from sensor_msgs.msg import Image, PointCloud2
from cv_bridge import CvBridge

save_path = None

def img_loader_1(image_msg):
    bridge = CvBridge()
    camera_img_1 = bridge.imgmsg_to_cv2(image_msg, "bgr8")
    timestamp = image_msg.header.stamp.secs + ((image_msg.header.stamp.nsecs + 0.0) / 1000000000)
    save_image(camera_img_1, timestamp, save_path, '1')


def save_image(img, timestamp, path, sfx):
    cv2.imwrite(path + '/camera_' + sfx + '_' + "{:.5f}".format(timestamp) + '.png', img)

def rosbag_data_extract_sample():
    global save_path
    try:
        save_path = sys.argv[1]
        topic = sys.argv[2]
    except Exception, e:
        sys.exit("Please specify the save path. Example: rosbag_data_extract_unsync.py /media/0/output/")

    node_name = "get_%s_and_convert_to_RGB_Image" % topic
    rospy.init_node('rosbag_data_extract_unsync', anonymous=True)

    rospy.Subscriber(topic, Image, img_loader_1)
    rospy.spin()

if __name__ == '__main__':
    rosbag_data_extract_sample()
