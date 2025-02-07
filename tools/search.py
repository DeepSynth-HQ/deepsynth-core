
import trafilatura, os, json
from phi.tools.searxng import Searxng
from config import settings
def extract_text_from_link(url):
    downloaded = trafilatura.fetch_url(url)
    text = trafilatura.extract(downloaded)
    return text if text else None
def search(query: str, max_results: int):
    """Use this function to search the web.

        Args:
            query (str): The query to search the web with.
            max_results (int, optional): The maximum number of results to return. Defaults to 5.

        Returns:
            The results of the search.
    """
    print("searching for:    ", query)
    search_tools = Searxng(host = settings.SEARXNG_HOST, news = True)
    print("search_tools:   \n", search_tools)
    search_results = json.loads(search_tools.search(query, max_results= max_results))
    print("search_results:    \n", search_results)
    urls = [result['url'] for result in search_results['results']]
    docs = []
    for url in urls:
        if len(docs) > 3:
            break
        if extract_text_from_link(url):
            docs.append(extract_text_from_link(url))
    texts =  ""
    for index, doc in enumerate(docs):
        texts += "============== Document " + str(index + 1) + " ==============\n" + doc + "\n\n"
    print("texts:    \n", texts) 
    return texts