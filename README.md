# Harbor

Статичний сайт Nginx має головну сторінку з ідентифікатором `devops6-harbor-42` та JSON з полями `status` і `release`. Правила маршрутизації описано в `nginx/harbor.conf`. Python-залежності та базовий образ зафіксовано.

## Підготовка та запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export BASE_URL=http://127.0.0.1:8388
export EXPECTED_RELEASE=devops6-harbor-42
export CHECK_TIMEOUT=3
docker build -t harbor-web:lab .
docker run -d --name harbor-web -p 127.0.0.1:8388:80 harbor-web:lab
curl -fsS --retry 5 --retry-all-errors --max-time 2 "$BASE_URL/"
```

## Перевірка

```bash
python -m pytest -v --hosts=docker://harbor-web tests
python verify_web.py
```

Testinfra перевіряє файли та синтаксис Nginx у контейнері. Тести Requests перевіряють фактичні HTTP-коди, ідентифікатор і JSON через опублікований порт. `verify_web.py` запускає curl для головної сторінки. Коди завершення 0, 1 і 2 відповідають успіху, невдалій перевірці та тайм-ауту.

## Локальні досліди

Починай кожний дослід зі справного контейнера. Виконуй команди в блоках по одній. Повтори pytest і `python verify_web.py` після зміни та відновлення.

1. Пошкодь вміст health.json. Для відновлення скопіюй початковий файл.

   ```bash
   docker exec harbor-web sh -c 'echo invalid-json > /usr/share/nginx/html/health.json'
   curl -si --max-time 5 "$BASE_URL/health.json"
   docker cp web/health.json harbor-web:/usr/share/nginx/html/health.json
   ```

2. Видали конфігурацію в контейнері, що працює, і поверни її з репозиторію.

   ```bash
   docker exec harbor-web rm /etc/nginx/conf.d/default.conf
   docker cp nginx/harbor.conf harbor-web:/etc/nginx/conf.d/default.conf
   ```

3. Призупини контейнер, перевір реакцію на тайм-аут і віднови роботу.

   ```bash
   docker pause harbor-web
   python -m pytest -v --hosts=docker://harbor-web tests
   python verify_web.py
   docker unpause harbor-web
   ```

Після дослідів виконай `docker rm -f harbor-web`. Контейнер повторно збирається й запускається командами з першого розділу.

## GitHub Actions

`.github/workflows/harbor.yml` запускає тести на Ubuntu. Для контрольованої помилки закоміть пошкоджений `web/health.json` у гілці `harbor-health-contract` і створи pull request до `main`. Дочекайся невдалого прогону. Наступним комітом у цій гілці віднови JSON. Тести та значення `EXPECTED_RELEASE` в обох прогонах однакові. У `harbor-run-reports` зберігаються окремі XML-звіти трьох груп, вивід команди та журнал Nginx. Після перевірок контейнер видаляється.

## Базовий приклад

```bash
docker build -t devops6-demo ./baseline
docker run -d --name devops6-web -p 127.0.0.1:8080:80 devops6-demo
curl --fail --max-time 5 http://127.0.0.1:8080/
python -m pytest -v --hosts=docker://devops6-web baseline/tests/infra
docker rm -f devops6-web
```
