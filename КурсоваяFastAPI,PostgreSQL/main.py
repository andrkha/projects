# ==================== ИМПОРТ БИБЛИОТЕК ====================
from sqlmodel import SQLModel, Field, Session, select, create_engine
from typing import Optional, List
from datetime import datetime, date
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import uvicorn
import psycopg2
import sys

# ==================== НАСТРОЙКА БАЗЫ ДАННЫХ POSTGRESQL ====================
POSTGRES_CONFIG = {
    "user": "postgres",
    "password": "password",
    "host": "localhost",
    "port": "5432",
    "database": "общежитие"
}

DATABASE_URL = f"postgresql://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}@{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}"

# ==================== ОПРЕДЕЛЕНИЕ МОДЕЛЕЙ (СУЩНОСТЕЙ) ====================

class ЛьготнаяКатегория(SQLModel, table=True):
    """Справочник типов льгот"""
    льготная_категория_id: Optional[int] = Field(default=None, primary_key=True)
    название: str = Field(index=True)
    описание: Optional[str] = None
    коэффициент_скидки: float = Field(index=True)
    подтверждающий_документ: str

class Студент(SQLModel, table=True):
    """Информация о студентах"""
    студент_id: Optional[int] = Field(default=None, primary_key=True)
    телефон: str = Field(index=True, unique=True)
    имя: str = Field(index=True)
    фамилия: str = Field(index=True)
    статус_пропуска: bool = Field(default=True)

class Льгота(SQLModel, table=True):
    """Льготы, присвоенные студентам"""
    льгота_id: Optional[int] = Field(default=None, primary_key=True)
    студент_id: int = Field(foreign_key="студент.студент_id")
    льготная_категория_id: int = Field(foreign_key="льготнаякатегория.льготная_категория_id")
    дата_начала: date
    дата_окончания: Optional[date] = None

class Общежитие(SQLModel, table=True):
    """Информация об общежитиях"""
    общежитие_id: Optional[int] = Field(default=None, primary_key=True)
    номер: str = Field(index=True, unique=True)
    адрес: str
    количество_комнат: int

class Комната(SQLModel, table=True):
    """Информация о комнатах в общежитиях"""
    комната_id: Optional[int] = Field(default=None, primary_key=True)
    номер: str = Field(index=True)
    общежитие_id: int = Field(foreign_key="общежитие.общежитие_id")
    вместимость: int
    стоимость: float
    этаж: int

class Договор(SQLModel, table=True):
    """Договоры на проживание"""
    договор_id: Optional[int] = Field(default=None, primary_key=True)
    студент_id: int = Field(foreign_key="студент.студент_id")
    комната_id: int = Field(foreign_key="комната.комната_id")
    дата_заключения: date = Field(default_factory=date.today)
    дата_начала: date
    дата_окончания: Optional[date] = None

class Квитанция(SQLModel, table=True):
    """Квитанции об оплате"""
    квитанция_id: Optional[int] = Field(default=None, primary_key=True)
    договор_id: int = Field(foreign_key="договор.договор_id")
    сумма: float
    месяц_оплаты: date
    дата_оплаты: datetime = Field(default_factory=datetime.utcnow)
    дата_просрочки: Optional[date] = None

class Задолженность(SQLModel, table=True):
    """Задолженности по оплате"""
    задолженность_id: Optional[int] = Field(default=None, primary_key=True)
    договор_id: int = Field(foreign_key="договор.договор_id")
    сумма: float
    дата_возникновения: date = Field(default_factory=date.today)
    дата_погашения: Optional[date] = None
    статус: str = Field(default="непогашенная")

# ==================== ПОДГОТОВКА БАЗЫ ДАННЫХ ====================

def setup_postgresql_database():
    """Проверяет подключение к PostgreSQL и создает базу данных если она не существует"""
    print("🔍 Проверяю подключение к PostgreSQL...")
    
    try:
        conn = psycopg2.connect(
            user=POSTGRES_CONFIG["user"],
            password=POSTGRES_CONFIG["password"],
            host=POSTGRES_CONFIG["host"],
            port=POSTGRES_CONFIG["port"],
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Пытаемся удалить существующую базу данных
        cursor.execute(f"DROP DATABASE IF EXISTS {POSTGRES_CONFIG['database']}")
        print(f"🗑️  Старая база данных удалена (если существовала)")
        
        # Создаем новую базу данных
        print(f"📁 Создаю базу данных '{POSTGRES_CONFIG['database']}'...")
        cursor.execute(f"""
            CREATE DATABASE {POSTGRES_CONFIG['database']}
            WITH 
            OWNER = postgres
            ENCODING = 'UTF8'
            CONNECTION LIMIT = 100
        """)
        print(f"✅ База данных создана")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"Ошибка подключения: {e}")
        print("\nВозможные причины:")
        print(f"1. Неправильный пароль для пользователя '{POSTGRES_CONFIG['user']}'")
        print(f"2. PostgreSQL не запущен на {POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}")
        print(f"3. Пользователь '{POSTGRES_CONFIG['user']}' не существует")
        return False
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def init_database():
    """Инициализирует базу данных: создает таблицы и добавляет тестовые данные"""
    print("\n🔧 Инициализация базы данных...")
    
    if not setup_postgresql_database():
        print("\nНе могу подключиться к PostgreSQL!")
        print("Проверьте пароль и убедитесь, что PostgreSQL запущен.")
        sys.exit(1)
    
    try:
        engine = create_engine(DATABASE_URL, echo=True)
        
        # Создаем все таблицы
        SQLModel.metadata.create_all(engine)
        print("✅ Таблицы созданы успешно")
        
        # Добавляем тестовые данные
        with Session(engine) as session:
            # Проверяем, есть ли уже данные
            if not session.exec(select(ЛьготнаяКатегория)).first():
                print("📝 Добавляю тестовые данные...")
                
                # 1. Добавляем льготные категории
                льготные_категории = [
                    ЛьготнаяКатегория(
                        название="Дети-сироты",
                        описание="Дети, оставшиеся без попечения родителей",
                        коэффициент_скидки=1.0,
                        подтверждающий_документ="Справка из детдома"
                    ),
                    ЛьготнаяКатегория(
                        название="Потерявшие одного из родителей",
                        описание="Студенты, потерявшие одного из родителей",
                        коэффициент_скидки=0.5,
                        подтверждающий_документ="Справка о потере кормильца"
                    ),
                    ЛьготнаяКатегория(
                        название="Инвалиды 1 и 2 групп",
                        описание="Студенты с инвалидностью 1 или 2 группы",
                        коэффициент_скидки=1.0,
                        подтверждающий_документ="Справка об инвалидности"
                    ),
                    ЛьготнаяКатегория(
                        название="Многодетные семьи",
                        описание="Студенты из многодетных семей",
                        коэффициент_скидки=0.5,
                        подтверждающий_документ="Справка о многодетной семье"
                    ),
                    ЛьготнаяКатегория(
                        название="Из дальнего региона",
                        описание="Студенты, приехавшие из дальних регионов",
                        коэффициент_скидки=0.3,
                        подтверждающий_документ="Прописка"
                    )
                ]
                
                for категория in льготные_категории:
                    session.add(категория)
                
                # 2. Добавляем студентов
                студенты = [
                    Студент(
                        телефон="+79123456789",
                        имя="Иван",
                        фамилия="Иванов",
                        статус_пропуска=True
                    ),
                    Студент(
                        телефон="+79161234567",
                        имя="Мария",
                        фамилия="Петрова",
                        статус_пропуска=True
                    ),
                    Студент(
                        телефон="+79031112233",
                        имя="Алексей",
                        фамилия="Сидоров",
                        статус_пропуска=True
                    ),
                    Студент(
                        телефон="+79052223344",
                        имя="Анна",
                        фамилия="Козлова",
                        статус_пропуска=True
                    )
                ]
                
                for студент in студенты:
                    session.add(студент)
                
                session.commit()
                
                # 3. Добавляем льготы студентам
                все_студенты = session.exec(select(Студент)).all()
                все_категории = session.exec(select(ЛьготнаяКатегория)).all()
                
                льготы = [
                    Льгота(
                        студент_id=все_студенты[0].студент_id,
                        льготная_категория_id=все_категории[0].льготная_категория_id,
                        дата_начала=date(2024, 9, 1),
                        дата_окончания=date(2025, 6, 30)
                    ),
                    Льгота(
                        студент_id=все_студенты[1].студент_id,
                        льготная_категория_id=все_категории[2].льготная_категория_id,
                        дата_начала=date(2024, 9, 1),
                        дата_окончания=date(2025, 6, 30)
                    )
                ]
                
                for льгота in льготы:
                    session.add(льгота)
                
                # 4. Добавляем общежития
                общежития = [
                    Общежитие(
                        номер="1",
                        адрес="ул. Студенческая, д. 1",
                        количество_комнат=100
                    ),
                    Общежитие(
                        номер="2",
                        адрес="ул. Общежитийная, д. 5",
                        количество_комнат=150
                    )
                ]
                
                for общежитие in общежития:
                    session.add(общежитие)
                
                session.commit()
                
                # 5. Добавляем комнаты
                все_общежития = session.exec(select(Общежитие)).all()
                
                комнаты = [
                    Комната(
                        номер="101",
                        общежитие_id=все_общежития[0].общежитие_id,
                        вместимость=3,
                        стоимость=1500.00,
                        этаж=1
                    ),
                    Комната(
                        номер="102",
                        общежитие_id=все_общежития[0].общежитие_id,
                        вместимость=2,
                        стоимость=2000.00,
                        этаж=1
                    ),
                    Комната(
                        номер="201",
                        общежитие_id=все_общежития[0].общежитие_id,
                        вместимость=4,
                        стоимость=1200.00,
                        этаж=2
                    ),
                    Комната(
                        номер="301",
                        общежитие_id=все_общежития[1].общежитие_id,
                        вместимость=3,
                        стоимость=1800.00,
                        этаж=3
                    )
                ]
                
                for комната in комнаты:
                    session.add(комната)
                
                session.commit()
                
                # 6. Добавляем договоры
                все_комнаты = session.exec(select(Комната)).all()
                
                договоры = [
                    Договор(
                        студент_id=все_студенты[0].студент_id,
                        комната_id=все_комнаты[0].комната_id,
                        дата_начала=date(2024, 9, 1),
                        дата_окончания=date(2025, 6, 30)
                    ),
                    Договор(
                        студент_id=все_студенты[1].студент_id,
                        комната_id=все_комнаты[1].комната_id,
                        дата_начала=date(2024, 9, 1),
                        дата_окончания=date(2025, 6, 30)
                    )
                ]
                
                for договор in договоры:
                    session.add(договор)
                
                session.commit()
                
                # 7. Добавляем квитанции
                все_договоры = session.exec(select(Договор)).all()
                
                квитанции = [
                    Квитанция(
                        договор_id=все_договоры[0].договор_id,
                        сумма=1500.00,
                        месяц_оплаты=date(2024, 10, 1)
                    ),
                    Квитанция(
                        договор_id=все_договоры[0].договор_id,
                        сумма=1500.00,
                        месяц_оплаты=date(2024, 11, 1)
                    ),
                    Квитанция(
                        договор_id=все_договоры[1].договор_id,
                        сумма=1000.00,  # 2000 * 0.5 (скидка 50% за инвалидность)
                        месяц_оплаты=date(2024, 10, 1)
                    )
                ]
                
                for квитанция in квитанции:
                    session.add(квитанция)
                
                session.commit()
                
                print("✅ Тестовые данные добавлены:")
                print(f"   - Льготных категорий: {len(льготные_категории)}")
                print(f"   - Студентов: {len(студенты)}")
                print(f"   - Льгот: {len(льготы)}")
                print(f"   - Общежитий: {len(общежития)}")
                print(f"   - Комнат: {len(комнаты)}")
                print(f"   - Договоров: {len(договоры)}")
                print(f"   - Квитанций: {len(квитанции)}")
            
        print("База данных готова к работе")
        return engine
        
    except Exception as e:
        print(f"Ошибка при инициализации БД: {e}")
        raise

# ==================== СОЗДАНИЕ FASTAPI ПРИЛОЖЕНИЯ ====================

app = FastAPI(
    title="Система управления общежитиями API",
    version="1.0",
    description="API для автоматизации процессов заселения студентов, учета комнат, управления льготами и контроля оплаты проживания"
)

# ==================== МОДЕЛИ ДЛЯ ВХОДНЫХ ДАННЫХ API ====================

class СтудентCreate(BaseModel):
    телефон: str
    имя: str
    фамилия: str
    статус_пропуска: bool = True

class ЛьготаCreate(BaseModel):
    студент_id: int
    льготная_категория_id: int
    дата_начала: date
    дата_окончания: Optional[date] = None

class ОбщежитиеCreate(BaseModel):
    номер: str
    адрес: str
    количество_комнат: int

class КомнатаCreate(BaseModel):
    номер: str
    общежитие_id: int
    вместимость: int
    стоимость: float
    этаж: int

class ДоговорCreate(BaseModel):
    студент_id: int
    комната_id: int
    дата_начала: date
    дата_окончания: Optional[date] = None

class КвитанцияCreate(BaseModel):
    договор_id: int
    сумма: float
    месяц_оплаты: date

class ЗадолженностьCreate(BaseModel):
    договор_id: int
    сумма: float
    статус: str = "непогашенная"

# ==================== ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ ====================

print("=" * 70)
print("СИСТЕМА УПРАВЛЕНИЯ СТУДЕНЧЕСКИМИ ОБЩЕЖИТИЯМИ")
print("=" * 70)

engine = init_database()

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def get_session():
    """Функция для получения сессии работы с базой данных"""
    with Session(engine) as session:
        yield session

def рассчитать_стоимость_проживания(стоимость_комнаты: float, студент_id: int, session: Session) -> float:
    """Рассчитывает стоимость проживания с учетом льгот студента"""
    # Получаем активные льготы студента
    льготы = session.exec(
        select(Льгота).where(
            Льгота.студент_id == студент_id,
            Льгота.дата_окончания == None
        )
    ).all()
    
    if not льготы:
        return стоимость_комнаты
    
    # Получаем максимальную скидку из всех льгот
    максимальный_коэффициент = 0.0
    for льгота in льготы:
        категория = session.get(ЛьготнаяКатегория, льгота.льготная_категория_id)
        if категория and категория.коэффициент_скидки > максимальный_коэффициент:
            максимальный_коэффициент = категория.коэффициент_скидки
    
    # Применяем формулу: Полная сумма - (Полная сумма × Коэффициент скидки)
    return стоимость_комнаты * (1 - максимальный_коэффициент)

# ==================== API ЭНДПОИНТЫ ====================

@app.get("/")
def read_root():
    """Корневой эндпоинт API"""
    return {
        "message": "Добро пожаловать в систему управления студенческими общежитиями!",
        "database": "PostgreSQL - общежитие",
        "endpoints": {
            "студенты": "/студенты",
            "льготы": "/льготы",
            "льготные_категории": "/льготные_категории",
            "общежития": "/общежития",
            "комнаты": "/комнаты",
            "договоры": "/договоры",
            "квитанции": "/квитанции",
            "задолженности": "/задолженности",
            "документация": "/docs"
        }
    }

# ==================== ЭНДПОИНТЫ ДЛЯ СТУДЕНТОВ ====================

@app.get("/студенты", response_model=List[Студент])
def get_студенты(session: Session = Depends(get_session)):
    """Получить всех студентов"""
    return session.exec(select(Студент)).all()

@app.get("/студенты/{студент_id}", response_model=Студент)
def get_студент(студент_id: int, session: Session = Depends(get_session)):
    """Получить студента по ID"""
    студент = session.get(Студент, студент_id)
    if not студент:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return студент

@app.post("/студенты", response_model=Студент, status_code=201)
def create_студент(студент: СтудентCreate, session: Session = Depends(get_session)):
    """Создать нового студента"""
    # Проверяем уникальность телефона
    существующий = session.exec(select(Студент).where(Студент.телефон == студент.телефон)).first()
    if существующий:
        raise HTTPException(status_code=400, detail="Студент с таким телефоном уже существует")
    
    новый_студент = Студент(**студент.dict())
    session.add(новый_студент)
    session.commit()
    session.refresh(новый_студент)
    return новый_студент

@app.put("/студенты/{студент_id}", response_model=Студент)
def update_студент(студент_id: int, студент_данные: СтудентCreate, session: Session = Depends(get_session)):
    """Обновить информацию о студенте"""
    студент = session.get(Студент, студент_id)
    if not студент:
        raise HTTPException(status_code=404, detail="Студент не найден")
    
    # Проверяем уникальность телефона (если изменился)
    if студент.телефон != студент_данные.телефон:
        существующий = session.exec(
            select(Студент).where(Студент.телефон == студент_данные.телефон)
        ).first()
        if существующий:
            raise HTTPException(status_code=400, detail="Студент с таким телефоном уже существует")
    
    for ключ, значение in студент_данные.dict().items():
        setattr(студент, ключ, значение)
    
    session.add(студент)
    session.commit()
    session.refresh(студент)
    return студент

# ==================== ЭНДПОИНТЫ ДЛЯ ЛЬГОТНЫХ КАТЕГОРИЙ ====================

@app.get("/льготные_категории", response_model=List[ЛьготнаяКатегория])
def get_льготные_категории(session: Session = Depends(get_session)):
    """Получить все льготные категории"""
    return session.exec(select(ЛьготнаяКатегория)).all()

# ==================== ЭНДПОИНТЫ ДЛЯ ЛЬГОТ ====================

@app.get("/льготы", response_model=List[Льгота])
def get_льготы(session: Session = Depends(get_session)):
    """Получить все льготы"""
    return session.exec(select(Льгота)).all()

@app.post("/льготы", response_model=Льгота, status_code=201)
def create_льгота(льгота: ЛьготаCreate, session: Session = Depends(get_session)):
    """Создать новую льготу для студента"""
    # Проверяем существование студента и категории
    студент = session.get(Студент, льгота.студент_id)
    if not студент:
        raise HTTPException(status_code=404, detail="Студент не найден")
    
    категория = session.get(ЛьготнаяКатегория, льгота.льготная_категория_id)
    if not категория:
        raise HTTPException(status_code=404, detail="Льготная категория не найдена")
    
    новая_льгота = Льгота(**льгота.dict())
    session.add(новая_льгота)
    session.commit()
    session.refresh(новая_льгота)
    return новая_льгота

# ==================== ЭНДПОИНТЫ ДЛЯ ОБЩЕЖИТИЙ ====================

@app.get("/общежития", response_model=List[Общежитие])
def get_общежития(session: Session = Depends(get_session)):
    """Получить все общежития"""
    return session.exec(select(Общежитие)).all()

@app.get("/общежития/{общежитие_id}", response_model=Общежитие)
def get_общежитие(общежитие_id: int, session: Session = Depends(get_session)):
    """Получить общежитие по ID"""
    общежитие = session.get(Общежитие, общежитие_id)
    if not общежитие:
        raise HTTPException(status_code=404, detail="Общежитие не найден")
    return общежитие

@app.post("/общежития", response_model=Общежитие, status_code=201)
def create_общежитие(общежитие: ОбщежитиеCreate, session: Session = Depends(get_session)):
    """Создать новое общежитие"""
    новое_общежитие = Общежитие(**общежитие.dict())
    session.add(новое_общежитие)
    session.commit()
    session.refresh(новое_общежитие)
    return новое_общежитие

# ==================== ЭНДПОИНТЫ ДЛЯ КОМНАТ ====================

@app.get("/комнаты", response_model=List[Комната])
def get_комнаты(session: Session = Depends(get_session)):
    """Получить все комнаты"""
    return session.exec(select(Комната)).all()

@app.get("/комнаты/свободные", response_model=List[Комната])
def get_свободные_комнаты(session: Session = Depends(get_session)):
    """Получить свободные комнаты (не занятые по договорам)"""
    # Получаем все комнаты, которые не используются в активных договорах
    занятые_комнаты = session.exec(
        select(Договор.комната_id).where(
            Договор.дата_окончания == None  # Активные договоры
        )
    ).all()
    
    if занятые_комнаты:
        return session.exec(
            select(Комната).where(Комната.комната_id.not_in(занятые_комнаты))
        ).all()
    else:
        return session.exec(select(Комната)).all()

@app.get("/комнаты/общежитие/{общежитие_id}", response_model=List[Комната])
def get_комнаты_по_общежитию(общежитие_id: int, session: Session = Depends(get_session)):
    """Получить комнаты конкретного общежития"""
    return session.exec(
        select(Комната).where(Комната.общежитие_id == общежитие_id)
    ).all()

@app.post("/комнаты", response_model=Комната, status_code=201)
def create_комната(комната: КомнатаCreate, session: Session = Depends(get_session)):
    """Создать новую комнату"""
    # Проверяем существование общежития
    общежитие = session.get(Общежитие, комната.общежитие_id)
    if not общежитие:
        raise HTTPException(status_code=404, detail="Общежитие не найден")
    
    новая_комната = Комната(**комната.dict())
    session.add(новая_комната)
    session.commit()
    session.refresh(новая_комната)
    return новая_комната

# ==================== ЭНДПОИНТЫ ДЛЯ ДОГОВОРОВ ====================

@app.get("/договоры", response_model=List[Договор])
def get_договоры(session: Session = Depends(get_session)):
    """Получить все договоры"""
    return session.exec(select(Договор)).all()

@app.get("/договоры/активные", response_model=List[Договор])
def get_активные_договоры(session: Session = Depends(get_session)):
    """Получить активные договоры (без даты окончания)"""
    return session.exec(
        select(Договор).where(Договор.дата_окончания == None)
    ).all()

@app.post("/договоры", response_model=Договор, status_code=201)
def create_договор(договор: ДоговорCreate, session: Session = Depends(get_session)):
    """Создать новый договор на проживание"""
    # Проверяем существование студента
    студент = session.get(Студент, договор.студент_id)
    if not студент:
        raise HTTPException(status_code=404, detail="Студент не найден")
    
    # Проверяем существование комнаты
    комната = session.get(Комната, договор.комната_id)
    if not комната:
        raise HTTPException(status_code=404, detail="Комната не найдена")
    
    # Проверяем, свободна ли комната
    занятая = session.exec(
        select(Договор).where(
            Договор.комната_id == договор.комната_id,
            Договор.дата_окончания == None  # Проверяем активные договоры
        )
    ).first()
    
    if занятая:
        raise HTTPException(status_code=400, detail="Комната уже занята")
    
    новый_договор = Договор(**договор.dict())
    session.add(новый_договор)
    session.commit()
    session.refresh(новый_договор)
    return новый_договор

# ==================== ЭНДПОИНТЫ ДЛЯ КВИТАНЦИЙ ====================

@app.get("/квитанции", response_model=List[Квитанция])
def get_квитанции(session: Session = Depends(get_session)):
    """Получить все квитанции"""
    return session.exec(select(Квитанция)).all()

@app.post("/квитанции", response_model=Квитанция, status_code=201)
def create_квитанция(квитанция: КвитанцияCreate, session: Session = Depends(get_session)):
    """Создать новую квитанцию об оплате"""
    # Проверяем существование договора
    договор = session.get(Договор, квитанция.договор_id)
    if not договор:
        raise HTTPException(status_code=404, detail="Договор не найден")
    
    # Получаем стоимость комнаты
    комната = session.get(Комната, договор.комната_id)
    if not комната:
        raise HTTPException(status_code=404, detail="Комната не найдена")
    
    # Рассчитываем стоимость с учетом льгот
    рассчитанная_стоимость = рассчитать_стоимость_проживания(
        комната.стоимость,
        договор.студент_id,
        session
    )
    
    # Создаем квитанцию
    новая_квитанция = Квитанция(**квитанция.dict())
    session.add(новая_квитанция)
    session.commit()
    session.refresh(новая_квитанция)
    return новая_квитанция

# ==================== ЭНДПОИНТЫ ДЛЯ ЗАДОЛЖЕННОСТЕЙ ====================

@app.get("/задолженности", response_model=List[Задолженность])
def get_задолженности(session: Session = Depends(get_session)):
    """Получить все задолженности"""
    return session.exec(select(Задолженность)).all()

@app.get("/задолженности/непогашенные", response_model=List[Задолженность])
def get_непогашенные_задолженности(session: Session = Depends(get_session)):
    """Получить непогашенные задолженности"""
    return session.exec(
        select(Задолженность).where(Задолженность.статус != "погашенная")
    ).all()

@app.post("/задолженности", response_model=Задолженность, status_code=201)
def create_задолженность(задолженность: ЗадолженностьCreate, session: Session = Depends(get_session)):
    """Создать новую задолженность"""
    # Проверяем существование договора
    договор = session.get(Договор, задолженность.договор_id)
    if not договор:
        raise HTTPException(status_code=404, detail="Договор не найден")
    
    новая_задолженность = Задолженность(**задолженность.dict())
    session.add(новая_задолженность)
    session.commit()
    session.refresh(новая_задолженность)
    return новая_задолженность

# ==================== СПЕЦИАЛЬНЫЕ ЭНДПОИНТЫ ====================

@app.get("/студенты/{студент_id}/льготы")
def get_льготы_студента(студент_id: int, session: Session = Depends(get_session)):
    """Получить льготы конкретного студента"""
    студент = session.get(Студент, студент_id)
    if not студент:
        raise HTTPException(status_code=404, detail="Студент не найден")
    
    льготы = session.exec(
        select(Льгота).where(Льгота.студент_id == студент_id)
    ).all()
    
    result = []
    for льгота in льготы:
        категория = session.get(ЛьготнаяКатегория, льгота.льготная_категория_id)
        result.append({
            "льгота": льгота,
            "категория": категория
        })
    
    return result

@app.get("/договоры/{договор_id}/квитанции")
def get_квитанции_договора(договор_id: int, session: Session = Depends(get_session)):
    """Получить квитанции конкретного договора"""
    договор = session.get(Договор, договор_id)
    if not договор:
        raise HTTPException(status_code=404, detail="Договор не найден")
    
    return session.exec(
        select(Квитанция).where(Квитанция.договор_id == договор_id)
    ).all()

@app.post("/студенты/{студент_id}/расчет_стоимости")
def рассчитать_стоимость_для_студента(студент_id: int, комната_id: int, session: Session = Depends(get_session)):
    """Рассчитать стоимость проживания для студента в конкретной комнате"""
    студент = session.get(Студент, студент_id)
    if not студент:
        raise HTTPException(status_code=404, detail="Студент не найден")
    
    комната = session.get(Комната, комната_id)
    if not комната:
        raise HTTPException(status_code=404, detail="Комната не найдена")
    
    полная_стоимость = комната.стоимость
    рассчитанная_стоимость = рассчитать_стоимость_проживания(полная_стоимость, студент_id, session)
    
    return {
        "студент": f"{студент.имя} {студент.фамилия}",
        "комната": комната.номер,
        "полная_стоимость": полная_стоимость,
        "рассчитанная_стоимость": рассчитанная_стоимость,
        "скидка": полная_стоимость - рассчитанная_стоимость
    }

@app.post("/студенты/{студент_id}/блокировка_пропуска")
def блокировать_пропуск(студент_id: int, session: Session = Depends(get_session)):
    """Блокировать пропуск студента (при наличии задолженностей)"""
    студент = session.get(Студент, студент_id)
    if not студент:
        raise HTTPException(status_code=404, detail="Студент не найден")
    
    # Проверяем наличие непогашенных задолженностей
    договоры = session.exec(
        select(Договор).where(Договор.студент_id == студент_id)
    ).all()
    
    has_debt = False
    for договор in договоры:
        задолженности = session.exec(
            select(Задолженность).where(
                Задолженность.договор_id == договор.договор_id,
                Задолженность.статус != "погашенная"
            )
        ).all()
        
        if задолженности:
            has_debt = True
            break
    
    if has_debt:
        студент.статус_пропуска = False
        session.add(студент)
        session.commit()
        session.refresh(студент)
        return {"message": "Пропуск заблокирован", "студент": студент}
    else:
        return {"message": "Задолженностей нет, пропуск активен", "студент": студент}

@app.get("/база_данных/статус")
def database_health(session: Session = Depends(get_session)):
    """Проверка состояния базы данных"""
    try:
        session.exec(select(1))
        return {
            "статус": "работает",
            "база_данных": "PostgreSQL - общежитие",
            "подключение": "успешно",
            "время": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")

# ==================== ЗАПУСК СЕРВЕРА ====================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("FASTAPI СЕРВЕР ЗАПУЩЕН!")
    print("=" * 70)
    print("Документация API: http://localhost:8000/docs")
    print("\nОСНОВНЫЕ ЭНДПОИНТЫ:")
    print("  GET  /студенты              - Получить всех студентов")
    print("  POST /студенты              - Создать нового студента")
    print("  GET  /комнаты/свободные     - Получить свободные комнаты")
    print("  POST /договоры              - Создать договор на проживание")
    print("  POST /квитанции             - Создать квитанцию об оплате")
    print("  GET  /договоры/активные     - Получить активные договоры")
    print("\nСПЕЦИАЛЬНЫЕ ЭНДПОИНТЫ:")
    print("  POST /студенты/{id}/расчет_стоимости - Рассчитать стоимость для студента")
    print("  POST /студенты/{id}/блокировка_пропуска - Блокировать пропуск при задолженности")
    print("  GET  /база_данных/статус    - Проверить состояние БД")
    print("\nДЛЯ ТЕСТИРОВАНИЯ:")
    print('  curl http://localhost:8000/студенты')
    print('  curl -X POST http://localhost:8000/студенты \\')
    print('       -H "Content-Type: application/json" \\')
    print('       -d \'{"телефон": "+79009998877", "имя": "Петр", "фамилия": "Васильев"}\'')
    print("\nДля остановки сервера нажмите Ctrl+C")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
