import json
from pprint import pp, pprint
 
import pandas as pd
import os

import requests
from requests.models import Response

def GetJsonData (url):
     
    payload={}
    headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Accept-Language': 'es-ES,es;q=0.9,pt;q=0.8,en;q=0.7',
    'Cookie': 'PHPSESSID=nd3mu7h6hq8ogkv21e197gvhr1; _ga=GA1.3.1474432205.1646696214; _gid=GA1.3.1862841478.1647195923; incap_ses_173_1277320=clWNNMcLpkfVjRF2Dp9mAnliGWgAAAAAos7J5N1tO6nI+/nFPb851A==; visid_incap_1277320=2bjA389PRaO8AeLzYqRq2kn9GGgAAAAAQkIPAAAAAACDzZFozXuGd0L/ACweqqOK'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = json.loads(response.text)
    
    return (data)


# web scrapping

# retreaving index
firms_raw = []
pages = GetJsonData ("https://www.biva.mx/emisoras/empresas?size=10&page={}".format(0))["totalPages"]
for page in range (pages):
    data_raw = GetJsonData ("https://www.biva.mx/emisoras/empresas?size=10&page={}".format(page))["content"]
    for firm_raw in data_raw:
        firms_raw.append (firm_raw)
    
pprint (firms_raw)

# reordering index data from each profile
firms = {}

for position, firm_raw in enumerate(firms_raw):
    firm_id = firms_raw[position]["id"]
    firm_clave = firms_raw[position]["clave"]
    firm_nombre = firms_raw[position]["nombre"]
    
    firm = {"id":firm_id,
            "clave":firm_clave,
            "nombre":firm_nombre}
    
    firms[firm_id]= firm

pprint (firms)

# reordering data from each profile's general information
for position, firm in enumerate(firms):

    url_infogen = "https://www.biva.mx/emisoras/empresas/{}".format(firm)
    firm_raw_infogen = GetJsonData (url_infogen)
    
    pprint (firm_raw_infogen)
    
    try:
        firm_actividadEconomica = firm_raw_infogen["actividadEconomica"]
    except:
        firm_actividadEconomica = ""

    firm_bolsa = firm_raw_infogen["bolsa"]
    firm_clave = firm_raw_infogen["clave"]

    firm_estatus  = firm_raw_infogen["estatus"]
    
    try:
        firm_fechalistado  = firm_raw_infogen["fechaListado"]
    except:
        firm_fechalistado = ""

    firm_razon  = firm_raw_infogen["razonSocial"]
    
    try:
        firm_logo  = firm_raw_infogen["logo"]
    except:
        firm_logo = ""

    firm_sector = firm_raw_infogen["sector"]["nombre"]
    firm_subsector = firm_raw_infogen["subsector"]["nombre"]
    firm_ramo  = firm_raw_infogen["ramo"]["nombre"]
    firm_subramo  = firm_raw_infogen["subramo"]["nombre"]
    
    firms[firm]["Actividad económica"] = firm_actividadEconomica
    firms[firm]["Bolsa"] = firm_bolsa
    firms[firm]["Clave"] = firm_clave

    firms[firm]["Estatus"] = firm_estatus
    firms[firm]["Fecha de listado"] = firm_fechalistado

    firms[firm]["Razón Social"] = firm_razon
    firms[firm]["Logo"] = firm_logo

    firms[firm]["Sector"] = firm_sector
    firms[firm]["Subsector"] = firm_subsector
    firms[firm]["Ramo"] = firm_ramo
    firms[firm]["Subramo"] = firm_subramo

    # if position == 0:
    pprint (firm_raw_infogen)

    # Guardar en un archivo JSON
import json
import csv

with open("Firms.json", "w", encoding="utf-8") as archivo:
    json.dump(firms, archivo, indent=4, ensure_ascii=False)

filas = []
for firm_id, data in firms.items():
    fila = {'firm_id': firm_id}
    fila.update(data)
    filas.append(fila)

# Obtener los encabezados (campos)
campos = filas[0].keys()

# Escribir CSV con codificación UTF-8
with open('01092025_Firms.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=campos)
    writer.writeheader()
    writer.writerows(filas)

emissions = []
firms_no_emissions = {}

for firm in firms:
    # getting data
    url_emisiones = "https://www.biva.mx/emisoras/empresas/{}/emisiones?size=100000&page=0".format(firm)
    print (url_emisiones)

    try:
        content = GetJsonData(url_emisiones)["content"]
        pprint (content)
    except:
        content = 404

    if content == 404:
        firms_no_emissions[firm] = firms[firm]
    else: 
        for position, emission in enumerate(content):
            content[position]["id"] = firm
            content[position]["clave"] = firms[firm]["clave"]
            content[position]["nombre"] = firms[firm]["nombre"]
        emissions.extend(content)

for firm in firms:
        
    # getting pages
    url_emisiones_pages = "https://www.biva.mx/emisoras/empresas/{}/emisiones?size=1&page=0&cotizacion=true".format(str(firm))

    pages = GetJsonData(url_emisiones_pages)["totalPages"]
    

    for page in range (pages):
        # getting data
        print (page)
        url_emisiones = "https://www.biva.mx/emisoras/empresas/{}/emisiones?size=1&page={}&cotizacion=true".format(firm,page)
        
        emission_raws = GetJsonData (url_emisiones)["content"]
        pprint (emission_raws)

        for emission_raw in emission_raws:
            print (emission_raw)
            emission_isin = emission_raw["isin"]
            emission_tipovalor = emission_raw["tipoValor"]
            emission_tipoinstrumento = emission_raw["tipoInstrumento"]
            emission_tipoemision = emission_raw["tipoEmision"]
            emission_fechaemision = emission_raw["fechaEmision"]
            emission_tipolistado = emission_raw["modoListado"]
            
            try:
                emission_numeroemisiones = emission_raw["accionesEnCirculacion"]
            except:
                emission_numeroemisiones = emission_raw["titulosEnCirculacion"]
                
            emissions[emission_isin] = {}
            emissions[emission_isin]["isin"] = emission_isin
            emissions[emission_isin]["tipoValor"] = emission_tipovalor
            emissions[emission_isin]["tipoInstrumento"] = emission_tipoinstrumento
            emissions[emission_isin]["tipoEmision"] = emission_tipoemision
            emissions[emission_isin]["fechaEmision"] = emission_fechaemision
            emissions[emission_isin]["modoListado"] = emission_tipolistado
            emissions[emission_isin]["NumeroEmisiones"] = emission_numeroemisiones


            emissions[emission_isin]["Razón Social"] = firms[firm]["Razón Social"]
            emissions[emission_isin]["clave"] = firms[firm]["clave"]
            emissions[emission_isin]["Sector"] = firms[firm]["Sector"]
            emissions[emission_isin]["Subsector"] = firms[firm]["Subsector"]
            emissions[emission_isin]["Ramo"] = firms[firm]["Ramo"]
            emissions[emission_isin]["Subramo"] = firms[firm]["Subramo"]

# Guardar en un archivo JSON
import json

with open("080525_Firms.json", "w", encoding="utf-8") as archivo:
    json.dump(firms, archivo, indent=4, ensure_ascii=False)

with open("080525_Emissions.json", "w", encoding="utf-8") as archivo:
    json.dump(emissions, archivo, indent=4, ensure_ascii=False) 

with open("080525_Firms with no emissions.json", "w", encoding="utf-8") as archivo:
    json.dump(no_emissions, archivo, indent=4, ensure_ascii=False) 

# Guardar en un archivo CSV
import csv
 
df = open("Emissions.csv", 'w', newline='', encoding = "utf-8")
cw = csv.writer(df) #, encoding="utf-8-sig"

c = 0
for data in emissions:
    if c == 0:
        header = emissions[data].keys()
        cw.writerow(header)
        c += 1
    cw.writerow(emissions[data].values())

df.close()
