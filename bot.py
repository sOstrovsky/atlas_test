import logging
import time
import os
import argparse
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    MessageHandler,
    Filters,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--env", default=".env")
args = parser.parse_args()

load_dotenv(dotenv_path=args.env)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
VK_GROUP_URL = os.getenv("VK_GROUP_URL", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Клавиатуры
keyboard = [
    [InlineKeyboardButton("Каталог", url=VK_GROUP_URL)],
    [InlineKeyboardButton("Оплата", callback_data='payment')],
    [InlineKeyboardButton("Определить размер", callback_data='measure')],
    [InlineKeyboardButton("Информация", callback_data='info')],
    [InlineKeyboardButton("Хочу в клуб: заполнить анкету", callback_data='join_club')]
]

secondary_keyboard = [
    [
        InlineKeyboardButton("О нас", callback_data='about'),
        InlineKeyboardButton("Доставка", callback_data='delivery')
    ],
    [
        InlineKeyboardButton("Возврат", callback_data='returns'),
        InlineKeyboardButton("Вопросы", callback_data='faq'),
    ],
    [InlineKeyboardButton("Назад", callback_data='back')]
]

# Исправлено: пропущенная запятая
join_keyboard = [
    [InlineKeyboardButton("Заполнить анкету", callback_data='fill_the_form')],
    [InlineKeyboardButton("Назад", callback_data='back')]
]

payment_root_keyboard = [
    [InlineKeyboardButton("СБП (по QR-коду)", callback_data='sbp')],
    [InlineKeyboardButton("Наличными", callback_data='cash')],
    [InlineKeyboardButton("Переводом", callback_data='phone')],
    [InlineKeyboardButton("Назад", callback_data='back')]
]

sbp_keyboard = [
    [InlineKeyboardButton("ВТБ", callback_data='vtb')],
    [InlineKeyboardButton("СБЕР", callback_data='sber')],
    [InlineKeyboardButton("Т-Банк", callback_data='tbank')],
    [InlineKeyboardButton("Назад", callback_data='payment')]
]

image_paths = [
    './images/measure.jpeg',
    './images/nike.jpeg',
    './images/adidas.jpeg',
    './images/anta.jpeg',
    './images/asics.jpeg',
    './images/bmai.jpeg',
    './images/brooks_2.jpeg',
    './images/hoka.jpeg',
    './images/lining.jpeg',
    './images/mizuno.jpeg',
    './images/nb.jpeg',
    './images/puma.jpeg',
    './images/reebok.jpeg',
    './images/salomon.jpeg',
    './images/saucony.jpeg',
    './images/ua.jpeg',
]

# Анкета
FORM_QUESTIONS = [
    "Пожалуйста представься (Фамилия и Имя):",
    "Телефон для СВЯЗИ:",
    "Контактный email:\n(Если есть аккаунт на Final Surge, оставь email с которого регистрировался)",
    "Укажи пожалуйста возраст / рост / вес:",
    "В каком городе ты живешь?",
    "Имеется ли опыт занятий бегом или другими видами спорта?\n(Чем? Сколько лет, месяцев?\nСамостоятельно или с тренером?)\n(ФИО предыдущего тренера и причина ухода (по желанию))",
    "Расскажи о своих личных рекордах и достижениях в беговых дисциплинах\n(Укажите официальные личные рекорды и тренировочные результаты)",
    "Основные цели и старты:\n(Укажите какие у вас спортивные цели / ожидания и есть ли запланированные старты)",
    "Оцени свою нынешнюю форму по 10 - бальной шкале:",
    "Ссылка на Strava или любое друго приложение для тренировок:"
]

FORM_STATE_KEY = "form_state"       # индекс текущего вопроса
FORM_ANSWERS_KEY = "form_answers"   # список ответов
FORM_ACTIVE_KEY = "form_active"     # флаг, что анкета активна


def start(update: Update, context: CallbackContext) -> None:
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        update.message.reply_text('Добро пожаловать в Atlas Store!', reply_markup=reply_markup)
    elif update.callback_query:
        context.bot.send_message(
            chat_id=update.callback_query.message.chat.id,
            text='Добро пожаловать в Atlas Store!',
            reply_markup=reply_markup
        )


def info(update: Update, context: CallbackContext) -> None:
    reply_markup = InlineKeyboardMarkup(secondary_keyboard)
    query = update.callback_query

    if query:
        query.answer()
        query.edit_message_text('Выберите раздел информации:', reply_markup=reply_markup)


def payment(update: Update, context: CallbackContext) -> None:
    reply_markup = InlineKeyboardMarkup(payment_root_keyboard)
    query = update.callback_query

    if query:
        query.answer()
        query.edit_message_text('Выберите способ оплаты:', reply_markup=reply_markup)


def sbp(update: Update, context: CallbackContext) -> None:
    reply_markup = InlineKeyboardMarkup(sbp_keyboard)
    query = update.callback_query

    if query:
        query.answer()
        query.edit_message_text('Выберите банк:', reply_markup=reply_markup)


def get_sbp_qr(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    back_buttons = [
        [InlineKeyboardButton("Выбрать другой банк", callback_data='sbp')],
        [InlineKeyboardButton("Выбрать другой способ оплаты", callback_data='payment')]
    ]

    photo = None
    try:
        if query.data == 'vtb':
            photo = open('./images/vtb.png', 'rb')
        elif query.data == 'sber':
            photo = open('./images/sber.png', 'rb')
        elif query.data == 'tbank':
            photo = open('./images/tbank.png', 'rb')
        elif query.data == 'cash':
            photo = open('./images/cash.png', 'rb')
            back_buttons = [[InlineKeyboardButton("Выбрать другой способ оплаты", callback_data='payment')]]
        elif query.data == 'phone':
            photo = open('./images/phone.jpeg', 'rb')
            back_buttons = [[InlineKeyboardButton("Выбрать другой способ оплаты", callback_data='payment')]]
    except Exception as e:
        logger.exception("Не удалось открыть файл изображения: %s", e)

    if photo:
        query.message.reply_photo(photo=photo)

    reply_markup = InlineKeyboardMarkup(back_buttons)
    query.message.reply_text('К другим способам оплаты:', reply_markup=reply_markup)


def about(update: Update, context: CallbackContext):
    query = update.callback_query
    if query:
        query.answer()
        query.edit_message_text(
            'Вас приветствует команда интернет-магазина «Atlas Store»!\n\n'
            'Мы импортируем оригинальные товары из Европы, Азии и США.\n\n'
            'Шиповки и кроссовки, а также спортивная одежда для легкой атлетики по самым низким ценам в России!\n\n'
            'Работаем с организациями по договору.\n\n'
            'В случае брака или подделки мы вернём вам деньги. Возврат допускается только в этих двух случаях '
            'в течение 14 дней с момента получения вами товара при условии сохранения товарного вида. В отдельных '
            'случаях допускается возврат в течение 30 дней с момента получения вами товара.\n\n'
            'Наши сотрудники всегда готовы ответить на все ваши вопросы и помочь вам подобрать нужный товар.\n\n'
            'ИП: Агапов Дмитрий Евгеньевич\n\nИНН: 781425071169'
        )

        kb = secondary_keyboard
        reply_markup = InlineKeyboardMarkup(kb)
        query.message.reply_text('Выберите раздел информации:', reply_markup=reply_markup)


def delivery(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query:
        query.answer()
        query.edit_message_text(
            'Срок доставки до нашего основного склада в СПб (21-24 дня)\n\n'
            'Срок доставки по РФ🇷🇺:\n\n'
            '🚛CDEK (2-8 дней)\n\n'
            '🚚 Почта России (3-10 дней)'
        )

        kb = secondary_keyboard
        reply_markup = InlineKeyboardMarkup(kb)
        query.message.reply_text('Выберите раздел информации:', reply_markup=reply_markup)


returns_message = r'☑️ Возврат в течение 14 дней с момента получения вами товара\! В отдельных случаях 30 дней\! Возврат допускается только в случае брака или подделки\!\n\n☑️ Весь товар проходит через проверку на оригинальность и подтверждается [видеофиксацией](https://vk.com/album-227326583_308474149)\!\n\n☑️ По всем остальным вопросам обращайтесь к @dm\_agapov или @FedyaLuchkin'


def returns(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query:
        query.answer()
        query.edit_message_text(
            returns_message,
            parse_mode='MarkdownV2',
            disable_web_page_preview=True
        )
        kb = secondary_keyboard
        reply_markup = InlineKeyboardMarkup(kb)
        query.message.reply_text('Выберите раздел информации:', reply_markup=reply_markup)


join_club_message = 'Привет! Рады, что ты хочешь тренироваться в ATLAS!\n\nЗаполни нашу анкету. Это займет не более 5 минут.\nВся работа ведется на платформе Microsoft Excel.\nДля начала максимально честно и развернуто заполни анкету.\nЭто необходимо для хорошего результата. А также очень важно, чтобы ты выполнял(а) тренировки, соблюдая их количество, объём и самое главное интенсивность (в первую очередь, не завышая!)\nМы же, в свою очередь, всегда ответим на все срочные, смешные, важные, глупые, насущные и вообще любые вопросы! Кстати, вот тебе первое правило:\nЕсли вопрос кажется глупым, задавай его в первую очередь!\n\nСтоимость услуг:\n - 9000 рублей онлайн формат работы на месяц\n - 2500 рублей офлайн индивидуальное занятие\n - 1000 рублей онлайн консультация\n\nВсё понятно и всё устраивает?\nОтлично, погнали к вопросам!'

def join_club(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query:
        query.answer()
        kb = join_keyboard
        reply_markup = InlineKeyboardMarkup(kb)
        query.message.reply_text(join_club_message, reply_markup=reply_markup)


def fill_the_form(update: Update, context: CallbackContext):
    query = update.callback_query
    if not query:
        return
    query.answer()

    # Инициализация состояния анкеты
    context.user_data[FORM_STATE_KEY] = 0
    context.user_data[FORM_ANSWERS_KEY] = []
    context.user_data[FORM_ACTIVE_KEY] = True

    intro = (
        "Начинаем анкету. Пожалуйста, отвечайте текстом на каждый вопрос.\n\n"
        "Чтобы прервать заполнение, напишите: стоп"
    )
    # Заменим сообщение с кнопкой на вводное
    query.edit_message_text(intro)
    # Отправим первый вопрос
    context.bot.send_message(chat_id=query.message.chat.id, text=FORM_QUESTIONS[0])


def handle_form_answer(update: Update, context: CallbackContext):
    # Обрабатываем только если анкета активна у пользователя
    if not context.user_data.get(FORM_ACTIVE_KEY):
        return

    text = (update.message.text or "").strip()

    # Возможность прерывания
    if text.lower() in ("стоп", "stop", "/stop"):
        context.user_data[FORM_ACTIVE_KEY] = False
        context.user_data.pop(FORM_STATE_KEY, None)
        context.user_data.pop(FORM_ANSWERS_KEY, None)
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Анкетирование прервано. Если захотите продолжить — нажмите «Хочу в клуб: заполнить анкету».", reply_markup=reply_markup)
        return

    # Сохраняем ответ
    answers = context.user_data.get(FORM_ANSWERS_KEY, [])
    answers.append(text)
    context.user_data[FORM_ANSWERS_KEY] = answers

    # Следующий вопрос
    idx = context.user_data.get(FORM_STATE_KEY, 0) + 1
    context.user_data[FORM_STATE_KEY] = idx

    if idx < len(FORM_QUESTIONS):
        update.message.reply_text(FORM_QUESTIONS[idx])
        return

    # Вопросы закончились — агрегируем и отправляем админу
    context.user_data[FORM_ACTIVE_KEY] = False

    parts = []
    for q, a in zip(FORM_QUESTIONS, answers):
        parts.append(f"{q}\n{a}")
    final_msg = "Новая анкета:\n\n" + "\n\n".join(parts)

    # Отправка админу
    try:
        if ADMIN_ID:
            context.bot.send_message(chat_id=ADMIN_ID, text=final_msg)
        else:
            update.message.reply_text("Внимание: ADMIN_ID не задан. Сообщение админу не отправлено.")
    except Exception as e:
        logger.exception("Ошибка при отправке анкеты админу: %s", e)
        update.message.reply_text("Произошла ошибка при отправке анкеты админу.")

    # Подтверждение пользователю + основное меню
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Спасибо! Анкета отправлена. Мы свяжемся с вами в ближайшее время.", reply_markup=reply_markup)

    # Очистка состояния
    context.user_data.pop(FORM_STATE_KEY, None)
    context.user_data.pop(FORM_ANSWERS_KEY, None)
    # Очистка состояния
    context.user_data.pop(FORM_STATE_KEY, None)
    context.user_data.pop(FORM_ANSWERS_KEY, None)


def faq(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query:
        query.answer()
        query.edit_message_text('По всем вопросам обращайтесь @dm_agapov')

        kb = secondary_keyboard
        reply_markup = InlineKeyboardMarkup(kb)
        query.message.reply_text('Выберите раздел информации:', reply_markup=reply_markup)


def back(update: Update, context: CallbackContext) -> None:
    start(update, context)


def measure(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'measure':
        for image_path in image_paths:
            try:
                with open(image_path, 'rb') as image_file:
                    query.message.reply_photo(photo=InputFile(image_file))
                time.sleep(0.5)
            except Exception as e:
                logger.exception("Не удалось отправить изображение %s: %s", image_path, e)

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text('Выберите раздел информации:', reply_markup=reply_markup)


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не задан. Проверьте .env")

    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(info, pattern='^info$'))
    dp.add_handler(CallbackQueryHandler(measure, pattern='^measure$'))
    dp.add_handler(CallbackQueryHandler(payment, pattern='^payment$'))
    dp.add_handler(CallbackQueryHandler(sbp, pattern='^sbp$'))
    dp.add_handler(CallbackQueryHandler(get_sbp_qr, pattern='^(vtb|sber|tbank|cash|phone)$'))
    dp.add_handler(CallbackQueryHandler(about, pattern='^about$'))
    dp.add_handler(CallbackQueryHandler(delivery, pattern='^delivery$'))
    dp.add_handler(CallbackQueryHandler(returns, pattern='^returns$'))
    dp.add_handler(CallbackQueryHandler(join_club, pattern='^join_club$'))
    dp.add_handler(CallbackQueryHandler(fill_the_form, pattern='^fill_the_form$'))
    dp.add_handler(CallbackQueryHandler(faq, pattern='^faq$'))
    dp.add_handler(CallbackQueryHandler(back, pattern='^back$'))

    # Обработчик текстовых ответов для анкеты
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_form_answer))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()