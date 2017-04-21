#include "get_Image.hpp"

static void check_arguments(int argc, char* argv[])
{
  cout << "Fuck you" << endl;
  if (argc == 3){
    cout << "correct arguments\n";
  }else{
    cout << "Please set arguments like below\n'rosrun dataprocess get_Image'\n";
    exit(EXIT_FAILURE);
  }
}

void SaveImage::save_image(const sensor_msgs::Image& msg)
{
  cv_bridge::CvImagePtr cv_image;
  stringstream ss;
  ss << msg.header.stamp;
  // cout << save_path_.size() << endl;
  // cout << save_path_[save_path_.size() - 1] << endl;
  // if save_path_[save_path_.size() - 1]

  try
  {
    cv_image = cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::BGR8);
  }
  catch (cv_bridge::Exception& e)
  {
    ROS_ERROR("cv_bridge exeption: %s", e.what());
  }
  cv::imwrite(save_path_ + ss.str() + ".jpg", cv_image->image);
}

void SaveImage::sub_image(int argc, char* argv[])
{
  ros::init(argc, argv, "Image_Subscriber");
  ros::NodeHandle n;
  ros::Subscriber sub = n.subscribe(topic_name_, 1, &SaveImage::save_image, this);
  ros::spin();
}

int main(int argc, char* argv[])
{
  check_arguments(argc, argv);
  SaveImage si;
  string path = argv[1];
  if (path[path.size() - 1] == '/'){
    cout << "OK\n";
    path.erase(path.begin() + path.size()-1);
    cout << path;
  }
  si.save_path_ = argv[1];
  si.topic_name_ = argv[2];
  si.sub_image(argc, argv);
  cout << "finish\n";
  return 0;
}
