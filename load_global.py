import datetime
import json
import feedparser
import re
from models import News, Grants

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

"""
def escribir_rss_xml_mensual(diccionario_contenido_noticias):
    mediaFeed = PyMediaRSS2Gen.MediaRSS2(
        title="Noticias FinTech",
        link="", #Cambiar a link Dropbox
        description="Noticias FinTech recopiladas durante el día."
    )
    mediaFeed.copyright = "Copyright (c) 2019 Banco Central de Chile. All rights reserved."
    mediaFeed.lastBuildDate = datetime.datetime.now()
    mediaFeed.items = list()
    for key, value in diccionario_contenido_noticias.items():
        for noticia in value:
            mediaFeed.items.append(PyMediaRSS2Gen.MediaRSSItem(
                title=str(noticia["fuente"])+": "+noticia["titulo"]+" - "+" Puntaje: "+str(noticia["puntaje"]),
                link=noticia["link"],
                description=noticia["summary"],
                pubDate=noticia["pubDate"]
            ))
    mediaFeed.write_xml(open("feed_rss.xml", "w"))
"""

def load_funds_dictionaries():
    with open("data/funds_grants.json", 'r') as grants_data:
        grants_dictionary = json.load(grants_data)
    with open("data/funds_news.json", 'r') as news_data:
        try:
            news_dictionary = json.load(news_data)
        except:
            news_dictionary = {"funds": [{"name": "European Cultural Foundation", "url": "https://www.culturalfoundation.eu/news", "location": "europe", "type": "webscraping", "area": "multiple"}, {"name": "Visegradfund", "url": "https://www.visegradfund.org/feed/?post_type=new", "location": "eastern-europe", "type": "rss", "area": "multiple"}, {"name": "Nordic Culture Point", "url": "https://www.nordiskkulturkontakt.org/en/news/", "location": "Nordic Countries", "type": "webscraping", "area": "multiple"}, {"name": "IIE", "url": "https://www.iie.org/en/RSS-Feeds/RSS-Announcements", "location": "worldwide", "type": "rss", "area": "multiple"}, {"name": "Asia-Europe Foundation", "url": "https://asef.org/feeds/", "location": "Asia", "type": "rss", "area": "multiple"}, {"name": "European Comission", "url": "https://ec.europa.eu/echo/echo-rss/news", "location": "Europe", "type": "rss", "area": "multiple"}, {"name": "UNESCO", "url": "https://en.unesco.org/rss.xml", "location": "worldwide", "type": "rss", "area": "multiple"}, {"name": "BFI", "url": "https://www.bfi.org.uk/latest/feed", "type": "rss", "area": "film"}, {"name": "On-The-Move", "url": "https://on-the-move.org/feed", "type": "rss", "area": "multiple"} ] } 
        return grants_dictionary, news_dictionary

def cargar_filtros():
    """FUNCIÓN QUE RETORNA EL DICCIONARIO DE FILTROS DE Filtros_FinTech.json"""
    with open("data/filtering_words.json", 'r', encoding="utf-8") as filters_file:
        filters_dict = json.load(filters_file)
        return filters_dict 

def cargar_combinaciones_palabras():
    with open("data/word_combinations.json", "r") as combinations_file:
        combinations_list = json.load(combinations_file)["combinaciones"]
        return combinations_list

def get_webscraping_content(fund_name, url):
    page_response = requests.get(url, timeout=5)
    soup = BeautifulSoup(page_response.content, "html.parser")
    textContent = ""
    for node in soup.findAll('p'):
        textContent += str(node.findAll(text=True))
    """
    lista_palabras = textContent.strip(",").strip(".").strip("[").strip("]").strip("(").strip(")").split(" ")
    lista_palabras_lower = [palabra.lower() for palabra in lista_palabras]"""
    return textContent

def get_rss_content(fund_name, contenido):
    lista_diccionarios_entries = []
    for entry in contenido.entries:
        """Loop por todos los articulos de la fuente"""
        try:
            titulo_noticia = cleanhtml(entry.title)
        except:
            continue
        """AQUI EL PROBLEMA"""
        cotenido = ""
        try:
            contenido = entry.summary
        except AttributeError as error:
            pass
        """----------------------"""
        link_noticia = entry.link
        fecha_actual = datetime.datetime.now().ctime()
        lista_elementos_fecha_actual = fecha_actual.split(" ")
        """La llave 'published' no siempre existe en el diccionario entregado por
         el RSS feed por lo que se debe tomar en cuenta la llave 'updated'"""
        if "published" in entry.keys():
            pubdate = entry.published
            """if "-" in entry.published:
                lista1_elems_fecha_articulo = entry.published.split("T")
                lista_elems_fecha_articulo = list()
                for elem in lista1_elems_fecha_articulo:
                    lista_elems_fecha_articulo.extend(elem.split("-"))
            else:
                lista_elems_fecha_articulo = entry.published.split(" ")
            num_ocurrencias = 0
            for elemento in lista_elementos_fecha_actual:
                if len(elemento) == 1:
                    elemento = '0' + elemento
                for elem in lista_elems_fecha_articulo:
                    if elemento == elem:
                        num_ocurrencias += 1
            if num_ocurrencias == 3:
                print("si")"""
            """Si es que la fecha de publicación de la noticia es el día de
             hoy entonces incluir"""
            lista_diccionarios_entries.append({"titulo":titulo_noticia, "link":link_noticia,"summary": contenido,"pubDate": pubdate,"fuente": fund_name})
            continue
        elif "updated" in entry.keys():
            pubdate = entry.updated
            """if "-" in entry.updated:
                lista1_elems_fecha_articulo = entry.updated.split("T")
                lista_elems_fecha_articulo = list()
                for elem in lista1_elems_fecha_articulo:
                    lista_elems_fecha_articulo.extend(elem.split("-"))
            else:
                lista_elems_fecha_articulo = entry.updated.split(" ")
            num_ocurrencias = 0
            for elemento in lista_elementos_fecha_actual:
                if len(elemento) == 1:
                    elemento = '0' + elemento
                for elem in lista_elems_fecha_articulo:
                    if elemento == elem:
                        num_ocurrencias += 1
            if num_ocurrencias == 3:
                print("si")"""
            lista_diccionarios_entries.append({"titulo":titulo_noticia, "link":link_noticia,"summary": contenido,"pubDate": pubdate,"fuente": fund_name})
            continue
    return lista_diccionarios_entries

def webscraper(webscraping_list):
    for dict_webscraping in webscraping_list:
        name = dict_webscraping["name"]
        url = dict_webscraping["url"]
        content_text = get_webscraping_content(name, url)
    return None

def rss_parser(rss_list):
    content_dicts_list = []
    for dict_rss in rss_list:
        name = dict_rss["name"]
        url = dict_rss["url"]
        url_content = feedparser.parse(url)
        """[{"titulo":titulo_noticia, "link":link_noticia,"summary": contenido,"pubDate": pubdate,"fuente": fund_name}...]"""
        content_list = get_rss_content(name, url_content)
        content_dicts_list.extend(content_list)
    return content_dicts_list

def organize_grants_info():
    return None

def organize_news_info():
    return None

def organize(grants_dict, news_dict):
    grants_webscraping_list = []
    grants_rss_list = []
    for fund_dict in grants_dict["funds"]:
        name = fund_dict["name"]
        print(name)
        url = fund_dict["url"]
        type_data = fund_dict["type"]
        area = fund_dict["area"]
        if type_data == "webscraping":
            grants_webscraping_list.append(fund_dict)
        elif type_data == "rss":
            grants_rss_list.append(fund_dict)
        else:
            continue
    news_webscraping_list = []
    news_rss_list = []
    for fund_dict in news_dict["funds"]:
        name = fund_dict["name"]
        url = fund_dict["url"]
        type_data = fund_dict["type"]
        area = fund_dict["area"]
        if type_data == "webscraping":
            news_webscraping_list.append(fund_dict)
        elif type_data == "rss":
            news_rss_list.append(fund_dict)
        else:
            continue
    #webscraped_grants_data_dict = webscraper(grants_webscraping_list)
    rss_grants_data_dict_list = rss_parser(grants_rss_list)
    #grants_data_dict = webscraped_grants_data_dict.update(rss_grants_data_dict)
    #webscraped_news_data_dict = webscraper(news_webscraping_list)
    rss_news_data_dict_list = rss_parser(news_rss_list)
    #news_data_dict = webscraped_news_data_dict.update(rss_news_data_dict)
    """organize_grants_info(rss_grants_data_dict_list)
    organize_news_info(rss_news_data_dict_list)"""
    return rss_grants_data_dict_list, rss_news_data_dict_list


def load_all():
    grants_dictionary, news_dictionary = load_funds_dictionaries()
    rss_grants_data_dict_list, rss_news_data_dict_list = organize(grants_dictionary, news_dictionary)
    return rss_grants_data_dict_list, rss_news_data_dict_list