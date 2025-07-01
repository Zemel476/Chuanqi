from Chuanqi.items import ChuanqiItem

def parse(response, task_data):
    # 使用ItemLoader处理数据
    item = ChuanqiItem()

    # 分页处理
    # next_page = response.css('a.next-page::attr(href)').get()
    # if next_page:
    #     yield response.follow(
    #         next_page,
    #         callback=self.parse,
    #         meta={'task_data': task_data}
    #     )
    #
    # yield loader.load_item()

    yield item
