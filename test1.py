#!/usr/bin/env python3
import sys
import json
import requests
import argparse
import signal
import time
import os
import itertools
import multiprocessing.dummy as mp
from random import randint

from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib.parse import unquote
from bs4 import BeautifulSoup

try:
    import cPickle as pickle
except:
    import pickle

TIME_INTERVAL = 3600

######## CHANGE THESE  (Or use `--email` and `--password` arguments) #########


USER_EMAIL = "821348914@qq.com"
USER_PASSWORD = "1qaz2wsx#EDC"

##############################################################################

COUNTRY_BR = {'Andorra': 'AD', 'United Arab Emirates': 'AE', 'Afghanistan': 'AF', 'Antigua and Barbuda': 'AG',
              'Anguilla': 'AI', 'Albania': 'AL', 'Armenia': 'AM', 'Angola': 'AO', 'Argentina': 'AR', 'Austria': 'AT',
              'Australia': 'AU', 'Azerbaijan': 'AZ', 'Barbados': 'BB', 'Bangladesh': 'BD', 'Belgium': 'BE',
              'Burkina-faso': 'BF', 'Bulgaria': 'BG', 'Bahrain': 'BH', 'Burundi': 'BI', 'Benin': 'BJ',
              'Palestine': 'BL', 'Bermuda Is.': 'BM', 'Brunei': 'BN', 'Bolivia': 'BO', 'Brazil': 'BR', 'Bahamas': 'BS',
              'Botswana': 'BW', 'Belarus': 'BY', 'Belize': 'BZ', 'Canada': 'CA', 'Central African Republic': 'CF',
              'Congo': 'CG', 'Switzerland': 'CH', 'Cook Is.': 'CK', 'Chile': 'CL', 'Cameroon': 'CM', 'China': 'CN',
              'Colombia': 'CO', 'Costa Rica': 'CR', 'Czech': 'CS', 'Cuba': 'CU', 'Cyprus': 'CY', 'Czech Republic': 'CZ',
              'Germany': 'DE', 'Djibouti': 'DJ', 'Denmark': 'DK', 'Dominica Rep.': 'DO', 'Algeria': 'DZ',
              'Ecuador': 'EC', 'Estonia': 'EE', 'Egypt': 'EG', 'Spain': 'ES', 'Ethiopia': 'ET', 'Finland': 'FI',
              'Fiji': 'FJ', 'France': 'FR', 'Gabon': 'GA', 'United Kingdom': 'GB', 'Grenada': 'GD', 'Georgia': 'GE',
              'French Guiana': 'GF', 'Ghana': 'GH', 'Gibraltar': 'GI', 'Gambia': 'GM', 'Guinea': 'GN', 'Greece': 'GR',
              'Guatemala': 'GT', 'Guam': 'GU', 'Guyana': 'GY', 'Hongkong': 'HK', 'Honduras': 'HN', 'Haiti': 'HT',
              'Hungary': 'HU', 'Indonesia': 'ID', 'Ireland': 'IE', 'Israel': 'IL', 'India': 'IN', 'Iraq': 'IQ',
              'Iran': 'IR', 'Iceland': 'IS', 'Italy': 'IT', 'Jamaica': 'JM', 'Jordan': 'JO', 'Japan': 'JP',
              'Kenya': 'KE', 'Kyrgyzstan': 'KG', 'Kampuchea': 'KH', 'North Korea': 'KP', 'Republic of Korea': 'KR',
              'Republic of Ivory Coast': 'KT', 'Kuwait': 'KW', 'Kazakstan': 'KZ', 'Laos': 'LA', 'Lebanon': 'LB',
              'St.Lucia': 'LC', 'Liechtenstein': 'LI', 'Sri Lanka': 'LK', 'Liberia': 'LR', 'Lesotho': 'LS',
              'Lithuania': 'LT', 'Luxembourg': 'LU', 'Latvia': 'LV', 'Libya': 'LY', 'Morocco': 'MA', 'Monaco': 'MC',
              'Moldova, Republic of': 'MD', 'Madagascar': 'MG', 'Mali': 'ML', 'Burma': 'MM', 'Mongolia': 'MN',
              'Macao': 'MO', 'Montserrat Is': 'MS', 'Malta': 'MT', 'Mauritius': 'MU', 'Maldives': 'MV', 'Malawi': 'MW',
              'Mexico': 'MX', 'Malaysia': 'MY', 'Mozambique': 'MZ', 'Namibia': 'NA', 'Niger': 'NE', 'Nigeria': 'NG',
              'Nicaragua': 'NI', 'The Netherlands': 'NL', 'Norway': 'NO', 'Nepal': 'NP', 'Nauru': 'NR',
              'New Zealand': 'NZ', 'Oman': 'OM', 'Panama': 'PA', 'Peru': 'PE', 'French Polynesia': 'PF',
              'Papua New Cuinea': 'PG', 'Philippines': 'PH', 'Pakistan': 'PK', 'Poland': 'PL', 'Puerto Rico': 'PR',
              'Portugal': 'PT', 'Paraguay': 'PY', 'Qatar': 'QA', 'Romania': 'RO', 'Russia': 'RU', 'Saudi Arabia': 'SA',
              'Solomon Is': 'SB', 'Seychelles': 'SC', 'Sudan': 'SD', 'Sweden': 'SE', 'Singapore': 'SG',
              'Slovenia': 'SI', 'Slovakia': 'SK', 'Sierra Leone': 'SL', 'San Marino': 'SM', 'Senegal': 'SN',
              'Somali': 'SO', 'Suriname': 'SR', 'Sao Tome and Principe': 'ST', 'EI Salvador': 'SV', 'Syria': 'SY',
              'Swaziland': 'SZ', 'Chad': 'TD', 'Togo': 'TG', 'Thailand': 'TH', 'Tajikstan': 'TJ', 'Turkmenistan': 'TM',
              'Tunisia': 'TN', 'Tonga': 'TO', 'Turkey': 'TR', 'Trinidad and Tobago': 'TT', 'Taiwan': 'TW',
              'Tanzania': 'TZ', 'Ukraine': 'UA', 'Uganda': 'UG', 'United States': 'US', 'Uruguay': 'UY',
              'Uzbekistan': 'UZ', 'Saint Vincent': 'VC', 'Venezuela': 'VE', 'Vietnam': 'VN', 'Yemen': 'YE',
              'Yugoslavia': 'YU', 'South Africa': 'ZA', 'Zambia': 'ZM', 'Zaire': 'ZR', 'Zimbabwe': 'ZW'}

# COLORS !!
RED = '\x1b[91m'
RED1 = '\033[31m'
BLUE = '\033[94m'
GREEN = '\033[32m'
BOLD = '\033[1m'
NORMAL = '\033[0m'
ENDC = '\033[0m'

# Safely stop the loops in case of CTRL+C
global interrputed
interrputed = False


# CTRL+C handling
def signal_handler(sig, frame):
    print(BLUE + '\n [*] You pressed Ctrl+C!')
    interrputed = True
    sys.exit(1)


signal.signal(signal.SIGINT, signal_handler)


class ZoomEye(object):
    def __init__(self, filename, dork):

        self.file_name = filename
        self.dork = dork
        self.io = open(self.file_name, 'a')
        self.base_url = 'https://www.zoomeye.org'
        self.url_first = 'https://www.zoomeye.org/searchResult?q='
        self.search_url = unquote(self.url_first) + dork  # unquote() is used to decode the url  %20 -> ' ' %26 -> '&' etc.   https://www.zoomeye.org/searchResult?q=app:%22Apache%20httpd%22%20country:%22CN%22%20port:%2243%22

    def login(self):

        service_args = []

        options = webdriver.ChromeOptions()  # webdriver.ChromeOptions() 创建了一个选项对象 options，接下来可以通过 options.add_argument() 方法添加一些启动选项，例如 --headless 就是启用无头模式的选项。
        options.add_argument("start-maximized")  # 最大化窗口
        options.add_argument(
            "disable-infobars")  # 禁用浏览器正在被自动化程序控制的提示,通过添加这个参数可以防止被浏览器识别出是通过自动化测试进行访问，从而避免被检测出来并降低网站的反爬虫门槛。
        options.add_argument("--disable-extensions")  # 禁用扩展
        options.add_argument('--disable-blink-features=AutomationControlled')  # 禁用自动化控制
        self.driver = webdriver.Chrome(
            options=options)  # webdriver.Chrome() 创建了一个 Chrome 浏览器对象，并且使用定义好的选项和服务参数来启动浏览器。这个浏览器实例可以用于后续的模拟用户行为，比如自动化测试、数据爬取等。

        self.driver.get(
            "https://sso.telnet404.com/cas/login?service=https%3A%2F%2Fwww.zoomeye.org%2Flogin")  # 通过 driver.get() 方法，可以让浏览器打开指定的 URL。这里我们打开了zoomeye的登录页面。
        self.driver.find_element(By.NAME, 'email').send_keys(
            USER_EMAIL)  # 通过 driver.find_element() 方法，可以通过各种方式定位到页面中的元素，例如通过 By.NAME 的方式定位到 name 属性为 email 的元素，然后通过 send_keys() 方法模拟键盘输入。
        self.driver.find_element(By.NAME, 'password').send_keys(
            USER_PASSWORD)  # 通过 driver.find_element() 方法，可以通过各种方式定位到页面中的元素，例如通过 By.NAME 的方式定位到 name 属性为 password 的元素，然后通过 send_keys() 方法模拟键盘输入。
        input(
            '登入後請按任意鍵繼續')  # 通过 input() 方法，可以让程序暂停下来，等待用户输入任意字符之后再继续执行。这里我们暂停下来，等待用户输入任意字符之后再继续执行，这样就可以在浏览器中完成登录操作了。

    def save_to_file(self, s):
        with open(self.file_name, 'r') as f:
            original_data = set(f.read().splitlines())
        if s.strip('\n') in original_data:
            print("重复条目，不写入文件")
        else:
        # 写入新数据
            with open(self.file_name, 'a') as file:
                file.write(s.strip('\n') + '\n')
            print("数据已成功写入文件")

    def get_one(self):

        print('-' * 80)
        print('getting page 1....')

        self.driver.get(self.search_url)

        # Ugly code here should get the result first
        try:
            wait = WebDriverWait(self.driver, TIME_INTERVAL)
            element = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="search-result-item clearfix"]')))
        except TimeoutException as e:
            return 0

        result_counts = ""
        while "结果" not in result_counts:  # 通过 driver.find_elements() 方法，可以通过各种方式定位到页面中的元素，例如通过 By.CLASS_NAME 的方式定位到 class 属性为 search-result-summary 的元素，然后通过 text 属性获取到该元素的文本内容。
            result_summary = self.driver.find_elements(By.CLASS_NAME, 'search-result-summary')[0]
            result_counts = result_summary.text
            print(result_counts)
            time.sleep(1)

        result_countsn = int(result_summary.text[4:].split(' ')[0].replace(',', ''))
        print(GREEN + str(result_countsn))

        if result_countsn % 20:
            pages = int(result_countsn / 20) + 1
        else:
            pages = int(result_countsn / 20)

        if pages >= 100:
            pages = 100

        print('total pages:', pages)

        cnt = 1
        # find results
        while cnt <= pages:
            print("page: ", cnt)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            all_class = soup.find_all("div", class_="search-result-item-info")
            # print(all_class)
            for c in all_class:
                # not all ip have urls
                try:
                    if args.port:
                        port = c.find_all("div", class_="search-result-tags")[0]("a")[0]["href"]
                        port = port.split('port:"')[1].split('" %2bser')[0]
                        print(port)
                        # url = c.find_all("h3", style="font-size: 18px;")[0]("a")[1]["href"]
                        # print('url:', url)
                    else:
                        ip = c.find_all("h3", style="font-size: 18px;")[0]("a")[0].string
                        # print(c.find_all("div", class_="ant-tag ant-tag-red", style="cursor: pointer;")[0]("span")[0].text)
                        div_element = c.find_all("div", class_="ant-tag ant-tag-red", style="cursor: pointer;")[0]
                        span_element = div_element.find_all("span", class_="ant-tag-text")[0]
                        label = span_element.find(text=True, recursive=False)
                        print("ip_label:",ip + ":" +label)
                    text = c.find_next_sibling().string
                    # print(text)
                except Exception as e:
                    print('ip:', ip)
                    self.save_to_file(ip)
                    continue

                # check text
                if args.text != "" and args.text not in text:  #
                    continue

                # if port with ip
                if args.port:
                    self.save_to_file(ip + ":" + port)
                else:
                    self.save_to_file(ip + ":" + label)
                print("-" * 80)
            # click next
            if cnt < pages:
                self.driver.find_element(By.XPATH, '//li[@class=" ant-pagination-next"]').click()  #
                wait = WebDriverWait(self.driver, TIME_INTERVAL)
                element = wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@class="search-result-item clearfix"]')))
                time.sleep(randint(1, 9))

            cnt += 1

    # def xpath_soup(element):
    #     """
    #     Generate xpath of soup element
    #     :param element: bs4 text or node
    #     :return: xpath as string
    #     """
    #     components = []
    #     child = element if element.name else element.parent
    #     for parent in child.parents:
    #         """
    #         @type parent: bs4.element.Tag
    #         """
    #         previous = itertools.islice(parent.children, 0, parent.contents.index(child))
    #         xpath_tag = child.name
    #         xpath_index = sum(1 for i in previous if i.name == xpath_tag) + 1
    #         components.append(xpath_tag if xpath_index == 1 else '%s[%d]' % (xpath_tag, xpath_index))
    #         child = parent
    #     components.reverse()
    #     return '/%s' % '/'.join(components)

    def interceptor(self, request):
        # Use the interceptor to get the Cube-Authorization headers
        if 'Cube-Authorization' in request.headers:
            self.cube_authorization = request.headers['Cube-Authorization']
            self.driver.request_interceptor = None

    def get_result(self):

        # check year
        if args.year:  # year=2022
            year = int(args.year)  # year=2022
            year_str = f'%2Bafter:"{year}-01-01" %2Bbefore:"{year + 1}-01-01"'  # year_str=%2Bafter:"2022-01-01" %2Bbefore:"2023-01-01"
            print(year_str)  # %2Bafter:"2022-01-01" %2Bbefore:"2023-01-01"
            self.search_url = self.search_url.strip(
                "&t=all") + year_str  # https://www.zoomeye.org/searchResult?q=title%3A"VMware%20vRealize%20Network%20Insight"

        if not args.country and args.subdivision:  # 如果没有指定国家，但是指定了subdivision，则为true

            self.driver.get(self.search_url)

            wait = WebDriverWait(self.driver, TIME_INTERVAL)  # 等待
            element = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//p[@class="search-result-filter-title"]')))  # 等待元素加载完成
            soup = BeautifulSoup(self.driver.page_source, "html.parser")  # 解析网页
            subdivision = soup.find_all("p", class_="search-result-filter-title")[
                2]  # 找到<p>标签且class属性值等于"search-result-filter-title"的所有元素，然后返回一个列表，其中第 3 个匹配元素被赋值给 subdivision。

            while True:
                subdivision = subdivision.find_next_sibling()  # 找到下一个兄弟元素  例如：<p>1</p><p>2</p>，那么<p>1</p>的下一个兄弟元素就是<p>2</p>
                if subdivision == None or subdivision.contents[
                    0] == "More":  # 如果没有下一个兄弟元素或者下一个兄弟元素的内容为More  判断 subdivison 的第一个子元素是否为 "More" 可以帮助我们判断当前这个段落是否是一个可折叠/展开的段落，如果是，则直接跳过该段落，继续查找下一个合适的段落。
                    print(subdivision.contents)
                    break
                print(subdivision.contents[0])  # 打印 subdivison 的第一个子元素
                print(subdivision.contents[0].string)  # 打印 subdivison 的第一个子元素的内容

                # check subdivision name
                subdivision_name = subdivision.contents[0].string
                if subdivision_name == "Unknown":
                    break

                subdivision_url = subdivision.contents[0]["href"]  # 打印 subdivison 的第一个子元素的 href 属性值
                print(subdivision_url)
                self.search_url = unquote(self.base_url) + subdivision_url
                print(self.search_url)
                self.get_one()  # 调用 get_one() 函数
                time.sleep(randint(1, 9))

        if args.country:

            self.driver.request_interceptor = self.interceptor

            # get all the countries
            self.driver.get(self.search_url)
            wait = WebDriverWait(self.driver, TIME_INTERVAL)
            element = wait.until(EC.element_to_be_clickable((By.XPATH, '//p[@class="search-result-filter-title"]')))

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            # country = soup.find_all("p", string="Country")[0]
            # countries = country.find_next_sibling().contents[0].contents[0]['href']
            # self.driver.get(f"{self.base_url}{countries}")
            # print(countries)

            # Find More country
            cookies = self.driver.get_cookies()
            # print(cookies)

            r = requests.Session()
            for cookie in cookies:
                r.cookies.set(cookie['name'], cookie['value'])
            # This header needs to be captured in :More: request headers
            headers = {
                "Cube-Authorization": f"{self.cube_authorization}",
                "Referer": "https://www.zoomeye.org/toolbar/aggregation",
                "Host": "www.zoomeye.org",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36",
                "Accept": "application/json, text/plain, */*"
            }
            res = r.get(f"https://www.zoomeye.org/analysis/aggs?language=en&field=country&q={self.dork}",
                        headers=headers)
            res_j = res.json()
            assert "country" in res_j
            countries = res_j["country"]
            for i in range(min(len(countries), 20)):
                c_name = countries[i]["name"]
                assert c_name in COUNTRY_BR
                self.search_url = f'{unquote(self.base_url)}/searchResult?q={self.dork}%20%2Bcountry:"{COUNTRY_BR[c_name]}"&t=all'
                print(self.search_url)

                # get all subdivisions
                if args.subdivision:
                    self.driver.get(self.search_url)
                    wait = WebDriverWait(self.driver, TIME_INTERVAL)
                    element = wait.until(
                        EC.element_to_be_clickable((By.XPATH, '//p[@class="search-result-filter-title"]')))
                    soup = BeautifulSoup(self.driver.page_source, "html.parser")
                    subdivision = soup.find_all("p", string=c_name)
                    assert len(subdivision) != 0
                    subdivision = subdivision[0]

                    while True:
                        subdivision = subdivision.find_next_sibling()
                        if subdivision == None or subdivision.contents[0] == "More":
                            print(subdivision.contents)
                            break
                        print(subdivision.contents[0])
                        print(subdivision.contents[0].string)

                        # check subdivision name
                        subdivision_name = subdivision.contents[0].string
                        if subdivision_name == "Unknown":
                            break

                        subdivision_url = subdivision.contents[0]["href"]
                        print(subdivision_url)
                        self.search_url = unquote(self.base_url) + subdivision_url
                        print(self.search_url)
                        self.get_one()
                        time.sleep(randint(1, 9))

                    # get next country
                    continue

                self.get_one()
                time.sleep(randint(3, 9))

            self.driver.close()
            return

        self.get_one()
        self.driver.close()
        return


parser = argparse.ArgumentParser(
    description='Simple ZoomEye searcher, outputs IPs to stdout or file')

parser.add_argument("-q", "--query", help="Your ZoomEye Search")
parser.add_argument(
    "-s", "--save", help="Save output to <file>, default file name: results.txt", nargs="?", type=str,
    default="results1.txt")
parser.add_argument(
    "-t", "--text", help="Find specific text in the HTML page", type=str, default="")
parser.add_argument(
    "-p", "--port", help="Save ip and port", action='store_true')
parser.add_argument(
    "-y", "--year", help="Set the year", type=str, default="")
parser.add_argument(
    "-c", "--country", help="Search by countries", action='store_true')
parser.add_argument(
    "-d", "--subdivision", help="Search by subdivision", action='store_true')

global args
args = parser.parse_args()  # 解析命令行参数

zoom = ZoomEye(args.save, args.query)  # 将保存文件和查询语句传入ZoomEye类中
zoom.login()
zoom.get_result()



