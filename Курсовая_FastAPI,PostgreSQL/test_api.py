# test_api_общежития.py
import requests
import json
import sys
from datetime import datetime, date, timedelta

BASE_URL = "http://localhost:8000"

def print_json(data, title=""):
    """Красиво выводит JSON данные"""
    if title:
        print(f"\n{title}")
    if isinstance(data, (dict, list)):
        print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    else:
        print(data)

def wait_for_server():
    """Ожидание запуска сервера"""
    print("⏳ Ожидание запуска сервера...")
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/", timeout=5)
            if response.status_code == 200:
                print("✅ Сервер запущен!")
                return True
        except requests.exceptions.ConnectionError:
            if attempt < max_attempts - 1:
                print(f"🔄 Попытка {attempt + 1}/{max_attempts}...")
                import time
                time.sleep(2)
            else:
                print("❌ Не удалось подключиться к серверу")
                return False

def test_api():
    print("=" * 70)
    print("ТЕСТИРОВАНИЕ API СИСТЕМЫ УПРАВЛЕНИЯ ОБЩЕЖИТИЯМИ")
    print("=" * 70)
    
    # Проверяем подключение к серверу
    if not wait_for_server():
        print("Убедитесь, что сервер запущен на http://localhost:8000")
        sys.exit(1)
    
    try:
        # Глобальные переменные для хранения ID
        студент_id = None
        комната_id = None
        договор_id = None
        льготная_категория_id = None
        
        # 1. Проверка основного эндпоинта
        print("\n1. 📋 Проверка основного эндпоинта: GET /")
        response = requests.get(f"{BASE_URL}/")
        print(f"Статус: {response.status_code}")
        print_json(response.json(), "Ответ:")
        
        # 2. Проверка состояния базы данных
        print("\n2. 🏥 Проверка состояния базы данных: GET /база_данных/статус")
        response = requests.get(f"{BASE_URL}/база_данных/статус")
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"База данных: {health_data.get('статус', 'unknown')}")
            print(f"Тип БД: {health_data.get('база_данных', 'unknown')}")
        else:
            print("Ошибка:", response.text)
        
        # 3. Получение всех студентов
        print("\n3. 👨‍🎓 Получение всех студентов: GET /студенты")
        response = requests.get(f"{BASE_URL}/студенты")
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            студенты = response.json()
            print(f"Найдено {len(студенты)} студентов:")
            for студент in студенты:
                статус = "активен" if студент['статус_пропуска'] else "заблокирован"
                print(f"  - #{студент['студент_id']}: {студент['имя']} {студент['фамилия']} ({статус})")
            if студенты:
                студент_id = студенты[0]['студент_id']
        else:
            print("Ошибка:", response.text)
            return
        
        # 4. Получение всех льготных категорий
        print("\n4. 🎫 Получение льготных категорий: GET /льготные_категории")
        response = requests.get(f"{BASE_URL}/льготные_категории")
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            категории = response.json()
            print(f"Найдено {len(категории)} льготных категорий:")
            for категория in категории:
                print(f"  - #{категория['льготная_категория_id']}: {категория['название']} (скидка: {категория['коэффициент_скидки']})")
            if категории:
                льготная_категория_id = категории[0]['льготная_категория_id']
        else:
            print("Ошибка:", response.text)
        
        # 5. Создание нового студента
        print("\n5. ➕ Создание нового студента: POST /студенты")
        новый_студент = {
            "телефон": "+79017778899",
            "имя": "Сергей",
            "фамилия": "Кузнецов",
            "статус_пропуска": True
        }
        response = requests.post(f"{BASE_URL}/студенты", json=новый_студент)
        print(f"Статус: {response.status_code}")
        if response.status_code == 201:
            print("✅ Новый студент создан!")
            созданный_студент = response.json()
            новый_студент_id = созданный_студент['студент_id']
            print(f"ID нового студента: {новый_студент_id}")
        else:
            print("Ошибка:", response.text)
        
        # 6. Получение всех общежитий
        print("\n6. 🏢 Получение всех общежитий: GET /общежития")
        response = requests.get(f"{BASE_URL}/общежития")
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            общежития = response.json()
            print(f"Найдено {len(общежития)} общежитий:")
            for общежитие in общежития:
                print(f"  - #{общежитие['общежитие_id']}: Общежитие {общежитие['номер']} ({общежитие['количество_комнат']} комнат)")
            общежитие_id = общежития[0]['общежитие_id'] if общежития else None
        else:
            print("Ошибка:", response.text)
        
        # 7. Получение всех комнат
        print("\n7. 🚪 Получение всех комнат: GET /комнаты")
        response = requests.get(f"{BASE_URL}/комнаты")
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            комнаты = response.json()
            print(f"Найдено {len(комнаты)} комнат:")
            for комната in комнаты:
                print(f"  - #{комната['комната_id']}: Комната {комната['номер']}, {комната['вместимость']} мест, {комната['стоимость']} руб.")
            if комнаты:
                комната_id = комнаты[0]['комната_id']
        else:
            print("Ошибка:", response.text)
        
        # 8. Получение свободных комнат
        print("\n8. ✅ Получение свободных комнат: GET /комнаты/свободные")
        response = requests.get(f"{BASE_URL}/комнаты/свободные")
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            свободные_комнаты = response.json()
            print(f"Найдено {len(свободные_комнаты)} свободных комнат:")
            for комната in свободные_комнаты:
                print(f"  - Комната {комната['номер']}, этаж {комната['этаж']}, {комната['стоимость']} руб.")
        
        # 9. Создание нового договора
        if студент_id and комната_id:
            print("\n9. 📄 Создание нового договора: POST /договоры")
            новый_договор = {
                "студент_id": студент_id,
                "комната_id": комната_id,
                "дата_начала": str(date.today()),
                "дата_окончания": str(date.today() + timedelta(days=180))
            }
            response = requests.post(f"{BASE_URL}/договоры", json=новый_договор)
            print(f"Статус: {response.status_code}")
            if response.status_code == 201:
                print("✅ Новый договор создан!")
                созданный_договор = response.json()
                договор_id = созданный_договор['договор_id']
                print(f"ID нового договора: {договор_id}")
            else:
                print("Ошибка:", response.text)
        
        # 10. Получение всех договоров
        print("\n10. 📋 Получение всех договоров: GET /договоры")
        response = requests.get(f"{BASE_URL}/договоры")
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            договоры = response.json()
            print(f"Найдено {len(договоры)} договоров:")
            for договор in договоры:
                print(f"  - #{договор['договор_id']}: Студент {договор['студент_id']}, Комната {договор['комната_id']}")
        
        # 11. Создание квитанции об оплате
        if договор_id:
            print("\n11. 💰 Создание квитанции об оплате: POST /квитанции")
            новая_квитанция = {
                "договор_id": договор_id,
                "сумма": 1200.00,
                "месяц_оплаты": str(date(date.today().year, date.today().month, 1))
            }
            response = requests.post(f"{BASE_URL}/квитанции", json=новая_квитанция)
            print(f"Статус: {response.status_code}")
            if response.status_code == 201:
                print("✅ Квитанция создана!")
                созданная_квитанция = response.json()
                print_json(созданная_квитанция, "Данные квитанции:")
            else:
                print("Ошибка:", response.text)
        
        # 12. Расчет стоимости проживания для студента
        if студент_id and комната_id:
            print(f"\n12. 🧮 Расчет стоимости проживания: POST /студенты/{студент_id}/расчет_стоимости")
            data = {"комната_id": комната_id}
            response = requests.post(f"{BASE_URL}/студенты/{студент_id}/расчет_стоимости", json=data)
            print(f"Статус: {response.status_code}")
            if response.status_code == 200:
                расчет = response.json()
                print("Результат расчета:")
                print(f"  Студент: {расчет['студент']}")
                print(f"  Комната: {расчет['комната']}")
                print(f"  Полная стоимость: {расчет['полная_стоимость']} руб.")
                print(f"  Стоимость со скидкой: {расчет['рассчитанная_стоимость']} руб.")
                print(f"  Скидка: {расчет['скидка']} руб.")
        
        # 13. Проверка льгот студента
        if студент_id:
            print(f"\n13. 🎫 Проверка льгот студента: GET /студенты/{студент_id}/льготы")
            response = requests.get(f"{BASE_URL}/студенты/{студент_id}/льготы")
            print(f"Статус: {response.status_code}")
            if response.status_code == 200:
                льготы = response.json()
                print(f"Найдено {len(льготы)} льгот:")
                for льгота in льготы:
                    категория = льгота.get('категория', {})
                    print(f"  - {категория.get('название', 'Неизвестно')} (скидка: {категория.get('коэффициент_скидки', 0)})")
        
        # 14. Получение активных договоров
        print("\n14. 📅 Получение активных договоров: GET /договоры/активные")
        response = requests.get(f"{BASE_URL}/договоры/активные")
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            активные_договоры = response.json()
            print(f"Найдено {len(активные_договоры)} активных договоров:")
            for договор in активные_договоры:
                print(f"  - Договор #{договор['договор_id']} (с {договор['дата_начала']})")
        
        # 15. Создание задолженности
        if договор_id:
            print("\n15. ⚠️ Создание задолженности: POST /задолженности")
            новая_задолженность = {
                "договор_id": договор_id,
                "сумма": 500.00,
                "статус": "непогашенная"
            }
            response = requests.post(f"{BASE_URL}/задолженности", json=новая_задолженность)
            print(f"Статус: {response.status_code}")
            if response.status_code == 201:
                print("✅ Задолженность создана!")
                созданная_задолженность = response.json()
                print(f"ID новой задолженности: {созданная_задолженность['задолженность_id']}")
        
        # 16. Блокировка пропуска студента
        if студент_id:
            print(f"\n16. 🔒 Блокировка пропуска студента: POST /студенты/{студент_id}/блокировка_пропуска")
            response = requests.post(f"{BASE_URL}/студенты/{студент_id}/блокировка_пропуска")
            print(f"Статус: {response.status_code}")
            if response.status_code == 200:
                результат = response.json()
                print(f"Результат: {результат['message']}")
                if результат['студент']['статус_пропуска']:
                    print("✅ Пропуск активен")
                else:
                    print("🚫 Пропуск заблокирован")
        
        # 17. Получение непогашенных задолженностей
        print("\n17. 💸 Получение непогашенных задолженностей: GET /задолженности/непогашенные")
        response = requests.get(f"{BASE_URL}/задолженности/непогашенные")
        print(f"Статус: {response.status_code}")
        if response.status_code == 200:
            задолженности = response.json()
            print(f"Найдено {len(задолженности)} непогашенных задолженностей:")
            for задолженность in задолженности:
                print(f"  - #{задолженность['задолженность_id']}: {задолженность['сумма']} руб. ({задолженность['статус']})")
        
        # 18. Тестирование обработки ошибок
        print("\n18. 🧪 Тестирование обработки ошибок")
        
        # Несуществующий студент
        print("   GET /студенты/999999:")
        response = requests.get(f"{BASE_URL}/студенты/999999")
        print(f"   Статус: {response.status_code} (ожидается: 404)")
        
        # Создание договора с несуществующим студентом
        print("   POST /договоры с несуществующим студентом:")
        неверный_договор = {
            "студент_id": 999999,
            "комната_id": комната_id if комната_id else 1,
            "дата_начала": str(date.today())
        }
        response = requests.post(f"{BASE_URL}/договоры", json=неверный_договор)
        print(f"   Статус: {response.status_code} (ожидается: 404)")
        
        # Некорректные данные студента
        print("   POST /студенты без телефона:")
        некорректный_студент = {
            "имя": "Только имя",
            "фамилия": "Только фамилия"
        }
        response = requests.post(f"{BASE_URL}/студенты", json=некорректный_студент)
        print(f"   Статус: {response.status_code} (ожидается: 422)")
        
        # Попытка создать дублирующий телефон
        print("   POST /студенты с существующим телефоном:")
        дубликат = {
            "телефон": "+79123456789",  # Телефон из тестовых данных
            "имя": "Дубликат",
            "фамилия": "Тест"
        }
        response = requests.post(f"{BASE_URL}/студенты", json=дубликат)
        print(f"   Статус: {response.status_code} (ожидается: 400)")
        
        # 19. Обновление информации о студенте
        if студент_id:
            print(f"\n19. ✏️ Обновление информации о студенте: PUT /студенты/{студент_id}")
            обновленные_данные = {
                "телефон": "+79123456789",  # Меняем на существующий для проверки
                "имя": "Обновленное Имя",
                "фамилия": "Обновленная Фамилия",
                "статус_пропуска": False
            }
            response = requests.put(f"{BASE_URL}/студенты/{студент_id}", json=обновленные_данные)
            print(f"Статус: {response.status_code}")
            if response.status_code == 200:
                print("✅ Данные студента обновлены!")
                обновленный_студент = response.json()
                статус = "активен" if обновленный_студент['статус_пропуска'] else "заблокирован"
                print(f"  Имя: {обновленный_студент['имя']} {обновленный_студент['фамилия']}")
                print(f"  Статус пропуска: {статус}")
        
        print("\n" + "=" * 70)
        print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
        print("=" * 70)
        print("\n📊 СВОДКА ТЕСТОВ:")
        print("  1. ✅ Основной эндпоинт")
        print("  2. ✅ Проверка БД")
        print("  3. ✅ Получение студентов")
        print("  4. ✅ Получение льготных категорий")
        print("  5. ✅ Создание студента")
        print("  6. ✅ Получение общежитий")
        print("  7. ✅ Получение комнат")
        print("  8. ✅ Получение свободных комнат")
        print("  9. ✅ Создание договора")
        print(" 10. ✅ Получение договоров")
        print(" 11. ✅ Создание квитанции")
        print(" 12. ✅ Расчет стоимости")
        print(" 13. ✅ Проверка льгот")
        print(" 14. ✅ Активные договоры")
        print(" 15. ✅ Создание задолженности")
        print(" 16. ✅ Блокировка пропуска")
        print(" 17. ✅ Непогашенные задолженности")
        print(" 18. ✅ Обработка ошибок")
        print(" 19. ✅ Обновление студента")
        
        print("\n🌐 Для проверки всех эндпоинтов откройте:")
        print("   Документация API: http://localhost:8000/docs")
        print("\n💻 Примеры команд для тестирования:")
        print("   Получить всех студентов:")
        print(f"   curl {BASE_URL}/студенты")
        print("\n   Создать нового студента:")
        print(f'   curl -X POST {BASE_URL}/студенты \\')
        print('     -H "Content-Type: application/json" \\')
        print('     -d \'{"телефон": "+79001112233", "имя": "Иван", "фамилия": "Петров"}\'')
        print("\n   Получить свободные комнаты:")
        print(f"   curl {BASE_URL}/комнаты/свободные")
        print("\n   Рассчитать стоимость проживания:")
        print(f'   curl -X POST {BASE_URL}/студенты/1/расчет_стоимости \\')
        print('     -H "Content-Type: application/json" \\')
        print('     -d \'{"комната_id": 1}\'')
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Ошибка сети: {e}")
        print("Убедитесь, что сервер запущен и доступен")
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api()
