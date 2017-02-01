#!/usr/bin/env python
import sys
import rospy
import numpy as np
import time
import matplotlib.pyplot as plt
import sensor_msgs.point_cloud2 as pc2
import cv2
import PIL.Image
from sensor_msgs.msg import Image, PointCloud2
from cv_bridge import CvBridge
from scipy import ndimage

PATH = '/home/katou01/.autoware/20150831_Center_Camera'
save_path = None
index = 0

# reads calibration file
CAMERA_EXTRINSIC_MAT = np.asmatrix(np.array(cv2.cv.Load(PATH, cv2.cv.CreateMemStorage(), "CameraExtrinsicMat")))
CAMERA_MAT = np.array(cv2.cv.Load(PATH, cv2.cv.CreateMemStorage(), "CameraMat"))
DIST_COEFF = np.transpose(np.array(cv2.cv.Load(PATH, cv2.cv.CreateMemStorage(), "DistCoeff")))
#reads image size variable
with open(PATH) as f:
    content = f.readlines()
for line in content:
    if 'ImageSize' in line:
        WIDTH=int(line[line.index('[')+1:line.index(',')])
        HEIGHT=int(line[line.index(',')+1:line.index(']')])
print "Image Size: [",WIDTH,",",HEIGHT,"]"

INV_R = np.transpose(CAMERA_EXTRINSIC_MAT[0:3, 0:3])
INV_T = -INV_R * (CAMERA_EXTRINSIC_MAT[0:3, 3])
INV_R_T=np.transpose(INV_R)
INV_T_T=np.transpose(INV_T)
SUB_MAT_SIZE=40
MAT_RATIO=3
MAX_COLOR_VAL=1

#global variables
cv_image=np.empty((HEIGHT,WIDTH))
cloud=PointCloud2()
in_callback = False
cloud_ready = False
img_ready = False

def callback():
    global in_callback
    global save_path
    in_callback=True
    curr_image=cv_image.copy()
    curr_cloud=cloud

    d_mat=np.empty((HEIGHT,WIDTH))
    d_mat[:]=np.NaN

    xyz = pc2.read_points(curr_cloud, field_names=('x','y','z'))

    t0 = time.time()

    list_x=[]
    list_y=[]
    list_z=[]

    for p in xyz:
        if p[0]>0:
            list_x.append(p[0])
            list_y.append(p[1])
            list_z.append(p[2])

    c_length=len(list_x)
    points_mat=np.empty([c_length,3])

    for i, (x, y, z) in enumerate(zip(list_x,list_y,list_z)):
        points_mat[i,0]=x
        points_mat[i,1]=y
        points_mat[i,2]=z

    for i in range(0,c_length):
        points_mat[i]=points_mat[i] * INV_R_T + INV_T_T

    tmp_x = points_mat[:,0:1] / points_mat[:,2:3]
    tmp_y = points_mat[:,1:2] / points_mat[:,2:3]

    r2 = tmp_x * tmp_x + tmp_y * tmp_y
    tmp_d= 1 + DIST_COEFF[0] * r2 + DIST_COEFF[1] * r2 * r2 + DIST_COEFF[4] * r2 * r2 * r2

    p_image_x = tmp_x * tmp_d + 2 * DIST_COEFF[2] * tmp_x * tmp_y + DIST_COEFF[3] * (r2 + 2 * tmp_x * tmp_x)
    p_image_y = tmp_y * tmp_d + DIST_COEFF[2] * (r2 + 2 * tmp_y * tmp_y) + 2 * DIST_COEFF[3] * tmp_x * tmp_y
    p_image_x = CAMERA_MAT[0, 0] * p_image_x + CAMERA_MAT[0, 2]
    p_image_y = CAMERA_MAT[1, 1] * p_image_y + CAMERA_MAT[1, 2]

    p_x = p_image_x + 0.5
    p_x=p_x.astype(int)
    p_y = p_image_y + 0.5
    p_y=p_y.astype(int)
    p_z = points_mat[:,2:3]*100 # in cm

    for i_x, i_y, i_z in zip(p_x,p_y,p_z):
        if 0 <= i_x < WIDTH and 0 <= i_y < HEIGHT:
            d_mat[i_y,i_x]=i_z

    t1 = time.time()
    print "Projection Time: ", t1-t0

    to_distance_image(d_mat,curr_image)
    in_callback = False
    reset_flags()

def to_distance_image(img_mat,curr_image):
    global index
    index += 1
    h=HEIGHT
    w=WIDTH

    d_max=np.nanmax(img_mat)
    #d_max=d_max-3500  #optional. clips max distance so depth sense is more visible
    img_mat=img_mat/d_max

    new_mat=img_mat.copy()
    sub_mat_size=SUB_MAT_SIZE
    step_size=sub_mat_size/2
    mat_ratio=MAT_RATIO

    t0 = time.time()

    #Patty's interpolation implementation
    for x in range(0,w,step_size):
       for y in range(0,h,step_size):
           sub_mat=img_mat[y:y+sub_mat_size*mat_ratio,x:x+sub_mat_size].copy()
           mask=np.isnan(sub_mat)
           avg=np.ma.average(np.ma.array(sub_mat,mask=mask))
           sub_mat.fill(avg)
           new_mat[y:y+sub_mat_size*mat_ratio,x:x+sub_mat_size]=sub_mat
    t1 = time.time()
    print "Interpolation time: ", t1-t0
    new_mat[np.isnan(new_mat)] = MAX_COLOR_VAL

    d_img = PIL.Image.fromarray(plt.cm.jet_r(new_mat, bytes=True))
    # rgba_img=PIL.Image.fromarray(curr_image).convert("RGBA")
    # overlay_img = PIL.Image.blend(rgba_img,d_img, 0.5)

    timestamp = time.time()
    d_img.save(save_path + '/depth_img_%08d.jpg' % index)
    save_img = PIL.Image.fromarray(curr_image)
    save_img.save(save_path + '/rgb_img_%08d.jpg' % index)

def img_loader(image_msg):
    global cv_image
    global img_ready
    bridge = CvBridge()
    cv_image = bridge.imgmsg_to_cv2(image_msg, "bgr8")
    img_ready = True

def pc2_loader(msg):
    global cloud
    global cloud_ready
    cloud=msg
    cloud_ready = True

def reset_flags():
    global in_callback
    global cloud_ready
    global img_ready
    in_callback = False
    img_ready = False
    cloud_ready = False

def pc2_to_depth_image():
    global save_path
    rospy.init_node('pc2_to_depth_image', anonymous=True)

    try:
        save_path = sys.argv[1]
        topic = sys.argv[2]
        image = sys.argv[3]
        pointcloud = sys.argv[4]
    except Exception, e:
        sys.exit("Please specify the save path. Example: rosbag_data_extract_unsync.py /media/0/output/")

    rospy.Subscriber(image, Image, img_loader)
    rospy.Subscriber(pointcloud, PointCloud2, pc2_loader)

    r=rospy.Rate(20)
    while not rospy.is_shutdown():
        if cloud_ready and img_ready:
            callback()
        r.sleep()

if __name__ == '__main__':
    pc2_to_depth_image()
