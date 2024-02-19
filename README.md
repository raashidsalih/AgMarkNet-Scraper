# Agriculture Dataset Scraping

## Overview
This is the repo where I store my proposed solution to the assignment provided.

I'll begin by sharing the answer to the second question which is the SQL query, followed by instructions on installation and usage. Beyond that, I provide auxiliaries like the data dictionary, my justification for design decisions, and other sundries.

## SQL Solution
###### QUESTION
***Write a single SQL query to return the top 5 states for 4 commodities (Potato, Onion, Wheat, tomato) – Output should contain 20 records only.***

###### SOLUTION
- The query employs CTE and a window function to generate the final solution. 
- State's Rank included in final table for readability.
- Assuming "top" in the question refers to price. In this case, modal price was chosen (compared to min and max) since it is the average. Refer to data dictionary to understand the available columns.

```SQL
with top_5 as
 (SELECT
    commodity,
    state,
    ROUND(AVG(modal_price),2) as AVERAGE,
    ROW_NUMBER() OVER (PARTITION BY commodity Order by ROUND(AVG(modal_price),2)  DESC) RANK
     
    FROM schema_project.agmarket_monthly
     
    Group by state, commodity
    Order BY commodity, AVERAGE DESC)
    
SELECT * FROM top_5 WHERE RANK<=5 AND commodity IN ('Potato', 'Onion', 'Wheat', 'Tomato')
```
## Installation Instructions
#### Prerequisites
1. Ensure selenium is operational using the Chrome WebDriver. Selenium 4.6 and later downloads the appropriate driver without any manual intervention required. However, if you're on the latest version and still run into any issues, [troubleshoot using the instructions here.](https://www.selenium.dev/documentation/webdriver/troubleshooting/errors/driver_location/)
2. Tested on Windows, can work on other OSs with a little tinkering.
3. Can likewise use WebDrivers other than Chrome.
4. The process to get Selenium with Chrome WebDriver working seems to be a bit elaborate on Linux, so would recommend sticking with Windows.

##### Step 1: Clone
Clone this git repository using:
```bash
git clone https://github.com/raashidsalih/AgMarkNet-Scraper.git
```

##### Step 2: Configure
- Rename ```sample.env``` to ```.env``` and replace the contents with the connection information required for your Postgres database.
- These details are separated from the code for security purposes.
- If you want to name the ```.env``` file anything else, you can specify so in the ```dotenv``` command when it is loading the environment variables.

##### Step 3: Define Python Virtual Environment [Optional]
I suggest running the program in a Python venv for stability and reproducibility. Although optional, it is highly recommended to avoid potential dependency related issues. Navigate to the cloned directory and create a Python virtual environment using the following command *[Windows]:*
```bash
python -m venv myenv
```
Activate your Python venv using:
```bash
myenv\Scripts\activate
```
If you get a permission error with regards to not being able to run scripts, use this command first:
```bash
Set-ExecutionPolicy Unrestricted -Scope Process
```
It'll not enforce restrictions for the rest of the session.

##### Step 4: Install Requirements
Install the dependencies for the program to run via the handy requirements.txt:
```bash
pip install -r requirements.txt
```

##### Step 5: Ready To Go
All the requirements have been satisfied, and you are now ready to use the program. Make a mental note of the states, commodities, and dates that you'd like to try and ensure that they adhere to the format which will be explained below.


## Usage Instructions
- CLI developed using ```argparse```. You can use -h to get the following details while using the interface.
- General syntax of command is:
```
python scrape_agmarket.py [-h] --commodity COMMODITY --state STATE [STATE ...] --from_date FROM_DATE --to_date TO_DATE [--time_agg {daily,monthly,yearly}]
```
- You can try multiple states at once by separating them with space after the flag.
- The general format of the arguments after the flag is provided below:

| Parameter   | Parameter Description    |                                                       Format                                                       |
|-------------|--------------------------|:------------------------------------------------------------------------------------------------------------------:|
| \-\-commodity | Commodity Name           | Make sure the first letter is capitalized. **See: Potato**                                                             |
| \-\-state     | State Name               | Make sure the first letter is capitalized. Can input multiple states at once, separate by space. **See: Kerala Bihar** |
| \-\-from_date | From Date of Results     | Make sure date adheres to following format, first letter of month capitalized. **See: 20-Sep-2023**                    |
| \-\-to_date   | To Date of Results       | Make sure date adheres to following format, first letter of month capitalized. **See: 20-Sep-2023**                    |
| \-\-time_agg  | Time Aggregate Parameter | time aggregate options to group data by. Options are [Daily, Monthly, Yearly]. Default is monthly.                 |

- Note that if the program fails for one state in a list, then it won't run for the other states following it automatically. 
- Any argument that has a space will need to be surrounded by quotes. See:
```
"chili red", "Tamil Nadu"
```
- Keeping all of this in mind, an example:
```powershell
python scrape_agmarket.py --commodity Onion --state Gujarat Haryana Punjab "Tamil Nadu" --from_date 01-Sep-2023 --to_date 24-Sep-2023 --time_agg monthly
```
## Data Dictionary
| **_Column Name_** |          **_Description_**          |
|:-----------------:|:-----------------------------------:|
|       state       |              State Name             |
|      district     |            District Name            |
|       market      |             Market Name             |
|     commodity     |            Commodity Name           |
|    com_variety    |          Commodity Variety          |
|     com_group     |           Commodity Group           |
|      arrival      |       Arrival amount in Tonnes      |
|     min_price     |     Minimum Price (Rs./Quintal)     |
|     max_price     |     Maximum Price (Rs./Quintal)     |
|    modal_price    | Modal (Average) Price (Rs./Quintal) |
|    date_arrival   |       Reported Date of Arrival      |

## Alternative Deployment
We use venv for the benefits it provides in terms of isolation and therefore, reproducibility. However, if given the chance, the better method (and some would consider the de facto standard even) is using ***docker*** for deployment.

This would also take into account:
- Potential issues with Chrome and Selenium compatibility, and
- A good chunk of the installation steps necessary to get the program running.

This is what such a solution would look like in practice:
1. Dockerize the pipeline
2. Host it on an image registry
3. Pull from the image registry whenever the program needs to be run
4. Every github push to the repo updates the image in the registry via a CD (Continuous Deployment) implementation

## Design Considerations

 - I organized the Python project following the Model-View-Controller (MVC) Architectural pattern for better separation of concerns. The controller has been renamed to ```scrape_agmarket.py``` to reflect the naming in the question. The other components remain unchanged.
--------
 - The straightforward approach would be to use Selenium to navigate from the AgMarkNet homepage, navigate using the parameters we want, and finally scrape the results.
 - The issue is that the site is irregular in its availability. In the off chance that one does gain access, it either has a server error or is very slow to load and respond.
 - This makes rapid prototyping and experimentation rather cumbersome. It also brings into question the reliability of whatever solution that has been developed.
 - Thus a conscious design decision was to use Selenium as scarcely as possible to bypass such outages.
----------
 - An alternative approach is to inject the parameters straight into the URL to directly get the results. However, certain parameters were encoded (commodity and state, for instance), for which the mapping was unknown. You can see it in part of the URL below:
```https://agmarknet.gov.in/SearchCmmMkt.aspx?Tx_Commodity=19&Tx_State=TN&Tx_District=0....```
- Notice ```Tx_Commodity``` and ```Tx_State```. The number 19 represents the commodity **"Banana"**, while TN represents the state of **"Tamil Nadu".**
- I was able to find the mappings by looking into the source code of the website, and generate CSVs of said mapping from the HTML. This is where ```generator.py``` was used. The results are the data sources that you can observe in the repo.
--------
- Employed ```.env``` file for security with regards to database connection credentials. GitHub typically ignores ```.env``` files, therefore the need to rename it to ```sample.env```.
- Error handling implemented for the inputs using a variety of methods, and in general using try-except.
- The rate determining step here is how quickly AgMarkNet is able to load. I implemented timeout using a function bundled with Selenium, and had to use ```time.sleep()``` to provide enough time for the download to begin after the *"download excel"* button was clicked. 
- Downloading the data in CSV/TSV as mentioned in the question was not possible (perhaps they stopped offering that service). The alternative would be to scrape the resulting table page by page using Selenium, which was an option I was not willing to consider.
---------
- The CLI was developed using ```argparse```, although various alternatives exist like ```Click```, and ```docopt```.  However, ```argparse```seems to be the most popular framework for the usecase.
- The SQL commands were tested on a table defined with the following SQL query:
```SQL
DROP TABLE IF EXISTS schema_project.agmarket_monthly;

CREATE TABLE IF NOT EXISTS schema_project.agmarket_monthly
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    state character varying(50) COLLATE pg_catalog."default",
    district character varying(50) COLLATE pg_catalog."default",
    market character varying(50) COLLATE pg_catalog."default",
    commodity character varying(50) COLLATE pg_catalog."default",
    com_variety character varying(50) COLLATE pg_catalog."default",
    com_group character varying(50) COLLATE pg_catalog."default",
    arrival numeric(10,4),
    min_price numeric(10,4),
    max_price numeric(10,4),
    modal_price numeric(10,4),
    date_arrival date,
    CONSTRAINT " agmarket_monthly_pkey" PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS schema_project.agmarket_monthly
    OWNER to postgres;
```
## Things to Watch Out For
- The things that can potentially break this implementation are:
1. A change in the ArgMarkNet interface, and
2. A change in how the backend processes user inputs (think source data files for commodity and state encoding)
- Therefore, it would be wise to monitor for such changes to pre-emptively catch any potential issues and avoid broken pipelines.

- In the next iteration, I'd like to:
1. Find an alternative to Selenium due to the external browser dependency, and also the lag encountered by actually clicking the button instead of somehow directly triggering the JavaScript to do so.
2. Implement unit and integration tests as a part of a CI (Continuous Integration) pipeline to promote robust updates.
