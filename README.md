# Mini agente evaluador de ficheros - Google ADK

Clonar el repositorio e instalar la siguientes dependencias:

``` sh
pip install google-adk mcp python-dotenv PyPDF2 python-docx beautifulsoup4
```

crear un un fichero .env con esta estructura:

```python
GOOGLE_GENAI_USE_VERTEXAI = FALSE
GOOGLE_API_KEY = API Key de Gemini , se obtiene de Google IA Studio
TARGET_FOLDER_PATH = Ruta del directorio a trabajar .
```

Cuando todo este es su sitio y preferiblemente en un entorno virtual venv, ejecutar adk(web o terminal)

```sh
#Interfaz CLI
adk run (carpeta del agente)

#Interfaz Web
adk web
```
