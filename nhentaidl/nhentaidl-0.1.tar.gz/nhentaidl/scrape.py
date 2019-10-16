from bs4 import BeautifulSoup
import requests
# from multiprocessing import Pool, freeze_support
# from concurrent.futures import ProcessPoolExecutor, as_completed
import os
import wget
import sys


base_url = 'https://nhentai.net'
all_pages_url = []
manga_images = list()
total_manga_pages = 1
manga_name = ''
desktop_directory = ''
save_directory = ''
download_index = 1
site_url = ''

if os.name == 'nt':
    desktop_directory = os.path.join(
        os.environ["HOMEPATH"], "Desktop")
elif os.name == 'posix':
    desktop_directory = os.path.join(
        os.path.expanduser('~'), 'Desktop')
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}


def find_total_pages():
    global site_url
    site_url = f'{base_url}/g/{sys.argv[1]}/1'
    global total_manga_pages
    global manga_name
    html = requests.get(site_url, headers)
    soup = BeautifulSoup(html.content, 'lxml')
    total_manga_pages = soup.find('span', {'class': 'num-pages'}).text
    manga_name = (soup.title.text.split('-')[0]).strip()


def save_files(url):
    wget.download(url, save_directory)


def generate_all_urls():
    global manga_name
    global save_directory

    find_total_pages()
    for num in range(1, int(total_manga_pages) + 1):
        all_pages_url.append(f'{base_url}/g/{sys.argv[1]}/{str(num)}')

    mode = int('0775')

    if os.name == 'nt':
        save_directory = os.path.join(desktop_directory, manga_name)
    else:
        save_directory = os.path.join(desktop_directory, manga_name)

    if not os.path.exists(save_directory):
        os.makedirs(save_directory, mode)


def scrape_images(url):
    global manga_images
    global download_index
    try:
        html = requests.get(url, headers)
        soup = BeautifulSoup(html.content, 'lxml')
        image = soup.find('img', {'class': 'fit-horizontal'})
        print('\nDownloading ' + str(download_index) +
              ' of ' + str(total_manga_pages))
        wget.download(image['src'], save_directory)
        download_index += 1
        # print(image['src'])
        # save_files(image['src'])
    except:
        print('error')


if __name__ == '__main__':
    find_total_pages()
    generate_all_urls()
    for index, url in enumerate(all_pages_url):
        scrape_images(url)

    # with Pool() as pool:
    #     pool.map(scrape_images, all_pages_url)

    # for url in manga_images:
    #     save_files(url)
