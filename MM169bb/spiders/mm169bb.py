# -*- coding: utf-8 -*-
import scrapy
from scrapy import selector
from urllib import request
import re


class Mm169bbSpider(scrapy.Spider):
    name = 'mm169bb'
    allowed_domains = ['169mi.com']
    start_urls = ['http://www.169mi.com/guoneimeinv/', 'http://www.169mi.com/xingganmeinv/', 'http://www.169mi.com/xiyangmeinv/', 'http://www.169mi.com/gaogensiwa/', 'http://www.169mi.com/wangyouzipai/']
    download_path = 'D:/mm169/'

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, method='GET', callback=self.parse, meta={'base_url':url})

    def parse(self, response):
        base_url = response.meta['base_url']
        pages = response.selector.xpath('//div[@class="page"]/ul/li/a/@href').extract()[-1]
        cate = pages.split('_')[1]
        total_page = pages.split('_')[-1][:-5]
        for i in range(1, int(total_page)+1):
            cate_list_url = base_url + 'list_' + str(cate) + '_' + str(i) + '.html'
            yield scrapy.Request(url=cate_list_url, method='GET', callback=self.lists_parse)

    def lists_parse(self, response):
        lists = response.selector.xpath('//ul[@class="product01"]/li/a')
        for info in lists:
            cate_info_url = info.xpath('@href').extract()[0]
            yield scrapy.Request(url=cate_info_url, method='GET', callback=self.info_parse, meta={'info_url':cate_info_url})

    def info_parse(self, response):
        info_url = response.meta['info_url']
        pages = response.selector.xpath('//*[@class="pagelist"]/ li[1]/a').re('\d+')
        if pages:
            for i in range(2, int(pages[0])+1):
                info_page_url = info_url[:-5] + '_' + str(i) + '.html'
                yield scrapy.Request(url=info_page_url, method='GET', callback=self.detail_parse)
        yield scrapy.Request(url=info_url, method='GET', callback=self.detail_parse)

    def detail_parse(self, response):
        detail_img = response.selector.xpath('//div[@class="big_img"]/p/img')
        for img in detail_img:
            img_url = img.xpath('@src').extract()[0]
            try:
                request.urlretrieve(img_url, self.download_path + img_url[-17:].replace('/', ''))
                print('---Succssful!---')
            except:
                print('%s Failed!---' %img_url)