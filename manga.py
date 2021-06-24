from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import requests
import shutil
import time
import os


def pdfDirectory(outputPDFName):
    '''
    Função gera o PDF
    '''
    dirim = os.path.abspath("./manga/")
    print("Dirim: ", dirim)
    output = str(outputPDFName)
    c = canvas.Canvas(output, pagesize=A4)
    for root, dirs, files in os.walk(dirim):
        for name in files:
            lname = name.lower()
            if lname.endswith(".jpg") or lname.endswith(".gif") or lname.endswith(".png"):
                filepath = os.path.join(root, name)
                print(filepath)
                c.drawImage(filepath, 0, 1)
                c.showPage()
    c.save()
    time.sleep(3)

class MangaDown():

    def __init__(self, options=None):
      self.driver = webdriver.Firefox(options=options)
      
      #self.driver.install_addon(os.path.abspath(os.getcwd()+'/browsers/firefox/extensions/https-everywhere@eff.org.xpi'))
      #self.driver.install_addon(os.path.abspath(os.getcwd()+'/browsers/firefox/extensions/adblockultimate@adblockultimate.net.xpi'))
      self.link_cap = None
      self.name_cap = None

    def abrir_pagina_manga_genero(self, seconds=10):
        self.driver.execute_script(
            "window.open('https://www.brmangas.com/lista-de-generos-de-mangas/','_blank');")
        self.driver.switch_to.window(window_name=self.driver.window_handles[-1])
        time.sleep(seconds)

    def pesquisar_manga(self, manga, seconds):
        self.driver.execute_script(
            "window.open('https://www.brmangas.com/?s={}','_blank');".format(manga))
        self.driver.switch_to.window(window_name=self.driver.window_handles[-1])

        time.sleep(seconds)
        try:
            div_mangas = self.driver.find_element_by_class_name("listagem")
            mangas_disponiveis = div_mangas.find_elements_by_class_name("col-lg-2")
            mangas_txt = [mang_txt.find_element_by_class_name('titulo').text for mang_txt in mangas_disponiveis]
            mangas_obj = [mang_obj.find_element_by_class_name('item') for mang_obj in mangas_disponiveis]
        except:
            mangas_txt = []
            mangas_obj = []
        return mangas_txt, mangas_obj

    def pesquisar_link(self, link, seconds):
        self.driver.execute_script(
            "window.open('{}','_blank');".format(link))
        self.driver.switch_to.window(window_name=self.driver.window_handles[-1])
        time.sleep(seconds)

    def fechar_pagina_manga(self):
        self.driver.execute_script("window.close();")
        self.driver.switch_to.window(window_name=self.driver.window_handles[0])

    def listar_generos(self):
        div_gen = self.driver.find_element_by_class_name("genres_page")
        generos = div_gen.find_element_by_tag_name("ul")
        generos = generos.find_elements_by_tag_name("a")
        generos_names = []
        generos_obj = []
        for gen in generos:
            generos_names.append(gen.text)
            generos_obj.append(gen)
        return generos_names, generos_obj

    def listar_mangas(self):
        titulos_obj = self.driver.find_elements_by_class_name("titulo")
        titulos_text = [titulo.text for titulo in titulos_obj]
        return titulos_text, titulos_obj

    def listar_capitulos(self):
        capitulos = self.driver.find_element_by_class_name("capitulos")
        capitulos_obj = capitulos.find_elements_by_class_name("lista_ep")
        capitulos_text = [cap.find_element_by_tag_name("a").text for cap in capitulos_obj]
        capitulos_obj = [cap.find_element_by_tag_name("a") for cap in capitulos_obj]
        return capitulos_text, capitulos_obj

    def listar_paginas(self):
        options = self.driver.find_element_by_id("modo_leitura")
        options.click()
        time.sleep(1)
        modo_leitura = options.find_elements_by_tag_name("option")[2]
        modo_leitura.click()
        time.sleep(1)
        imagens = self.driver.find_element_by_id("images_all")
        imagens = imagens.find_elements_by_class_name('img-manga')
        imagens_manga = []
        for img in imagens:
            imagens_manga.append(img.get_attribute('src'))
        return imagens_manga

    def salvar_imagens(self, lista_paginas, nome_pdf):
        try:
            for i, img in enumerate(lista_paginas):
                r = requests.get(img,
                                 stream=True)
                if r.status_code == 200:
                    with open("manga/{}.png".format(i), 'wb') as f:
                        r.raw.decode_content = True
                        shutil.copyfileobj(r.raw, f)
            print("Imagens salvas!")
        except Exception:
            print("Ocorreu um erro: ", Exception)
        finally:
            output = os.path.abspath("./static/{}.pdf".format(nome_pdf))
            print(output)
            pdfDirectory(output)
            for i in range(len(lista_paginas)):
                arquivo = "{}.png".format(i)
                os.remove(os.path.abspath("./manga/{}".format(arquivo)))
    
    def ultimo_capitulo(self, msg):
      manga_escolhido = msg.split()[2:]
      manga_escolhido = " ".join(manga_escolhido)
      if manga_escolhido.isdigit():
          self.fechar_pagina_manga()
          return None
      mangas_txt, mangas_obj = self.pesquisar_manga(manga_escolhido, 5)
      mangas_txt = [mng.lower().strip() for mng in mangas_txt]
      manga_escolhido = manga_escolhido.lower().strip()
      if manga_escolhido in mangas_txt:
          index = mangas_txt.index(manga_escolhido)
          self.name_cap = index
          self.link_cap = mangas_obj[index].find_element_by_tag_name('a').get_attribute(
              'href')
          mangas_obj[index].click()
          lista_capitulos = self.listar_capitulos()[0]
          self.fechar_pagina_manga()
          return lista_capitulos[-1]
      return "nada encontrado"

    def escolher_capitulo(self, msg):
      capitulo_escolhido = msg.split()[2:]
      capitulo_escolhido = " ".join(capitulo_escolhido)
      self.pesquisar_link(self.link_cap, 2)
      capitulo_text, capitulo_obj = self.listar_capitulos()
      capitulos_formatados = [x.lower().strip() for x in capitulo_text]
      capitulo_escolhido = capitulo_escolhido.lower().strip()
      cap_text = "0"
      if capitulo_escolhido in capitulos_formatados:
          index = capitulos_formatados.index(capitulo_escolhido)
          capitulo_escolhido = capitulo_obj[index]
          cap_text = capitulo_text[index]
          capitulo_escolhido.click()
      lista_paginas = self.listar_paginas()
      self.fechar_pagina_manga()
      #po o nome do manga
      nome = cap_text
      self.salvar_imagens(lista_paginas, nome)
      return nome+".pdf"
