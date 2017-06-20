#!/usr/env/python
# -*- coding: utf-8 -*-
import os
import sys
import rosbag

"""
仕様
1. Bagfileの名前 を第一引数
2. 使用するトピックの名前のリスト を第二引数

ここで行うのは、caffeでの訓練
必要なのは、h5ファイル！

このスクリプトファイルで、最終的なh5ファイルを生成する
"""
if __name__ == '__main__':
    import rosbag
    bag = rosbag.Bag('/home/katou01/download/toyota_01_2016-11-14.bag')
    for topic, msg, t in bag.read_messages(topics=['/image_raw', '/can_info']):
        # print topic
        # print msg.header
        if topic == "/can_info":
            if msg.bbrakepress > 0:
                print msg.bbrakepress
            if msg.brakepedal:
                print msg.brakepedal

    print bag.read_messages(topics=['/can_info'])
    bag.close()

    # try:
    #     file_path = sys.argv[1]
    # except Exception, e:
    #     sys.exit("Please specify bag file. Example: get_rosbaginfo ex.bag")
    # else:
    #     rostopic_list = get_rosbagtopics(file_path)
    #     topictype_list = get_type_of_topics(file_path)
    #     for rostopic, topic_type in zip(rostopic_list, topictype_list):
    #         print(rostopic, topic_type)
