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

```python
email = 'hasan.nagib@gmail.com'
password = getpass('Enter WodUP password:')
movements = ['front-squat', 'back-squat', 'deadlift', 'barbell-bench-press']

# Log into WodUp
wu = WodUp(email, password, url=f'http://wodup.com/{user}')
time.sleep(2)

for movement in movements:
    wu.get_log(movement)
    wu.clean_log(movement)
    
# Raw scraped data
wu.raw_logs['deadlift']

# Cleaned scraped data
wu.logs['deadlift']

# Exploded view
wu.gen_movement_hist('deadlift')
```
