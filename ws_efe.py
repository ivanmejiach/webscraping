
# coding: utf-8

# In[1]:


from requests import get
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display


# In[148]:


def get_url_detalle():
    web_main = "https://www.efe.com.pe/"
    response = get(web_main)
    page_soup = BeautifulSoup(response.text, 'lxml')
    pag_principal = page_soup.find_all('ul',{'class':'categoryList'})

    rows=[]
    for menu in pag_principal:
        sub_pag= menu.find_all('li')

        i=0
        for sp in sub_pag:        
            if i>=1:
                sub_category = sp.find_all('a',{'class':'menuLink'})                        
                for sub in sub_category:              
                    url= sub.get('href')                
                    row=[url]
                    rows.append(row)              
            i += 1
    df_url = pd.DataFrame(rows, columns=['Url_Grupo'])     

    maximo = len(df_url)-1
    rows=[]
    for index,i in df_url.iterrows():
        url = i["Url_Grupo"]
        #Id = i["ID"]

        if maximo != index:
            sig = df_url["Url_Grupo"][index+1]
            separar =sig.split('/')[-1]
            extract = sig[:-(len(separar)+1)]        
            if extract !=url :
                row=[url]
                rows.append(row)          
    df_url_fin = pd.DataFrame(rows, columns=['Url_Grupo'])           

    array = df_url_fin.Url_Grupo.unique()
    return array


# In[142]:


maximo = len(df_url)-1
rows=[]
for index,i in df_url.iterrows():
    url = i["Url_Grupo"]
    Id = i["ID"]
        
    if maximo != index:
        sig = df_url["Url_Grupo"][index+1]
        separar =sig.split('/')[-1]
        extract = sig[:-(len(separar)+1)]        
        if extract !=url :
            row=[url]
            rows.append(row)
            #print(url + " ==> "+ extract)            
df_url_fin = pd.DataFrame(rows, columns=['Url_Grupo'])           

array = df_url_fin.Url_Grupo.unique()


# In[150]:


def scrollDown(browser, numberOfScrollDowns):
    body = browser.find_element_by_tag_name("body")
    while numberOfScrollDowns >=0:
        body.send_keys(Keys.PAGE_DOWN)
        numberOfScrollDowns -= 1
    return browser


# In[153]:


def get_url_producto(v_url):
    browser = webdriver.Chrome(executable_path=r"chromedriver.exe") #"D:\Chrome\chromedriver.exe"
    browser.get(v_url)
    browser_1 = scrollDown(browser, 300)
    all_hover_elements = browser_1.find_elements_by_class_name("image")

    rows =[]
    for hover_element in all_hover_elements:    
        a =  hover_element.find_element_by_tag_name("a")    
        product_link = a.get_attribute("href")
        rows.append([product_link])
        #print (product_link)    

    browser.quit()
    return rows


# In[288]:


def get_datos(v_url):
    import requests
    from scrapy.http import TextResponse
    
    url = v_url
    user_agent = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58: .0.3029.110 Chrome/58.0.3029.110 Safari/537.36'}
    
    r = requests.get(url,headers=user_agent)
    response2 = TextResponse(r.url, body=r.text, encoding='utf-8')

    row=[]
    exists = response2.xpath('//div[@class="top namePartPriceContainer"]') 

    if len(exists)>0:    
        grupo_lis = response2.xpath('//div[@id="widget_breadcrumb"]/ul/li/a//text()').extract()

        if len(grupo_lis)==4:
            t_grupo= grupo_lis[2].strip()
            t_subgrupo= grupo_lis[3].strip()   
        elif len(grupo_lis)==3:
            t_grupo= grupo_lis[1].strip()
            t_subgrupo= grupo_lis[2].strip()
        else :        
            t_grupo= v_url.split('/')[-3].upper()
            t_subgrupo=v_url.split('/')[-2].upper()

        t_marca = response2.xpath('//div[@class="Manufacturer"]//text()').extract()[0]
        t_desc = response2.xpath('//div[@class="top namePartPriceContainer"]/div/h1//text()').extract()[0].strip()
        skuId = response2.xpath('//div[@class="top namePartPriceContainer"]/span//text()').extract()[0].strip().split(':')[1]

        p_validate = response2.xpath('//div[@class="top namePartPriceContainer"]/div/span[@class="old_price"]//text()')
        p_normal=''
        if len(p_validate)>0:
            p_normal = response2.xpath('//div[@class="top namePartPriceContainer"]/div/span[@class="old_price"]//text()').extract()[0].strip()

        p_internet = response2.xpath('//div[@class="top namePartPriceContainer"]/div/span[@class="price"]//text()').extract()[0].strip()

        t_modelo=''
        tabla = response2.xpath('//div[@class="content"]/ul/li')
        for t in tabla:
            x= t.xpath('span//text()').extract()
            y= x[0].strip()
            z= x[1].strip()
            if y[:-1].upper() == 'MODELO':
                t_modelo= z
                break

        row = [t_grupo,t_subgrupo,skuId,t_marca,t_desc,p_normal,p_internet,t_modelo,v_url]
    else:
        row = ['','','','','','','','','']
    return row


# In[289]:


rows_url = get_url_detalle()

cont=0
for r in rows_url:
    url_grupo   = r    
    rows=[]    
    url_productos= get_url_producto(url_grupo)
    print(url_grupo)
    for u in url_productos:
        print(u[0])
        datos = get_datos(u[0])            
        rows.append(datos)
    df_rows = pd.DataFrame(rows, columns=['Grupo','Sub_Grupo','SkuId','Marca','Nombre' ,'PrecioNormal','PrecioInternet','Modelo','Url_Producto'])    
            
    if cont==0:
        df_result = df_rows
    df_result = df_result.append(df_rows)    
    cont +=1 


# In[291]:


import datetime
i = datetime.datetime.now()
fecha= i.strftime('%Y%m%d')
filename = "tiendasefe_"+ fecha +".csv"
df_result.to_csv(filename, sep='|', encoding='utf-8',index=False)
#################################### fin ###############################


# In[219]:


tabla = response2.xpath('//div[@class="content"]/ul/li')
for t in tabla:
    x= t.xpath('span//text()').extract()
    y= x[0].strip()
    z= x[1].strip()
    if y[:-1].upper() == 'MODELO':
        modelo= z
        print(y.upper() +" ==> "+z)
        break
        


# In[286]:


import requests
from scrapy.http import TextResponse

#url = 'https://www.efe.com.pe/efe/tv-y-audio/televisores/ultra-hd/tv-sony-ultra-hd-4k-smart-49-kd-49x706e-kd-49x706e'
url= 'https://www.efe.com.pe/efe/c%C3%B3mputo-y-tecnolog%C3%ADa/calculadoras--24/calculadora-casio-fx-9860gii-sd-fx-9860gii-sd'
user_agent = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58: .0.3029.110 Chrome/58.0.3029.110 Safari/537.36'}

r = requests.get(url,headers=user_agent)
response2 = TextResponse(r.url, body=r.text, encoding='utf-8')

row=[]
exists = response2.xpath('//div[@class="top namePartPriceContainer"]') 

if len(exists)>0:
    grupo_lis = response2.xpath('//div[@id="widget_breadcrumb"]/ul/li/a//text()').extract()

    if len(grupo_lis)==4:
        t_grupo= grupo_lis[2].strip()
        t_subgrupo= grupo_lis[3].strip()   
    elif len(grupo_lis)==3:
        t_grupo= grupo_lis[1].strip()
        t_subgrupo= grupo_lis[2].strip()
    else :        
        t_grupo= v_url.split('/')[-3].upper()
        t_subgrupo=v_url.split('/')[-2].upper()
    
    t_marca = response2.xpath('//div[@class="Manufacturer"]//text()').extract()[0]
    t_desc = response2.xpath('//div[@class="top namePartPriceContainer"]/div/h1//text()').extract()[0].strip()
    skuId = response2.xpath('//div[@class="top namePartPriceContainer"]/span//text()').extract()[0].strip().split(':')[1]

    p_validate = response2.xpath('//div[@class="top namePartPriceContainer"]/div/span[@class="old_price"]//text()')
    p_normal=''
    if len(p_validate)>0:
        p_normal = response2.xpath('//div[@class="top namePartPriceContainer"]/div/span[@class="old_price"]//text()').extract()[0].strip()

    p_internet = response2.xpath('//div[@class="top namePartPriceContainer"]/div/span[@class="price"]//text()').extract()[0].strip()

    t_modelo=''
    tabla = response2.xpath('//div[@class="content"]/ul/li')
    for t in tabla:
        x= t.xpath('span//text()').extract()
        y= x[0].strip()
        z= x[1].strip()
        if y[:-1].upper() == 'MODELO':
            t_modelo= z
            break

    row = [t_grupo,t_subgrupo,skuId,t_marca,t_desc,p_normal,p_internet,t_modelo,v_url]
row


# In[285]:


v_url='https://www.efe.com.pe/efe/tv-y-audio/televisores/ultra-hd/tv-samsung-qled-uhd-4k-smart-55-qn-55q6fam-qn-55q6fam'
v_url.split('/')[-2].upper()
v_url.split('/')[-3].upper()

