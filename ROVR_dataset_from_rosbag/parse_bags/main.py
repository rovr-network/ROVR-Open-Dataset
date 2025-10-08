#!/usr/bin/env python3
import os
import glob
import csv
import shutil
import argparse
import numpy as np
from multiprocessing import Pool
from .bag_reader import Ros2BagProcessor

def process_single_bag(args):
  """Process a single bag file"""
  bag_file, output_base_dir, sn_base_dir = args
  try:
      base_name = os.path.basename(bag_file)
      output_dir_name = base_name[:-5] if base_name.endswith('.data') else base_name
      output_dir = os.path.join(output_base_dir, output_dir_name)

      print(f"\nProcessing {bag_file} -> {output_dir}")
      os.makedirs(output_dir, exist_ok=True)
      processor = Ros2BagProcessor(bag_file, output_dir, sn_base_dir)
      processor.process_bag()

      avg_diff = processor.capture_diff / processor.total_count if processor.total_count > 0 else 0

      if processor.valid_count < 0:
          print(f"Warning: Only {processor.valid_count} valid pairs found, deleting output directory...")
          return (base_name, processor.valid_count, avg_diff, False)
      return (base_name, processor.valid_count, avg_diff, True)
  except Exception as e:
      print(f"[ERROR] Failed to process {bag_file}: {str(e)}")
      return (base_name, -1, -1, False)

def process_all_bags(input_dir, output_base_dir, sn_base_dir, output_sample_dir):
  """Process all bag files in input directory"""
  os.makedirs(output_base_dir, exist_ok=True)
  os.makedirs(output_sample_dir, exist_ok=True)

  input_folder_name = os.path.basename(os.path.normpath(input_dir))
  stats_csv_path = os.path.join(output_base_dir, f'processing_stats_{input_folder_name}.csv')

  with open(stats_csv_path, 'w', newline='') as csvfile:
      csvwriter = csv.writer(csvfile)
      csvwriter.writerow(['BagFile', 'ValidPair', 'AverageCaptureDiff', 'Valid'])

  # bag_files = glob.glob(os.path.join(input_dir, '*.data'))
  bag_files = []
  for root, _, files in os.walk(input_dir):
      for file in files:
          if file.endswith('.data'):
              bag_files.append(os.path.join(root, file))

  args_list = [(bag_file, output_base_dir, sn_base_dir) for bag_file in bag_files]

  num_processes = min(4, len(bag_files))
  print(f"Using {num_processes} processes to handle {len(bag_files)} bag files")

  with Pool(processes=num_processes) as pool:
      results = pool.map(process_single_bag, args_list)

  with open(stats_csv_path, 'a', newline='') as csvfile:
      csvwriter = csv.writer(csvfile)
      for result in results:
          csvwriter.writerow(result)

  for result in results:
      base_name, valid_count, avg_diff, is_valid = result
      output_dir = os.path.join(output_base_dir, base_name[:-5] if base_name.endswith('.data') else base_name)

      if not is_valid:
          try:
              shutil.rmtree(output_dir)
              print(f"Deleted invalid directory: {output_dir}")
          except Exception as e:
              print(f"Failed to delete {output_dir}: {str(e)}")
      else:
          try:
              project_dir = os.path.join(output_dir, 'project')
              if os.path.exists(project_dir):
                  project_files = glob.glob(os.path.join(project_dir, '*.png'))
                  if project_files:
                      selected_file = np.random.choice(project_files)
                      new_name = f"{os.path.basename(output_dir)}_{os.path.basename(selected_file)}"
                      shutil.copy(selected_file, os.path.join(output_sample_dir, new_name))
                      print(f"Saved valid frame: {new_name}")
          except Exception as e:
              print(f"Error processing valid directory {output_dir}: {str(e)}")

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Process ROS2 bag files in a directory')
  parser.add_argument('--input', required=True, help='Input directory containing .data files')
  parser.add_argument('--output', required=True, help='Base output directory')
  parser.add_argument('--sn-dir', required=True, help='Base directory containing SN folders')
  parser.add_argument('--sample', 
                    required=False,
                    default=None,
                    help='Output samples directory (default: output/sample)')
  args = parser.parse_args()

  if args.sample is None:
      args.sample = os.path.join(args.output, 'sample')
      print(f"No sample directory specified, using default: {args.sample}")


  process_all_bags(args.input, args.output, args.sn_dir, args.sample)