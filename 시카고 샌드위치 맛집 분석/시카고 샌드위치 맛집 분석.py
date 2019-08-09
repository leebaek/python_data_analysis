#!/usr/bin/env python
# coding: utf-8

# # 시카고 샌드위치 맛집 분석

# In[1]:


from bs4 import BeautifulSoup
from urllib.request import urlopen, urljoin


# ###### * 전체 html 코드 받기

# In[2]:


url = 'http://www.chicagomag.com/Chicago-Magazine/November-2012/Best-Sandwiches-Chicago/'

html = urlopen(url)
soup = BeautifulSoup(html, "html.parser")

soup


# In[3]:


# 'div'태그의 class가 'sammy'인 것을 출력
print(soup.find_all('div', 'sammy'))


# In[4]:


# url에 있는 맛집의 수가 50개이므로 50이 나온다.
len(soup.find_all('div', 'sammy'))


# In[5]:


# 맛집 rank 
print(soup.find_all('div', 'sammy')[0])


# ### * 원하는 데이터 추출하고 정리하기

# In[6]:


tmp_one = soup.find_all('div', 'sammy')[0]
type(tmp_one)
# bs4.element.Tag


# In[7]:


tmp_one.find(class_='sammyRank')
# <div class="sammyRank">1</div>


# ###### * 랭킹 값 추출

# In[8]:


tmp_one.find(class_='sammyRank').get_text()
# '1'


# ###### * 메뉴 이름과 가게 이름 추출(BLT, Old Oak Tap)

# In[9]:


tmp_one.find(class_='sammyListing').get_text()
# 'BLT\r\nOld Oak Tap\nRead more '


# In[10]:


# a태그에서 href정보로 클릭했을 때 연결될 주소
tmp_one.find('a')['href']


# ### * Regular Express(정규식)

# In[8]:


import re # 정규식

tmp_string = tmp_one.find(class_='sammyListing').get_text()
# 'BLT\r\nOld Oak Tap\nRead more '

re.split(('\n|\r\n'), tmp_string) # \n이거나 \r\n이면 분리시키겠다는 의미

print(re.split(('\n|\r\n'), tmp_string)[0])
print(re.split(('\n|\r\n'), tmp_string)[1])


# ###### * 메뉴 명과 가게 이름을 출력한다.

# In[9]:


rank = []
main_menu = []
cafe_name = []
url_add = []

list_soup = soup.find_all('div', 'sammy')

for item in list_soup:
    rank.append(item.find(class_='sammyRank').get_text())
    # 순위 append
    
    tmp_string = item.find(class_='sammyListing').get_text()
    
    main_menu.append(re.split(('\n|\r\n'), tmp_string)[0])
    # 메뉴 명 append
    cafe_name.append(re.split(('\n|\r\n'), tmp_string)[1])
    # 가게 이름 append
    
    url_add.append(urljoin(url, item.find('a')['href']))
    # url append


# In[10]:


rank
main_menu
cafe_name
url_add


# ###### * 순위, 메뉴, 가게, URL 추출한 내용을 데이터프레임에 정리

# In[11]:


import pandas as pd

data = {'Rank':rank, 'Menu':main_menu, 'Cafe':cafe_name, 'URL':url_add}
df = pd.DataFrame(data)
df


# In[12]:


# columns 순서 재배치
df = pd.DataFrame(data, columns=['Rank','Cafe','Menu','URL'])
df


# In[13]:


# df.to_csv('best_sandwiches_list_chicago.csv', sep=',', encoding='utf-8')


# ### * 다수의 웹 페이지에 자동으로 접근해서 정보 추출

# In[14]:


df = pd.read_csv('best_sandwiches_list_chicago.csv', index_col=0)
df.head()


# ###### * 위 표에서 URL column에 있는 내용을 읽어서 각각 가게주소, 샌드위치 가격, 연락처를 얻는다.

# In[15]:


df['URL'][0]


# In[16]:


# 1등 메뉴와 식당의 URL
html = urlopen(df['URL'][0])
soup_tmp = BeautifulSoup(html, "html.parser")
soup_tmp


# In[17]:


# 주소, 가격, 연락처
print(soup_tmp.find('p', 'addy'))


# In[18]:


# 텍스트만 추출
price_tmp = soup_tmp.find('p', 'addy').get_text()
price_tmp


# In[19]:


# 텍스트 분리시키기 -> list로 추출
price_tmp.split()


# In[20]:


# list에서 가격만 추출
price_tmp.split()[0]


# In[21]:


# 추출한 가격에서 . 빼기
price_tmp.split()[0][:-1]


# In[22]:


# .join(문자열을 리스트로) <=> .split(리스트를 문자열로)
' '.join(price_tmp.split()[1:-2])


# In[23]:


df.head()


# In[24]:


# 반복문으로 3위까지의 홈페이지 크롤링
price = []
address = []

for n in df.index[:3]:
    html = urlopen(df['URL'][n])
    soup_tmp = BeautifulSoup(html, 'lxml')
    
    gettings = soup_tmp.find('p', 'addy').get_text()
    
    price.append(gettings.split()[0][:-1])
    address.append(' '.join(gettings.split()[1:-2]))


# In[25]:


# 1,2,3위의 메뉴 가격
price


# In[26]:


# 1,2,3위의 가게 주소
address


# ### * 상태 진행바 생성하여 50개 웹 페이지 정보 가져오기

# In[27]:


from tqdm import tqdm_notebook

price = []
address = []

for n in tqdm_notebook(df.index):
    html = urlopen(df['URL'][n])
    soup_tmp = BeautifulSoup(html, 'lxml')
    
    gettings = soup_tmp.find('p', 'addy').get_text()
    
    price.append(gettings.split()[0][:-1])
    address.append(' '.join(gettings.split()[1:-2]))


# In[28]:


# 1~50위 가격
price


# In[29]:


# 1~50위 주소
address


# In[30]:


df['Price'] = price
df['Address'] = address

df.loc[:, ['Rank', 'Cafe', 'Menu', 'Price', 'Address']]
df.set_index('Rank', inplace=True) # Rank를 index로 잡기
df.head()


# In[31]:


# df.to_csv('best_sandwiches_list_chicago2.csv', sep=',', encoding='utf-8')


# ### * 맛집 위치를 지도에 표기

# In[42]:


import folium
import googlemaps
import numpy as np


# In[33]:


df = pd.read_csv('best_sandwiches_list_chicago2.csv', index_col=0)
df.head()


# In[34]:


gmaps_key = "*****"
gmaps = googlemaps.Client(key=gmaps_key)


# In[39]:


df['Address'][1]


# ###### * 50개 맛집의 위도, 경도 정보를 받아오기

# In[40]:


df['Address']


# In[53]:


lat = []
lng = []

for n in tqdm_notebook(df.index): # df.index : rank column 1~50
    if df['Address'][n] != 'Multiple': # 1~50위 맛집이 Multiple이 아닌 경우만
        target_name = df['Address'][n]+ ' ' + 'Chicago'
        gmaps_output = gmaps.geocode(target_name)
        location_output = gmaps_output[0].get('geometry')
        lat.append(location_output['location']['lat'])
        lng.append(location_output['location']['lng'])
        
    else:
        lat.append(np.nan)
        lng.append(np.nan)


# In[67]:


# df의 column에 lat, lng추가
df['lat'] = lat
df['lng'] = lng


# ###### * 1위 가게의 위치

# In[68]:


mapping = folium.Map(location=[df['lat'].mean(), df['lng'].mean()], zoom_start=11)
folium.Marker([df['lat'].mean(), df['lng'].mean()], popup='center').add_to(mapping)
mapping


# ###### * 1~50위 가게의 위치

# In[69]:



mapping = folium.Map(location=[df['lat'].mean(), df['lng'].mean()], zoom_start=11)

for n in df.index:
    if df['Address'][n] != 'Multiple':
        folium.Marker([df['lat'][n], df['lng'][n]], popup=df['Cafe'][n]).add_to(mapping)
        # 마커 생성, popup : 마커를 눌렀을 때, 나타나는 글자
        
mapping

