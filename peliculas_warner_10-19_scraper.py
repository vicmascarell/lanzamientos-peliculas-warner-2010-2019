
# Importamos las librerias necesarias
import pandas as pd
import re
import requests
from datetime import datetime 
from bs4 import BeautifulSoup as bs

# Cargamos la página con el listado de pelis y enlaces a las mismas
c = requests.get("https://en.wikipedia.org/wiki/List_of_Warner_Bros._films_(2010–2019)")

# Pasamos a objeto BeautifulSoup
webcontent_list = bs(c.content)

# Definimos función que a partir de una url de pelicula de wikipedia
# Nos sacque la información que nos interesa

def sacar_info_peli (url):

    p = requests.get(url)
    # Pasamos contenido (p) a objeto BeautifulSoup 
    pagecontent_info = bs(p.content)

    # Creamos función para eliminar los superindices e info adicional que está en tag sup y span
    def clean_tags(content):
        for tag in content.find_all(["sup","span"] ):
            tag.decompose()

    # Limpiamos superindices
    clean_tags(pagecontent_info)

    # Aislamos información del cuadro de características
    info_pelicula = pagecontent_info.find(class_="infobox vevent")

    # Aislamos información de las filas de características
    info_rows = info_pelicula.find_all("tr")

    # Funcion para sacar el contenido de las "filas"
    def sacar_datos(row):
    
        # Tratamos el contenido en listas indicadas con "li"
        if row.find("li"):
            return [content.get_text(" ", strip=True).replace("\xa0", " ") for content in row.find_all("li")]
    
        # Tratamos las listas del contenido separado por "br" 
        elif row.find("br"):
            return[i for i in row.find("td").stripped_strings]
        
        # Si no hay lista devolvemos el contenido de td
        else:
            return row.find("td").get_text(" ", strip=True).replace("\xa0", " ")
    
    # Creamos diccionario para poner la info
    data_pelicula= {}
    
    # Recorremos el contenido aislado y metemos los datos en el diccionario
    for index, row in enumerate(info_rows):
    
        # El titulo se encuentra en th no en td. En la primera fila
        if index == 0:
            data_pelicula["Title"] = row.find("th").get_text(" ", strip=True) 
        else:
            try:
                # Las caracteristicas que nos interesan están en th y td
                # Controlamos si tiene la etiqueta th para evitar que es la descripción de caracteristica
                header = row.find("th")
                if header:
                    llave = row.find("th").get_text(" ", strip=True)
                    data_pelicula [llave] = sacar_datos(row)
        
            except Exception as e:
                print(index)
                print(e)

    return data_pelicula




# SACAR LISTADO DE URL A PARTI DE webcontent_list
# OBTENIDO DE https://en.wikipedia.org/wiki/List_of_Warner_Bros._films_(2010–2019)
# CARGAR CONTENIDO DE PELICULAS

# Indicamos la ruta básica de wikipedia
basic_wiki ="https://en.wikipedia.org"

# Seleccionamos del contenido las zonas en cursiva de la clase wikitable sortable
list_peliculas = webcontent_list.select(".wikitable.sortable i")

# Creamos una lista para añadir los datos
data_peliculas = []

# Recorremos el contenido con la lista de links y hacemos scrapping a los páginas individuales con sacar_info_peli(url)
for index, row in enumerate(list_peliculas):
    # Añadimos un marcador para que nos indique cuantas páginas ha procesado (de 10 en 10)
    if index %10 ==0:
        print(index)
    
    try:
        # Creamos el link final de cada película  
        link_parcial = row.a["href"]
        link_full = basic_wiki + link_parcial   
        
        # Añadimos a la lista el resultado de la función sacar_info_peli()
        data_peliculas.append(sacar_info_peli(link_full))
    except Exception as e:
        print(e)
        print(index)



# FUNCIONES DE LIMPIEZA

# Unificar dinero
def unificar_dinero_dolar (dinero):
    
    # Sacamos los patrones con regex para hacer los calculos 
    patron_num = r"\d+(,\d{3})*\.*\d*"
    million_p = r"million"
    million_euro_p = rf"\€({patron_num})(–|-|\s–|,)?({patron_num})?\s({million_p})"
    million_dolar_p = rf"\$({patron_num})(–|-|\s–|,)?({patron_num})?\s({million_p})"
    billion_p = r"billion"
    billion_euro_p = rf"\€({patron_num})(–|-|\s–|,)?({patron_num})?\s({billion_p})"
    billion_dolar_p = rf"\$({patron_num})(–|-|\s–|,)?({patron_num})?\s({billion_p})"
    value_euro_p = rf"\€{patron_num}"
    value_dolar_p = rf"\${patron_num}"
    
    # Si es una lista tomaremos el primer item
    if isinstance (dinero, list):
        dinero = dinero[0]
    
    # Guardamos los patrones para tratarlos con if/else
    value_syntax_dolar = re.search(value_dolar_p, dinero)
    value_syntax_euro = re.search(value_euro_p, dinero)
    million_syntax_dolar = re.search(million_dolar_p, dinero)
    million_syntax_euro = re.search(million_euro_p, dinero)
    billion_syntax_dolar = re.search(billion_dolar_p, dinero)
    billion_syntax_euro = re.search(billion_euro_p, dinero)
    

    # Cambio euro dolar
    Euro_dolar = 1.19
    
    # Controlamos los posibles formatos y realizamos los cambios
    
    if billion_syntax_dolar:

        value = billion_syntax_dolar.group()
        # Multiplicamos por un billon y pasamos a int
        value = int(float(re.search(patron_num, value).group())*1000000000)
        return value
    
    elif billion_syntax_euro:

        value= billion_syntax_euro.group()
        # Multiplicamos por un billon y por el cambio y pasamos a int
        value = int(float((re.search(patron_num, value).group()))*Euro_dolar*1000000000)
        return value  
     
    elif million_syntax_dolar:

        value = million_syntax_dolar.group()
        # Multiplicamos por un millon y pasamos a int
        value = int(float(re.search(patron_num, value).group())*1000000)
        return value
    
    elif million_syntax_euro:

        value= million_syntax_euro.group()
        # Multiplicamos por un millon y por el cambio y pasamos a int
        value = int(float((re.search(patron_num, value).group()))*Euro_dolar*1000000)
        return value
        
    elif value_syntax_dolar:
 
        # eliminamos las comas
        value= value_syntax_dolar.group().replace(",","")
        value = int(float(re.search(patron_num, value).group()))
        return value
        
    elif value_syntax_euro:
        
        # eliminamos las comas
        value= value_syntax_euro.group().replace(",","")
        # Multiplicamos por un millon y por el cambio y pasamos a int
        value = int(float((re.search(patron_num, value).group()))*Euro_dolar)
        return value
   
    else:
        return None

# Unificar fecha formato dd/mm/yyyy
def unificar_fecha_numerica(fecha):
   
    # Si es None retornamos None
    if fecha == "None":
        return None
    # Si es una lista retornamos el primer item
    if isinstance  (fecha, list):
        fecha = fecha[0]
   
    # Limpiemos los parentesis
    fecha_str = fecha.split("(")[0].strip()
   
    # indicamos los 3 formatos que tienen nuestros datos
    dt_format =["%B %d, %Y","%d %B %Y", "%B %Y"]
    
    # Creamos un bucle para problar la lista de formatos y retornar en formato dd/mm/yyyy
    for format_ in dt_format:
        try:
            new_date = datetime.strptime(fecha_str, format_)
            return new_date.strftime("%d/%m/%Y")
        except: 
            pass

# Cambiar fecha a solo día semana
def sacar_dia(fecha):
   
    # Si es None retornamos None
    if fecha == "None":
        return None
    # Si es una lista retornamos el primer item
    if isinstance  (fecha, list):
        fecha = fecha[0]
   
    # Limpiemos los parentesis
    fecha_str = fecha.split("(")[0].strip()
   
    # indicamos los 3 formatos que tienen nuestros datos
    dt_format =["%B %d, %Y","%d %B %Y", "%B %Y"]
    
    # Creamos un bucle para problar la lista de formatos y retornar el dia
    for format_ in dt_format:
        try:
            new_date = datetime.strptime(fecha_str, format_)
            # retornamos el formato deseado
            return new_date.strftime("%a")
        except: 
            pass

# Cambiar duración a minutos numérico
def minutos_a_int (running_time):
    
    # Si es None retornamos None
    if running_time == "None":
        return None
    # Si es una lista
    elif isinstance  (running_time,list):
        # Seleccionamos el primer item que es el que utilizaremos
        time = running_time[0]
        # Dividimos el string para eliminar el texto(minutes) y seleccionamos la primera parte
        return int(time.split(" ")[0])
    
    # Sino retornamos int
    else:
        # dividimos el string por el espacio y seleccionamos el primer campo
        return int(running_time.split(" ")[0])




# APLICAMOS FUNCIONES DE LIMPIEZA a los datos extraídos, añadiendo las nuevas características modificadas

for row in data_peliculas:
    row["Budget dolar"]= unificar_dinero_dolar(row.get("Budget", "None"))
    row["Box office office dolar"]= unificar_dinero_dolar(row.get("Box office", "None"))
    row["Release dates"]= unificar_fecha_numerica(row.get("Release date", "None"))
    row["Release day"]= sacar_dia(row.get("Release date", "None"))
    row["Time min"]= minutos_a_int(row.get("Running time", "None"))




# PASAMOS A DATAFRAME - SELECCION COMPOS - EXPORTAR CSV
df_peliculas = pd.DataFrame(data_peliculas)
df_peliculas_filtrado=df_peliculas.filter(regex='(Country|Budget dolar|Budget dolar|Directed|Time min|Starring|Title|Written|Distributed|Release dates|Release day|Production company|Music)')




# Guardamos el df como .csv separado por ;
df_peliculas_filtrado.to_csv("peliculas_warner_2010-2019.csv",sep=';')

