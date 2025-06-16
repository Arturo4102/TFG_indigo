# 🌌 TFG_INDIGO

Este repositorio contiene el **Trabajo de Fin de Grado (TFG)** en Ingeniería Informática desarrollado por **Arturo Arellano Romo**, centrado en la creación de un cliente en **Python** para el sistema **[INDIGO](https://github.com/indigo-astronomy/indigo)**, utilizado para la **gestión y control de dispositivos astronómicos**.

## 📁 Estructura del Proyecto

- **`myIndigoLibrary/`**  
  Carpeta principal del desarrollo. Contiene:
  - Código fuente de la biblioteca y la interfaz gráfica.
  - Instrucciones de instalación y ejecución.
  - Requisitos y dependencias.
  - Documentación técnica y de usuario.

- **`indigo-master/`**  
  Versión modificada del repositorio oficial de INDIGO.  
  Se utiliza para lanzar un **servidor local de pruebas**, necesario para validar la comunicación con el cliente Python.  
  Repositorio original: [indigo-astronomy/indigo](https://github.com/indigo-astronomy/indigo)

## ⚙️ Requisitos

- Python 3.8 o superior
- pip
- `make` (para compilar el servidor INDIGO)
- Sistema operativo Linux (recomendado para pruebas con servidor)

## 📥 Clonar el repositorio

```bash
git clone https://github.com/Arturo4102/TFG_indigo.git
cd TFG_indigo
````

## 🛠️ Instalación

```bash
cd myIndigoLibrary
# (Opcional) Crear entorno virtual
python3 -m venv env
source env/bin/activate

# Instalar dependencias del proyecto
pip install -r requirements.txt

# (Solo en Linux) Instalar soporte para Tkinter
sudo apt install python3-tk
```
## 🚀 Ejecutar la aplicación gráfica

```bash
cd myIndigoLibrary/myIndigoLibrary
python3 Cliente_INDIGO_Gui.py
```

## 🛰️ (Opcional) Lanzar servidor INDIGO de prueba
(Este servidor simula dispositivos CCD para probar la funcionalidad del cliente.)
```bash
cd ../../indigo-master
make all
./build/bin/indigo_server -v indigo_ccd_simulator
```
## 📜 Notas adicionales
Los logs y las imágenes descargadas se guardan en el directorio desde el que se ejecuta la aplicación.

Para generar la documentación técnica, ve a la carpeta docs/ y ejecuta:
```bash
cd  myIndigoLibrary/myIndigoLibrary/docs/
make html
```

## 👨‍💻 Autor
Arturo Arellano Romo

Universidad de Granada – Grado en Ingeniería Informática - Junio - 2025

