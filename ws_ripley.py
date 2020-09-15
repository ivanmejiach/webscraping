
# coding: utf-8

# In[1]:


from requests import get
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
import numpy as np


# In[2]:


def f_url_subCategoria (v_url,grupo):
    response = get(v_url)
    page_soup = BeautifulSoup(response.text, 'lxml')
    pag_principal = page_soup.find_all('div',{'class':'col-xs-12 col-md-6'})
    
    rows =[]
    #data = pd.DataFrame(columns=('grupo','url_sub_grupo' ))
    for x in pag_principal:
        row=[grupo,x.a.get("href")]
        rows.append(row)
        #data.loc[len(data)]=row
        
    pag_principal_i = page_soup.find_all('div',{'class':'col-xs-12 col-md-4'})
    for y in pag_principal_i:
        row=[grupo,y.a.get("href")]
        rows.append(row)
        #data.loc[len(data)]=row 
        
    pag_principal_j = page_soup.find_all('div',{'class':'container'})
    pag= pag_principal_j[1].findAll('a',{'class':'tcbloque'})

    #rows =[]
    for x in pag:
        row=[grupo,x.get("href")]
        rows.append(row)
        #data.loc[len(data)]=row
    return rows
      


# In[3]:


def f_nro_Paginas(v_url): 
    response = get(v_url)
    page_soup = BeautifulSoup(response.text, 'lxml')
    pag_principal = page_soup.find_all('ul',{'class':'pagination'})
    pag = pag_principal[0].find_all('a')

    mayor=0
    for x in pag:
        s= x.text.replace('\t', '').replace('\n', '')
        if s.isdigit():
            if int(s)>= mayor :
                mayor= int(s)
    return mayor       


# In[4]:


def get_url_detalle():
    web_main = 'https://simple.ripley.com.pe'
    grupo =['tv-y-video','electrohogar','celulares','computo','entretenimiento']

    rows_url=[]
    for g in grupo:
        web_menu = web_main +'/'+g

        url_sub_grupo = f_url_subCategoria(web_menu,g)
        #rows_url.append(url_sub_grupo)
        for x in url_sub_grupo:
            fila= x[1]
            if fila.find(".cl")<=0:
                rows_url.append(x)
                #print(x)
    df_url = pd.DataFrame(rows_url, columns=['grupo','Url_Subgrupo'])     
    return df_url 


# In[9]:


def get_datos(v_url):
    from requests import get
    from bs4 import BeautifulSoup
    
    href = v_url          
    response = get(href)
    html_soup = BeautifulSoup(response.text, 'lxml')
    containers = html_soup.find_all('table',{'class','table table-striped'})

    modelo=''

    if len(containers)>0:
        tr = containers[0].find_all('tr')
        if len(tr)>0:
            for t in tr:            
                td= t.find_all('td')
                tag = td[0].text.strip()
                #print(tag)
                if tag.upper()=='MODELO':
                    modelo =td[1].text.strip()
                    break
    return modelo  


# In[6]:


def f_extraccion(v_url_grupo,v_ult_pag,v_grupo):
    min_pag = 1 
    while min_pag <= v_ult_pag:
        url = v_url_grupo +'?page='+str(min_pag)+''
        my_url = url         
        sub_grupo = v_url_grupo.split("/")[-1].upper()
        
        response = get(my_url)
        page_soup = BeautifulSoup(response.text, 'lxml')
        #pag_principal = page_soup.find_all('div',{'class':'product-description'})#
        pag_principal = page_soup.find_all('a',{'class':'catalog-product catalog-item '}) 

        rows =[]
        for p in pag_principal:
            
            i= p.find_all('div',{'class':'product-description'})
            url_prod=p.get("href")
            
            #obtener modelo
            web_main = 'https://simple.ripley.com.pe'
            modelo = get_datos(web_main+url_prod)
            
            marca= i[0].span.text

            nombre_l = i[0].findAll("span",{"class":"js-clamp catalog-product-name"})
            nombre=""
            if len(nombre_l)>0 :
                nombre = nombre_l[0].text.replace('\t', '').replace('\n', '')

            preNormal_l = i[0].findAll("span",{"class":"catalog-product-list-price"})
            preNormal=""
            if len(preNormal_l)>0 :
                preNormal = preNormal_l[0].text.replace('\t', '').replace('\n', '')

            preInternet_l = i[0].findAll("span",{"class":"catalog-product-offer-price best-price "})
            preInternet=""
            if len(preInternet_l)>0 :
                preInternet = preInternet_l[0].text.replace('\t', '').replace('\n', '')

            preTarjeta_l = i[0].findAll("span",{"class":"catalog-product-card-price"})
            preTarjeta=""
            if len(preTarjeta_l)>0 :
                preTarjeta = preTarjeta_l[0].text.replace('\t', '').replace('\n', '')    
                
                
            dscto_l = i[0].findAll("span",{"class":"product-discount-tag"})
            dscto=""
            if len(dscto_l)>0 :
                dscto = dscto_l[0].text.replace('\t', '').replace('\n', '')

            row = [v_grupo,sub_grupo,marca,nombre ,modelo,preNormal,preInternet,preTarjeta,dscto,my_url,url_prod]
            rows.append(row)
            
            df_rows = pd.DataFrame(rows, columns=['Grupo','Sub_Grupo','Marca','Nombre','Modelo' ,'PrecioNormal','PrecioInternet','PrecioTarjeta','Dscto','Url','Url_Producto'])    
            
            if min_pag==1:
                df_result = df_rows
            df_result = df_result.append(df_rows)            
        
        min_pag +=1    
    return df_result    
                          


# In[7]:


df=get_url_detalle()
j=0
for index,i in df.iterrows():
        
    nro_pag = f_nro_Paginas(i["Url_Subgrupo"])
    url     = i["Url_Subgrupo"]
    grupo   = i["grupo"]
    
    print(i["Url_Subgrupo"]+"-->"+str(nro_pag))    
    df_result = f_extraccion(url,nro_pag,grupo)
    
    if j==0 :
        df_result_f=df_result
    df_result_f = df_result_f.append(df_result) 
    j += 1        


# In[8]:


import datetime
i = datetime.datetime.now()
fecha= i.strftime('%Y%m%d')
filename = "ripley_"+ fecha +".csv"
df_result_f.to_csv(filename, sep='|', encoding='utf-8',index=False)


# In[32]:




