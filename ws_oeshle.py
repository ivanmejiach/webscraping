
# coding: utf-8

# In[68]:


from requests import get
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
import numpy as np


# In[2]:


def get_url_detalle():
    web_main = "https://www.oechsle.pe/"
    response = get(web_main)
    page_soup = BeautifulSoup(response.text, 'lxml')
    pag_principal = page_soup.find_all('div',{'class':'MnNonFood'})
    pag = pag_principal[0].find_all('li',{'class':'hmi-submenu-item n1'}) 
    rows =[]
    for p in pag:
        grupo = p.a.text
        sub_pag = p.find_all('a',{'class':'hmi-link n2'})

        for sp in sub_pag: 
            row =[grupo,sp.text.strip(),sp.get("href")]
            rows.append(row)
            #print(sp.get("href")+" ==>"+sp.text.strip())
    df_url = pd.DataFrame(rows, columns=['Grupo','SubGrupo','Url_Subgrupo'])
    return df_url 


# In[106]:


web_main = "https://www.oechsle.pe/"
response = get(web_main)
page_soup = BeautifulSoup(response.text, 'lxml')
pag_principal = page_soup.find_all('body')
#pag_principal = page_soup.find_all('li',{'class','col -xs-6 col -sm-2 '})
#pag = pag_principal[0].find_all('li',{'class':'hmi-submenu-item n1'}) 
pag_principal[0]



# In[107]:


web_main = "https://www.oechsle.pe/tecnologia"
response = get(web_main)
page_soup = BeautifulSoup(response.text, 'lxml')
pag_principal = page_soup.find_all('body')
#pag_principal = page_soup.find_all('div',{'class','container-categorias-dpto'})
#pag = pag_principal[0].find_all('li',{'class':'hmi-submenu-item n1'}) 
pag_principal


# In[157]:


import requests
from scrapy.http import TextResponse
from scrapy.selector import Selector

web_main = "https://www.oechsle.pe"
user_agent = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58: .0.3029.110 Chrome/58.0.3029.110 Safari/537.36'}
#user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}


r = requests.get(web_main,headers=user_agent)
response2 = TextResponse(r.url, body=r.text, encoding='utf-8')

rows=[]
pag = response2.xpath('//ul[@class="menu"]/li[@class="nav-departamento"]')
#pag[0].xpath('div[@id="rotador-categorias-dpto"]')
pag[0].xpath('ul/li/ul')

x = response2.css(".nav-departamento")
y=response2.css('img::attr(lozad)').extract()
y

# Selector(response = response2).xpath('//div[@class="wrapper"]/div[@id="container-categorias-dpto"]').extract()

# for p in pag:
#     #sub_grupo = p.xpath('li').extract()    
#     #print (p.xpath('a//@href').extract())
#     grupo= p.xpath('ul[@class="nav-categorias"]')
#     print (p)
#     for g in grupo:
#         sub_grupo = g.xpath('ul[@class="nav-subcategorias n1"]/li')
#         for s in sub_grupo:
#             a = a.xpath('a//text()').extract()[0].strip()
#             print (a)
#pag[0].xpath('div[@class="active-slider slick-initialized slick-slider"]')

#     for s in sub_grupo:
#         grupo = s.xpath('div[@class="poptitulogrupo"]//text()').extract()[0].strip()
#         #print(re.sub('[\W]+','', s.xpath('div[@class="poptitulogrupo"]//text()').extract()[0].strip()) )

#         for a in s.xpath('a[@class="popitem"]'):
#             url = web_main+''+ a.xpath('@href').extract()[0].strip()
#             sg = a.xpath('text()').extract()[0].strip()
#             #re.sub('[\W]+', '', url)
#             row=[url , sg , grupo]
#             #print(re.sub('[\W]+', '', a.xpath('@href').extract()[0].strip()))

#             rows.append(row)        
#df_url = pd.DataFrame(rows, columns=['Url_Grupo','Sub_Grupo','Grupo'])


# In[115]:


from scrapy.selector import Selector 
from scrapy.http import HtmlResponse

web_main = "https://www.oechsle.pe/tecnologia"
user_agent = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58: .0.3029.110 Chrome/58.0.3029.110 Safari/537.36'}

response = HtmlResponse(url = web_main, body = user_agent) 
Selector(response = response).xpath('//a@href').extract()


# In[10]:


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display
from selenium.common.exceptions import NoSuchElementException
import time

browser = webdriver.Chrome(executable_path=r"chromedriver.exe")
browser.get('https://tienda.plazavea.com.pe/electro/televisores/tv-led')

button = browser.find_elements_by_xpath('//a[@id="clickLoading"]')[0]
button.click()
time.sleep(30)
rows =[]

all_hover_elements = browser.find_elements_by_class_name("g-nombre-prod")

for hover_element in all_hover_elements:        
    product_link = hover_element.get_attribute("href")    
    rows.append([product_link])    
    
browser.quit()
rows


# In[19]:


def get_url_producto(v_url):
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from pyvirtualdisplay import Display
    from selenium.common.exceptions import NoSuchElementException
    import time

    browser = webdriver.Chrome(executable_path=r"chromedriver.exe")
    browser.get(v_url)

    rows =[]
    pages_remaining = True

    i=0
    while pages_remaining:     
        try:
            #Checks if there are more pages with links
            print(pages_remaining)

            next_link = browser.find_elements_by_xpath('//a[@id="clickLoading"]')[0]                
            next_link.click()
            time.sleep(15)                

            print (i)
        except Exception as e:
            pages_remaining = False
            break

            print("error"+ str(e))                  
        i +=1    

    all_hover_elements = browser.find_elements_by_class_name("g-nombre-prod")
    for hover_element in all_hover_elements:        
        product_link = hover_element.get_attribute("href")    
        rows.append([product_link])     
    browser.quit()
    return rows


# In[43]:


def get_datos(v_url,v_grupo,v_sub_grupo):
    row=[]
    my_url = v_url
    response = get(my_url)
    page_soup = BeautifulSoup(response.text, 'lxml')

    containers = page_soup.find_all('body')
    first = containers[0]
    ter =first.findAll('script')
    data = re.findall("vtex.events.addData(.+?);", str(ter[1]), re.S)
    row= json.loads(data[0][1:-1])    
    #nombre=y["pageTitle"]

    moneda_lis = page_soup.find_all('section',{'class':'b12-resum-price'})
    moneda= moneda_lis[0].i.text.strip() 

    modelo=''
    table = page_soup.find_all('table',{'class':'group Especificaciones'})
    if len(table)>0:
        tr=table[0].find_all('tr')

        for t in tr:            
            td= t.td
            tag = t.th.text.strip()
            #print(tag)
            if tag.upper()=='MODELO':
                modelo =td.text.strip()
                break

    row.update({'model':modelo})
    row.update({'group':v_grupo})
    row.update({'sub_group':v_sub_grupo})
    row.update({'moneda':moneda})
    return row     


# In[45]:


df = get_url_detalle()

cont=0
for index,i in df.iterrows():
    url_grupo   = i["Url_Subgrupo"]
    grupo       = i["Grupo"]
    sub_grupo   = i["SubGrupo"]
    rows=[] 
    
    pagina = get_url_producto(url_grupo)  
    
    for p in pagina:
        datos = get_datos(p[0],grupo,sub_grupo)
        rows.append(datos)

    df_rows = pd.DataFrame(rows, columns=['pageCategory','pageDepartment','pageFacets' ,'pageUrl','productBrandId'
                                        ,'productBrandName','productCategoryId','productCategoryName','productDepartmentId','productDepartmentName','productId'
                                        ,'productListPriceFrom','productListPriceTo','productName','productPriceFrom','productPriceTo','productReferenceId'
                                        ,'skuStocks','model','group','sub_group','moneda'])    
    
    if cont==0:
        df_result = df_rows
    df_result = df_result.append(df_rows)
    cont +=1


# In[46]:


import datetime
i = datetime.datetime.now()
fecha= i.strftime('%Y%m%d')
filename = "plazavea_"+ fecha +".csv"
df_result.to_csv(filename, sep='|', encoding='utf-8',index=False)
#============================== fin ==============================


# In[30]:


row=[]
my_url = 'https://tienda.plazavea.com.pe/televisor-lg-led-49-fhd-smart-tv-49lj5500/p'
response = get(my_url)
page_soup = BeautifulSoup(response.text, 'lxml')

containers = page_soup.find_all('body')
first = containers[0]
ter =first.findAll('script')
data = re.findall("vtex.events.addData(.+?);", str(ter[1]), re.S)
row= json.loads(data[0][1:-1])    

modelo=''
table = page_soup.find_all('table',{'class':'group Especificaciones'})
if len(table)>0:
    tr=table[0].find_all('tr')

    for t in tr:            
        td= t.td
        tag = t.th.text.strip()
        #print(tag)
        if tag.upper()=='MODELO':
            modelo =td.text.strip()
            break

row.update({'model':modelo})
row.update({'group':'XXXXX'})
row.update({'sub_group':'YYYY'})
moneda = page_soup.find_all('section',{'class':'b12-resum-price'})
moneda[0].i 


# In[44]:


row=get_datos('https://tienda.plazavea.com.pe/televisor-samsung-led-49-fhd-smart-tv-ua49j5200akxx/p','xxx','yyy')
row


# In[9]:


from scrapy import Selector
sel = Selector(response2)
sel.xpath("//h1")
sel.xpath("//h1").extract()         # this includes the h1 tag
sel.xpath("//h1/text()").extract() 

