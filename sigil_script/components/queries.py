from pyodide.http import pyfetch
import json

base_url: str = ""


# ----------------------------------------------------------------
async def query_ex(url: str) -> dict:
    try:
        response: str = await pyfetch(url)
        result: dict = await response.json()
        return result
    except Exception as e:
        result: dict = {"error": str(e)}
        return result


# ----------------------------------------------------------------
async def get_page(url: str) -> str:
    try:
        response: str = await pyfetch(url)
        result: str = await response.string()
        return result
    except Exception as e:
        result: dict = {"error": str(e)}
        return result


# ----------------------------------------------------------------
async def get_svg(item) -> dict:
    url = f"{base_url}/stock_gallery/{item}"
    try:
        response: str = await pyfetch(url)
        result: str = await response.string()
        return result
    except Exception as e:
        result: dict = {"error": str(e)}
        return result


# ----------------------------------------------------------------
async def get_svg_list(file_list) -> dict:
    svg_dict = dict()
    for item in file_list:
        i = await get_svg(item)
        key = item.strip(".svg")
        svg_dict[key] = i
    return svg_dict


# ----------------------------------------------------------------
async def get_folder(dir) -> dict:
    response = await pyfetch(f"{base_url}/dir/{dir}")
    result = await response.json()
    return result



# ----------------------------------------------------------------
