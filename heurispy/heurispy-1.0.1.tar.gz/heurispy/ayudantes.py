
"""
 Copyright 2019, LANIA, A.C.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
   """

class AyudanteGraficas:

    def __init__(self, instancia_recolector_resultados):
        self.recolector_resultados = instancia_recolector_resultados

    def crear_grafica_parametro(self, nombre_datos_a_graficar, parametros_bloque, pp, ylim_inf=None, ylim_sup=None,
                                titulo=""):
        import matplotlib.pyplot as plt

        plt.figure()
        plt.clf()

        diccionario_resultados = self.recolector_resultados.diccionario_dataframes[parametros_bloque]

        dataframe_iteraciones = diccionario_resultados['iter']
        dataframe_parametro = diccionario_resultados[nombre_datos_a_graficar]

        for i in range(dataframe_parametro.shape[0]):
            plt.plot(dataframe_iteraciones.iloc[i], dataframe_parametro.iloc[i])

        if ylim_inf is not None and ylim_sup is not None:
            plt.ylim(ylim_inf, ylim_sup)

        plt.ylabel(nombre_datos_a_graficar)
        plt.title(titulo)

        pp.savefig()
        plt.close()

    def crear_grafica_promedio_parametro(self, nombre_datos_a_graficar, parametros_bloque, pp,
                                         ylim_inf=None, ylim_sup=None, titulo=""):
        import matplotlib.pyplot as plt

        plt.figure()
        plt.clf()

        diccionario_resultados = self.recolector_resultados.diccionario_dataframes[parametros_bloque]
        mejores_f = self.recolector_resultados.diccionario_mejores_f[parametros_bloque]
        indices_mejores_f = self.recolector_resultados.diccionario_indices_mejores_f[parametros_bloque]

        dataframe_parametro = diccionario_resultados[nombre_datos_a_graficar]

        dataframe_parametro.mean().plot()

        if ylim_inf is not None and ylim_sup is not None:
            dataframe_parametro.mean().plot(ylim=(ylim_inf-1, ylim_sup+1))
        else:
            dataframe_parametro.mean().plot()

        if nombre_datos_a_graficar == 'f_sol':
            for i in range(len(indices_mejores_f)):
                plt.plot(indices_mejores_f[i], mejores_f[i], 'o')

        plt.ylabel(nombre_datos_a_graficar)
        plt.title(titulo)

        pp.savefig()
        plt.close()

    def crear_grafica_mejores_f(self, nombre_datos_a_graficar, parametros_bloque, pp, ylim_inf=None, ylim_sup=None,
                                titulo=""):
        import matplotlib.pyplot as plt

        plt.figure()
        plt.clf()

        parametros_bloque = str(parametros_bloque)

        diccionario_resultados = self.recolector_resultados.diccionario_dataframes[parametros_bloque]

        mejores_f = self.recolector_resultados.diccionario_mejores_f[parametros_bloque]

        dataframe_iteraciones = diccionario_resultados['iter']
        dataframe_parametro = diccionario_resultados[nombre_datos_a_graficar]

        for i in range(dataframe_parametro.shape[0]):
            plt.plot(dataframe_iteraciones.iloc[i], dataframe_parametro.iloc[i])

        plt.ylim(min(mejores_f)-1, max(mejores_f)+1)

        plt.ylabel(nombre_datos_a_graficar)
        plt.title(titulo)

        pp.savefig()
        plt.close()


class AyudanteEstadisticas:
    def __init__(self, instancia_recolector_resultados):
        self.recolector_resultados = instancia_recolector_resultados

    def solucion_minima(self, parametros_bloque):
        lista_mejores_f = self.recolector_resultados.diccionario_mejores_f[parametros_bloque]
        return min(lista_mejores_f)

    def solucion_maxima(self, parametros_bloque):
        lista_mejores_f = self.recolector_resultados.diccionario_mejores_f[parametros_bloque]
        return max(lista_mejores_f)

    def calcula_desv_estandar(self, parametros_bloque):
        import numpy as np
        lista_mejores_f = self.recolector_resultados.diccionario_mejores_f[parametros_bloque]
        return np.std(lista_mejores_f)

    def calcula_desv_minima(self, parametros_bloque):
        import numpy as np
        lista_mejores_f = self.recolector_resultados.diccionario_mejores_f[parametros_bloque]
        array_mejores_f = np.array(lista_mejores_f)
        minimo = np.sqrt(np.mean(abs(array_mejores_f - array_mejores_f.min())**2))
        return minimo

    def calcula_media(self, parametros_bloque):
        lista_mejores_f = self.recolector_resultados.diccionario_mejores_f[parametros_bloque]
        print(lista_mejores_f)
        media = sum(lista_mejores_f)/len(lista_mejores_f)
        print(media)
        return media

    def crea_listas_mejores_resultados_pdf(self, parametros_bloque):
        lista_mejores_f = self.recolector_resultados.diccionario_mejores_f[parametros_bloque]
        lista_indices_mejores_f = self.recolector_resultados.diccionario_indices_mejores_f[parametros_bloque]
        lista_contador_f = self.recolector_resultados.diccionario_contadores_llamados_f[parametros_bloque]
        lista_total_iteraciones = self.recolector_resultados.diccionario_total_iteraciones[parametros_bloque]
        return lista_mejores_f, lista_indices_mejores_f, lista_contador_f, lista_total_iteraciones


class AyudantePDFs:
    def __init__(self, parametros_bloque, ayudante_estadistico, ayudante_grafico,
                 formato={"fuente": "Arial", "tamaño": 12}):
        from fpdf import FPDF
        from matplotlib.backends.backend_pdf import PdfPages

        self.lista_funciones_a_txt = []

        if "fuente" in formato:
            self.font = formato["fuente"]
        else:
            self.font = "Arial"

        if "tamaño" in formato:
            self.size = formato["tamaño"]
        else:
            self.size = 12

        self.lista_nombres_pdfs = []

        self.pdf_estadisticas = FPDF()
        self.pdf_estadisticas.add_page()
        self.pdf_estadisticas.set_y(0)

        self.parametros_bloque = parametros_bloque

        self.nombre_pdf_graficas = 'G-' + str(self.parametros_bloque) +'.pdf'

        self.pdf_graficas = PdfPages(self.nombre_pdf_graficas)

        self.ayudante_estadistico = ayudante_estadistico
        self.ayudante_grafico = ayudante_grafico

        self.parametros = parametros_bloque.replace("[", "")
        self.parametros = self.parametros.replace("]", "")
        self.parametros = self.parametros.replace(",", "")
        self.parametros = self.parametros.split()

    def texto(self, texto, estilo="", alineacion="L", funcion_estadistica=None):
        self.pdf_estadisticas.set_font(family=self.font, size=self.size, style=estilo)

        if funcion_estadistica is None:
            self.pdf_estadisticas.cell(200, 10, txt=texto, ln=1, align=alineacion)
        else:
            self.lista_funciones_a_txt.append(funcion_estadistica.__name__)
            texto = texto + str(funcion_estadistica(self.parametros_bloque))
            self.pdf_estadisticas.cell(200, 10, txt=texto, ln=1, align=alineacion)

    def crear_tabla_mejores_resultados(self):
        parametros_bloque = self.parametros_bloque

        lista_mejores_f, lista_indices_mejores_f, lista_contador_f, lista_total_iteraciones = \
            self.ayudante_estadistico.crea_listas_mejores_resultados_pdf(parametros_bloque)

        self.pdf_estadisticas.cell(40, 10, 'Iteración', border=1, ln=0, align='C')
        self.pdf_estadisticas.cell(40, 10, 'Valor de solución', border=1, ln=0, align='C')
        self.pdf_estadisticas.cell(45, 10, 'Llamadas a función', border=1, ln=0, align='C')
        self.pdf_estadisticas.cell(45, 10, 'Total iteraciones', border=1, ln=1, align='C')
        for i in range(len(lista_mejores_f)):
            self.pdf_estadisticas.cell(40, 10, str(lista_indices_mejores_f[i]), border=1, ln=0, align='C')
            self.pdf_estadisticas.cell(40, 10, str(lista_mejores_f[i]), border=1, ln=0, align='C')
            self.pdf_estadisticas.cell(45, 10, str(lista_contador_f[i]), border=1, ln=0, align='C')
            self.pdf_estadisticas.cell(45, 10, str(lista_total_iteraciones[i]), border=1, ln=1, align='C')

    def finalizar_pdf_estadisticas(self, nombre):
        nombre_pdf = nombre + '.pdf'
        self.pdf_estadisticas.output(nombre_pdf)
        self.lista_nombres_pdfs.append(nombre_pdf)

    def guardar_grafica(self, titulo_grafica="Gráfica", nombre_parametro=None, funcion_ayudante_grafico=None):

        if funcion_ayudante_grafico is None:
            print("Error. Se necesita definir la función del ayudante gráfico a utilizar.")
        else:
            parametros_bloque = self.parametros_bloque
            funcion_ayudante_grafico(nombre_datos_a_graficar=nombre_parametro,
                                     parametros_bloque=parametros_bloque, pp=self.pdf_graficas,
                                     titulo=titulo_grafica)

    def finalizar_pdf_graficas(self):
        self.lista_nombres_pdfs.append(self.nombre_pdf_graficas)
        self.pdf_graficas.close()

    def generar_txt_funciones(self, nombre_txt_final):
        with open(nombre_txt_final, 'w') as archivo_texto:
            for funcion in self.lista_funciones_a_txt:
                archivo_texto.write(funcion+"\n")

    def generar_pdf_final(self, nombre_pdf_final):
        from PyPDF2 import PdfFileMerger
        import os

        lista_nombres_pdfs = self.lista_nombres_pdfs

        merger = PdfFileMerger()

        for pdf in lista_nombres_pdfs:
            merger.append(pdf)

        merger.write(nombre_pdf_final)

        merger.close()

        for pdf in lista_nombres_pdfs:
            os.remove(pdf)

        return nombre_pdf_final

