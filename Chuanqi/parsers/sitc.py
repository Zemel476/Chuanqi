from Chuanqi.items import ChuanqiItem


def parse(response, task):
    print('SITC')
    print(response.text)
    item = ChuanqiItem()

    # 应用配置中的解析规则
    yield item
