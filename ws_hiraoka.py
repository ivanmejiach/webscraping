
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


# # *********** inicio***********

# In[2]:


def get_url_detalle():
    import requests
    from scrapy.http import TextResponse

    web_main = "http://www.hiraoka.com.pe/"
    user_agent = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58: .0.3029.110 Chrome/58.0.3029.110 Safari/537.36'}
                                
    r = requests.get(web_main,headers=user_agent)
    response2 = TextResponse(r.url, body=r.text, encoding='utf-8')

    rows=[]
    pag = response2.xpath('//div[@class="inners"]')
    for p in pag:
        sub_grupo = p.xpath('div[@class="popgrupo"]')

        for s in sub_grupo:
            grupo = s.xpath('div[@class="poptitulogrupo"]//text()').extract()[0].strip()
            #print(re.sub('[\W]+','', s.xpath('div[@class="poptitulogrupo"]//text()').extract()[0].strip()) )

            for a in s.xpath('a[@class="popitem"]'):
                url = web_main+''+ a.xpath('@href').extract()[0].strip()
                sg = a.xpath('text()').extract()[0].strip()
                #re.sub('[\W]+', '', url)
                row=[url , sg , grupo]
                #print(re.sub('[\W]+', '', a.xpath('@href').extract()[0].strip()))

                rows.append(row)        
    df_url = pd.DataFrame(rows, columns=['Url_Grupo','Sub_Grupo','Grupo'])
    return df_url 


# In[3]:


def get_url_producto(v_url):
#url = 'http://www.hiraoka.com.pe/productlist.php?ss=060&t=De%20pie'
    user_agent = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58: .0.3029.110 Chrome/58.0.3029.110 Safari/537.36'}

    web_main = "http://www.hiraoka.com.pe/"
    r = requests.get(v_url,headers=user_agent)
    response2 = TextResponse(r.url, body=r.text, encoding='utf-8')

    rows=[]
    urls = response2.xpath('//div[@class="proditem col-sm-12 col-xs-12"]/div/a//@href').extract()
    for u in urls:
        rows.append( [web_main+''+u])
    return rows    


# In[4]:


def get_datos(v_url,v_grupo,v_subgrupo):
    import requests
    from scrapy.http import TextResponse

    my_url = v_url
    #url = 'http://www.hiraoka.com.pe/viewprod.php?id=P000003015&n=Cocina%20a%20Gas'
    user_agent = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58: .0.3029.110 Chrome/58.0.3029.110 Safari/537.36'}

    r = requests.get(my_url,headers=user_agent)
    response2 = TextResponse(r.url, body=r.text, encoding='utf-8')

    row=[]
    t_nombre=''
    t_marca=''
    t_modelo=''
    skuID=''
    p_normal=''
    p_online=''

    datos = response2.xpath('//div[@class="col-sm-12 col-lg-6 col-md-6"]/div[@class="vpmodelo vptexto"]')
    for d in datos:
        tipo  = d.xpath('span//text()').extract()[0].strip().upper()

        valor=''
        #print(d.xpath('text()').extract())
        if len(d.xpath('text()').extract()) >0:
            valor = d.xpath('text()').extract()[0].strip()

        if tipo.upper() =='MARCA:':
            t_marca = valor
        if tipo.upper() =='MODELO:':
            t_modelo = valor
        if tipo.upper() =='CÃ³DIGO:':
            skuID = valor    
        if tipo.upper() =='PRECIO NORMAL:':
            p_normal = d.xpath('span[@class="tachado"]//text()').extract()[0].upper() 

    online = response2.xpath('//div[@class="col-sm-12 col-lg-6 col-md-6"]/div[@class="blockprecio"]/span[@class="precio"]//text()').extract()
    p_online = online[0].strip()

    nombre = response2.xpath('//div[@class="col-sm-12 col-lg-6 col-md-6"]/div[@class="vpnombre"]//text()').extract()
    t_nombre= nombre[0].strip()+' '+t_marca + ' '+ t_modelo

    row = [v_grupo,v_subgrupo,skuID,t_marca,t_nombre,p_normal,p_online,t_modelo,v_url]  
    return row


# In[591]:


df_url_grupos = get_url_detalle()

cont=0
for index,i in df_url_grupos.iterrows():
    url_grupo     = i["Url_Grupo"]
    grupo   = i["Grupo"]
    sub_grupo = i["Sub_Grupo"]
    rows=[]    
    url_productos= get_url_producto(url_grupo)
    print(url_grupo)
    for u in url_productos:
        #print(u[0])
        datos = get_datos(u[0],grupo,sub_grupo)            
        rows.append(datos)
    df_rows = pd.DataFrame(rows, columns=['Grupo','Sub_Grupo','SkuId','Marca','Nombre' ,'PrecioNormal','PrecioInternet','Modelo','Url_Producto'])    
            
    if cont==0:
        df_result = df_rows
    df_result = df_result.append(df_rows)    
    cont +=1 


# In[592]:


import datetime
i = datetime.datetime.now()
fecha= i.strftime('%Y%m%d')
filename = "hiraoka_"+ fecha +".csv"
df_result.to_csv(filename, sep='|', encoding='utf-8',index=False)
#################################### fin ###############################


# # *********** fin ***********

# In[ ]:


web_main = "http://www.hiraoka.com.pe/"
request_headers = {"Accept-Language": "es-pe,en;q=0.5", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Referer": "http://google.com", "Connection": "keep-alive"}
response = get(web_main,headers=request_headers)
soup  = BeautifulSoup(response.text, 'lxml')
pag_principal = soup.find_all('div',{'class':'inners'})

rows =[]
for p in pag_principal:
    #sub_grupo = p.xpath('div[@class="popgrupo"]')
    sub_grupo = p.find_all('div',{'class':'popgrupo'}) 
    
    for s in sub_grupo:
        #grupo = s.xpath('div[@class="poptitulogrupo"]//text()').extract()[0].strip()
        grupo = s.find_all('div',{'class':'poptitulogrupo'}) 
        
        #print( (grupo[0].text.encode('ascii','ignore')))    
        for a in s.find_all('a',{'class':'replace'}):
            #url = a.xpath('@href').extract()[0].strip()
            url = a.get('href').strip()
            sg = a.text.strip()
            row=[url,sg,grupo[0].text]
            rows.append(row)  
df_url = pd.DataFrame(rows, columns=['Url_Grupo','Sub_Grupo','Grupo'])    


# In[ ]:


from unicodedata import normalize

var=b'\xc3\x83\xc2\xad'
#var.decode('ascii','es')
#var.decode('ascii','ignore')

type(var)

range(128)
#unicodedata.normalize('NFKD', x).encode('ascii','ignore')
#re.sub('\W+','', x)
#x

#city = b'Ribeir\xc3\xa3o Preto'
#print (city.decode('ascii','replace').encode('utf-8'))
#str(var,'ascii',errors='replace')
#var.decode(encoding='utf-8',errors='strict')
#help(bytes)
#type('Ã³ddff')

#unicodedata.normalize('NFKD','Ã³ddff')
#print (unicode("¡Huevos!", encoding='utf-8'))
#string = unicode(raw_input(), 'utf8')


# In[5]:


get_url_detalle()

