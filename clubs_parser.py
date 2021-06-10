# !pip install beautifulsoup4
from bs4 import BeautifulSoup
import urllib.request
import tqdm
import pandas as pd
import re


def gethrefs(url_name, num=2):
  a_hrefs = []
  pages_range = range(num) #2388
  for page_num in tqdm.tqdm(pages_range):
    url_ = url_name +"{}"
    url = url_.format(page_num)
    
    try: 
      page_files = urllib.request.urlopen(url)
    except:
      print('page_not_found')
      return None
    file_data = ""
    for line in page_files:
      decoded_line = line.decode("utf-8")
      file_data += decoded_line
    soup = BeautifulSoup(file_data, 'html.parser') #make soup that is parse-able by bs

    for div in soup.find_all('div', class_='overBox' ):
      for a_tag in div.find_all('a', class_='name'):
        a_str = a_tag.get('href')
        # a_str += 'stat/'
        a_hrefs.append(a_str)

  return a_hrefs

def gethrefs_tournament(url_name):
  a_hrefs = []
  # print(url_name)
  try: 
    page_files = urllib.request.urlopen(url_name)
  except:
    print('page_not_found')
    return None
  file_data = ""
  for line in page_files:
    decoded_line = line.decode("utf-8")
    file_data += decoded_line
  soup = BeautifulSoup(file_data, 'html.parser') #make soup that is parse-able by bs
  for div in soup.find_all('ul', class_='options' ):
    for a_tag in div.find_all('a', class_='option'):
      a_str = a_tag.get('href')
      # a_str += 'stat/'
      a_hrefs.append(a_str)

  return a_hrefs


def parse_club_page(url):
  try: 
    page_files = urllib.request.urlopen(url)
  except:
    print('page_not_found')
    return None, None, None

  keyword = "stat/"
  before_keyword, keyword, past_keyword = url.partition(keyword)
  season_year = past_keyword.split('/')[0]
  # print(season_year)

  file_data = ""
  for line in page_files:
    decoded_line = line.decode("utf-8")
    file_data += decoded_line
  soup = BeautifulSoup(file_data, 'html.parser') #make soup that is parse-able by bs

  for div in soup.find_all('h1', class_='titleH1' ):
    try:
      club_name = div.text.split(' - ')[0]
    except:
      return None, None, None
    try:
      league = str(div.text.split('статистика ')[1][:-5])
    except:
      return None, None, None
    # print(league)

  df_all = pd.read_html(url)
  if len(df_all) < 2:
    return None, None, None
  citycountry = df_all[0][1][0].split(', ')
  if len(citycountry) == 2:
    city, country = citycountry
  else:
    country = citycountry
    city = None
  df_club = df_all[1]
  if len(df_club) <= 15:
    return None, None, None

  df_club.insert(1, "Club", club_name, True)
  df_club.insert(2, "League", league, True)
  df_club.drop(["Номер"], axis=1, inplace=True)

  return df_club, city, country


hrefs_clubs = gethrefs(url_name="https://www.sports.ru/football/club/?page=", num=20)
club_names = []
for s in hrefs_clubs:
  keyword = ".ru/"
  before_keyword, keyword, after_keyword = s.partition(keyword)
  club_names.append(after_keyword)

# tournament_name
links_clubs = dict()
for club_name in club_names:
  href_tournament = gethrefs_tournament(url_name="https://www.sports.ru/{}stat".format(club_name))
  links_clubs[club_name] = href_tournament


table_clubs = []
for links in tqdm.tqdm(links_clubs.values()):
  if links is not None:
    for link_season in links:
      # print(link_season)
      if link_season[-7:-1] != '/stat/':
        try:
          club_df, city, country = parse_club_page(link_season)
        except:
          continue
      if club_df is not None:
        table_clubs.append(club_df)
        #print(club_df)


res_clubs = pd.concat(table_clubs, axis=0, ignore_index=True)
#print(res_clubs.head(10))
res_clubs.to_csv('res_clubs.csv', index=False, encoding='utf-8-sig')