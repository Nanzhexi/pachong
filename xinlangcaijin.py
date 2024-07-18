import requests
from bs4 import BeautifulSoup
import re
import pymysql
from openai import OpenAI

# DeepSeek API Key
api_key = 'sk-cbaf83ca18874515961249c3cb6c4ef8'  # 请替换为你的DeepSeek API密钥
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# 目标URL
url = 'https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh600519.phtml'

# MySQL数据库连接配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'a257814256',  # 请替换为你的MySQL密码
    'database': 'web_scraping',
    'charset': 'utf8mb4'
}

# 发送HTTP请求获取页面内容
response = requests.get(url)
response.encoding = 'gbk'  # 确保正确的编码

# 解析页面内容
soup = BeautifulSoup(response.text, 'html.parser')

# 找到<div class="datelist">
datelist_div = soup.find('div', class_='datelist')

# 提取所有<ul>中的<a>标签
ul = datelist_div.find('ul')
items = ul.find_all('a')

# 存储提取结果
data = []

# 正则表达式模式匹配时间
time_pattern = re.compile(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}')

# 解析每个<a>标签中的内容
for item in items:
    # 提取链接和标题
    link = item['href']
    title = item.get_text(strip=True)

    # 提取前面的时间
    previous_text = item.previous_sibling.strip()
    match = time_pattern.search(previous_text)
    if match:
        date_time = match.group()
    else:
        date_time = "未知时间"

    # 移除特殊字符
    date_time = date_time.replace('\xa0', ' ')
    title = title.replace('\xa0', ' ')

    # 添加到数据列表
    data.append([date_time, link, title])


# 读取链接并抓取每个链接中的文章内容
def clean_text(text):
    return text.encode('gbk', errors='ignore').decode('gbk', errors='ignore')


# 连接到MySQL数据库
connection = pymysql.connect(**db_config)
try:
    with connection.cursor() as cursor:
        # 插入数据的SQL
        sql = "INSERT INTO articles (date_time, title, content) VALUES (%s, %s, %s)"

        for entry in data:
            date_time, link, title = entry

            response = requests.get(link)
            response.encoding = 'utf-8'  # 这里设为 'utf-8'

            article_soup = BeautifulSoup(response.text, 'html.parser')
            article_div = article_soup.find('div', class_='article', id='artibody')

            if article_div:
                article_text = article_div.get_text(strip=True, separator='\n')
                article_text = clean_text(article_text)
                # 插入数据
                cursor.execute(sql, (date_time, title, article_text))
            else:
                cursor.execute(sql, (date_time, title, '未找到文章内容'))

    # 提交事务
    connection.commit()
finally:
    connection.close()

print("数据已成功提取并存储到数据库中。")

# 连接到MySQL数据库并读取内容进行总结
connection = pymysql.connect(**db_config)
try:
    with connection.cursor() as cursor:
        # 选择所有文章内容
        cursor.execute("SELECT id, content FROM articles")
        articles = cursor.fetchall()

        # 更新每篇文章的总结
        for article in articles:
            article_id = article[0]
            content = article[1]

            # 使用DeepSeek API进行内容总结
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是茅台AI研究员你会对每一个内容生成一个简洁的文章摘要，专门为贵州茅台公司提供市场趋势、消费者行为、竞争分析和产品改进的深入分析和建议。你的目标是帮助贵州茅台公司在市场上保持竞争力。请根据以下提示进行分析：市场趋势分析:当前全球和国内酒类市场的主要趋势是什么？有哪些新的市场机会和潜在威胁？茅台在这些趋势中的位置如何？消费者行为分析:消费者对茅台产品的偏好和行为模式是什么？社交媒体上关于茅台的讨论热点是什么？销售数据中有哪些值得注意的变化？竞争分析:茅台的主要竞争对手有哪些？竞争对手的市场策略和产品特点是什么？茅台可以从竞争对手那里学到什么？产品改进建议:基于市场和消费者分析，茅台可以如何改进现有产品？有哪些新产品开发的机会？如何提升产品的市场竞争力？品牌管理:茅台的品牌知名度和美誉度如何？有哪些品牌推广和管理的策略建议？如何提升品牌在消费者心中的地位？请根据以上提示进行详细分析，并提供具体的建议和策略"},
                    {"role": "user", "content": f"请对以下内容进行总结：\n\n{content}\n"},
                ],
                stream=False
            )
            summary = response.choices[0].message.content.strip()

            # 更新数据库中的总结
            update_sql = "UPDATE articles SET summary=%s WHERE id=%s"
            cursor.execute(update_sql, (summary, article_id))

    # 提交事务
    connection.commit()
finally:
    connection.close()

print("内容总结已成功提取并存储到数据库中。")
