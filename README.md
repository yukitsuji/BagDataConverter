# BagDataConverter
Bag Data Converter  from Image Topic to RGB Image, from PointClound2 to PCD

# Movie
[![ScreenShot](http://img.youtube.com/vi/oejMGJrsObo/0.jpg)](https://www.youtube.com/watch?v=oejMGJrsObo&feature=youtu.be)


# How To Run Code

```bash
# After setting like Autoware(https://github.com/CPFL/Autoware) ver Indigo, Ubuntu 14.04
# ROS package for indigo
sudo apt-get install ros-indigo-desktop-full ros-indigo-nmea-msgs ros-indigo-nmea-navsat-driver ros-indigo-sound-play ros-indigo-jsk-visualization ros-indigo-grid-map
sudo apt-get install ros-indigo-controller-manager ros-indigo-ros-control ros-indigo-ros-controllers ros-indigo-gazebo-ros-control ros-indigo-sicktoolbox ros-indigo-sicktoolbox-wrapper ros-indigo-joystick-drivers ros-indigo-novatel-span-driver
sudo apt-get install libnlopt-dev freeglut3-dev qtbase5-dev libqt5opengl5-dev libssh2-1-dev libarmadillo-dev libpcap-dev gksu libgl1-mesa-dev
sudo apt-get install ros-indigo-velodyne

# OpenCV(python)

# pcl
sudo apt-get update libusb-1.0-0-dev libusb-dev libudev-dev mpi-default-dev openmpi-bin openmpi-common libflann1.8 libflann-dev libeigen3-dev libboost-all-dev libvtk5.10-qt4 libvtk5.10 libvtk5-dev libqhull* libgtest-dev freeglut3-dev pkg-config
sudo apt-get install libxmu-dev libxi-dev mono-complete qt-sdk openjdk-8-jdk openjdk-8-jre
git clone https://github.com/PointCloudLibrary/pcl.git
cd pcl
mkdir release
cd release
cmake -DCMAKE_BUILD_TYPE=None -DCMAKE_INSTALL_PREFIX=/usr \
      -DBUILD_GPU=ON -DBUILD_apps=ON -DBUILD_examples=ON \
      -DCMAKE_INSTALL_PREFIX=/usr ..
make
sudo make install

# python pcl
git clone https://github.com/strawlab/python-pcl.git
sudo python setup.py install

cd ~
git clone https://github.com/yukitsuji/BagDataConverter.git
cd ~/BagDataConverter/src
catkin_init_workspace
cd ..
catkin_make -DCMAKE_BUILD_TYPE=Release
source ./devel/setup.bash
./run  
```
# Note
If you change output directory under already checking box, please uncheck, and then check it.  
This is for changing output directory that extract images or pcd.  

![png](https://github.com/yukitsuji/BagDataConverter/blob/master/image_for_readme/output_dir.png)


# Prerequirement Packages
Same as Autoware <https://github.com/CPFL/Autoware>  
Ros version: Indigo  
Ubuntu: 14.04
