# settings.py配置
## 邮件配置
```python
EMAIL_HOST = ''   # 用于发送电子邮件的主机
EMAIL_HOST_USER = ""    # 发送邮件的邮箱地址
EMAIL_HOST_PASSWORD = ""     # 发送邮件的邮箱密码
EMAIL_PORT = 465       # SMTP服务器端口号。通常，使用SSL加密的端口是465，而非SSL加密的端口是25或587，具体取决于你的邮件提供商。
EMAIL_USE_SSL = True    # 是否使用隐式的安全连接

# 个后端实际上并不发送电子邮件，而是将邮件内容输出到控制台（终端或命令行界面）供调试和开发使用。
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
## redis配置
```python
################### redis 配置 ##########################
CACHES = {
    "default": {            # 缓存别名，用于标识不同的缓存配置。通常用于定义多个缓存
        "BACKEND": "django_redis.cache.RedisCache",     # 使用django-redis 提供的 redis 缓存后端
        "LOCATION": "redis://127.0.0.1:6379/",                  # 连接地址和端口
        "OPTIONS": {                                                        # 配置项
            "CLIENT_CLASS": "django_redis.client.DefaultClient",    # 客户端实现类，通常固定使用
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 100,
                "encoding":'utf-8',
            },     # 最大连接数 100  字符编码为 utf-8
            "PASSWORD": "******",  # 密码  无 则为空
        },
        #"KEY_PREFIX": "example",    # 缓存键的前缀，用于在存储缓存键时防止与其他应用程序的键冲突。在这个示例中，键的前缀为 "example"。
    }
}
```
## 数据库配置
```python
################### mysql 配置 ##########################
DATABASES = {
    'default': {   # 数据库别名，用于标识不同的数据库配置。通常用于定义多个数据库
        'ENGINE': 'django.db.backends.mysql',
        'NAME': "aaa",     # 数据库名
        'USER': "aaa",     # 用户名
        'PASSWORD': "111111",  # 密码
        'HOST': 'localhost',    # 连接地址
        "PORT": '3306',         # 连接端口
    }
}
```
# 运行
## 数据库初始化
```bash
python ./manager makemigrations
python ./manager migrate
```
## 创建管理员账户
```bash

```
## 启动项目
```bash
python manager runserver
```