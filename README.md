# Тестовое задание на позицию стажёра в "Авито"
Приложение представляет собой микросервис для работы с балансом пользователей.

Сервис предоставляет JSON API по следующим URL:
- **POST** `api/change-balance/` - метод изменения баланса пользователя
- **GET** `api/get-balance/<int:user_id>` - метод получения баланса пользователя
- **POST** `api/make-transfer/` - метод перевода средств между пользователями
- **GET** `api/get-transactions/<int:user_id>/[sort_by=date|amount/]` - метод получения списка операций пользователя

## Использованные технологии
Так как Golang я начал изучать совсем недавно, я выбрал технологии, с которыми я уже работал.
* **Python + Django** - для создания API я использую надстройки **Django REST Framework** (позволяет создать эндпоинты для API и удобно обрабатывать входные данные)
* **PostgreSQL** в качестве базы данных
* **uWSGI** в качестве продакшен-сервера
* **nginx** в качетсве прокси-сервера, который является единственной входной точкой в сеть приложения.
* **Docker** и **docker-compose** для разворачивания приложения

## Архитектура приложения
Сущности БД и архитектура приложения описаны на [Miro](https://miro.com/app/board/o9J_lyxUyZo=/)

## Установка и запуск
1. Склонировать репозиторий
```
git clone https://github.com/r-egorov/avito-intern
```
2. В корневой директории в файл **.env** поместить свой секретный ключ для Django-приложений (можно не трогать)
3. При желании изменить имена пользователей и пароли в том же **.env**-файле.
4. Поднять сеть контейнеров с помощью docker-compose
```
docker-compose up [-d]
```
5. Для запуска unit-тестов можно воспользоваться командой
```
docker exec uwsgi-nginx sh -c "python manage.py test"
```

## Контракт API
<details>
  <summary>Спойлер</summary>
  В каждом методе входные данные валидируются. При ошибках возрващается соответстующий код ответа и ошибка в ответном JSON.
  Данные сообщений должны быть обёрнуты в поле `data`, например:
  
  ```
  POST api/change-balance/
  
  {
    "data": {
        "user_id": 1,
        "amount": 10000.00
    }
  }
  ```
  
  **Метод изменения баланса пользователя**
  
  Принимает `user_id` пользователя и `amount` - то, на сколько изменить баланс пользователя. `amount` может быть отрицательным, для списания средств у пользователя.
  В случае, если пользователя с таким `user_id` не существует, то проверяет операцию: списываются ли средства или зачисляются. Если зачисляются, то создаёт   `Balance` с `user_id`.
  
  ```
  POST api/change-balance/ (ChangeBalanceIn) -> ChangeBalanceOut
  
  message ChangeBalanceIn {
    user_id int
    amount float
  }
  
  message ChangeBalanceOut {
    user_id int
    balance float
    last_update datetime
  }
  ```
  
  Коды ответов:
  - `200 OK` - успешное списание средств
  - `201 CREATED` - первое зачисление средств a.k.a. создание нового `Balance`
  - `404 NOT FOUND` - пользователь с `user_id` не найден, списание средств невозможно
  
  
  **Метод получения баланса пользователя**
  
  Принимает `user_id` пользователя.
  
  ```
  GET api/get-balance/<int:user_id> -> GetBalanceOut
  
  message GetBalanceOut {
    user_id int
    balance float
    last_update datetime
  }
  ```
  
  Коды ответов:
  - `200 OK` - запрос выполнен успешно
  - `404 NOT FOUND` - пользователь с `user_id` не найден
  
  **Метод перевода средств от одного пользователя другому**
  
  Принимает:
  - `source_id` - идентификатор пользователя, у которого списываются средства
  - `target_id` - идентификатор пользователя, которому зачисляются средства
  - `amount` - сумма средств для перевода. Не может быть отрицательной.
  
  Возвращает описание сущности `Transaction`.
  
  ```
  POST api/make-transfer/ (MakeTransferIn) -> MakeTransferOut
  
  message MakeTransferIn {
    source_id int
    target_id int
    amount float
  }
  
  message MakeTransferOut {
    source_id int
    target_id int
    amount float
    comment string
    timestamg datetime
  }
  
  Коды ответов:
  - `200 OK` - запрос выполнен успешно
  - `404 NOT FOUND` - пользователь с `source_id` или `target_id` не найден (в ответном сообщение указано, в каком идентификаторе ошибка)
  - `400 BAD REQUEST` - у пользователя, с баланса которого должны быть списаны средства, средств не хватает
  
  ```
  
  Пример исходного сообщения:
  ```
  {
    "data": {
    	"source_id": 2,
    	"target_id": 3,
    	"amount": 1500
    }
  }
  ```
  
  **Метод получения списка операций**
  
  Принимает `user_id` пользователя в URL, а также опциональный параметр `sort_by`, который может быть либо `date`, либо `amount`.
  По умолчанию на странице 10 операций, отсортированных по дате, от новой операции к старой.
  
  Принимает: 
    - `user_id` - идентификатор пользователя
    - `sort_by` - параметр сортировки.
  
  Возвращает список сущностей `Transactions`.
    
  ```
  GET api/get-transactions/<int:user_id>/[sort_by=date|amount/] -> GetTransactionsOut
  
  message GetTransactionsOut {
    count int
    next link
    previous link
    results list[Transaction]
  }
  ```
  
  Коды ответов:
  - `200 OK` - запрос выполнен успешно
  - `404 NOT FOUND` - пользователь с `user_id` не найден
  - `400 BAD REQUEST` - в `sort_by` передали невалидный параметр
  
</details>
  
## Дерево проекта
  
  ```
  .
  ├── README.md
  ├── balance
  │   ├── Dockerfile
  │   ├── balance
  │   │   ├── __init__.py
  │   │   ├── api
  │   │   │   ├── __init__.py
  │   │   │   ├── admin.py
  │   │   │   ├── apps.py
  │   │   │   ├── exceptions.py
  │   │   │   ├── migrations
  │   │   │   │   ├── 0001_initial.py
  │   │   │   │   └── __init__.py
  │   │   │   ├── models.py
  │   │   │   ├── pagination.py
  │   │   │   ├── serializers.py
  │   │   │   ├── tests
  │   │   │   │   ├── __init__.py
  │   │   │   │   ├── test_base.py
  │   │   │   │   ├── test_models.py
  │   │   │   │   └── test_views.py
  │   │   │   └── views.py
  │   │   ├── asgi.py
  │   │   ├── settings.py
  │   │   ├── urls.py
  │   │   └── wsgi.py
  │   ├── manage.py
  │   ├── requirements.txt
  │   └── uwsgi.ini
  ├── db
  │   └── scripts
  │       └── 01-init.sh
  └── docker-compose.yml
  ```

## Как можно развивать приложение дальше?
  Сейчас моё приложение полностью синхронное. В **Django** добавили поддержку асинхронных функций, поэтому ручки можно сделать асинхронными. К сожалению, ORM-вызовы в Django всё ещё синхронные, поэтому если мы хотим полностью асинхронное приложение, тогда нам нужно перейти на другой фреймворк или переписать приложение с нуля, подняв собтсвенный сервер.
  
  **uWSGI** - это синхронный сервер, при переходе на асинхронный код следует использовать **ASGI**.
