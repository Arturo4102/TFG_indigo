# TFG_INDIGO

Este repositorio contiene el Trabajo de Fin de Grado (TFG) de Ingeniería Informática desarrollado por Arturo Arellano Romo, centrado en la integración de un cliente desarrollado en Python para el sistema **INDIGO**, para la gestión y control de dispositivos de dispositivos astronómicos.

## Estructura del proyecto

La carpeta principal de trabajo es la de myIndigoLibrary, la cual contiene:
  - Código fuente de la biblioteca y la interfaz gráfica.
  - Instrucciones detalladas para instalar y ejecutar la aplicación.
  - Requisitos y dependencias.
  - Documentación técnica y de usuario.

La carpeta indigo-master, es usada para crear un servidor de pruebas que podemos levantar para usar nuestro proyecto. Esta carpeta indigo-master es un clon del repositorio oficial de Indigo: https://github.com/indigo-astronomy/indigo, pero con mejoras para que funcione.

## Descargar el repositorio

git clone https://github.com/Arturo4102/TFG_indigo.git
cd TFG_indigo

## Instalar dependencias de Python
cd myIndigoLibrary
(Opcional)
  python3 -m venv env
  source env/bin/activate

## Instalar dependencias del proyecto
pip install -r requirements.txt

## Instalar Tkinter si se usa Linux
sudo apt install python3-tk

## Ejecutar la aplicación gráfica
cd myIndigoLibrary/myIndigoLibrary
python3 Cliente_INDIGO_Gui.py

## (Opcional) Ejecutar el servidor INDIGO para probar el Cliente_INDIGO_Gui.py
cd ../../indigo-master
make all
./build/bin/indigo_server -v indigo_ccd_simulator

## Notas adicionales
Si se quiere generar la documentación, ve a docs y ejecuta make html.
Los logs y las imágenes descargadas se guardarán en la carpeta donde ejecutes la aplicación.
