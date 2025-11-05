import os # Required for path operations
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters, StdioConnectionParams
import PyPDF2
import docx
import requests
from bs4 import BeautifulSoup


TARGET_FOLDER_PATH = os.getenv('TARGET_FOLDER_PATH')
#tool 1: Leer archivos PDF

def read_pdf_file(file_path: str) -> str:
    """Lee y extrae texto de un archivo PDF desde la carpeta objetivo."""
    try:
        # solo tomar el nombre del archivo para evitar duplicar rutas
        file_name = os.path.basename(file_path)
        full_path = os.path.join(TARGET_FOLDER_PATH, file_name)

        if not os.path.exists(full_path):
            return f"Error: el archivo '{file_name}' no existe en la carpeta destino."

        with open(full_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += (page.extract_text() or "") + "\n"
            return f"Contenido del PDF '{file_name}':\n{text.strip()}"
    except Exception as e:
        return f"Error leyendo PDF '{file_path}': {str(e)}"


# tool 2: Leer archivos DOCX

def read_docx_file(file_path: str) -> str:
    """Lee y extrae texto de un archivo DOCX desde la carpeta objetivo."""
    try:
        # solo tomar el nombre del archivo
        file_name = os.path.basename(file_path)
        full_path = os.path.join(TARGET_FOLDER_PATH, file_name)

        if not os.path.exists(full_path):
            return f"Error: el archivo '{file_name}' no existe en la carpeta destino."

        doc = docx.Document(full_path)
        text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
        return f"Contenido del DOCX '{file_name}':\n{text.strip()}"
    except Exception as e:
        return f"Error leyendo DOCX '{file_path}': {str(e)}"

# tool 3: Buscar informacion por internet

def web_search(query: str, max_results: int = 5) -> str:
    """Realiza búsquedas en internet para contrastar información"""
    try:
        # Usando DuckDuckGo como motor de búsqueda
        search_url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        for result in soup.find_all('div', class_='result')[:max_results]:
            title_elem = result.find('a', class_='result__a')
            snippet_elem = result.find('a', class_='result__snippet')
            
            if title_elem and snippet_elem:
                results.append({
                    'title': title_elem.get_text(),
                    'snippet': snippet_elem.get_text(),
                    'url': title_elem.get('href')
                })
        
        formatted_results = "\n".join([
            f"Resultado {i+1}:\nTítulo: {r['title']}\nResumen: {r['snippet']}\nURL: {r['url']}\n"
            for i, r in enumerate(results)
        ])
        
        return f"Resultados de búsqueda para '{query}':\n{formatted_results}"
    
    except Exception as e:
        return f"Error en búsqueda web: {str(e)}"

root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='filesystem_assistant_agent',
    instruction='Help the user manage their files. You can list files, read files, etc.',
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                command='npx',
                args=[
                    "-y",  # Argument for npx to auto-confirm install
                    "@modelcontextprotocol/server-filesystem",
                    # IMPORTANT: This MUST be an ABSOLUTE path to a folder the
                    # npx process can access.
                    # Replace with a valid absolute path on your system.
                    # For example: "/Users/youruser/accessible_mcp_files"
                    # or use a dynamically constructed absolute path:
                    os.path.abspath(TARGET_FOLDER_PATH),
                ],
                ),
            timeout=60
            ),
            # Optional: Filter which tools from the MCP server are exposed
            #tool_filter=['list_directory', 'read_file']
        ),

        read_pdf_file,
        read_docx_file, 
        web_search
    ],
)