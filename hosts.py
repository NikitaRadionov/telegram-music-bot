import aiohttp, os
from aiofile import async_open
from bs4 import BeautifulSoup
from Crypto.Util.Padding import unpad



class DrivemusicHost:

    def __init__(self):
        self.base_url = 'https://www.drivemusic.club'
        self._search_req = 'https://www.drivemusic.club/?do=search&subaction=search&story='
        self.parse_params = ["popular-download-link", "song-author-btn btn-download"]
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 YaBrowser/23.1.4.776 Yowser/2.5 Safari/537.36'}


    def _make_search_request(self, q):
        string_request = "+".join(q.replace(' - ', ' ').split())
        return string_request


    async def _parserequest_to_drivemusic(self, url: str, parse_param: str) -> str:

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                html_doc = await response.text()


        soup = BeautifulSoup(html_doc, 'html.parser')
        link_end = soup.find("a", parse_param).get("href")

        link = self.base_url + link_end

        return link


    async def get_download_link(self, q):
        string_request = self._make_search_request(q)
        try:
            download_page_url = await self._parserequest_to_drivemusic(self._search_req + string_request, self.parse_params[0])
            download_link = await self._parserequest_to_drivemusic(download_page_url, self.parse_params[1])
            return download_link
        except AttributeError:
            return None


    def preprocess(self):
        try:
            os.mkdir("media")
            os.mkdir("media/music")
        except:
            pass


    async def download_file(self,  q):
        self.preprocess()
        download_link = await self.get_download_link(q)

        if download_link is None:
            return False

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(download_link) as response:
                data = await response.read()
                async with async_open(f'media/music/{q}.mp3', 'wb') as f:
                    await f.write(data)

        return True


HOSTS ={'Drive': DrivemusicHost}