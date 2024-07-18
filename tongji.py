# -*- coding: gbk -*-
import pymysql
from openai import OpenAI

# DeepSeek API Key
api_key = 'sk-cbaf83ca18874515961249c3cb6c4ef8'  # 请替换为你的DeepSeek API密钥
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# MySQL数据库连接配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'a257814256',  # 请替换为你的MySQL密码
    'database': 'web_scraping',
    'charset': 'utf8mb4'
}

# 连接到MySQL数据库并读取总结内容
connection = pymysql.connect(**db_config)
summaries = []

try:
    with connection.cursor() as cursor:
        # 选择所有总结内容
        cursor.execute("SELECT summary FROM articles WHERE summary IS NOT NULL")
        summaries = [summary[0] for summary in cursor.fetchall()]
finally:
    connection.close()

# 将所有总结内容合并为一个字符串
all_summaries = "\n".join(summaries)

# 使用DeepSeek API进行统计分析生成报告
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个统计分析生成报告师，你面对数据时会遵循以下规则数据概述 - 概述数据集的基本信息，包括数据来源、时间范围、和数据维度。数据质量检查 - 描述数据的完整性、准确性和一致性的检查结果。预处理步骤 - 详细说明数据清洗、缺失值处理、异常值处理等步骤。描述性统计 - 提供数据的基本统计描述，如均值、中位数、标准差、分位数等。数据可视化 - 描述使用的图表类型（如条形图、折线图、箱型图等），以及这些图表揭示的关键发现。假设检验 - 列出进行的统计假设检验，包括检验类型、使用的显著性水平和结果。相关性分析 - 分析变量之间的相关性，包括使用的相关系数（如皮尔逊、斯皮尔曼）和主要发现。回归分析 - 如果进行了回归分析，描述模型的类型、关键变量、模型拟合度和解释。主成分分析/因子分析 - 如果应用了降维技术，说明选择的方法、结果和解释。聚类分析 - 描述使用的聚类算法、确定的簇数、簇的特征和分析结果。机器学习模型 - 如果涉及机器学习，描述模型类型、训练过程、评估指标和模型表现。结果解释 - 提供对分析结果的详细解释，包括数据分析对业务或研究问题的具体含义。结论和建议 - 基于分析结果，提出结论和可能的业务或研究建议。数据限制 - 讨论数据或方法的局限性，以及这些限制可能对分析结果产生的影响。未来工作方向 - 建议未来可以探索的数据分析方向或方法改进。"},
        {"role": "user", "content": f"请对以下内容进行统计分析并生成报告：\n\n{all_summaries}\n"},
    ],
    stream=False
)
report = response.choices[0].message.content.strip()

# 将报告存储为文本文件
with open('综合报告.txt', 'w', encoding='utf-8') as file:
    file.write(report)

print("综合报告已成功生成并存储为文本文件。")
