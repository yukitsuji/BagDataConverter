# BagDataConverter
Bag Data Converter  from Image Topic to RGB Image, from PointClound2 to PCD

# Movie
[![ScreenShot](http://img.youtube.com/vi/oejMGJrsObo/0.jpg)](https://www.youtube.com/watch?v=oejMGJrsObo&feature=youtu.be)


# How To Run Code

```bash
# After setting like Autoware(https://github.com/CPFL/Autoware) ver Indigo, Ubuntu 14.04
# ros package / opencv(python) for converting rosbag to Image, PCD file.  
sudo apt-get install ros-indigo-desktop-full ros-indigo-nmea-msgs ros-indigo-nmea-navsat-driver ros-indigo-sound-play ros-indigo-jsk-visualization ros-indigo-grid-map
sudo apt-get install ros-indigo-controller-manager ros-indigo-ros-control ros-indigo-ros-controllers ros-indigo-gazebo-ros-control ros-indigo-sicktoolbox ros-indigo-sicktoolbox-wrapper ros-indigo-joystick-drivers ros-indigo-novatel-span-driver
sudo apt-get install libnlopt-dev freeglut3-dev qtbase5-dev libqt5opengl5-dev libssh2-1-dev libarmadillo-dev libpcap-dev gksu libgl1-mesa-dev

sudo apt-get install ros-indigo-velodyne

cd ~
git clone https://github.com/yukitsuji/BagDataConverter.git
cd ~/BagDataConverter/src
catkin_init_workspace
cd ..
catkin_make -DCMAKE_BUILD_TYPE=Release
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
