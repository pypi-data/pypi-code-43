from get_fshare import FSAPI


a = FSAPI('doanhtu@yandex.com', 'Tu0703$$')
a.login()

link = a.download('https://www.fshare.vn/file/T97D2P2STT')
print(link)

folder = a.get_folder_urls('https://www.fshare.vn/folder/T79W846Q3T')
print(folder)

r = a.upload('/Users/tu/Downloads/WebStorm-2018.2.3.dmg', '/Photos')
print(r)
