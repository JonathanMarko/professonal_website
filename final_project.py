#importing the libraries i will use for this project
import requests
import pandas as pd
import pathlib
import time
import statistics


##Part One:
##Extracting data from the NYT API and saving the data to a csv

#The key and url for my api access
API_KEY = 'your_api_key'
URL = 'https://api.nytimes.com/svc/search/v2/articlesearch.json'

#creating a path, a new dir and a new csv file to save the data to 
cwd = pathlib.Path.cwd()

new_dir = cwd/'final_project_results'
new_dir.mkdir(exist_ok=True)

results = new_dir/'results.csv'
results.touch(exist_ok=True)




#a list of all democratic and republican nominees in each election from 1900 to 2016 including the date range i will be searching for each election
#the data is in the form of [election_year, democrat_nominee, republican_nominee, beginning_date, end_date, incumbent_in_elect]
elections = [
    ['1900','Bryan', 'McKinley', '19000701', '19001101', True],
    ['1904','Parker', 'Roosevelt', '19040701', '19041101', True],
    ['1908','Bryan', 'Taft', '19080701', '19081101', False],
    ['1912','Wilson', 'Taft', '19120701', '19121101', True],
    ['1916','Wilson', 'Hughes', '19160701', '19161101', True],
    ['1920','Cox', 'Harding', '19200701', '19201101', False],
    ['1924','Davis', 'Coolidge', '19240701', '19241101', True],
    ['1928','Smith', 'Hoover', '19280701', '19281101', False],
    ['1932','Roosevelt', 'Hoover', '19320701', '19321101', True],
    ['1936','Roosevelt', 'Landon', '19360701', '19361101', True],
    ['1940','Roosevelt', 'Willkie', '19400701', '19401101', True],
    ['1944','Roosevelt', 'Dewey', '19440701', '19441101', True],
    ['1948','Truman', 'Dewey', '19480701', '19481101', True],
    ['1952','Stevenson', 'Eisenhower', '19520701', '19521101', False],
    ['1956','Stevenson', 'Eisenhower', '19560701', '19561101', True],
    ['1960','Kennedy', 'Nixon', '19600701', '19601101', False],
    ['1964','Johnson', 'Goldwater', '19640701', '19641101', True],
    ['1968','Humphrey', 'Nixon', '19680701', '19681101', False],
    ['1972','McGovern', 'Nixon', '19720701', '19721101', True],
    ['1976','Carter', 'Ford', '19760701', '19761101', True],
    ['1980','Carter', 'Reagan', '19800701', '19801101', True],
    ['1984','Mondale', 'Reagan', '19840701', '19841101', True],
    ['1988','Dukakis', 'Bush', '19880701', '19881101', False],
    ['1992','Clinton', 'Bush', '19920701', '19921101', True],
    ['1996','Clinton', 'Dole', '19960701', '19961101', True],
    ['2000','Gore', 'Bush', '20000701', '20001101', False],
    ['2004','Kerry', 'Bush', '20040701', '20041101', True],
    ['2008','Obama', 'McCain', '20080701', '20081101', False],
    ['2012','Obama', 'Romney', '20120701', '20121101', True],
    ['2016','Clinton', 'Trump', '20160701', '20161101', False],
]

#creating a fucntion which places the data inputed into its appropriate
#  place in the parameters of a search. This function than takes the data 
# from the api, extracts the total hit count and returns it as the value
def search(q,start_date, end_date):
    """This function takes the arguments and places them 
    within the parameters of a NYT API query. It then 
    extracts the total hits a query gets and returns that 
    value. 

    Args:
        q (string): The keyword to search for 
        start_date (string): The date should the search start
        end_date (string): The date to stop searching at

    Returns:
        integer : The total hits for the keyword
    """
    params = {
        'q' : q,
        'api-key' : API_KEY,
        'begin_date' : start_date,
        'end_date' : end_date,
        'fq' : 'section.name("politics")'}
    content_elect = requests.get(URL, params = params).json()
    total_hits = content_elect['response']['metadata']['hits']
    return total_hits
    

#creating an empty data frame using pandas with column headers
raw_data = pd.DataFrame(columns=['election','dem_hits', 'rep_hits','incumbent_in_elect'])


#using a for loop to go through the list of elections. This for loop calls 
# on the function "search()" to place the appropriate data from the lists 
# into their respective places in the paramaters of a api quary
for i in elections:
    data_dem = search(i[1],i[3],i[4])
    time.sleep(14)
    data_rep = search(i[2],i[3],i[4])
    raw_data.loc[len(raw_data)] = [i[0] , data_dem , data_rep , i[-1]]
    time.sleep(14)


#saving the data frame as a cvs file in the dir created using pathlib
raw_data.to_csv(results, index=False)




##Part two:
##Transforming the data into a usable form and extracting information

#creating two lists to house the data extracted with a for loop later in the code. First list is for all elections the second is for elections with incumbents running. 
disparity_percent_total = []
disparity_percent_incumbent = []


#using a for loop to extract the data from the dataframe created 
# in the previous step. This loop finds the disparity percentage 
# between articles writen about each canidate and appends it to 
# two lists expressed in decimal form
for info in raw_data.itertuples():
    total_hits = info.dem_hits + info.rep_hits
    disparity = abs(info.dem_hits - info.rep_hits)
    disparity_percent = disparity / total_hits
    disparity_percent_total.append(disparity_percent)
    if info.incumbent_in_elect == True:
        disparity_percent_incumbent.append(disparity_percent)
    

#these are two a final quaries to the api to get the data from the 2020 election 
trump_hits = search('trump', '20200701','20201101')
biden_hits = search('biden', '20200701','20201101')


#Using the stdev function from the statistics library to find the standard dev of the hit desparities of previous elections and the mean to find the average discrepancy
stand_dev_total = statistics.stdev(disparity_percent_total)
stand_dev_incumbent = statistics.stdev(disparity_percent_incumbent)
mean_total = statistics.mean(disparity_percent_total)
mean_incumbent = statistics.mean(disparity_percent_incumbent)

#creating upper and lower limits of what is normal deviations 

upper_total = mean_total + (2*stand_dev_total)
low_total = mean_total - (2*stand_dev_total)

upper_incumbent = mean_incumbent + (2*stand_dev_incumbent)
low_incumbent = mean_incumbent - (2*stand_dev_incumbent)

#finding the discrepancy for 2020
disparity_2020 = abs(trump_hits - biden_hits) / (trump_hits + biden_hits)




#printing out the results
print(f"The total hits for trump is {trump_hits}.")
print(f"The total hits for biden is {biden_hits}.")
print(f"The disparity between articles about Biden and Trump is {(disparity_2020*100):.2f}%")

print(f"Normal disparity for all elections: {(low_total*100):.2f}% to {(upper_total*100):.2f}%")
print(f"Normal disparity for incumbent elections: {(low_incumbent*100):.2f}% to {(upper_incumbent*100):.2f}%")


if (disparity_2020 > upper_total or disparity_2020 < low_total) and (disparity_2020 > upper_incumbent or disparity_2020 < low_incumbent):
    print(f'The disparity between the articles written about trump and biden is greater than two standard diviations way from the mean making it statistically abnormal.')
elif (disparity_2020 > upper_total or disparity_2020 < low_total) and (low_incumbent <= disparity_2020 <= upper_incumbent):
    print(f'The disparity between the articles written about trump and biden is greater than two standard diviations way from the mean for all elections but less than two standard deviations way from the mean for incumbents making the disparity normal')
else:
    print(f'The disparity between the articles written about trump and biden is less than two standard diviations way from the mean making the discrepancy normal.') 

