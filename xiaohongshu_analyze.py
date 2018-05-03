# -*- coding: utf-8 -*-

import requests
import jieba.posseg as psg
import matplotlib.pyplot as plt
import time
import re
from wordcloud import WordCloud, STOPWORDS  # , ImageColorGenerator

num = 0
score = 0
keys = []
jieba_keys = []
scores = []
key_num = {}


def get_goods(num, goods_response):
    '''获取商品信息'''
    goods = {}

    if len(goods_response['data']['items']) > 0:
        goods['goods_title'] = goods_response['data']['items'][num]['title']
        goods['goods_name'] = goods_response['data']['items'][num]['desc']
        goods['goods_id'] = goods_response['data']['items'][num]['id']
        goods['goods_link'] = goods_response['data']['items'][num]['link']
        goods['goods_image'] = goods_response['data']['items'][num]['image']
        goods['sale_price'] = goods_response['data']['items'][num]['item_price'][0]['price']

        if len(goods_response['data']['items'][num]['item_price']) > 1:
            if goods_response['data']['items'][num]['item_price'][1]['type'] == 'member_price':
                goods['vip_price'] = goods_response['data']['items'][num]['item_price'][1]['price']

            if goods_response['data']['items'][num]['item_price'][1]['type'] == 'origin_price':
                goods['origin_price'] = goods_response['data']['items'][num]['item_price'][1]['price']

        goods['vendor_name'] = goods_response['data']['items'][num]['vendor_name']
        goods['vendor_link'] = goods_response['data']['items'][num]['vendor_link']

    else:
        if len(goods_response['data']['recommended_items']) == 0:
            print('系统出错或您的输入有误，建议检查输入或反馈问题')
            exit()
        goods['goods_title'] = goods_response['data']['recommended_items'][num]['title']
        goods['goods_name'] = goods_response['data']['recommended_items'][num]['desc']
        goods['goods_id'] = goods_response['data']['recommended_items'][num]['id']
        goods['goods_link'] = goods_response['data']['recommended_items'][num]['link']
        goods['goods_image'] = goods_response['data']['recommended_items'][num]['image']
        goods['sale_price'] = goods_response['data']['recommended_items'][num]['item_price'][0]['price']

        if goods_response['data']['recommended_items'][num]['item_price'][1]['type'] == 'member_price':
            goods['vip_price'] = goods_response['data']['recommended_items'][num]['item_price'][1]['price']

        if goods_response['data']['recommended_items'][num]['item_price'][1]['type'] == 'origin_price':
            goods['origin_price'] = goods_response['data']['recommended_items'][num]['item_price'][1]['price']

        goods['vendor_name'] = goods_response['data']['recommended_items'][num]['vendor_name']
        goods['vendor_link'] = goods_response['data']['recommended_items'][num]['vendor_link']

    return goods


def analyze(note):
    '''测评关键词与正/负面情绪分析（依据网站：https://bosonnlp.com/demo）'''
    key_url = 'https://bosonnlp.com/analysis/key'
    summary_url = 'https://bosonnlp.com/analysis/sentiment?analysisType='
    times = int(time.time())

    header = {
        'cookie': 'Hm_lvt_6629d4aae357d8d3e47238c93f1e1d78=1525078115,1525154972; Hm_lpvt_6629d4aae357d8d3e47238c93f1e1d78=1525165090'.format(
            times),
        'origin': 'https://bosonnlp.com',
        'referer': 'https://bosonnlp.com/demo',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    param = {'data':note.encode('utf-8')}

    res_keys = requests.post(url=key_url, headers=header, data=param)

    res_scores = requests.post(url=summary_url, headers=header, data=param)

    for i in [num for num in range(1,len(res_keys.content.decode('utf-8').split(',')) + 1)]:
        if i % 2 != 0:
            j = re.match('"([^["]+).*', res_keys.content.decode('utf-8').split(',')[i]).group(1)
            if '试' not in j and '小红书' not in j and len(j) >= 2:
                keys.append(j)

    scores.append(float(re.match('.*\[([0-9.]+).*', res_scores.content.decode('utf-8').split(',')[0]).group(1)))

    for x in psg.cut(note):
        if x.flag.startswith('t'):
            if '春' in x.word or '夏' in x.word or '秋' in x.word or '冬' in x.word or '早' in x.word or '中' in x.word or '晚' in x.word:
                keys.append(x.word)


def word_cloud():
    '''生成词云'''
    backgroud_Image = plt.imread('xiaohongshu_logo.jpg')
    wc = WordCloud( background_color = 'white',    # 设置背景颜色
                    mask = backgroud_Image,        # 设置背景图片
                    max_words = 2000,            # 设置最大现实的字数
                    stopwords = STOPWORDS,        # 设置停用词
                    font_path = 'C:/Users/Windows/fonts/msyh.ttf',# 设置字体格式，如不设置显示不了中文
                    max_font_size = 80,            # 设置字体最大值
                    random_state = 30,            # 设置有多少种随机生成状态，即有多少种配色方案
                    )
    wc.generate(str(key_num))
    # image_colors = ImageColorGenerator(backgroud_Image)
    # wc.recolor(color_func = image_colors)
    plt.imshow(wc)
    plt.axis('off')
    plt.savefig('word_cloud/{}.jpg'.format(key), dpi=800)
    plt.show()


if __name__ == '__main__':
    key = input('请输入商品名 >')
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
    }

    goods_url = 'https://www.xiaohongshu.com/api/store/ps/products?deviceId=C4C7DFB7-6B30-4D3B-9EC3-01157BAED9D8&keyword={}&lang=zh&page=1&size=20&t={}'.format(
        key, int(time.time()))
    goods_response = requests.get(goods_url, headers=header).json()
    goods = get_goods(num, goods_response)

    review_url = 'https://www.xiaohongshu.com/api/store/hf/items/{}/notes?per_page=10'.format(goods['goods_id'])
    review_response = requests.get(review_url, headers=header).json()

    if len(review_response['data']['normal_notes']) >= 5:
        notes = review_response['data']['normal_notes']
        for note in notes:
            analyze(note['desc'])

    else:
        num += 1
        goods = get_goods(num, goods_response)
        review_url = 'https://www.xiaohongshu.com/api/store/hf/items/{}/notes?per_page=10'.format(goods['goods_id'])
        review_response = requests.get(review_url, headers=header).json()
        notes = review_response['data']['normal_notes']
        for note in notes:
            analyze(note['desc'])

    # print(review_url)

    for i in scores:
        score += i

    for ky in keys:
        if ky in key_num.keys():
            key_num[ky] += 1
        else:
            key_num[ky] = 1

    print('商品描述：', goods['goods_title'], '\n', '商品名：', goods['goods_name'], '\n', '商品ID：', goods['goods_id'], '\n',
          '商品链接：', goods['goods_link'], '\n', '商品原价：', goods['sale_price'], 'CNY')

    print('推荐值：', round(score / len(notes) * 100, 5), '%')

    if score / len(notes) >= 0.8:
        print('推荐值分析：', '根据评测分析，值得购买')

    elif score / len(notes) >= 0.75 and score / len(notes) < 0.8:
        print('推荐值分析：', '请酌情考虑（偏向推荐购买）')

    elif score / len(notes) >= 0.6 and score / len(notes) < 0.75:
        print('推荐值分析：', '请酌情考虑')

    else:
        print('推荐值分析：', '根据评测分析，不推荐购买')

    # print('关键字：', key_num)

    word_cloud()
