# View component of ArgMarkNet Web Crawler

import sys
import argparse
import pandas as pd

# Define argparse structure
def parse_arguments():
  try:
    parser = argparse.ArgumentParser(description = "ArgMarkNet Web Crawler")
    parser.add_argument("--commodity", help="Make sure the first letter is capitalized. See: Potato", required=True)
    parser.add_argument("--state", help="Make sure the first letter is capitalized. Can input multiple states at once, separate by space. See: Kerala Bihar", required=True, nargs='+')
    parser.add_argument("--from_date", help="Make sure date adheres to following format, first letter of month capitalized. See: 20-Sep-2023", required=True)
    parser.add_argument("--to_date", help="Make sure date adheres to following format, first letter of month capitalized. See: 20-Sep-2023", required=True)
    parser.add_argument("--time_agg", help="time aggregate options to group data by. Default is monthly.", choices=["daily", "monthly", "yearly"], default="monthly")
    args = parser.parse_args()
    return args
  
  except argparse.ArgumentError as e:
    print(f"Argument error: {e}")
    sys.exit(1)
