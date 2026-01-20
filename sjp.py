'''
class for taking words' definitions from sjp.pwn.pl
'''
import aiohttp
from bs4 import BeautifulSoup
import urllib.parse


class SJP:
    def __init__(self, sess: aiohttp.ClientSession):
        self.sess = sess

    async def close(self):
        await self.sess.close()

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def get_autocomplete(self, query):
        async with self.sess.get('https://sjp.pwn.pl/api/autocomplete', params={'query': query}) as r:
            completions = await r.json()['hits']['hits']
            return [item['_source']['title'] for item in completions]

    async def get_definition(self, word):
        async with self.sess.get('https://sjp.pwn.pl/szukaj/' + urllib.parse.quote_plus(word) + '.html') as r:
            soup = BeautifulSoup(await r.text(), 'html.parser')
            sjp_results = soup.find("div", attrs={"class": "sjp-wyniki"})
            return sjp_results.find(attrs={"class": "entry-body"}).get_text().strip().replace('\xa0', ' ') if sjp_results is not None else None
