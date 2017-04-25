#include "get_Depth.hpp"
// catkin_create_pkg pcd_tutorial std_msgs roscpp pcl_ros pcl_msgs pcl_conversions libpcl-all-dev

// static cv::Mat CameraExtrinsicMat;
// static cv::Mat CameraMat;
// static cv::Mat DistCoeff;
// static cv::Size ImageSize;

static void check_arguments(int argc, char* argv[])
{
  cout << "Fuck you" << endl;
  if (argc != 5){
    cout << "Please set arguments like below\n'rosrun dataprocess get_PCD save_dir topic_name'\n";
    exit(EXIT_FAILURE);
  }
}

void SaveDepth::get_pcd(const sensor_msgs::PointCloud2::ConstPtr& msg)
{
  stringstream ss;
  ss << msg->header.stamp;
  // string file_name = save_path_ + ss.str() + ".pcd";
  // pcl::PointCloud<pcl::PointXYZ> points;
  // pcl::fromROSMsg(*msg, points_);
  points_ = *msg;
  is_pc2_ = true;
  // pcl::io::savePCDFileASCII(file_name, points);
}


void SaveDepth::get_image(const sensor_msgs::Image& msg)
{
  cv_bridge::CvImagePtr cv_image;
  stringstream ss;
  ss << msg.header.stamp;
  try
  {
    cv_image = cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::BGR8);
  }
  catch (cv_bridge::Exception& e)
  {
    ROS_ERROR("cv_bridge exeption: %s", e.what());
  }
  image_ = cv_image->image;
  is_image_ = true;
  // cv::imwrite(save_path_ + ss.str() + ".jpg", cv_image->image);
}

void SaveDepth::read_CalibFile(){
  cv::FileStorage fs(calib_path_, cv::FileStorage::READ);
  if (!fs.isOpened())
  {
    cout << "Cannot Open " << calib_path_ << endl;
    exit(EXIT_FAILURE);
  }
  fs["CameraExtrinsicMat"] >> CameraExtrinsicMat_;
  fs["CameraMat"] >> CameraMat_;
  fs["DistCoeff"] >> DistCoeff_;
  fs["ImageSize"] >> ImageSize_;
}

void SaveDepth::reset_flags(){
  is_pc2_ = false;
  is_image_ = false;
}

void SaveDepth::create_depth(){
  // cout << CameraMat_ << endl;
  cout << CameraExtrinsicMat_ << endl;
  // cout << DistCoeff_ << endl;
  cout << points_.header << endl;
  // stringstream ss;
  // ss << width << " : " << height << endl;
  // cout << ss.str() << endl;
  // cout << points_.header << endl;
  int width = ImageSize_.width;
  int height = ImageSize_.height;
  cv::Mat invR = CameraExtrinsicMat_(cv::Rect(0,0,3,3)).t();
	cv::Mat invT = -invR*(CameraExtrinsicMat_(cv::Rect(3,0,1,3)));
  cv::Mat invR_T = invR.t();
  cv::Mat invT_T = invT.t();

  cv::Mat depth = cv::Mat::zeros(cv::Size(width, height), CV_8U);
  depth.at<double>(50, 50) = 1;
  cv::imwrite(save_path_ + "otameshi" +".jpg", depth);

  reset_flags();
}

void SaveDepth::depthConverter(int argc, char* argv[]){
  ros::init(argc, argv, "Depth_Conveter");
  ros::NodeHandle n;
  ros::Subscriber image_sub = n.subscribe(image_topic_name_, 1, &SaveDepth::get_image, this);
  ros::Subscriber pc2_sub = n.subscribe(pc2_topic_name_, 1, &SaveDepth::get_pcd, this);
  ros::Rate r(10);
  while (ros::ok())
  {
    cout << is_image_ << is_pc2_ << endl;
    if ((is_image_ == true) && (is_pc2_ == true)){
      cout << "Hello3\n";
      create_depth();
    }
    ros::spinOnce();
    r.sleep();
  }
}

int main(int argc, char* argv[])
{
  check_arguments(argc, argv);
  SaveDepth si;
  string path = argv[1];
  if (path[path.size() - 1] == '/'){
    path.erase(path.begin() + path.size()-1);
  }
  si.save_path_ = path + '/';
  si.calib_path_ = argv[2];
  si.image_topic_name_ = argv[3];
  si.pc2_topic_name_ = argv[4];
  si.read_CalibFile();
  si.depthConverter(argc, argv);
  cout << "finish\n";
  return 0;
}
