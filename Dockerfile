# 使用官方Python基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录内容到工作目录
COPY . /app

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口（如果有Web服务）
EXPOSE 8000

# 运行应用
CMD ["python", "your_script.py"]  # 替换为你的Python脚本名称
