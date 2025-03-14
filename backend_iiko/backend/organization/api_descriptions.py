restaurant = {
    "get_list_restaurants": {
        "summary": "Получить список ресторанов",
        "description": "Возвращает список всех ресторанов.",
        "parameters": [
            {
                "name": "my_restaurant",
                "type": "bool",
                "description": "Если True, возвращает только рестораны, где текущий пользователь является автором."
            },
            {
                "name": "me_in_restaurant",
                "type": "bool",
                "description": "Если True, то возвращает рестораны, в которых находится текущий пользователь."
            }
        ]
    },
    "get_restaurant": {
        "summary": "Получить детали ресторана",
        "description": "Возвращает информацию о конкретной ресторане по её ID."
    },
    "create_restaurant": {
        "summary": "Создать новый ресторан",
        "description": "Создает новый ресторан.",
        "request": "PostPatchRestaurantSerializer"
    },
    "partial_update_restaurant": {
        "summary": "Частично обновить ресторан",
        "description": "Можно обновить имя или сеть ресторана по отдельности.",
        "request": "PostPatchRestaurantSerializer"
    },
    "delete_restaurant": {
        "summary": "Удалить ресторан",
        "description": "Удаляет ресторан по её ID."
    },
    "add_user_in_restaurant": {
        "summary": "Добавить пользователя в ресторан",
        "description": "Можно добавить пользователя в ресторан по ID пользователя и ID ресторана.",
        "request": "AddUserToRestaurantSerializer"
    },
    "delete_user_in_restaurant": {
        "summary": "Удалить пользователя из ресторана",
        "description": "Удаляет пользователя из ресторана по ID пользователя и ID ресторана.",
        "parameters": [
            {
                "name": "user_id",
                "type": "int",
                "description": "Нужно указать ID пользователя, которого нужно удалить из ресторана."
            },
            {
                "name": "restaurant_id",
                "type": "int",
                "description": "Нужно указать ID ресторана, из которой нужно удалить пользователя."
            }
        ]
    }
}

organization = {
    "get_list_organizations": {
        "summary": "Получить список организаций",
        "description": "Возвращает список всех организаций. Но можно указывать только один параметр, два одновременно нельзя.",
        "parameters": [
            {
                "name": "my_organization",
                "type": "bool",
                "description": "Если True, возвращает только организации, где текущий пользователь является автором."
            },
            {
                "name": "me_in_organization",
                "type": "bool",
                "description": "Если True, возвращает только организации, где текущий пользователь находится в организациях."
            }
        ]
    },
    "get_organization": {
        "summary": "Получить детали организации",
        "description": "Возвращает детали конкретной организации по её ID."
    },
    "create_organization": {
        "summary": "Создать новую организацию",
        "description": "Создает новую организацию."
    },
    "partial_update_organization": {
        "summary": "Частично обновить организацию",
        "description": "Частично обновляет организацию по её ID."
    },
    "delete_organization": {
        "summary": "Удалить организацию",
        "description": "Удаляет организацию по её ID."
    },
    "add_author": {
        "summary": "Добавить автора в организацию",
        "description": "Позволяет текущим авторам добавлять новых авторов в организацию.",
        "request": "PostAddAuthorOrUserSerializer"
    },
    "delete_author": {
        "summary": "Удалить автора из организации",
        "description": "Позволяет удалить текущего пользователя из организации."
    },
    "add_user_in_organization": {
        "summary": "Добавить пользователя в организацию",
        "description": "Позволяет добавить пользователя в организацию по ID пользователя и ID организации.",
        "request": "PostAddAuthorOrUserSerializer"
    },
    "delete_user_in_organization": {
        "summary": "Удалить пользователя из организации",
        "description": "Позволяет удалить пользователя из организации по ID пользователя и ID организации.",
        "parameters": [
            {
                "name": "user_id",
                "type": "int",
                "description": "ID пользователя"
            },
            {
                "name": "organization_id",
                "type": "int",
                "description": "ID организации"
            }
        ]
    }
}

chain_des = {
    "get_list_chains": {
        "summary": "Получить список сетей",
        "description": "Возвращает список всех сетей. Доступна фильтрация по параметрам.",
    },
    "get_chain": {
        "summary": "Получить детали сети",
        "description": "Возвращает информацию о конкретной сети по её ID."
    },
    "create_chain": {
        "summary": "Создать новую сеть",
        "description": "Создает новую сеть."
    },
    "partial_update_chain": {
        "summary": "Частично обновить сеть",
        "description": "Можно обновить имя или организацию сети по отдельности."
    },
    "delete_chain": {
        "summary": "Удалить сеть",
        "description": "Удаляет сеть по её ID."
    },
    "add_user_in_chain": {
        "summary": "Добавить пользователя в сеть",
        "description": "Можно добавить пользователя в сеть по ID пользователя и ID сети.",
        "request": "AddUserToChainSerializer"
    },
    "delete_user_in_chain": {
        "summary": "Удалить пользователя из сети",
        "description": "Удаляет пользователя из сети по ID пользователя и ID сети.",
        "parameters": [
            {
                "name": "user_id",
                "type": "int",
                "description": "Нужно указать ID пользователя, которого нужно удалить из сети."
            },
            {
                "name": "chain_id",
                "type": "int",
                "description": "Нужно указать ID сети, из которой нужно удалить пользователя."
            }
        ]
    }
}
