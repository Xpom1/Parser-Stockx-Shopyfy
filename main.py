import random
from selenium import webdriver
from selenium_stealth import stealth
import json
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import chromedriver_autoinstaller
import shopify
import requests


def serch(sku, proxy):
    prise = {}
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "eager"
    options = webdriver.ChromeOptions()
    options.add_argument('--proxy-server=%s' % proxy)
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--headless")
    options.add_argument("--log-level=3")
    chromedriver_autoinstaller.install()
    driver = webdriver.Chrome(desired_capabilities=caps, options=options)
    driver.set_window_size(1920, 1080)
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    i = sku
    try:
        url = f"https://stockx.com/search?s={i}"
        driver.get(url)
        q = driver.find_element_by_xpath('//*[@id="browse-grid"]/div[1]/div/a').get_attribute('href')
        q = q.split("/")
        z = 'https://stockx.com/api/products/' + str(q[3]) + '?includes=market,360&currency=USD&country=GB'
        driver.execute_script(f"window.location.replace('{z}')")
        info = json.loads(driver.find_element_by_xpath('/html/body/pre').text)
        a = list(info.get("Product").get("children").keys())
        for i in range(len(a)):
            prise[info.get("Product").get("children").get(a[i]).get('shoeSize')] = \
                info.get("Product").get("children").get(a[i]).get('market').get('lowestAsk')
        name = info.get("Product").get('title')
        driver.close()
        return name, prise
    except:
        driver.close()


shop_url = "https://%s:%s@name.myshopify.com/admin" % (
    '...', '...')
shopify.ShopifyResource.set_site(shop_url)

url = "..."


def get_info(id):
    send_url = url + 'products/' + str(id) + '.json'
    r = requests.get(send_url)
    return r.json()


def change(variants, price, product, title, stockx_us, inventory_quantity):
    if price != 0:
        if price * 0.3 > 70:
            price = price * 1.3
            price = round(price / 10) * 10
            variant = shopify.Variant(dict(id=variants, price=price))
            product.add_variant(variant)
            print(f'[+] {title} = {stockx_us}US -> {price}')
        else:
            price = price + 70
            variant = shopify.Variant(dict(id=variants, price=price))
            product.add_variant(variant)
            print(f'[+] {title} = {stockx_us}us -> {price} +')
    elif price == 0 and inventory_quantity > 0:
        print(f'[+] {title} = {stockx_us}US -> Please fix Available!!!')
    else:
        print(f'[+] {title} = {stockx_us}US -> don`t change')


def id_done(id):
    FIND = f"{id}"
    INFILE = "Need/id.txt"
    OUTFILE = 'Need/id_done.txt'
    ENC = "utf-8"
    with open(INFILE, 'r', encoding=ENC) as f:
        r = f.read().strip().split('\n')
        r.remove(FIND)
    open(INFILE, 'w').close()
    with open(INFILE, 'w', encoding=ENC) as f:
        for i in r:
            f.write(i + '\n')
    with open(OUTFILE, 'a', encoding=ENC) as f:
        f.write(FIND + '\n')


def update(id, proxy):
    para = get_info(id)
    name = para['product'].get('title')
    name_stockx, price = serch(name, proxy)
    stockx_us = list(price.keys())
    price = list(price.values())
    print(f'{name} = {name_stockx}')
    id_para = []
    title = []
    inventory_quantity = []
    var = para['product'].get('variants')
    for i in range(len(var)):
        inventory_quantity.append(var[i].get('inventory_quantity'))
        id_para.append(var[i].get('id'))
        title.append(var[i].get('title'))
    product = shopify.Product(dict(id=id))
    for i in range(len(stockx_us)):
        for j in range(len(title)):
            q = title[j].split(' - ')[0]
            q = ''.join(i for i in q if not i.isalpha())
            q = q.replace('(', '').replace(')', '')
            s = stockx_us[i]
            s = ''.join(i for i in s if not i.isalpha())
            if s == q:
                change(id_para[j], price[i], product, title[j], stockx_us[i], inventory_quantity[j])
                break
    print('Save...')
    product.save()
    id_done(id)
    print(f'[✓] {id} Done')
    print()


with open('Need/proxy.txt') as f:
    proxy_ = f.read().strip().split('\n')

start = time.time()


def main():
    try:
        with open('Need/id.txt') as f:
            id_ = f.read().strip().split('\n')
        random.shuffle(proxy_)
        proxy_count = 0
        for id in id_:
            if proxy_count + 1 == len(proxy_):
                print(f'Start {id} on {proxy_[proxy_count]}')
                update(id, proxy_[proxy_count])
                proxy_count = 0
                print('Sleep 60 seconds...')
                print()
                time.sleep(60)
            else:
                print(f'Start {id} on {proxy_[proxy_count]}')
                update(id, proxy_[proxy_count])
                proxy_count += 1
                print('Sleep 10 seconds...')
                print()
                time.sleep(10)
    except:
        print('\n[!] Stockx don`t respond\n[!] Try again after 5 minutes\n')
        time.sleep(300)
        main()


main()

end = time.time() - start
print(end)
print('\nEND')
time.sleep(3600)
