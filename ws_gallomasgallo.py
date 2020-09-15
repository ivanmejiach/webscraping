
# coding: utf-8

# In[4]:


from requests import get
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display


# In[5]:


def get_url_detalle():
    web_main = "http://catalogope.gallomasgallo.com/"
    response = get(web_main)
    page_soup = BeautifulSoup(response.text, 'lxml')
    pag_principal = page_soup.find_all('li',{'class':'has-sublist'})
    pag_menu=pag_principal[0].findAll('li',{'class':'has-sublist'}) 
    
    rows_url=[]
    for p in pag_menu:
        sub_p = p.findAll('a',{'class':'lastLevelCategory'})
        for sp in sub_p:
            row= [sp.get("href"),sp.text,p.a.text] 
            rows_url.append(row)
            #print(sp.get("href")+"--"+sp.text+"--"+p.a.text)
    df_url = pd.DataFrame(rows_url, columns=['Url_Grupo','Sub_Grupo','Grupo'])     
    return df_url        
        


# In[3]:


get_url_detalle()
#http://catalogope.gallomasgallo.com/421_pantallas#/pageSize=12&viewMode=grid&orderBy=0&pageNumber=1


# In[6]:


def get_url_producto(v_url):
    web_main = "http://catalogope.gallomasgallo.com"
    my_url = web_main+ v_url
    browser = webdriver.Chrome(executable_path=r"chromedriver.exe") #"D:\Chrome\chromedriver.exe"
    browser.get(my_url)
    all_hover_elements = browser.find_elements_by_class_name("picture")

    rows =[]
    for hover_element in all_hover_elements:    
        a =  hover_element.find_element_by_tag_name("a")    
        product_link = a.get_attribute("href")
        rows.append([product_link])

    browser.quit()
    return rows


# In[8]:


def get_datos(v_url,v_grupo,v_subgrupo):
    import requests
    from scrapy.http import TextResponse

    url = v_url
    user_agent = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58: .0.3029.110 Chrome/58.0.3029.110 Safari/537.36'}

    r = requests.get(url,headers=user_agent)
    response2 = TextResponse(r.url, body=r.text, encoding='utf-8')

    p_normal = response2.xpath('//div[@class="prices"]/div/span//text()').extract()[0].strip()
    t_desc = response2.xpath('//div[@class="product-essential"]/div/h1//text()').extract()[0].strip()
    
    t_marca=''
    if len(response2.xpath('//div[@class="manufacturers"]/span/a//text()'))>0:
        t_marca = response2.xpath('//div[@class="manufacturers"]/span/a//text()').extract()[0].strip()
    else:   
        tabla = response2.xpath('//div[@class="productTabs-body"]/div/div/div/table[@class="data-table"]/tbody/tr')
        for t in tabla:
            tag = t.xpath('td//text()').extract()
            titulo = tag[0].strip()
            desc = tag[1].strip()
            if titulo.upper()=='MARCA':
                t_marca=desc
                break
                    
    skuId = response2.xpath('//div[@class="additional-details"]/div[@class="sku"]/span[@class="value"]//text()').extract()[0].strip()
    t_modelo = response2.xpath('//div[@class="additional-details"]/div[@class="gtin"]/span[@class="value"]//text()').extract()[0].strip()
    
    row = [v_grupo,v_subgrupo,skuId,t_marca,t_desc,p_normal,t_modelo,v_url]
    return row        


# In[9]:


df_url_grupos = get_url_detalle()

cont=0
for index,i in df_url_grupos.iterrows():
    url_grupo   = i["Url_Grupo"]
    sub_grupo   = i["Sub_Grupo"]
    grupo       = i["Grupo"]
    rows=[]    
    url_productos= get_url_producto(url_grupo)
    print(url_grupo)
    for u in url_productos:
        print(u[0])
        datos = get_datos(u[0],grupo,sub_grupo)            
        rows.append(datos)
    df_rows = pd.DataFrame(rows, columns=['Grupo','Sub_Grupo','SkuId','Marca','Nombre' ,'PrecioNormal','Modelo','Url_Producto'])    
            
    if cont==0:
        df_result = df_rows
    df_result = df_result.append(df_rows)    
    cont +=1   


# In[10]:


import datetime
i = datetime.datetime.now()
fecha= i.strftime('%Y%m%d')
filename = "galloMasgallo_"+ fecha +".csv"
df_result.to_csv(filename, sep='|', encoding='utf-8',index=False)
#################################### fin ###############################


# In[167]:


import requests
from scrapy.http import TextResponse

url = "http://catalogope.gallomasgallo.com/radio-para-carro-sony-cxsg124su"
user_agent = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58: .0.3029.110 Chrome/58.0.3029.110 Safari/537.36'}

r = requests.get(url,headers=user_agent)
response2 = TextResponse(r.url, body=r.text, encoding='utf-8')

#precio = response2.xpath('//div[@class="prices"]/div/span//text()').extract()[0].strip()
#nombre = response2.xpath('//div[@class="product-essential"]/div/h1//text()').extract()[0].strip()
if len(response2.xpath('//div[@class="manufacturers"]/span/a//text()'))>0:
    marca = response2.xpath('//div[@class="manufacturers"]/span/a//text()').extract()[0].strip()
else:     
    for t in tabla:
        tag = t.xpath('td//text()').extract()
        titulo = tag[0].strip()
        desc = tag[1].strip()
        if titulo.upper()=='MARCA':
            marca=desc
        #print (titulo +'-->'+desc)
marca
    
sku = response2.xpath('//div[@class="additional-details"]/div[@class="sku"]/span[@class="value"]//text()').extract()[0].strip()
modelo = response2.xpath('//div[@class="additional-details"]/div[@class="gtin"]/span[@class="value"]//text()').extract()[0].strip()
sku


# In[128]:


######### for each de table #########
tabla = response2.xpath('//div[@class="productTabs-body"]/div/div/div/table[@class="data-table"]/tbody/tr')

for t in tabla:
    tag = t.xpath('td//text()').extract()
    titulo = tag[0].strip()
    desc = tag[1].strip()
    print (titulo +'-->'+desc)
len(tabla)

