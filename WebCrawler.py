import requests
from bs4 import BeautifulSoup

class WebCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited = set()

    def fetch_data(self):
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            data = []
            for link in soup.find_all('a', href=True):
                if link['href'] not in self.visited:
                    self.visited.add(link['href'])
                    data.append({"url": link['href'], "content": "Fetched"})
            return data
        except Exception as e:
            return f"Error fetching data: {e}"
