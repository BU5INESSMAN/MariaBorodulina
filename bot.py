import os
import asyncio
import aiosqlite
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.deep_linking import create_start_link

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# --- Ссылки (Диплинки) ---
URL_INTENSIVE = "https://t.me/mariaborodylina?text=Здравствуйте!%20Хочу%20на%20интенсив%20«Связь%20с%20телом»."
URL_DIAGNOSTIC = "https://t.me/mariaborodylina?text=Здравствуйте!%20Хочу%20на%20бесплатную%20диагностику."

# --- Тексты результатов ---
RESULT_50_60 = (
    "**50 – 60 баллов. Высокая самоценность. «Я у себя есть».**\n\n"
    "Поздравляю! Вы обладаете тем самым внутренним стержнем. Вы не рухнете, если вас не похвалят, и не рассыпетесь от критики. Вы умеете быть опорой самой себе. В отношениях вы выбираете партнера, а не боретесь за него. Вы четко чувствуете свои границы.\n\n"
    "Но даже здесь есть нюанс: Проверьте, не закрылись ли вы в «броне» самодостаточности, чтобы не чувствовать боль? Иногда высокая самоценность — это маска, за которой прячется усталость быть «сильной».\n\n"
    "И об этой усталости громче всего говорит наше тело. Хроническое напряжение в спине и шее, будто вы несете невидимый груз; тяжесть в плечах; «деревянная» осанка; частые головные боли, боли в спине или ощущение комка в горле, сдавленности в груди — всё это сигналы того, что внутри копятся подавленные эмоции.\n\n"
    "На самом деле истинная самоценность — это не вечная боевая готовность, а способность быть гибкой, расслабленной, живой. Это умение иногда снимать доспехи и доверять миру.\n\n"
    "Если вы узнали себя в этом описании, у меня для вас есть решение — мини-интенсив «Связь с телом». Это бережное путешествие вглубь себя через техники, практики и медитации. Мы будем учиться слышать тихие сигналы своего тела, высвобождать застарелые эмоции, которые застыли в мышцах, и наконец-то разрешать себе расслабляться без чувства вины.\n\n"
    "Стоимость интенсива «Связь с телом» 990₽.\n\nЗапишись на интенсив в личные сообщения. Жду вас 🌹"
)

RESULT_36_49 = (
    "**36 – 49 баллов. Средний/Ситуативный уровень. «Я ок, если...»**\n\n"
    "У вас хорошая база, но ваша самоценность часто зависит от внешних факторов: похвалы начальника, настроения партнера, успеха детей. Вы можете быть сильной, но периодически проваливаетесь в состояние «я недостаточно хороша». Это зыбкая почва.\n\n"
    "Именно здесь чаще всего возникают истории про обесценивание (вы можете его притягивать) и желание «спасать» недоступных партнеров. Фундамент есть, но он требует укрепления.\n\n"
    "Если вы узнали себя в этом описании, приглашаю вас на бесплатную диагностическую консультацию. Это не просто разговор по душам. Это глубокая разведка вашего внутреннего ландшафта. За 30–40 минут мы:\n\n"
    "1. Найдем вашу «ахиллесову пяту» — ту конкретную сферу, где внешние опоры подменяют внутреннюю ценность.\n"
    "2. Увидим повторяющийся сценарий, который заставляет вас снова и снова доказывать, что вы «достойны», вместо того чтобы просто быть.\n"
    "3. Я дам вам обратную связь и конкретный вектор движения — что именно сейчас нужно укреплять, чтобы обрести устойчивость.\n\n"
    "Запишись на бесплатную консультацию в личные сообщения. Жду вас 🌹"
)

RESULT_22_35 = (
    "**22 – 35 баллов. Низкая самоценность. «Поиск себя через других».**\n\n"
    "Скорее всего, вам знакомо чувство, что вы «не тянете». Вы очень требовательны к себе, но при этом зависимы от мнения окружающих. В отношениях вы часто оказываетесь в роли «догоняющей» или «спасающей». Вы боитесь быть покинутой, поэтому можете терпеть неуважение или обесценивание.\n\n"
    "Ваш внутренний критик очень силен. Это состояние выматывает и не дает строить счастливые отношения, основанные на равенстве. Вы словно все время ищете подтверждение своей нужности вовне.\n\n"
    "Если вы узнали себя, дело не в том, что с вами «что-то не так». Дело в тех самых глубинных Я-программах, которые были заложены в детстве. Программах «я ценна, только если удобна/успешна/незаметна».\n\n"
    "Я приглашаю вас на бесплатную 30-минутную диагностику. На ней мы:\n"
    "1. Определим вашу ключевую разрушительную «Я-программу», которая сейчас управляет вашими отношениями.\n"
    "2. Посмотрим, как эта программа мешает вам чувствовать себя любимой и ценной.\n"
    "3. Я дам вам первый конкретный шаг к тому, чтобы начать ее менять.\n\n"
    "Не нужно больше терпеть и доказывать. Пора просто быть.\n\n"
    "Запишись на бесплатную консультацию в личные сообщения. Жду вас 🌹"
)

RESULT_15_21 = (
    "**15 – 21 балл. Критически низкая самоценность. «Я — пустота».**\n\n"
    "Вам сейчас очень больно. Мир кажется опасным, а вы — маленькой и беззащитной перед ним. Вы либо постоянно доказываете всем, что чего-то стоите (сгорая на работе), либо чувствуете себя полностью опустошенной.\n\n"
    "В любви вы либо растворяетесь в партнере без остатка, терпя любое обращение, либо выбираете тех, кто принципиально недоступен, чтобы лишний раз не раниться об реальную близость.\n\n"
    "Если вы узнали себя, дело не в том, что с вами «что-то не так». Дело в тех самых глубинных Я-программах, которые были заложены в детстве. Программах «я ценна, только если удобна/успешна/незаметна».\n\n"
    "Я приглашаю вас на бесплатную 30-минутную диагностику. На ней мы:\n"
    "1. Определим вашу ключевую разрушительную «Я-программу», которая сейчас управляет вашими отношениями.\n"
    "2. Посмотрим, как эта программа мешает вам чувствовать себя любимой и ценной.\n"
    "3. Я дам вам первый конкретный шаг к тому, чтобы начать ее менять.\n\n"
    "Не нужно больше терпеть и доказывать. Пора просто быть.\n\n"
    "Запишись на бесплатную консультацию в личные сообщения. Жду вас 🌹"
)

# --- Список вопросов ---
QUESTIONS = [
    {
        "text": "1. Вы просыпаетесь утром в выходной. Первая мысль, которая чаще всего приходит в голову:",
        "opts": [("А", "«Ура! Можно поваляться и ничего не делать».", 4),
                 ("Б", "«Надо бы вставать, столько дел, а то день пропадет зря».", 3),
                 ("В", "«Интересно, он мне написал/а?» (или «Почему мне никто не пишет?»).", 2),
                 ("Г", "«Опять утро... Нужно заставить себя встать».", 1)]
    },
    {
        "text": "2. Когда партнер (или близкий человек) молчит и задумчив, вы обычно:",
        "opts": [("А", "Спокойно занимаетесь своими делами, думаете, что ему, видимо, нужно побыть в тишине.", 4),
                 ("Б", "Аккуратно спрашиваете, всё ли в порядке, и если он не хочет говорить, оставляете в покое.", 3),
                 ("В", "Начинаете переживать и прокручивать: «Что я сделала не так?», «Он злится на меня?».", 2),
                 ("Г", "Тоже замолкаете и обижаетесь, считая, что он игнорирует вас намеренно.", 1)]
    },
    {
        "text": "3. Представьте: вы сделали важное дело, но никто этого не заметил и не похвалил. Ваше внутреннее ощущение:",
        "opts": [("А", "Я сама знаю, что сделала круто, мне и так хорошо.", 4),
                 ("Б", "Чуть-чуть грустно без похвалы, но я себя сама порадую.", 3),
                 ("В", "Возникает чувство, что это было зря, и вообще я могла бы и не стараться.", 2),
                 ("Г", "Меня это обесценивает, я расстраиваюсь и злюсь на окружающих.", 1)]
    },
    {
        "text": "4. Какое утверждение про деньги вам ближе?",
        "opts": [("А", "Деньги — это инструмент. Если они есть — хорошо, нет — заработаю.", 4),
                 ("Б", "Деньги дают свободу, но их отсутствие — не повод себя не уважать.", 3),
                 ("В", "Когда денег мало, я чувствую себя никчемной и неудачницей.", 2),
                 ("Г", "Я боюсь просить повышение или озвучивать цену за свою работу, мне неудобно.", 1)]
    },
    {
        "text": "5. Если в ссоре с любимым человеком он говорит вам: «Ты слишком остро реагируешь!», ваша реакция:",
        "opts": [("А", "Спокойно объясняю, что мои чувства имеют значение, и мы обсуждаем суть проблемы.", 4),
                 ("Б", "Задумываюсь, может, и правда перегнула, но прошу объяснить, что он имел в виду.", 3),
                 ("В", "Чувствую вину, начинаю извиняться за свои чувства и оправдываться.", 2),
                 ("Г", "Обижаюсь и ухожу в молчанку, внутри чувствуя, что я «плохая».", 1)]
    },
    {
        "text": "6. Вам сделали комплимент. Ваша первая внутренняя реакция:",
        "opts": [("А", "Искренняя радость, мне приятно.", 4),
                 ("Б", "Легкое смущение, но приятно.", 3),
                 ("В", "Желание ответить что-то вроде: «Да это платье старое/так получилось/пустяки».", 2),
                 ("Г", "Мысль: «Что ему нужно? Наверное, что-то просит хочет».", 1)]
    },
    {
        "text": "7. Вы совершили ошибку на работе или в быту. Что вы чувствуете к себе в этот момент?",
        "opts": [("А", "Это просто опыт. С кем не бывает.", 4),
                 ("Б", "Легкая досада, но я себя не ругаю.", 3),
                 ("В", "Злость на себя: «Вечно я всё порчу/туплю/недоделываю».", 2),
                 ("Г", "Желание все бросить, потому что я неудачница.", 1)]
    },
    {
        "text": "8. Когда вы остаетесь одна в тишине, что происходит?",
        "opts": [("А", "Кайфую, это мое время перезагрузки.", 4),
                 ("Б", "Нормально, могу помечтать или подумать о планах.", 3),
                 ("В", "Становится тревожно и некомфортно, хочется скорее включить что-то или кому-то написать.", 2),
                 ("Г", "В голову лезут неприятные мысли о себе и своей жизни.", 1)]
    },
    {
        "text": "9. Ваш партнер проводит время с друзьями без вас. Ваше истинное чувство:",
        "opts": [("А", "Радость за него, у меня тоже есть свои дела.", 4),
                 ("Б", "Спокойствие, я доверяю и понимаю, что это необходимо.", 3),
                 ("В", "Легкая тревога, что без меня ему лучше/веселее.", 2),
                 ("Г", "Обида и ощущение покинутости, ненужности.", 1)]
    },
    {
        "text": "10. Если сравнивать вашу жизнь с жизнью подруг/коллег, вы чаще чувствуете:",
        "opts": [("А", "У каждой свой путь, сравнение мне не интересно.", 4),
                 ("Б", "Иногда завидую успехам, но в целом понимаю, что у меня всё хорошо.", 3),
                 ("В", "Часто ощущаю, что я отстала, у них всё лучше, чем у меня.", 2),
                 ("Г", "Зависть, которая потом переходит в самоедство.", 1)]
    },
    {
        "text": "11. Когда вы просите о помощи, что вы чувствуете?",
        "opts": [("А", "Это нормально, люди помогают друг другу.", 4),
                 ("Б", "Нормально, но стараюсь не злоупотреблять.", 3),
                 ("В", "Мне очень трудно просить, я чувствую себя слабой и обузой.", 2),
                 ("Г", "Лучше сделаю сама, даже если умру от усталости, чем буду кому-то должна.", 1)]
    },
    {
        "text": "12. Выберите фразу, которая больше «откликается» в душе:",
        "opts": [("А", "Я имею право быть счастливой просто потому, что я есть.", 4),
                 ("Б", "Я имею право на ошибку и на отдых.", 3),
                 ("В", "Надо быть хорошей, удобной, чтобы меня любили.", 2),
                 ("Г", "Любовь и признание нужно заслужить.", 1)]
    },
    {
        "text": "13. Внешность. Вы ловите свое отражение в витрине магазина. Мысль:",
        "opts": [("А", "Привет, красотка!", 4),
                 ("Б", "Просто отмечаю, как сегодня выгляжу.", 3),
                 ("В", "Сразу начинаю искать недостатки: прическу, осанку, лишний вес.", 2),
                 ("Г", "Стараюсь не смотреть, чтобы лишний раз не расстраиваться.", 1)]
    },
    {
        "text": "14. В конфликте с мамой (или значимой фигурой из детства) вы:",
        "opts": [("А", "Спокойно отстаиваю свои границы, оставаясь в контакте.", 4),
                 ("Б", "Стараюсь договориться, но если нет, принимаю ситуацию.", 3),
                 ("В", "Проглатываю обиду, чтобы не расстраивать маму, но внутри всё кипит.", 2),
                 ("Г", "Срываюсь на крик или ухожу в глубокую обиду, чувствуя себя маленькой и непонятой.", 1)]
    },
    {
        "text": "15. В глубине души вы верите, что:",
        "opts": [("А", "Мир безопасен, и я справлюсь с любыми трудностями.", 4),
                 ("Б", "Я достойна любви и уважения просто за то, что я живу.", 3),
                 ("В", "Меня можно полюбить только если я буду соответствовать чьим-то ожиданиям.", 2),
                 ("Г", "В любой момент всё может рухнуть, и я останусь одна.", 1)]
    }
]


# --- FSM Состояния ---
class Questionnaire(StatesGroup):
    answering = State()


class AdminStates(StatesGroup):
    waiting_for_link_name = State()


# --- Инициализация БД ---
async def init_db():
    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute("""
                         CREATE TABLE IF NOT EXISTS stats
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             user_id
                             INTEGER,
                             username
                             TEXT,
                             source
                             TEXT,
                             score
                             INTEGER,
                             clicked_signup
                             BOOLEAN
                             DEFAULT
                             0
                         )
                         """)
        await db.commit()


# --- Клавиатуры ---
def get_admin_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Создать ссылку", callback_data="admin_createlink")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📝 Протестировать анкету", callback_data="start_questionnaire")]
    ])


def get_question_kb(q_index: int):
    buttons = []
    for label, _, points in QUESTIONS[q_index]["opts"]:
        buttons.append(InlineKeyboardButton(text=label, callback_data=f"ans_{points}"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


# Передаем тип действия: intensive или diagnostic
def get_signup_kb(action_type: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Записаться", callback_data=f"track_{action_type}")]
    ])


def get_real_url_kb(action_type: str):
    url = URL_INTENSIVE if action_type == "intensive" else URL_DIAGNOSTIC
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Перейти в личные сообщения", url=url)]
    ])


# --- Логика Администратора ---
@router.message(CommandStart(), F.from_user.id == ADMIN_ID)
async def admin_start(message: Message, command: CommandStart, state: FSMContext):
    await state.clear()
    await message.answer("Добро пожаловать в панель администратора!", reply_markup=get_admin_kb())


@router.callback_query(F.data == "admin_createlink", F.from_user.id == ADMIN_ID)
async def admin_create_link_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите название для ссылки (латиница, цифры, _, например: inst_1):")
    await state.set_state(AdminStates.waiting_for_link_name)
    await callback.answer()


@router.message(AdminStates.waiting_for_link_name, F.from_user.id == ADMIN_ID)
async def admin_generate_link(message: Message, state: FSMContext):
    link_name = message.text.strip().replace(" ", "_")
    link = await create_start_link(bot, link_name, encode=False)
    await message.answer(f"✅ Ссылка успешно создана:\n`{link}`", parse_mode="Markdown", reply_markup=get_admin_kb())
    await state.clear()


@router.callback_query(F.data == "admin_stats", F.from_user.id == ADMIN_ID)
async def admin_stats(callback: CallbackQuery):
    async with aiosqlite.connect("bot_database.db") as db:
        async with db.execute("SELECT source, COUNT(*) FROM stats GROUP BY source") as cursor:
            sources = await cursor.fetchall()
        async with db.execute("SELECT COUNT(*) FROM stats WHERE clicked_signup = 1") as cursor:
            clicks = await cursor.fetchone()
        async with db.execute("""
                              SELECT SUM(CASE WHEN score >= 50 THEN 1 ELSE 0 END),
                                     SUM(CASE WHEN score BETWEEN 36 AND 49 THEN 1 ELSE 0 END),
                                     SUM(CASE WHEN score BETWEEN 22 AND 35 THEN 1 ELSE 0 END),
                                     SUM(CASE WHEN score <= 21 THEN 1 ELSE 0 END)
                              FROM stats
                              WHERE score IS NOT NULL
                              """) as cursor:
            scores = await cursor.fetchone()

    stats_text = "📊 **Статистика:**\n\n**Переходы по ссылкам:**\n"
    for src, count in sources:
        stats_text += f"— {src if src else 'organic'}: {count}\n"

    stats_text += f"\n**Нажали 'Записаться':** {clicks[0]}\n"
    stats_text += f"\n**По категориям:**\n— 50-60 баллов: {scores[0] or 0}\n— 36-49 баллов: {scores[1] or 0}\n— 22-35 баллов: {scores[2] or 0}\n— 15-21 балл: {scores[3] or 0}"

    await callback.message.edit_text(stats_text, parse_mode="Markdown", reply_markup=get_admin_kb())
    await callback.answer()


# --- Пользовательская логика ---
@router.message(CommandStart())
async def user_start(message: Message, command: CommandStart, state: FSMContext):
    args = command.args or "organic"
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

    if message.from_user.id != ADMIN_ID:
        await bot.send_message(ADMIN_ID, f"🔔 Новый старт: {username} ({message.from_user.id}) | Источник: {args}")

    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute("INSERT INTO stats (user_id, username, source) VALUES (?, ?, ?)",
                         (message.from_user.id, username, args))
        await db.commit()

    await start_questionnaire_process(message, state, args)


@router.callback_query(F.data == "start_questionnaire")
async def admin_test_questionnaire(callback: CallbackQuery, state: FSMContext):
    await start_questionnaire_process(callback.message, state, "admin_test", is_callback=True)
    await callback.answer()


async def start_questionnaire_process(message_obj: Message, state: FSMContext, source: str, is_callback=False):
    await state.update_data(score=0, q_index=0, db_source=source)
    await state.set_state(Questionnaire.answering)
    await send_question(message_obj, 0, is_callback)


async def send_question(message_obj: Message, q_index: int, is_callback=False):
    q_data = QUESTIONS[q_index]

    text = f"**{q_data['text']}**\n\n"
    for label, opt_text, _ in q_data["opts"]:
        text += f"{label}) {opt_text}\n"

    kb = get_question_kb(q_index)

    if is_callback:
        await message_obj.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    else:
        await message_obj.answer(text, reply_markup=kb, parse_mode="Markdown")


# --- Обработка ответов ---
@router.callback_query(Questionnaire.answering, F.data.startswith("ans_"))
async def handle_answer(callback: CallbackQuery, state: FSMContext):
    points = int(callback.data.split("_")[1])
    data = await state.get_data()

    new_score = data['score'] + points
    next_index = data['q_index'] + 1

    await state.update_data(score=new_score, q_index=next_index)

    if next_index < len(QUESTIONS):
        await send_question(callback.message, next_index, is_callback=True)
    else:
        # Маршрутизация результатов и кнопок
        if 50 <= new_score <= 60:
            result_text = RESULT_50_60
            action_type = "intensive"
        elif 36 <= new_score <= 49:
            result_text = RESULT_36_49
            action_type = "diagnostic"
        elif 22 <= new_score <= 35:
            result_text = RESULT_22_35
            action_type = "diagnostic"
        else:
            result_text = RESULT_15_21
            action_type = "diagnostic"

        if data['db_source'] != "admin_test":
            async with aiosqlite.connect("bot_database.db") as db:
                await db.execute(
                    "UPDATE stats SET score = ? WHERE user_id = ? AND id = (SELECT MAX(id) FROM stats WHERE user_id = ?)",
                    (new_score, callback.from_user.id, callback.from_user.id))
                await db.commit()

            username = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.first_name
            await bot.send_message(ADMIN_ID, f"✅ Анкета пройдена: {username}\nБаллы: {new_score}")

        await callback.message.edit_text(result_text, reply_markup=get_signup_kb(action_type), parse_mode="Markdown")
        await state.clear()


# Перехватываем тип действия из callback_data (track_intensive или track_diagnostic)
@router.callback_query(F.data.startswith("track_"))
async def track_signup(callback: CallbackQuery):
    action_type = callback.data.split("_")[1]

    async with aiosqlite.connect("bot_database.db") as db:
        await db.execute(
            "UPDATE stats SET clicked_signup = 1 WHERE user_id = ? AND id = (SELECT MAX(id) FROM stats WHERE user_id = ?)",
            (callback.from_user.id, callback.from_user.id))
        await db.commit()

    # Меняем кнопку на реальный URL
    await callback.message.edit_reply_markup(reply_markup=get_real_url_kb(action_type))
    await callback.answer("Нажмите на кнопку ниже для перехода в личные сообщения!", show_alert=True)


# --- Запуск ---
async def main():
    await init_db()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())