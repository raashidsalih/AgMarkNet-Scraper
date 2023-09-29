# Controller component of ArgMarkNet Web Crawler

import model
import view
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
import time
import datetime
import sys
import os
import requests
from dotenv import load_dotenv


# Function to obtain user input from argparse
def get_input():
  try:
    args = view.parse_arguments()
    commodity = args.commodity
    states = args.state
    from_date = args.from_date
    to_date = args.to_date
    time_agg = args.time_agg

    # Check date format validity
    date_format = '%d-%b-%Y'
    try:
      dateObject = datetime.datetime.strptime(from_date, date_format)
    except ValueError:
      print("Incorrect from_date format, should be DD-MON-YYYY")
      sys.exit(1)

    try:
      dateObject = datetime.datetime.strptime(to_date, date_format)
    except ValueError:
      print("Incorrect to_date format, should be DD-MON-YYYY")
      sys.exit(1)
    
    # Check time_agg option validity
    avl_agg = ["daily", "monthly", "yearly"]
    if time_agg not in avl_agg:
      print("Invalid time_agg! available options are ", avl_agg)
      sys.exit(1)
    
    return commodity, states, from_date, to_date, time_agg
  except AttributeError as e:
    print(f"Attribute error: {e}")
    sys.exit(1)

# Function to obtain environment variables from .env and load it
def get_env():
  try:
    load_dotenv()
  except Exception as e:
    print(f"Environment error: {e}")
    sys.exit(1)


# Function to generate the url based on user parameters
def generate_url(commodity, state, from_date, to_date):

  #Get commodity and state encoded from source data
  commodity_code = model.read_csv_to_dict("source_data/commodity_source.csv")
  state_code = model.read_csv_to_dict("source_data/state_source.csv")
  
  #Check if state or commodity exists in system
  try:
    cmd_code = commodity_code[commodity]
  except KeyError as e:
    print(f"Entered Commodity Not Found! Ensure your formatting is correct as well. {e}")
    sys.exit(1)

  try:
    st_code = state_code[state]
  except KeyError as e:
    print(f"Entered State Not Found! Ensure your formatting is correct as well. {e}")
    sys.exit(1)

  url = f"https://agmarknet.gov.in/SearchCmmMkt.aspx?Tx_Commodity={cmd_code}&Tx_State={st_code}&Tx_District=0&Tx_Market=0&DateFrom={from_date}&DateTo={to_date}&Fr_Date={from_date}&To_Date={to_date}&Tx_Trend=2&Tx_CommodityHead={commodity}&Tx_StateHead={state}&Tx_DistrictHead=--Select--&Tx_MarketHead=--Select--"
  
  return url

# Function to determine if url is reachable
def check_url(url):
  try:
    page = requests.get(url)
  except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
    print(f"Error! Could not reach AgMarkNet! Server might be unavailable: {e}")
    sys.exit(1)
  

# Function to download the excel file from the url using Selenium
def download_excel(url):
  
  options = webdriver.ChromeOptions() 
  prefs = {"download.default_directory" : os.getcwd()}
  options.add_experimental_option("excludeSwitches", ["enable-logging"])
  options.add_experimental_option("prefs", prefs)
  options.add_argument('--headless')

  try:
    driver = webdriver.Chrome(options=options)

    driver.implicitly_wait(10) # For timeout purposes

    driver.get(url)

    # Check in case page is reachable but there is no data
    no_results = driver.find_element(By.ID, "cphBody_Label_Result").text
    if "Not Available" in no_results:
        print("Data Not Available for Specified Query")
        sys.exit(1)

    button = driver.find_element(By.ID, "cphBody_ButtonExcel")
    button.click()
    time.sleep(10) # Enough time for download to begin

  except NoSuchElementException as e:
    print(f"No Element Found. It could be that the page took too long to load (look into changing timeout duration), or the page is unavailable even if it is reachable. {e}")
    sys.exit(1)

  except (WebDriverException, ) as e:
    print(f"Webdriver Error {e}")
    sys.exit(1)


# Define the main function to run the program
def main():
  print("\nWelcome to the ArgMarkNet Web Crawler!\n")
  try:
    commodity, states, from_date, to_date, time_agg = get_input()

    for state in states:  #In case there are multiple states

        get_env()
        print(f"\nSearching for {commodity} prices in {state} from {from_date} to {to_date}\n")
        url = generate_url(commodity, state, from_date, to_date)
        print("Generated url")
        print("Checking connectivity to AgMarkNet...")
        check_url(url)
        print("Connection to AgMarkNet successful!")
        print("Downloading excel file...")
        download_excel(url)
        print("Excel file downloaded successfully")
        print("Reading data from excel file...")
        df = model.read_data_from_excel()
        print("Data read successfully")
        print("Transforming Data")
        result = model.transform_data(df, commodity, time_agg)
        print("Data transformed successfully")
        print("Writing data to database...")
        model.write_to_database(result)
        print("Data written successfully")
  except Exception as e:
    print(f"Unexpected error: {e}")
  print("Thank you for using the ArgMarkNet Web Crawler!")


# Run the main function
if __name__ == "__main__":
  main()
