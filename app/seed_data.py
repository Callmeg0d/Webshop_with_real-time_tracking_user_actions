"""
Seed данные для заполнения базы данных тестовыми данными.
"""

# Категории товаров
CATEGORIES = [
    {
        "name": "Телефоны",
        "description": "Смартфоны и мобильные телефоны"
    },
    {
        "name": "Ноутбуки",
        "description": "Портативные компьютеры и ноутбуки"
    },
    {
        "name": "Планшеты",
        "description": "Планшетные компьютеры"
    },
    {
        "name": "Наушники",
        "description": "Проводные и беспроводные наушники"
    },
    {
        "name": "Фитнес-трекеры",
        "description": "Умные часы и фитнес-браслеты"
    },
    {
        "name": "Фотоаппараты",
        "description": "Цифровые фотоаппараты и камеры"
    },
    {
        "name": "Аксессуары",
        "description": "Зарядные устройства, кабели и чехлы"
    },
]

# Продукты
PRODUCTS = [
    # Телефоны
    {
        "name": "iPhone 15 Pro",
        "description": "Новейший флагман Apple с чипом A17 Pro и титановым корпусом. Камера 48 Мп с 5x зумом.",
        "price": 129990,
        "product_quantity": 15,
        "image": 1,
        "features": {"Память": "256 ГБ", "Вес": "187 г", "Размеры": "146.6 x 70.6 x 8.25 мм", "Экран": "6.1 дюйма", "Камера": "48 Мп"},
        "category_name": "Телефоны"
    },
    {
        "name": "iPhone 13",
        "description": "Смартфон от Apple с A15 Bionic и 128 ГБ памяти. Надёжный и проверенный выбор.",
        "price": 79990,
        "product_quantity": 10,
        "image": 2,
        "features": {"Память": "128 ГБ", "Вес": "173 г", "Размеры": "146.7 x 71.5 x 7.65 мм", "Экран": "6.1 дюйма", "Камера": "12 Мп"},
        "category_name": "Телефоны"
    },
    {
        "name": "Samsung Galaxy S24 Ultra",
        "description": "Флагманский смартфон Samsung с камерой 200 Мп и S Pen. Процессор Snapdragon 8 Gen 3.",
        "price": 134990,
        "product_quantity": 12,
        "image": 3,
        "features": {"Память": "512 ГБ", "Вес": "232 г", "Размеры": "162.3 x 79 x 8.6 мм", "Экран": "6.8 дюйма", "Камера": "200 Мп"},
        "category_name": "Телефоны"
    },
    {
        "name": "Samsung Galaxy S22",
        "description": "Мощный смартфон с камерой 50 Мп и Snapdragon 8 Gen 1. Отличное соотношение цена-качество.",
        "price": 64990,
        "product_quantity": 8,
        "image": 4,
        "features": {"Память": "256 ГБ", "Вес": "167 г", "Размеры": "146 x 70.6 x 7.6 мм", "Экран": "6.1 дюйма", "Камера": "50 Мп"},
        "category_name": "Телефоны"
    },
    {
        "name": "Google Pixel 8 Pro",
        "description": "Флагман Google с лучшей камерой на рынке и чистым Android. Tensor G3 процессор.",
        "price": 99990,
        "product_quantity": 10,
        "image": 5,
        "features": {"Память": "256 ГБ", "Вес": "213 г", "Размеры": "162.6 x 76.5 x 8.8 мм", "Экран": "6.7 дюйма", "Камера": "50 Мп"},
        "category_name": "Телефоны"
    },
    {
        "name": "Xiaomi 13 Pro",
        "description": "Топовый смартфон Xiaomi с камерой Leica и быстрой зарядкой 120 Вт.",
        "price": 74990,
        "product_quantity": 14,
        "image": 6,
        "features": {"Память": "256 ГБ", "Вес": "229 г", "Размеры": "162.9 x 74.6 x 8.38 мм", "Экран": "6.73 дюйма", "Камера": "50 Мп"},
        "category_name": "Телефоны"
    },
    
    # Ноутбуки
    {
        "name": "MacBook Pro 14 M3 Pro",
        "description": "Новейший MacBook Pro с чипом M3 Pro и 14-дюймовым Liquid Retina XDR дисплеем.",
        "price": 199990,
        "product_quantity": 6,
        "image": 7,
        "features": {"Память": "512 ГБ SSD", "Вес": "1.55 кг", "Размеры": "355.7 x 248 x 15.5 мм", "Экран": "14.2 дюйма", "Процессор": "Apple M3 Pro"},
        "category_name": "Ноутбуки"
    },
    {
        "name": "MacBook Air M2",
        "description": "Легкий и производительный MacBook Air с чипом M2. Идеален для работы и учёбы.",
        "price": 139990,
        "product_quantity": 10,
        "image": 8,
        "features": {"Память": "256 ГБ SSD", "Вес": "1.24 кг", "Размеры": "304.1 x 215 x 11.3 мм", "Экран": "13.6 дюйма", "Процессор": "Apple M2"},
        "category_name": "Ноутбуки"
    },
    {
        "name": "Dell XPS 15",
        "description": "Премиальный ноутбук с процессором Intel Core i7 13-го поколения и NVIDIA RTX 4060.",
        "price": 159990,
        "product_quantity": 7,
        "image": 9,
        "features": {"Память": "1 ТБ SSD", "Вес": "1.86 кг", "Размеры": "344.72 x 230.14 x 18 мм", "Экран": "15.6 дюйма", "Процессор": "Intel Core i7-13700H"},
        "category_name": "Ноутбуки"
    },
    {
        "name": "ASUS ROG Zephyrus G14",
        "description": "Компактный игровой ноутбук с AMD Ryzen 9 и RTX 4070. Мощность в компактном корпусе.",
        "price": 179990,
        "product_quantity": 5,
        "image": 10,
        "features": {"Память": "1 ТБ SSD", "Вес": "1.65 кг", "Размеры": "312 x 227 x 19.5 мм", "Экран": "14 дюймов", "Процессор": "AMD Ryzen 9 7940HS"},
        "category_name": "Ноутбуки"
    },
    {
        "name": "Lenovo ThinkPad X1 Carbon",
        "description": "Бизнес-ноутбук с военной прочностью и Intel Core i7. Идеален для профессионалов.",
        "price": 169990,
        "product_quantity": 8,
        "image": 1,
        "features": {"Память": "512 ГБ SSD", "Вес": "1.12 кг", "Размеры": "315.6 x 222.5 x 14.95 мм", "Экран": "14 дюймов", "Процессор": "Intel Core i7-1365U"},
        "category_name": "Ноутбуки"
    },
    {
        "name": "HP Spectre x360",
        "description": "Трансформер премиум-класса с 4K OLED дисплеем и стилусом в комплекте.",
        "price": 149990,
        "product_quantity": 6,
        "image": 2,
        "features": {"Память": "512 ГБ SSD", "Вес": "1.39 кг", "Размеры": "298 x 220 x 17 мм", "Экран": "13.5 дюйма", "Процессор": "Intel Core i7-1355U"},
        "category_name": "Ноутбуки"
    },
    
    # Планшеты
    {
        "name": "iPad Pro 12.9 M2",
        "description": "Самый мощный планшет от Apple с чипом M2 и Liquid Retina XDR дисплеем.",
        "price": 129990,
        "product_quantity": 8,
        "image": 3,
        "features": {"Память": "256 ГБ", "Вес": "682 г", "Размеры": "280.6 x 214.9 x 6.4 мм", "Экран": "12.9 дюйма", "Процессор": "Apple M2"},
        "category_name": "Планшеты"
    },
    {
        "name": "iPad Air",
        "description": "Планшет с 10.9-дюймовым Liquid Retina дисплеем и чипом M1. Отличный баланс.",
        "price": 64990,
        "product_quantity": 12,
        "image": 4,
        "features": {"Память": "256 ГБ", "Вес": "461 г", "Размеры": "247.6 x 178.5 x 6.1 мм", "Экран": "10.9 дюйма", "Процессор": "Apple M1"},
        "category_name": "Планшеты"
    },
    {
        "name": "Samsung Galaxy Tab S9 Ultra",
        "description": "Огромный планшет с 14.6-дюймовым AMOLED дисплеем и S Pen в комплекте.",
        "price": 119990,
        "product_quantity": 6,
        "image": 5,
        "features": {"Память": "512 ГБ", "Вес": "732 г", "Размеры": "326.4 x 208.6 x 5.5 мм", "Экран": "14.6 дюйма", "Процессор": "Snapdragon 8 Gen 2"},
        "category_name": "Планшеты"
    },
    {
        "name": "Samsung Galaxy Tab S7",
        "description": "Планшет с AMOLED-экраном и поддержкой S Pen. Проверенная модель.",
        "price": 49990,
        "product_quantity": 9,
        "image": 6,
        "features": {"Память": "128 ГБ", "Вес": "500 г", "Размеры": "253.8 x 165.3 x 6.3 мм", "Экран": "11 дюймов", "Процессор": "Snapdragon 865+"},
        "category_name": "Планшеты"
    },
    
    # Наушники
    {
        "name": "AirPods Pro 2",
        "description": "Беспроводные наушники с активным шумоподавлением нового поколения и пространственным звуком.",
        "price": 24990,
        "product_quantity": 20,
        "image": 7,
        "features": {"Вес": "5.3 г (каждая)", "Время работы": "6 часов", "Тип": "Вкладыши", "Шумоподавление": "Да"},
        "category_name": "Наушники"
    },
    {
        "name": "Sony WH-1000XM5",
        "description": "Лучшие накладные наушники с шумоподавлением и поддержкой LDAC.",
        "price": 34990,
        "product_quantity": 15,
        "image": 8,
        "features": {"Вес": "250 г", "Время работы": "30 часов", "Тип": "Накладные", "Шумоподавление": "Да"},
        "category_name": "Наушники"
    },
    {
        "name": "Sony WH-1000XM4",
        "description": "Шумоподавляющие наушники с отличным звуком и DSEE Extreme. Предыдущая модель по выгодной цене.",
        "price": 27990,
        "product_quantity": 10,
        "image": 9,
        "features": {"Вес": "254 г", "Время работы": "30 часов", "Тип": "Накладные", "Шумоподавление": "Да"},
        "category_name": "Наушники"
    },
    {
        "name": "Bose QuietComfort 45",
        "description": "Комфортные наушники с легендарным шумоподавлением Bose.",
        "price": 29990,
        "product_quantity": 12,
        "image": 10,
        "features": {"Вес": "240 г", "Время работы": "24 часа", "Тип": "Накладные", "Шумоподавление": "Да"},
        "category_name": "Наушники"
    },
    {
        "name": "Sennheiser Momentum 4",
        "description": "Аудиофильские наушники с исключительным качеством звука и 60 часами работы.",
        "price": 32990,
        "product_quantity": 8,
        "image": 1,
        "features": {"Вес": "293 г", "Время работы": "60 часов", "Тип": "Накладные", "Шумоподавление": "Да"},
        "category_name": "Наушники"
    },
    {
        "name": "JBL Tune 760NC",
        "description": "Доступные наушники с шумоподавлением и фирменным звуком JBL.",
        "price": 7990,
        "product_quantity": 25,
        "image": 2,
        "features": {"Вес": "220 г", "Время работы": "35 часов", "Тип": "Накладные", "Шумоподавление": "Да"},
        "category_name": "Наушники"
    },
    
    # Фитнес-трекеры
    {
        "name": "Apple Watch Series 9",
        "description": "Умные часы Apple с двойным нажатием и ярким дисплеем. Полный контроль здоровья.",
        "price": 44990,
        "product_quantity": 15,
        "image": 3,
        "features": {"Вес": "32 г", "Время работы": "18 часов", "Экран": "1.9 дюйма", "Водозащита": "50 м"},
        "category_name": "Фитнес-трекеры"
    },
    {
        "name": "Apple Watch SE 2",
        "description": "Доступные умные часы Apple с основными функциями здоровья и фитнеса.",
        "price": 29990,
        "product_quantity": 20,
        "image": 4,
        "features": {"Вес": "27 г", "Время работы": "18 часов", "Экран": "1.78 дюйма", "Водозащита": "50 м"},
        "category_name": "Фитнес-трекеры"
    },
    {
        "name": "Garmin Forerunner 965",
        "description": "Профессиональные GPS-часы для бегунов с AMOLED дисплеем и картами.",
        "price": 69990,
        "product_quantity": 6,
        "image": 5,
        "features": {"Вес": "53 г", "Время работы": "23 дня", "Экран": "1.4 дюйма", "Водозащита": "50 м"},
        "category_name": "Фитнес-трекеры"
    },
    {
        "name": "Fitbit Charge 6",
        "description": "Умный фитнес-трекер с точным пульсометром и интеграцией с Google.",
        "price": 16990,
        "product_quantity": 20,
        "image": 6,
        "features": {"Вес": "29 г", "Время работы": "7 дней", "Экран": "1.04 дюйма", "Водозащита": "50 м"},
        "category_name": "Фитнес-трекеры"
    },
    {
        "name": "Xiaomi Mi Band 8",
        "description": "Доступный фитнес-браслет с большим экраном и автономностью до 16 дней.",
        "price": 3990,
        "product_quantity": 40,
        "image": 7,
        "features": {"Вес": "27 г", "Время работы": "16 дней", "Экран": "1.62 дюйма", "Водозащита": "50 м"},
        "category_name": "Фитнес-трекеры"
    },
    
    # Фотоаппараты
    {
        "name": "Sony A7 IV",
        "description": "Полнокадровая беззеркальная камера с 33 Мп матрицей и 4K 60p видео.",
        "price": 269990,
        "product_quantity": 4,
        "image": 8,
        "features": {"Матрица": "33 Мп", "Вес": "658 г", "Видео": "4K 60p", "Стабилизация": "5 осей"},
        "category_name": "Фотоаппараты"
    },
    {
        "name": "Canon EOS R6 Mark II",
        "description": "Универсальная полнокадровая камера с 24 Мп и отличным автофокусом.",
        "price": 289990,
        "product_quantity": 3,
        "image": 9,
        "features": {"Матрица": "24 Мп", "Вес": "670 г", "Видео": "4K 60p", "Стабилизация": "5 осей"},
        "category_name": "Фотоаппараты"
    },
    {
        "name": "Nikon Z6 III",
        "description": "Профессиональная камера с hybrid-viewfinder и невероятной скоростью съёмки.",
        "price": 279990,
        "product_quantity": 3,
        "image": 10,
        "features": {"Матрица": "24.5 Мп", "Вес": "760 г", "Видео": "6K RAW", "Стабилизация": "5 осей"},
        "category_name": "Фотоаппараты"
    },
    {
        "name": "Fujifilm X-T5",
        "description": "APS-C камера с классическим дизайном и 40 Мп матрицей X-Trans.",
        "price": 189990,
        "product_quantity": 5,
        "image": 1,
        "features": {"Матрица": "40 Мп", "Вес": "557 г", "Видео": "6K 30p", "Стабилизация": "5 осей"},
        "category_name": "Фотоаппараты"
    },
    
    # Аксессуары
    {
        "name": "Apple USB-C to Lightning Cable",
        "description": "Оригинальный кабель Apple для быстрой зарядки iPhone длиной 1 метр.",
        "price": 2490,
        "product_quantity": 50,
        "image": 2,
        "features": {"Длина": "1 м", "Тип": "USB-C to Lightning", "Быстрая зарядка": "Да"},
        "category_name": "Аксессуары"
    },
    {
        "name": "Anker PowerCore 20000mAh",
        "description": "Мощный внешний аккумулятор на 20000 мАч с быстрой зарядкой.",
        "price": 4990,
        "product_quantity": 30,
        "image": 3,
        "features": {"Ёмкость": "20000 мАч", "Вес": "356 г", "Порты": "USB-C, USB-A", "Быстрая зарядка": "18 Вт"},
        "category_name": "Аксессуары"
    },
    {
        "name": "Apple MagSafe Charger",
        "description": "Беспроводное зарядное устройство MagSafe для iPhone с магнитным креплением.",
        "price": 3990,
        "product_quantity": 25,
        "image": 4,
        "features": {"Мощность": "15 Вт", "Тип": "MagSafe", "Длина кабеля": "1 м"},
        "category_name": "Аксессуары"
    },
    {
        "name": "Samsung Silicone Case",
        "description": "Оригинальный силиконовый чехол для Samsung Galaxy S24 с мягким покрытием.",
        "price": 2990,
        "product_quantity": 35,
        "image": 5,
        "features": {"Материал": "Силикон", "Совместимость": "Galaxy S24", "Защита": "От ударов и царапин"},
        "category_name": "Аксессуары"
    },
    {
        "name": "Belkin BoostCharge Pro 3-in-1",
        "description": "Универсальная беспроводная зарядная станция для iPhone, Apple Watch и AirPods.",
        "price": 14990,
        "product_quantity": 12,
        "image": 6,
        "features": {"Устройства": "3", "Мощность": "15 Вт", "Совместимость": "MagSafe, Qi"},
        "category_name": "Аксессуары"
    },
]

# Тестовые пользователи (пароль для всех: "password123")
USERS = [
    {
        "email": "admin@example.com",
        "name": "Администратор",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lWqJZ.1Kq3Pu",  # password123
        "delivery_address": "Москва, ул. Тверская, д. 1"
    },
    {
        "email": "user1@example.com",
        "name": "Иван Иванов",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lWqJZ.1Kq3Pu",
        "delivery_address": "Санкт-Петербург, Невский проспект, д. 28"
    },
    {
        "email": "user2@example.com",
        "name": "Мария Петрова",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lWqJZ.1Kq3Pu",
        "delivery_address": "Казань, ул. Баумана, д. 45"
    },
    {
        "email": "user3@example.com",
        "name": "Александр Сидоров",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lWqJZ.1Kq3Pu",
        "delivery_address": "Екатеринбург, пр. Ленина, д. 78"
    },
    {
        "email": "user4@example.com",
        "name": "Елена Козлова",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lWqJZ.1Kq3Pu",
        "delivery_address": "Новосибирск, ул. Красный проспект, д. 15"
    },
]

# Отзывы (будут добавлены после создания пользователей и продуктов)
REVIEWS = [
    # Отзывы на iPhone 15 Pro (product_id: 1)
    {
        "user_email": "user1@example.com",
        "product_name": "iPhone 15 Pro",
        "rating": 5,
        "feedback": "Отличный телефон! Камера просто супер, а титановый корпус выглядит премиально."
    },
    {
        "user_email": "user2@example.com",
        "product_name": "iPhone 15 Pro",
        "rating": 5,
        "feedback": "Лучший iPhone, который у меня был. Производительность на высоте."
    },
    {
        "user_email": "user3@example.com",
        "product_name": "iPhone 15 Pro",
        "rating": 4,
        "feedback": "Хороший телефон, но цена кусается. В остальном без нареканий."
    },
    
    # Отзывы на Samsung Galaxy S24 Ultra (product_id: 3)
    {
        "user_email": "user1@example.com",
        "product_name": "Samsung Galaxy S24 Ultra",
        "rating": 5,
        "feedback": "Камера 200 Мп это нечто! Фотографии невероятные, особенно ночью."
    },
    {
        "user_email": "user4@example.com",
        "product_name": "Samsung Galaxy S24 Ultra",
        "rating": 5,
        "feedback": "S Pen очень удобен для заметок. Экран яркий и качественный."
    },
    
    # Отзывы на MacBook Pro 14 M3 Pro (product_id: 7)
    {
        "user_email": "user2@example.com",
        "product_name": "MacBook Pro 14 M3 Pro",
        "rating": 5,
        "feedback": "Мощный ноутбук для работы. Монтирую видео без проблем, не греется."
    },
    {
        "user_email": "user3@example.com",
        "product_name": "MacBook Pro 14 M3 Pro",
        "rating": 5,
        "feedback": "Лучший ноутбук для разработки. Батарея держит целый день."
    },
    
    # Отзывы на MacBook Air M2 (product_id: 8)
    {
        "user_email": "user1@example.com",
        "product_name": "MacBook Air M2",
        "rating": 5,
        "feedback": "Идеальный ноутбук для студента. Легкий, тихий, не греется."
    },
    {
        "user_email": "user4@example.com",
        "product_name": "MacBook Air M2",
        "rating": 4,
        "feedback": "Отличный ноутбук, но хотелось бы больше портов."
    },
    
    # Отзывы на AirPods Pro 2 (product_id: 17)
    {
        "user_email": "user1@example.com",
        "product_name": "AirPods Pro 2",
        "rating": 5,
        "feedback": "Шумоподавление работает отлично! Удобно сидят в ушах."
    },
    {
        "user_email": "user2@example.com",
        "product_name": "AirPods Pro 2",
        "rating": 5,
        "feedback": "Лучшие наушники для Apple экосистемы. Звук чистый и насыщенный."
    },
    {
        "user_email": "user3@example.com",
        "product_name": "AirPods Pro 2",
        "rating": 4,
        "feedback": "Хорошие наушники, но дороговаты. Качество на уровне."
    },
    
    # Отзывы на Sony WH-1000XM5 (product_id: 18)
    {
        "user_email": "user4@example.com",
        "product_name": "Sony WH-1000XM5",
        "rating": 5,
        "feedback": "Лучшее шумоподавление на рынке! Звук потрясающий."
    },
    {
        "user_email": "user1@example.com",
        "product_name": "Sony WH-1000XM5",
        "rating": 5,
        "feedback": "Очень комфортные, можно носить часами. Батарея держит долго."
    },
    
    # Отзывы на Apple Watch Series 9 (product_id: 23)
    {
        "user_email": "user2@example.com",
        "product_name": "Apple Watch Series 9",
        "rating": 5,
        "feedback": "Отличные смарт-часы! Функция двойного нажатия очень удобна."
    },
    {
        "user_email": "user3@example.com",
        "product_name": "Apple Watch Series 9",
        "rating": 4,
        "feedback": "Хорошие часы, но батарея всё ещё не держит больше дня."
    },
    
    # Отзывы на iPad Pro 12.9 M2 (product_id: 13)
    {
        "user_email": "user1@example.com",
        "product_name": "iPad Pro 12.9 M2",
        "rating": 5,
        "feedback": "Заменил ноутбук на iPad Pro. Для рисования и заметок идеален!"
    },
    {
        "user_email": "user4@example.com",
        "product_name": "iPad Pro 12.9 M2",
        "rating": 5,
        "feedback": "Мощный планшет с отличным экраном. Использую для работы."
    },
    
    # Отзывы на Sony A7 IV (product_id: 28)
    {
        "user_email": "user2@example.com",
        "product_name": "Sony A7 IV",
        "rating": 5,
        "feedback": "Профессиональная камера за разумные деньги. Отличный автофокус."
    },
    {
        "user_email": "user3@example.com",
        "product_name": "Sony A7 IV",
        "rating": 5,
        "feedback": "Использую для съёмки видео. Качество изображения превосходное."
    },
    
    # Отзывы на Google Pixel 8 Pro (product_id: 5)
    {
        "user_email": "user4@example.com",
        "product_name": "Google Pixel 8 Pro",
        "rating": 5,
        "feedback": "Камера делает невероятные фото! Чистый Android без лишнего."
    },
    {
        "user_email": "user1@example.com",
        "product_name": "Google Pixel 8 Pro",
        "rating": 4,
        "feedback": "Отличный телефон, но батарея могла бы быть лучше."
    },
]

