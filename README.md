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
# Log into WodUp
email = 'hasan.nagib@gmail.com'
password = getpass('Enter WodUP password:')
wu = WodUp(email, password, url=f'http://wodup.com/{user}')
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
