# 使用python运行时镜像
FROM python:3.6-slim

# 工作空间
WORKDIR /app

# 复制当前目录的内容到工作空间
COPY . /app

# 从网站下载依赖
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# 暴露容器的80端口
EXPOSE 80

# 定义环境变量
ENV NAME world

# 运行app.py,当容器启动时
CMD ["flask","run"]

