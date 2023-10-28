![TeamCity build status](https://teamcity.milkhunters.ru/app/rest/builds/buildType:id:MilkhuntersBackend_Build_Prod/statusIcon.svg)

# Hack Vacancy Service

# Сборка и запуск

## Docker

Соберите образ приложения:
```bash
docker build -t milky-backend .
```

Запустите контейнер на основе образа:
```bash
docker run -d --restart=always -u 0 --name milky-blog-dev -e DEBUG=1 -e CONSUL_ROOT=milk-back-dev -p 8000:8000 -m 1024m --cpus=2 milky-blog-dev
```
