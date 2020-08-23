# WodUp Scraper
Using python to scrape workout data from [WodUp](https://www.wodup.com/).

:open_file_folder: Repo Organization
--------------------------------

    ├── src                     
    │   ├── wodupscraper.py                   <-- wodup scraper    
    │   └── chromedriver                      <-- chromedriver executable (v84)      
    │
    ├── notebooks          
    │   ├── hn-wodup-crawler.ipynb            <-- using wodupscraper.py
    │   └── ...            
    │
    ├── Makefile                              <- Makefile with commands to automate installation of python environment
    ├── requirements.txt                      <- List of python packages required     
    ├── README.md
    └── .gitignore         

:blue_book: Example usage
--------------------------------
For a detailed example check out this [notebook](https://github.com/hnagib/WodUp-Scraper/blob/master/notebooks/hn-wodup-crawler.ipynb). It goes over how to pull data for multiple users and compare progress. 

<img width="600" height="360" src="https://github.com/hnagib/WodUp-Scraper/blob/master/img/back-squat-example.png">

Currently the scraper sources strength workout data from user movement pages. e.g. https://www.wodup.com/hasannagib/movements/barbell-bench-press. This might not be the cleanest place to scrape the data from. I have not explored options for scraping from individual workout pages yet. 

Here is an example of how to pull deadlift logs:
```python
# Log into WodUp
email = 'hasan.nagib@gmail.com'
password = getpass('Enter WodUP password:')
wu = WodUp(email, password, url='http://wodup.com/hasannagib}')
time.sleep(2)
    
# Raw scraped data
wu.get_log('deadlift')
wu.raw_logs['deadlift']

# Cleaned scraped data
wu.clean_log('deadlift')
wu.logs['deadlift']

# Exploded view
wu.gen_movement_hist('deadlift')
```
