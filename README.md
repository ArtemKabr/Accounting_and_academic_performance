Accounting_and_academic_performance/ # Корень проекта (латинские буквы, без дефисов)
│
├── src/                         # Основные модули
│   ├── handlers/                # Обработчики
│   │   ├── __init__.py
│   │   ├── start.py             # /start
│   │   ├── registration.py      # Регистрация
│   │   ├── schedule.py          # Расписание
│   │   └── navigation.py        # Навигация
│   ├── database/                # Данные
│   │   ├── users_db.json        # Данные зарегистрированных пользователей
│   │   └── schedule.json        # Данные уроков, других дополнений которые будут вводится преподавателем
│   ├── keyboards/               # Клавиатуры
│   │   ├── __init__.py
│   │   └── inline.py            # Кнопки
│   │
│   ├── states/                  # Состояния FSM
│   │   ├── __init__.py
│   │   └── registration.py      # Этапы регистрации
│   │
│   └── utils/                   # Утилиты
│       ├── __init__.py
│       └── database.py          # Работа с JSON
│
├── tests/                       # Тесты
│   ├── __init__.py
│   ├── test_handlers.py
│   └── test_imports.py
│

│
├── .gitignore                   # Игнорируемые файлы
├── main.py                      # Точка входа (в корне)
├── config.py                    # Конфигурация (в корне)
├── loader.py                    # Инициализация бота (в корне)
├── pyproject.toml               # Конфигурация Poetry
└── README.md                    # Описание проекта