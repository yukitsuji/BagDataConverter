#!/usr/bin/env python
import argparse
import cgi
import h5py

import os
import sys
import subprocess
import random
import rosbag
from cv_bridge import CvBridge
import numpy as np
import stat
import subprocess
import time

import caffe
from caffe.proto import caffe_pb2 
"""
def load_caffemodel(args):
    if args.gpu_id:
        caffe.set_device(int(args.gpu_id))
        caffe.set_mode_gpu()

    net = caffe.Net(args.deploy_prototxt,
              args.weight,
              caffe.TRAIN)

    transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
    transformer.set_transpose('data', (2, 0, 1))
    transformer.set_mean('data', np.array([104,117,123])) # mean pixel
    transformer.set_raw_scale('data', 255)  # the reference model operates on images in [0,255] range instead of [0,1]
    transformer.set_channel_swap('data', (2,1,0))  # the reference model has channels in BGR order instead of RGB
    image_resize = 300
    net.blobs['data'].reshape(1,3,image_resize,image_resize)

    image = caffe.io.load_image('examples/images/fish-bike.jpg')
    #
    # transformed_image = transformer.preprocess('data', image)
    # net.blobs['data'].data[...] = transformed_image
    #
    # # Forward pass.
    # detections = net.forward()['detection_out']
"""

def create_savedir(args):
    random_value = random.randint(0, 100000000000000000)
    save_dir = "/tmp/image/" + str(random_value)
    p1 = subprocess.check_call(['mkdir', save_dir])
    return save_dir

def create_topiclist(args):
    topic_list = []
    if args.image_topic:
        topic_list.append(args.image_topic)
    if args.caninfo_topic:
        topic_list.append(args.caninfo_topic)
    if topic_list == []:
        topic_list = [None]
    return topic_list

def create_brake_dataset(args, topic_list, output_file):
    sys.stderr.write("Create H5 file {}\n".format(output_file))
    image_dataset = None
    brake_dataset = None
    index = 0

    image = None
    images = None
    im_shape = None
    recent_brakepress = 0
    batch_size = int(args.h5_batch)
    prev_index = 0

    with rosbag.Bag(args.bagfile) as bag:
        num_image =  int(bag.get_type_and_topic_info()[1][args.image_topic][1])
        iter_num = int(np.ceil(num_image / batch_size))

        with h5py.File(output_file, "w") as h5file: # "data", "label"
            brake_dataset = h5file.create_dataset("label",shape=(num_image, ), compression="gzip")
            for topic, msg, t in bag.read_messages(topics=topic_list):
                if msg.header.frame_id == "/can":
                    recent_brakepress = msg.bbrakepress
                    recent_brakepedal = msg.brakepedal

                if msg.header.frame_id == "camera":
                    start = time.time()
                    bridge = CvBridge()
                    image = bridge.imgmsg_to_cv2(msg, "bgr8").astype(np.float32)
                    image /= image.max()
                    if image_dataset is None:
                        im_shape = image.shape
                        images = np.zeros((batch_size, im_shape[0], im_shape[1], im_shape[2]))
                        brakes = np.zeros((batch_size,))
                        image_dataset = h5file.create_dataset("data",
                                        shape=(num_image, im_shape[0], im_shape[1], im_shape[2]),
                                        dtype="float32",
                                        compression="gzip")

                    images[index % batch_size] = image
                    brakes[index % batch_size] = recent_brakepress
                    if (index % batch_size == (batch_size - 1) or index == (num_image - 1)):
                        image_dataset[prev_index : (index + 1)] = images[:index + 1 -prev_index]
                        brake_dataset[prev_index : (index + 1)] = brakes[:index + 1 -prev_index]
                        prev_index = index + 1
                        print "### saved ###"

                    image = None
                    recent_brakepress = None
                    index += 1
            h5file.flush()

def create_solver(args):
    solver = caffe_pb2.SolverParameter()

    # Train Parameters
    solver.random_seed = 52 #0xCAFFE
    solver.train_net = args.train_prototxt
    solver.max_iter = 1000 # 100000
    solver.type = "SGD"
    solver.base_lr = int(args.base_lr)
    solver.momentum = 0.9
    solver.weight_decay = 0.0005
    solver.lr_policy = 'inv'
    solver.gamma = 0.1

    solver.display = 100 # 1000
    solver.snapshot = 500
    solver.snapshot_prefix = args.snapshot

    if args.device_id:
        solver.device_id = int(args.device_id)
        solver.solver_mode = caffe_pb2.SolverParameter.GPU
    else:
        solver.solver_mode = caffe_pb2.SolverParameter.CPU

    # Test Parameters
    # solver.test_net.append(test_net_path)
    # solver.test_interval = 500
    # solver.test_iter.append(100)

    with open(args.solver_prototxt, 'w') as f:
        f.write(str(solver))

"""
def deploy_network():
    if args.gpu_id:
        caffe.set_device(args.gpu_id)
        caffe.set_mode_gpu()

    net = caffe.Net(args.deploy_prototxt,
              args.weight,
              caffe.TRAIN)

    transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
    transformer.set_transpose('data', (2, 0, 1))
    transformer.set_mean('data', np.array([104,117,123])) # mean pixel
    transformer.set_raw_scale('data', 255)  # the reference model operates on images in [0,255] range instead of [0,1]
    transformer.set_channel_swap('data', (2,1,0))  # the reference model has channels in BGR order instead of RGB
    image_resize = 300
    net.blobs['data'].reshape(1,3,image_resize,image_resize)

    image = caffe.io.load_image('examples/images/fish-bike.jpg')
"""

def create_jobfile(args):
    job_file = args.save_dir + "/exe.sh"
    with open(job_file, "w") as f:
        f.write("cd {}\n".format("$HOME/caffe"))
        if args.mode == "train":
            f.write("./build/tools/caffe train \\\n")
            f.write("--solver='{}' \\\n".format(args.solver_prototxt))
        else:
            f.write("./build/tools/caffe test  \\\n")
            f.write("--model='{}' \\\n".format(args.deploy_prototxt))

        if args.weight:
            f.write("--weights='{}' \\\n".format(args.weight))

        f.write("--gpu {}\n".format(args.gpu_id))

    os.chmod(job_file, stat.S_IRWXU)
    return job_file

def train_caffemodel(args):
    # create_solver(args)
    job_file = create_jobfile(args)
    subprocess.call(job_file, shell=True)

def deploy_caffemodel(args):
    job_file = create_jobfile(args)
    subprocess.call(job_file, shell=True)

def check_arguments(args):
    if not (args.theme == "brake" or args.theme == "ssd"):
        sys.stderr.write("Please selece theme from 'brake' and 'ssd'\n")
        sys.exit()
    if args.solver_prototxt is None:
        sys.stderr.write("Please assign solver Prototxt\n")
        sys.exit()
    if not (args.mode == "train" or args.mode == "test"):
        sys.stderr.write("Mode is 'train' or 'test'\n")
        sys.exit()
    if args.mode == "train":
        if args.solver_prototxt is None:
            sys.stderr.write("Please set solver prototxt when training\n")
            sys.exit()
    if args.mode == "test":
        if args.deploy_prototxt is None:         
            sys.stderr.write("Please set deploy prototxt when testing\n")
            sys.exit()
        if args.weight is None:
            sys.stderr.write("Please set weight when testing\n")
            sys.exit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='upload bagfile and convert to h5 file')
    parser.add_argument("bagfile", help="Bag file")
    parser.add_argument("--theme", help="select training theme from 'brake' and 'ssd'", default=None)
    parser.add_argument("--image_topic", help="image topic to training", default=None)
    parser.add_argument("--caninfo_topic", help="CanInfo topic to training", default=None)
    parser.add_argument("--output_file", help="output h5 file", default="/tmp/tmp.h5")
    parser.add_argument("--h5_batch", help="batch size for saving h5", default=50)


    parser.add_argument("--gpu_id", help="Use GPU or not", default=None)
    parser.add_argument("--deploy_prototxt", help="prototxt of model", default=None)
    parser.add_argument("--train_prototxt", help="prototxt of training model", default=None)
    parser.add_argument("--weight", help="weight of model network", default=None)
    parser.add_argument("--solver_prototxt", help="solver prototxt", default=None)
    parser.add_argument("--snapshot", help="name of snapshot", default="brake")

    parser.add_argument("--base_lr", help="base learning rate", default=0.001)
    parser.add_argument("--save_dir", help="save directory", default="./")
    parser.add_argument("--mode", help="Network mode", default="train")

    parser.add_argument("--create", help="Create h5 file", default=True)
    args = parser.parse_args()

    check_arguments(args)

    save_dir = args.save_dir #create_savedir(args.save_dir)
    topic_list = create_topiclist(args)
    if args.theme == "brake":
        if args.create == True:
            create_brake_dataset(args, topic_list, args.output_file)
        if args.mode == "train":
            train_caffemodel(args)

        elif args.mode == "test":
            deploy_caffemodel(args)

    if args.theme == "ssd":
        create_ssd_dataset(args, topic_list)
