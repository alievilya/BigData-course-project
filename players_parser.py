# !pip install beautifulsoup4
from bs4 import BeautifulSoup
import urllib.request
import tqdm
import pandas as pd
import re


def gethrefs():
  a_hrefs = []
  pages_range = range(2388) #2388
  for page_num in tqdm.tqdm(pages_range):
    url = "https://www.sports.ru/football/sportsman/?page={}".format(page_num)
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
        a_str += 'career'
        a_hrefs.append(a_str)

  return a_hrefs



def parse_page(url):
  player_name = 'None'
  followers = '0'

  try: 
    page_files = urllib.request.urlopen(url)
  except:
    print('page_not_found')
    return None
  file_data = ""
  for line in page_files:
    decoded_line = line.decode("utf-8")
    file_data += decoded_line
  soup = BeautifulSoup(file_data, 'html.parser')
  name_div = soup.find_all('div', class_='descr')
  # followers = soup.find_all('span', class_='count-less') 
  followers_span = soup.find("span", class_="count")
  
  # for f in followers_span:
  try:
    followers = followers_span.text
  except:
    print('err in followers')
    followers = '0'  
# name_str = soup.find('div').getText()
  for n in name_div:
    player_name = n.text
  try:
    df_football_player2 = pd.read_html(url)
  except:
    return None
  last_table = df_football_player2[-1].iloc[[-1]]

  info_df2 = df_football_player2[0].T
  info_df2 = info_df2.iloc[[1]]

  last_table.insert(0, "Name", player_name, True)
  last_table = last_table.reset_index()
  last_table.insert(1, "Followers", followers, True)
  last_table = last_table.reset_index()
  last_table.drop([0], axis=1, inplace=True)

  info_df2 = info_df2.reset_index()
  res_df = pd.concat([last_table, info_df2], axis=1, ignore_index=True)
  res_df.drop([0], axis=1, inplace=True)
  res_df.columns = range(res_df.shape[1])
  return res_df


def return_age(df, col_n=12):
  st = df.iloc[0,col_n]
  data_birth = st.split('|')
  age = data_birth[-1]
  match = re.search(r'\d\d', age)
  try:
    age = match.group()
  except:
    print('age none')
    return 'None'
  return age


def return_weight_height(df):
  el = df.iloc[0,-1]
  el_arr = el.split('|')
  if len(el_arr) == 1:
    return el_arr, 'None'
  else:
    
    weight = el_arr[1]
    height = el_arr[0]
  # match = re.search(r'\d\d', age)
  # age = match.group()
    return height, weight


def return_club_position(df):
  n_columns = df.shape[1]
  stroka = df.iloc[0,n_columns-2].split('|')
  if len(stroka) == 1:
    club = 'None'
    return club, stroka
  else:
    club, position = stroka
    return club, position

#table = parse_page('https://www.sports.ru/tags/161085686/career')
#a_hrefs = gethrefs()

#with open('all_links.txt', 'w') as wr:
#  for el in a_hrefs:
#    wr.write(el + '\n')

a_hrefs = []
with open('all_links.txt', 'r') as rea:
  for el in rea.readlines():
    a_hrefs.append(el)

table_field_players = []
table_goalkeepers = []

for i in tqdm.tqdm(range(len(a_hrefs))):
  try:
    table = parse_page(a_hrefs[i])
  except:
    print('err in parsing')
    continue
  if table is None:
    continue
  #print(len(table.columns))
  if len(table.columns) == 21:
    age = return_age(table, col_n=17)
    height, weight = return_weight_height(table)
    club, position = return_club_position(table)
    # print(table)
    # table.iloc[0,17] = age
    table.insert(1, "Weight", weight, True)
    table.insert(2, "Height", height, True)
    table.insert(3, "Age", age, True)
    table.insert(4, "Club", club, True)
    table.insert(5, "Position", position, True)

    table_goalkeepers.append(table)
  elif len(table.columns) == 16:
    # print(table)
    age = return_age(table, col_n=12)
    height, weight = return_weight_height(table)
    club, position = return_club_position(table)
    # table.iloc[0,12] = age
    # table.iloc[0,-1] = height

    table.insert(1, "Weight", weight, True)
    table.insert(2, "Height", height, True)
    table.insert(3, "Age", age, True)
    table.insert(4, "Club", club, True)
    table.insert(5, "Position", position, True)

    # table = table.reset_index()
    table_field_players.append(table)

res_field_players = pd.concat(table_field_players, axis=0, ignore_index=True)
res_goalkeepers = pd.concat(table_goalkeepers, axis=0, ignore_index=True)

res_field_players.to_csv('res_field_players.csv', index=False, encoding='utf-8-sig')
res_goalkeepers.to_csv('res_goalkeepers.csv', index=False, encoding='utf-8-sig')