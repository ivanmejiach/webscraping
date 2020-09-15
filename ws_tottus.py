
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


# In[2]:


def get_url_detalle():
    web_main = 'http://www.tottus.com.pe'    

    response = get(web_main)
    page_soup = BeautifulSoup(response.text, 'lxml')
    pag_principal = page_soup.find_all('li',{'class':'sm-ofertas'})
    
    id_lista=[3,4,5]
    rows_url=[]
    rows_grupo=[]
    cont =0
    for l in id_lista:
        p=pag_principal[l].findAll('a')
        
        for i in p:                        
            Id= int(str(cont) +"000"+str(l))
            #print (i.get("class"))                        
            if i.get("class") is not None:
                Id= int(str(cont+1) +"000"+str(l))
                grupo = i.text.strip()         
                row = [Id,grupo]
                rows_grupo.append(row)
                #print (str(Id)+"-->"+grupo) 
                cont +=1
            else:    
                if i.get("href") !="#":                        
                    web_menu = web_main +i.get("href")
                    #print (str(Id)+"-->"+web_menu)
                    row = [Id,web_menu]
                    rows_url.append(row)
            #cont +=1       
    df_url = pd.DataFrame(rows_url, columns=['Id','Url_Grupo'])     
    df_grupo = pd.DataFrame(rows_grupo, columns=['Id','grupo'])     
    
    df_union = pd.merge(df_grupo,df_url , on='Id')
    return df_union


# In[3]:


def scrollDown(browser, numberOfScrollDowns):
    body = browser.find_element_by_tag_name("body")
    while numberOfScrollDowns >=0:
        body.send_keys(Keys.PAGE_DOWN)
        numberOfScrollDowns -= 1
    return browser


# In[4]:


def get_url_producto(v_url):
#url = "http://www.tottus.com.pe/tottus/browse/Laptops/cat370021"
    browser = webdriver.Chrome(executable_path=r"chromedriver.exe") #"D:\Chrome\chromedriver.exe"
    browser.get(v_url)
    browser_1 = scrollDown(browser, 300)
    all_hover_elements = browser_1.find_elements_by_class_name("caption-bottom-wrapper")

    rows =[]
    for hover_element in all_hover_elements:    
        a =  hover_element.find_element_by_tag_name("a")    
        product_link = a.get_attribute("href")
        rows.append([product_link])
        #print (product_link)    
    
    browser.quit()
    return rows


# In[42]:


def get_datos(v_url,v_grupo,v_url_grupo):
    from requests import get
    from bs4 import BeautifulSoup    
    my_url = v_url
    response = get(my_url)
    page_soup = BeautifulSoup(response.text, 'lxml')
    pag_principal = page_soup.find_all('div',{'class':'col-md-12 col-sm-12'})
    
    s_grupo=pag_principal[0].h3.text.split('\n')[-1].strip()
    tit =pag_principal[0].find_all('div',{'class':'title'})
        
    t_desc= tit[0].h5.text.strip()

    t_marca= tit[0].span.text.strip()

    precio =pag_principal[0].find_all('div',{'class':'prices'})
    p_normal = precio[0].span.text.strip().replace('\n','').replace('\t','')

    p2=precio[0].find_all('span',{'class':'red'})
    if len(p2)>0: 
        p_online = p2[0].text.strip().replace('\n','').replace('\t','') 
    else: 
        p_online=''

    p_tarj= pag_principal[0].find_all('div',{'class':'offer-imbatible'}) 
    p_tarjeta=''
    if len(p_tarj)>0:
        get = p_tarj[0].img.get("src")
        if len(get)>0:
            p_tarjeta = get.split('?')[0].split('/')[-1].strip().replace('\n','').replace('\t','')

    skuId= my_url.split('?')[0].split('/')[-1]      
    table= pag_principal[0].find_all('table',{'class','table table-condensed'})
    modelo=''
    if len(table)>0:   
        tr = table[0].find_all('tr')
        if len(tr)>0:
            for t in tr:            
                td= t.find_all('td')
                if len(td)>0:
                    tag = td[0].text.strip()
                    #print(tag)
                    if tag[:6].upper() =='MODELO':
                        modelo =td[1].text.strip()
                        break    

    row=[v_grupo,s_grupo,skuId,t_marca,t_desc,p_normal,p_online,p_tarjeta,modelo,v_url_grupo,v_url]
    return row
    


# In[43]:


df_url_grupos = get_url_detalle()

cont=0
for index,i in df_url_grupos.iterrows():
    url_grupo     = i["Url_Grupo"]
    grupo   = i["grupo"]
    rows=[]    
    url_productos= get_url_producto(url_grupo)
    print(url_grupo)
    for u in url_productos:
        #print(u[0])
        datos = get_datos(u[0],grupo,url_grupo)            
        rows.append(datos)
    df_rows = pd.DataFrame(rows, columns=['Grupo','Sub_Grupo','SkuId','Marca','Nombre' ,'PrecioNormal','PrecioInternet','PrecioTarjeta','Modelo','Url_Grupo','Url_Producto'])    
            
    if cont==0:
        df_result = df_rows
    df_result = df_result.append(df_rows)    
    cont +=1    


# In[45]:


import datetime
i = datetime.datetime.now()
fecha= i.strftime('%Y%m%d')
filename = "tottus_"+ fecha +".csv"
df_result.to_csv(filename, sep='|', encoding='utf-8',index=False)


# In[35]:


from requests import get
from bs4 import BeautifulSoup    
my_url = 'http://www.tottus.com.pe/tottus/product/PARAISO/Colch%C3%B3n-Medall%C3%B3n-con-Ergosoft-Queen-One-Side-+-2-Alm-+-1-Prot/40851686?navAction=jump&navCount=8'
response = get(my_url)
page_soup = BeautifulSoup(response.text, 'lxml')
pag_principal = page_soup.find_all('div',{'class':'col-md-12 col-sm-12'})
tit =pag_principal[0].find_all('div',{'class':'title'})
t_desc= tit[0].h5.text.strip()

t_marca= tit[0].span.text.strip()

precio =pag_principal[0].find_all('div',{'class':'prices'})
p_normal = precio[0].span.text.strip().replace('\n','').replace('\t','')

p2=precio[0].find_all('span',{'class':'red'})
if len(p2)>0: 
    p_online = p2[0].text.strip().replace('\n','').replace('\t','') 
else: 
    p_online=''

p_tarj= pag_principal[0].find_all('div',{'class':'offer-imbatible'}) 
p_tarjeta=''
if len(p_tarj)>0:
    get = p_tarj[0].img.get("src")
    if len(get)>0:
        p_tarjeta = get.split('?')[0].split('/')[-1].strip().replace('\n','').replace('\t','')
      
    
skuId= my_url.split('?')[0].split('/')[-1]      
table= pag_principal[0].find_all('table',{'class','table table-condensed'})
modelo=''
if len(table)>0:   
    tr = table[0].find_all('tr')
    if len(tr)>0:
        for t in tr:            
            td= t.find_all('td')
            tag = td[0].text.strip()
            #print(tag)
            if tag[:6].upper() =='MODELO':
                modelo =td[1].text.strip()
                break

                

                
                
#row=[v_grupo,s_grupo,t_marca,t_desc,p_normal,p_online,p_tarjeta,modelo,v_url_grupo,v_url]


# In[31]:


url = "http://www.tottus.com.pe/tottus/browse/Laptops/cat370021"
browser = webdriver.Chrome(executable_path=r"chromedriver.exe") #"D:\Chrome\chromedriver.exe"

browser.get('https://www.w3.org/')
for a in browser.find_elements_by_xpath('.//a'):
    print(a.get_attribute('href'))

