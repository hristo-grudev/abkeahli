import scrapy

from scrapy.loader import ItemLoader

from ..items import AbkeahliItem
from itemloaders.processors import TakeFirst
import requests

url = "https://abk.eahli.com/abk/News_Promotions.aspx?type=news"

payload = {}
headers = {
  'Cookie': 'ASP.NET_SessionId=nqwyjk0buybfwdxb0lrhpky0; BIGipServer~WEBSITES~ABK_WEBSITE.app~ABK_WEBSITE_pool=rd65o00000000000000000000ffff0a01410ao443; TS01f27111=01393153b3d2a3c3982cfbb0bab1486d622dbe94aa6d72b7a808c06ca42d9e20115b89ea4b92f6ddf178b76f61e4d6da890f59a59e'
}


class AbkeahliSpider(scrapy.Spider):
	name = 'abkeahli'
	start_urls = ['https://abk.eahli.com/abk/News_Promotions.aspx?type=news']

	def parse(self, response):
		data = requests.request("GET", url, headers=headers, data=payload)
		data = scrapy.Selector(text=data.text)

		post_links = data.xpath('//div[@class="NewsBox"]//a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		data = requests.request("GET", response.url, headers=headers, data=payload)
		data = scrapy.Selector(text=data.text)
		title = data.xpath('//h3[@class="HeaderTitle"]/span/text()').get()
		description = data.xpath('//div[@class="PageContent"]//p//text()[normalize-space() and not(ancestor::i)]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()
		date = data.xpath('//p[@style="text-align:right;"]/i/text()').get()

		item = ItemLoader(item=AbkeahliItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
