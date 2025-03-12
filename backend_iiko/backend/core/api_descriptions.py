from drf_spectacular.utils import OpenApiParameter

user = {
    "get_user_list": {
        "summary": "Получить список пользователей",
        "description": "Можно получить список всех пользователей, так же можно фильтровать по ролям, организациям, цепочкам и ресторанам",
        "parameters": [
            {
                "name": "role",
                "type": "int",
                "description": "Filter for role, by name",
                "required": False
            },
            {
                "name": "organizations",
                "type": "int",
                "description": "Filter for organizations, by name",
                "required": False
            },
            {
                "name": "chains",
                "type": "int",
                "description": "Filter for chains, by name",
                "required": False
            },
            {
                "name": "restaurants",
                "type": "int",
                "description": "Filter for restaurants, by name",
                "required": False
            }
        ]
    },
    "get_user": {
        "summary": "Получить одного пользователя",
        "description": "Возвращает пользователя по его ID"
    },
    "create_user": {
        "summary": "Регистрация нового пользователя",
        "description": "Регистрация нового пользователя, после регистрации на почту придет письмо для подтверждения"
    },
    "delete_user": {
        "summary": "Удалить пользователя",
        "description": "Удаляет пользователя по её ID."
    },
    "login_user": {
        "summary": "Авторизация пользователя",
        "description": "Авторизация пользователя по username и паролю",
        "request": "LoginSerializer"
    },
    "login_user_with_code": {
        "summary": "Авторизация пользователя по коду",
        "description": "Авторизация пользователя по коду",
        "request": "LoginWithCodeSerializer"
    },
    "refresh_token": {
        "summary": "Обновление access и refresh токенов",
        "description": "Обновление access и refresh токенов",
        "request": "RefreshTokenSerializer"
    },
    "confirm_password_change": {
        "summary": "Подтверждение смены пароля по коду",
        "description": "Отправляет код, а пароль сохраняет в сессии, после подтверждения кода, пароль меняется",
        "request": "ConfirmPasswordChangeSerializer"
    },
    "resend_code": {
        "summary": "Повторная отправка кода для смены пароля",
        "description": "Повторная отправка кода для смены пароля"
    },
    "email_confirmed": {
        "summary": "Подтверждение почты и активация пользователя",
        "description": "Подтверждение почты и активация пользователя",
        "parameters": [
            {
                "name": "uidb64",
                "type": "str",
                "description": "Base64-encoded user ID",
                "required": True,
                "location": OpenApiParameter.QUERY
            },
            {
                "name": "token",
                "type": "str",
                "description": "Token for email confirmation",
                "required": True,
                "location": OpenApiParameter.QUERY
            },
        ]
    },
    "change_username_or_email": {
        "summary": "Смена имени или почты пользователя",
        "description": "Можно сменить только имя или только почту, так же можно сменить и имя и почту. "
                       "Если менять почту, то на новую почту будет отправлено письмо для подтверждения",
        "request": "ChangeUsernameOrEmail"
    },
    "change_password": {
        "summary": "Смена пароля пользователя",
        "description": "При смене пароля, на почту прийдет код для подтверждения",
        "request": "ChangePasswordSerializer"
    }
}
