import requests

url = "https://raw.githubusercontent.com/bambucode/catalogos_sat_JSON/master/c_ClaveProdServ.json"
with requests.get(url) as r:
    with open("C:/Users/WuilsonPc/Desktop/progra/gestionafacil/api/c_ClaveProdServ.json", "wb") as f:
        f.write(r.content)