# WodUp Scraper
Using python to scrape workout data from [WodUp](https://www.wodup.com/).

<img width=400 src="https://github.com/hnagib/WodUp-Scraper/blob/master/img/logo.png">

:clipboard: Usage Instructions
--------------------------------
1. Check the version of your Chrome browser and download the appropriate chromedriver executable from [here](https://chromedriver.chromium.org/downloads) into the `src` directory. The one included in this repo is for Chrome v84.
2. Run `make install-env` command from the root of this repository set up the `wodup` environment 
3. Make sure you have a valid WodUp login. Note the email address and password you use to login
4. Follow example in [`notebooks/hn-wodup-crawler.ipynb`](https://nbviewer.jupyter.org/github/hnagib/WodUp-Scraper/blob/master/notebooks/hn-wodup-crawler.ipynb)

:open_file_folder: Repo Organization
--------------------------------

    ├── src                     
    │   ├── wodupscraper.py                                 <-- wodup scraper    
    │   └── chromedriver                                    <-- chromedriver executable (v84)      
    │
    ├── data                                                <-- saved scraped data
    │   ├── hasannagib-back-squat.csv                     
    │   ├── hasannagib-front-squat.csv                    
    │   ├── hasannagib-deadlift.csv                       
    │   ├── hasannagib-barbell-bench-press.csv                
    │   └── ...            
    │
    ├── notebooks          
    │   ├── hn-wodup-crawler.ipynb                          <-- using wodupscraper.py
    │   └── ...            
    │
    ├── Makefile                                            <- Makefile with commands to automate installation of python environment
    ├── requirements.txt                                    <- List of python packages required     
    ├── README.md
    └── .gitignore         

:blue_book: Example Usage
--------------------------------
For a detailed example check out this [notebook](https://nbviewer.jupyter.org/github/hnagib/WodUp-Scraper/blob/master/notebooks/hn-wodup-crawler.ipynb). It goes over how to pull data for multiple users and compare progress. 

<table style="width:100%">
  <tr>
    <th><img alighn="left" width="350" src="https://github.com/hnagib/WodUp-Scraper/blob/master/img/back-squat-example.png">
</th>
    <th><img align="right" width="350" src="https://github.com/hnagib/WodUp-Scraper/blob/master/img/prplot.png">
</th>
  </tr>

</table>


The scraper sources strength workout data from user movement pages:`https://www.wodup.com/{user}/movements/{movement}`. This might not be the cleanest place to scrape the data from. I have not explored options for scraping from individual workout pages yet. 

Here is an example of how to pull deadlift logs:
```python
from getpass import getpass
from wodupscraper import WodUp

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
