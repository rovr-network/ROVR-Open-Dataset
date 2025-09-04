#pragma once
#include <string>
#include <vector>
#include <iostream>
#define ACCEPT_USE_OF_DEPRECATED_PROJ_API_H
#include <proj_api.h>
#include <Eigen/Core>

inline void LatLon2Utm(double lat, double lon, double alt, double& x, double& y, double& z) {
  projPJ pj_utm, pj_latlong;

  char pjValue[256] = {0};

  int zoneID = int((lon + 180) / 6) + 1;

  bool is_southern = (lat < 0);

  if (is_southern) {
    sprintf(pjValue,
            "+proj=utm +zone=%d +south +ellps=WGS84 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs",
            zoneID);
  } else {
    sprintf(pjValue,
            "+proj=utm +zone=%d +ellps=WGS84 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs",
            zoneID);
  }

  if (!(pj_utm = pj_init_plus(pjValue))) exit(1);
  if (!(pj_latlong = pj_init_plus("+proj=latlong +ellps=WGS84 +datum=WGS84")))
    exit(1);

  x = lon;
  y = lat;
  z = alt;

  x *= DEG_TO_RAD;
  y *= DEG_TO_RAD;

  pj_transform(pj_latlong, pj_utm, 1, 1, &x, &y, &z);

  pj_free(pj_utm);
  pj_free(pj_latlong);
}

inline double GetGaussGridConvergence(const double& latidude_deg,
                               const double& longitude_diff_deg) {
  // const double A_WGS84 = 6378137.00;
  // const double B_WGS84 = 6356752.3142;
  // const double C_WGS84 = 6399593.6258;
  // const double IB_WGS84 = 1 / 298.257223563;
  // const double EE_WGS84 = 0.006694379013;
  const double EEP_WGS84 = 0.00673949674227;

  double lat_rad = latidude_deg * DEG_TO_RAD;
  double long_rad = longitude_diff_deg * DEG_TO_RAD;
  double cosBB = pow(cos(lat_rad), 2);
  double sinB = sin(lat_rad);
  //    double convDeg1 = sin(lat_rad)*long_rad + sin(lat_rad)*cosBB*(1 + 3 *
  //    EEP_WGS84*cosBB*cosBB + 2 * EEP_WGS84*EEP_WGS84*pow(cosBB, 4))*
  //    pow(long_rad, 3) / 3
  //     + sin(lat_rad)*cosBB*cosBB*(2 - pow(tan(lat_rad), 2))* pow(long_rad, 5)
  //     / 15;
  double conv_rad =
      sinB * long_rad +
      sinB * cosBB *
          (1 + 3 * EEP_WGS84 * cosBB +
           2 * EEP_WGS84 * EEP_WGS84 * cosBB * cosBB) *
          pow(long_rad, 3) / 3 +
      sinB * cosBB * cosBB * (2 - pow(tan(lat_rad), 2)) * pow(long_rad, 5) / 15;
  // convDeg = convDeg*180.0 / 3.1415;

  return conv_rad;
}


struct GNRMC {
  double timestamp;

  double latitude;
  double longitude;
  double altitude;
  double x,y,z;
  double heading;

  double velocity; //m/s

  int zone_id;

  std::string NS;
  std::string EW;

  Eigen::Matrix3d rot33;
  Eigen::Vector3d trans;

  GNRMC(const std::string& str){
    timestamp = 0.0;
    latitude = longitude = altitude = heading = velocity = 0.0;
    NS = "N";
    EW = "E";
    rot33 = Eigen::Matrix3d::Identity();
    trans = Eigen::Vector3d::Zero();

    std::vector<std::string> fields;
    std::stringstream ss(str);
    std::string field;
    while (std::getline(ss, field, ',')) {
      fields.push_back(field);
    }

    if (fields.size() < 13) {
      // throw std::invalid_argument("Invalid GNRMC format");
      return;
    }
    if (fields[2] != "A") {
      // throw std::runtime_error("GNRMC data is invalid (status=V)");
      std:cout << "GNRMC data is invalid (status=V)" << std::endl;
      return;
    }


    // 3. lantitude（ddmm.mmmm）
    if (!fields[3].empty() && !fields[4].empty()) {
        double ddmm = std::stod(fields[3]);
        double dd = std::floor(ddmm / 100);
        double mm = ddmm - dd * 100;
        latitude = dd + mm / 60.0;
        NS = fields[4];
        if (NS == "S") latitude *= -1;
    }

    // 4. longitude（dddmm.mmmm）
    if (!fields[5].empty() && !fields[6].empty()) {
        double dddmm = std::stod(fields[5]);
        double ddd = std::floor(dddmm / 100);
        double mm = dddmm - ddd * 100;
        longitude = ddd + mm / 60.0;
        EW = fields[6];
        if (EW == "W") longitude *= -1;
    }
  
    // 5. vel
    if (!fields[7].empty()) {
        velocity = std::stod(fields[7]) * 0.514444; // 1 knot = 0.514444 m/s
    }
    // 6. heading
    if (!fields[8].empty()) {
        heading = std::stod(fields[8]);
    }

    //
    LatLon2Utm(latitude, longitude, altitude, x, y, z);
    trans = Eigen::Vector3d(x, y, z);
    //
    zone_id = int((longitude + 180) / 6) + 1;
    double center_longitude = 6 * zone_id - 3 - 180;
    double gauss_conv = GetGaussGridConvergence(latitude, longitude - center_longitude);
    double heading_rad = heading * M_PI / 180.0;

    // std::cout << "Gauss_conv : " << gauss_conv << std::endl;
    if(heading_rad < M_PI) {
      heading_rad = -heading_rad;
    } else if (heading_rad > M_PI) {
      heading_rad = 2*M_PI - heading_rad;
    }
    
    heading_rad += gauss_conv;
    if(heading_rad > M_PI) heading_rad -= 2*M_PI;
    else if(heading_rad < -M_PI) heading_rad += 2*M_PI;

    rot33 << std::cos(heading_rad), -std::sin(heading_rad), 0,
             std::sin(heading_rad),  std::cos(heading_rad), 0,
                             0,             0,              1;
  }

};