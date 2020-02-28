import re
import os
import requests
from PIL import Image
from io import BytesIO

proxies = {
  "http": "http://127.0.0.1:10809",
  "https": "http://127.0.0.1:10809",
}

def get_rank_id(yy, mm, ss):
    return f"rank{yy:02d}{mm:02d}{ss:02d}.jpg"

def get_url(yy, mm, ss):
    return f"http://203.104.209.7/kcscontents/information/image/{get_rank_id(yy, mm, ss)}"

def download_img(save_path, link):
    print('download_img from ', link)
    resp = requests.get(link, stream=True, proxies=proxies)
    print(f'status_code={resp.status_code}', end=' ')
    if 200 == resp.status_code:
        if re.search(r'image', resp.headers['content-type'], re.I):
            print(f'content=type is image, saving to {save_path}', end='...')
            img = Image.open(BytesIO(resp.content))
            img.save(save_path)
            print('OK', end='')
    print('\n', end='')


if __name__ == "__main__":
    for yy in range(20, 12, -1):
        for mm in range(12, 0, -1):
            for ss in range(1, 21):
                url = get_url(yy, mm, ss)
                save_path = os.path.expanduser(f'~/.hoshino/tmp/{get_rank_id(yy, mm, ss)}')
                download_img(save_path, url)
                