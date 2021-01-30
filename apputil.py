from datetime import datetime
from bs4 import BeautifulSoup as bs
import os
import requests


def download_image(url, filepath_without_extension, logpath=None, headers=None):
    filepath = filepath_without_extension + '.jpg'

    # Check local directory if the file exists
    if os.path.exists(filepath):
        return False

    if headers is None:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    # Download image:
    try:
        with requests.get(url, stream=True, headers=headers) as r:
            r.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        print("[INFO] Downloaded " + url)

        if logpath:
            try:
                timenow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                with open(logpath, 'a+', encoding='utf-8') as f:
                    f.write('%s\t%s\t%s\n' % (timenow, filepath, url))
            except:
                pass

        return True
    except Exception as e:
        print("[ERROR] Failed to download " + url)
        print(e)
        return False


def get_soup(url, headers=None):
    if headers is None:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    try:
        result = requests.get(url, headers=headers)
        return bs(result.text, 'html.parser')
    except Exception as e:
        print(e)
    return None
