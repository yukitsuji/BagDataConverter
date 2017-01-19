# BagDataConverter
Bag Data Converter  from Image Topic to RGB Image, from PointClound2 to PCD

# Movie
[![ScreenShot](http://img.youtube.com/vi/oejMGJrsObo/0.jpg)](https://www.youtube.com/watch?v=oejMGJrsObo&feature=youtu.be)


# How To Run Code

```bash
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
