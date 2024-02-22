from flask import Flask,render_template,request
import requests
from bs4 import BeautifulSoup
import pandas as pd

app = Flask(__name__)

headers = {
    'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0"
}

categories=['/hardware/processadores', '/hardware/placa-m-e', '/hardware/memorias', '/hardware/placa-de-video', 
            '/hardware/hard-disk-e-ssd', '/hardware/ssd','/hardware/gabinete', '/hardware/fonte', 
            '/hardware/cabos-extensores-sleeved', '/hardware/cooler-processador', '/hardware/ventoinhas-e-casemod', 
            '/hardware/pasta-termica-e-refrigerantes', '/hardware/placas-de-som', '/hardware/drive-optico', 
            '/hardware/acessorios-para-gabinete']
categories_names = ['Processadores', 'Placa mãe', 'Memorias', 'Placa de video', 'Hard disk e ssd', 'Ssd', 'Gabinete', 
                    'Fonte', 'Cabos extensores sleeved', 'Cooler de Processador', 'Ventoinhas e casemod', 
                    'Pasta termica e refrigerantes', 'Placas de som', 'Drive optico', 'Acessorios para gabinete']

dict_categories = {'name_complete':categories,'name_clean':categories_names}

def verifyItemName(category_name:str):
    category_name = category_name.replace(' ','-')
    for category in categories:
        if category_name.casefold() in category:
            print(category)
            return category

def limpar_sort(dt):
    print('limpando...')
    try:
        dt_limpo = dt.dropna(subset=['Preço à Vista(R$)'])
        dt['Preço à Vista(R$)'] = dt['Preço à Vista(R$)'].str.replace('.', '')
        dt['Preço à Vista(R$)'] = dt['Preço à Vista(R$)'].str.replace(',', '.')
        dt['Preço à Vista(R$)'] = dt['Preço à Vista(R$)'].astype(float)
        dt_limpo = dt.sort_values(by=['Preço à Vista(R$)'])
        dt_limpo['Preço à Vista(R$)'] = dt['Preço à Vista(R$)'].map('R$ {}'.format)
    except:
        print('.')

    try:
        dt_limpo = dt.drop(['Unnamed: 0.1','Unnamed: 0'],axis=1)
    except:
        pass

    dt_limpo.to_excel(r'C:\Users\joaor\OneDrive\Área de Trabalho\TodosProdutos.xlsx',index=False)
    
def get_item_by_category(category_name:str):
    dict_produtos = {}
    nome_produto = []
    preco_a_vista = []
    resultVerify = verifyItemName(category_name)

    if not resultVerify == None: 
        url = f'https://www.pichau.com.br{resultVerify}'
        site = requests.get(url,headers=headers)
        soup = BeautifulSoup(site.content,'html.parser')
        ultima_pagina = soup.find_all('button',class_='MuiButtonBase-root MuiPaginationItem-root MuiPaginationItem-page MuiPaginationItem-textPrimary MuiPaginationItem-sizeLarge')[4].get_text()

        for i in range(1,int(ultima_pagina)+1):
            url_pag = f'{url}?page={i}'
            site = requests.get(url_pag,headers=headers)
            soup = BeautifulSoup(site.content,'html.parser')
            categories_items = soup.find_all("div",class_="MuiGrid-root MuiGrid-container MuiGrid-spacing-xs-3")
            for item in categories_items:
                content = item.find_all("div",class_="MuiGrid-item")
                for item_div in content:
                    try:
                        placas_infoname = item_div.find('a').find('div',class_='MuiCardContent-root').find('h2',class_='MuiTypography-root').get_text()
                        nome_produto.append(placas_infoname)
                    except:
                        placas_infoname = 'Not Found'
                    #--numbers
                    try:
                        placas_infopreco = item_div.find('a').find('div',class_='MuiCardContent-root').find('div').find('div').find('s').get_text().replace('R$ ','')
                        preco_a_vista.append(placas_infopreco)
                    except:
                        placas_infopreco = 'Indisponível'

            dict_produtos['Nome do Produto'] = nome_produto
            dict_produtos['Preço à Vista(R$)'] = preco_a_vista
            produtosDf = pd.DataFrame.from_dict(dict_produtos,orient='index')
            produtosDf = produtosDf.transpose()
            limpar_sort(produtosDf)

    return dict_produtos

response = ''
response_dict = ''
@app.route('/')
def homepage():
    try:
        selected_category_name = request.args['select_categories']
        if selected_category_name:
            response = 'Success - Arquivo Excel Salvo na Área de Trabalho'
            response_dict = get_item_by_category(selected_category_name)
    except:
        response = ''

    return render_template('homepage.html',categories=dict_categories,Len=len(categories),response=response)

if __name__ == '__main__':
    app.config.update(
        TEMPLATES_AUTO_RELOAD=True,
        FLASK_DEBUG=1
    )
    app.run(debug=True,use_reloader=True)