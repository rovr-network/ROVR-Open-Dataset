#pragma once

#include <pdal/PointTable.hpp>
#include <pdal/PointView.hpp>
#include <pdal/Options.hpp>
#include <pdal/StageFactory.hpp>
#include <pdal/io/LasWriter.hpp>
#include <pdal/io/BufferReader.hpp>
#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include "preprocess.h"

inline void SaveLas(const std::string& filename, const pcl::PointCloud<rovr::Point>& input_pc, 
                    const double& offset_x, const double& offset_y, const double& offset_z) {
  pdal::PointTable table;
  table.layout()->registerDim(pdal::Dimension::Id::X);
  table.layout()->registerDim(pdal::Dimension::Id::Y);
  table.layout()->registerDim(pdal::Dimension::Id::Z);
  table.layout()->registerDim(pdal::Dimension::Id::Intensity);
  // table.layout()->registerDim(pdal::Dimension::Id::ScanAngleRank);
  table.layout()->registerDim(pdal::Dimension::Id::PointSourceId);
  // table.layout()->registerDim(pdal::Dimension::Id::Classification);
  // table.layout()->registerDim(pdal::Dimension::Id::UserData);
  // table.layout()->registerDim(pdal::Dimension::Id::GpsTime);

  pdal::PointViewPtr view(new pdal::PointView(table));

  for (uint i = 0; i < input_pc.size(); i++) {
    const auto& pt = input_pc.points[i];
    view->setField(pdal::Dimension::Id::X, i, pt.x + offset_x);
    view->setField(pdal::Dimension::Id::Y, i, pt.y + offset_y);
    view->setField(pdal::Dimension::Id::Z, i, pt.z + offset_z);
    view->setField(pdal::Dimension::Id::Intensity, i, pt.intensity);
    // view->setField(pdal::Dimension::Id::ScanAngleRank, i, static_cast<uint16_t>(pt.azimuth * 0.005 - 90));
    view->setField(pdal::Dimension::Id::PointSourceId, i, pt.index);
    // view->setField(pdal::Dimension::Id::Classification, i, pt.classification);
    // view->setField(pdal::Dimension::Id::UserData, i, GetHardwareRing16(pt.ring));
    // view->setField(pdal::Dimension::Id::GpsTime, i, pt.timestamp);
  }

  pdal::BufferReader reader;
  reader.addView(view);
  pdal::Options options;
  options.add("filename", filename);
  options.add("offset_x", offset_x);  
  options.add("offset_y", offset_y);
  options.add("offset_z", offset_z);
  options.add("scale_x", 0.01);
  options.add("scale_y", 0.01);
  options.add("scale_z", 0.01);
  options.add("compression", "false"); 

  pdal::StageFactory factory;
  pdal::Stage* writer = factory.createStage("writers.las");
  writer->setOptions(options);
  writer->setInput(reader);

  // pdal::PointTable dummyTable;
  writer->prepare(table);
  writer->execute(table);

  std::cout << "Saved LAS file: " << filename << std::endl;
}