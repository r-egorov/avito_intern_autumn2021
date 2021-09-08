# Тестовое задание

## Контракт API
<details>
  <summary>Спойлер</summary>


  **Метод создания пользователя**
  
  Принимает начальный баланс пользователя. Баланс не может быть отрицательным.

  ```
  POST api/create-user/ (CreateUserIn) -> CreateUserOut
  
  message CreateUserIn {
    balance float
  }
  
  message CreateUserOut {
    id int
    created datetime
  }
  ```
  
  
  **Метод изменения баланса пользователя**
  
  Принимает `id` пользователя и `amount` - то, на сколько изменить баланс пользователя. `amount` может быть отрицательным, для списания средств у пользователя.
  
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
  
  **Метод получения баланса пользователя**
  
  Принимает `id` пользователя.
  
  ```
  POST api/get-balance/ (GetBalanceIn) -> GetBalanceOut
  
  message GetBalanceIn {
    user_id int
  }
  
  message GetBalanceOut {
    user_id int
    balance float
    last_update datetime
  }
  ```
  
  **Метод перевода средств от одного пользователя другому**
  
  Принимает:
  - `source_id` - идентификатор пользователя, у которого списываются средства
  - `target_id` - идентификатор пользователя, которому зачисляются средства
  - `amount` - сумма средств для перевода. Не может быть отрицательной.
  
  Возвращает:
  - `status` если операция успешна
  - в случае неуспешной операции возвращает ошибки
  
  ```
  POST api/make-transfer/ (MakeTransferIn) -> MakeTransferOut
  
  message MakeTransferIn {
    source_id int
    target_id int
    amount float
  }
  
  message MakeTransferOut {
  }
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
</details>
