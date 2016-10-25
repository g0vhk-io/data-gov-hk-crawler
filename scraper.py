import requests
from lxml import etree
from StringIO import StringIO
from urlparse import urljoin
import sys
import json

ROOT_URL = "https://data.gov.hk/en-data/dataset"

def parse_page(page_number):
    print "Crawling page %d" % (page_number)
    r = requests.get(ROOT_URL + "?page=%d" % (page_number)) 
    parser = etree.HTMLParser()
    root   = etree.parse(StringIO(r.content), parser)
    content_div = root.xpath("//div[@class=\"view-content\"]")[0]
    data_set_items = content_div.xpath(".//div[@class=\"dataset-item\"]")
    urls = []
    for item in data_set_items:
        url = item.xpath(".//h3[@class=\"dataset-heading\"]/a/@href")[0] 
        urls.append(urljoin(ROOT_URL, url))
    return urls

def parse_detail(dataset_url):
    r = requests.get(dataset_url)
    parser = etree.HTMLParser()
    root   = etree.parse(StringIO(r.content), parser)
    title = root.xpath("//h1/text()")[0].strip()
    office = root.xpath("//img[@class=\"media-image\"]/@alt")[0]
    categories = [t.strip() for t in root.xpath("//a[@class=\"badge\"]/text()") if t != None]
    dataset_resources = root.xpath("//div[@class=\"span6 dataset-resource\"]")
    resources = []
    for resource in dataset_resources:
        dataset_resource_format = resource.xpath("./div[@class=\"dataset-resource-format\"]/span/text()")[0]
        dataset_resource_name = resource.xpath("./div[@class=\"dataset-resource-name\"]/div/div/a")[0].attrib['title']
        dataset_resource_relative_url = resource.xpath("./div[@class=\"dataset-resource-name\"]/div/div/a")[0].attrib['href']
        dataset_resource_link = urljoin(ROOT_URL, dataset_resource_relative_url)
        resources.append({'link': dataset_resource_link, 'name': dataset_resource_name, 'format': dataset_resource_format})
    return {'title': title, 'office': office,  'categories': categories, 'resources':resources}

r = requests.get(ROOT_URL)
parser = etree.HTMLParser()
root   = etree.parse(StringIO(r.content), parser)
pagination = root.xpath("//div[@class=\"pagination pagination-centered\"]")[0]
last_page_link = pagination.xpath("./ul/li")[-2].xpath('a')[0].attrib['href']
max_page_size = int(last_page_link.split('=')[-1])
detail_urls = []
datasets = []
for i in range(1, max_page_size + 1):
    detail_urls += parse_page(i)

for detail_url in detail_urls:
    datasets.append(parse_detail(detail_url))

with open('output.json', 'w') as outfile:
    json.dump({'datasets':datasets}, outfile)
