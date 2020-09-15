
# coding: utf-8

# In[144]:


from requests import get
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display


# In[251]:


def get_url_detalle():
    web_main = "https://www.oechsle.pe/"
            
    rows = ['https://www.oechsle.pe/tecnologia/tv-video'
            ,'https://www.oechsle.pe/tecnologia/computo'
            ,'https://www.oechsle.pe/tecnologia/audio'
            ,'https://www.oechsle.pe/tecnologia/videojuegos'
            ,'https://www.oechsle.pe/tecnologia/telefonia'
            ,'https://www.oechsle.pe/electrohogar/climatización'
            ,'https://www.oechsle.pe/electrohogar/cocina'
            ,'https://www.oechsle.pe/electrohogar/cuidado-personal'
            ,'https://www.oechsle.pe/electrohogar/electrodomesticos'
            ,'https://www.oechsle.pe/electrohogar/lavado'
            ,'https://www.oechsle.pe/electrohogar/refrigeracion']
    return rows 


# In[61]:


import requests
from scrapy.http import TextResponse

url = 'http://www.sodimac.com.pe/sodimac-pe/' 
user_agent = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58: .0.3029.110 Chrome/58.0.3029.110 Safari/537.36'}

r = requests.get(url,headers=user_agent)
response2 = TextResponse(r.url, body=r.text, encoding='utf-8')

row=[]   
grupo_lis = response2.xpath('//ul[@id="levelOneNew"]/li[@class="dropdown-submenu liWidthMenu"]')
grupo_lis[1].extract
# grupo_lis[1].xpath('//div/div/div[@class="panel-collapse collapse in"]').extract()


# In[48]:


from requests import get
from bs4 import BeautifulSoup    
my_url = 'http://www.sodimac.com.pe/sodimac-pe/category/cat1199005/Televisores'
response = get(my_url)
page_soup = BeautifulSoup(response.text, 'lxml')
pag_principal = page_soup.find_all('div',{'class':'jq-section1 section1 panel-heading accordion-toggle p-bottom-heading collapsed'})
pag_principal


# In[145]:


def scrollDown(browser, numberOfScrollDowns):
    body = browser.find_element_by_tag_name("body")
    while numberOfScrollDowns >=0:
        body.send_keys(Keys.PAGE_DOWN)
        numberOfScrollDowns -= 1
    return browser


# In[146]:


def get_url_producto(v_url):
#url = "http://www.tottus.com.pe/tottus/browse/Laptops/cat370021"
    browser = webdriver.Chrome(executable_path=r"chromedriver.exe") #"D:\Chrome\chromedriver.exe"
    browser.get(v_url)
    browser_1 = scrollDown(browser, 300)
    all_hover_elements = browser_1.find_elements_by_class_name("product-etiquetas-price")

    rows =[]
    for hover_element in all_hover_elements:    
        a =  hover_element.find_element_by_tag_name("a")    
        product_link = a.get_attribute("href")
        rows.append([product_link])
        #print (product_link)    
    
    browser.quit()
    return rows


# In[259]:


def get_datos(v_url):
    import requests
    from scrapy.http import TextResponse
    
    url = v_url 
    user_agent = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58: .0.3029.110 Chrome/58.0.3029.110 Safari/537.36'}

    r = requests.get(url,headers=user_agent)
    response2 = TextResponse(r.url, body=r.text, encoding='utf-8')

    row=[]   
    grupo_lis = response2.xpath('//div[@class="bread-crumb"]/ul/li/a//text()').extract()

    if len(grupo_lis)==4:
        t_grupo= grupo_lis[2].strip()
        t_subgrupo= grupo_lis[3].strip()   
    elif len(grupo_lis)==3:
        t_grupo= grupo_lis[1].strip()
        t_subgrupo= grupo_lis[2].strip()
    else :        
        t_grupo= ''
        t_subgrupo=''

    objeto = response2.xpath('//div[@class="fichprod-information"]')

    t_marca = objeto.xpath('div/div[@class="fichprod-prod-brand"]/div/a//text()').extract()[0].strip()
    t_desc = objeto.xpath('div/h1[@class="fichprod-prod-name"]/div//text()').extract()[0].strip()
    skuId = objeto.xpath('div/div/div[@class="skuReference"]//text()').extract()[0].strip()

    p_validate = objeto.xpath('//div[@class="fichprod-prices"]/div/p/em/strong[@class="skuListPrice"]')
    p_normal=''
    if len(p_validate) >0:
        p_normal = objeto.xpath('//div[@class="fichprod-prices"]/div/p/em/strong[@class="skuListPrice"]//text()').extract()[0].strip()

    p_validate = objeto.xpath('//div[@class="fichprod-prices"]/div/p/em/strong[@class="skuBestPrice"]')    
    p_internet=''
    if len(p_validate) >0:
        p_internet = objeto.xpath('//div[@class="fichprod-prices"]/div/p/em/strong[@class="skuBestPrice"]//text()').extract()[0].strip()


    p_validate= response2.xpath('//table[@class="group Ficha-Tecnica"]/tr/td[@class="value-field Modelo"]')
    t_modelo =''
    if len(p_validate) >0:
        t_modelo = response2.xpath('//table[@class="group Ficha-Tecnica"]/tr/td[@class="value-field Modelo"]/text()').extract()[0].strip()

    #p_tarjeta = objeto.xpath('//div[@class="fichprod-prices"]/div[@class="fichprod-price-after"]')
    #p_tarjeta
    row = [t_grupo,t_subgrupo,skuId,t_marca,t_desc,p_normal,p_internet,t_modelo,v_url]
    return row


# In[260]:


rows_url = get_url_detalle()

cont=0
for r in rows_url:
    url_grupo   = r
    rows=[]     
    pagina = get_url_producto(url_grupo)      
    for p in pagina:
        print(p[0])
        datos = get_datos(p[0])
        rows.append(datos)

    df_rows = pd.DataFrame(rows, columns=['Grupo','Sub_Grupo','SkuId','Marca','Nombre' ,'PrecioNormal','PrecioInternet','Modelo','Url_Producto'])    
    
    if cont==0:
        df_result = df_rows
    df_result = df_result.append(df_rows)
    cont +=1


# In[261]:


import datetime
i = datetime.datetime.now()
fecha= i.strftime('%Y%m%d')
filename = "oeshle_"+ fecha +".csv"
df_result.to_csv(filename, sep='|', encoding='utf-8',index=False)


# In[252]:


get_url_detalle()      

