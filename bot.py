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

MAIN_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton("Каталог", url=VK_GROUP_URL)],
    [InlineKeyboardButton("Оплата", callback_data='payment')],
    [InlineKeyboardButton("Определить размер", callback_data='measure')],
    [InlineKeyboardButton("Информация", callback_data='info')],
    [InlineKeyboardButton("Хочу в клуб", callback_data='join_club')],
])

INFO_MARKUP = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("О нас", callback_data='about'),
        InlineKeyboardButton("Доставка", callback_data='delivery'),
    ],
    [
        InlineKeyboardButton("Возврат", callback_data='returns'),
        InlineKeyboardButton("Вопросы", callback_data='faq'),
    ],
    [InlineKeyboardButton("Назад", callback_data='back')],
])

JOIN_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton("Наши тренеры", callback_data='get_coach')],
    [InlineKeyboardButton("Заполнить анкету", callback_data='fill_the_form')],
    [InlineKeyboardButton("Назад", callback_data='back')],
])

PAYMENT_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton("СБП (по QR-коду)", callback_data='sbp')],
    [InlineKeyboardButton("Наличными", callback_data='cash')],
    [InlineKeyboardButton("Переводом", callback_data='phone')],
    [InlineKeyboardButton("Назад", callback_data='back')],
])

SBP_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton("ВТБ", callback_data='vtb')],
    [InlineKeyboardButton("СБЕР", callback_data='sber')],
    [InlineKeyboardButton("Т-Банк", callback_data='tbank')],
    [InlineKeyboardButton("Назад", callback_data='payment')],
])

AFTER_SBP_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton("Выбрать другой банк", callback_data='sbp')],
    [InlineKeyboardButton("Выбрать другой способ оплаты", callback_data='payment')],
])

AFTER_PAYMENT_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton("Выбрать другой способ оплаты", callback_data='payment')],
])


MEASURE_IMAGE_PATHS = [
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

PAYMENT_IMAGES = {
    'vtb':   ('./images/vtb.png',    AFTER_SBP_MARKUP),
    'sber':  ('./images/sber.png',   AFTER_SBP_MARKUP),
    'tbank': ('./images/tbank.png',  AFTER_SBP_MARKUP),
    'cash':  ('./images/cash.png',   AFTER_PAYMENT_MARKUP),
    'phone': ('./images/phone.jpeg', AFTER_PAYMENT_MARKUP),
}

COACH_IMAGE = './images/coach.jpeg'


ABOUT_TEXT = (
    'Вас приветствует команда интернет-магазина «Atlas Store»!\n\n'
    'Мы импортируем оригинальные товары из Европы, Азии и США.\n\n'
    'Шиповки и кроссовки, а также спортивная одежда для легкой атлетики по самым низким ценам в России!\n\n'
    'Работаем с организациями по договору.\n\n'
    'В случае брака или подделки мы вернём вам деньги. Возврат допускается только в этих двух случаях '
    'в течение 14 дней с момента получения вами товара при условии сохранения товарного вида. '
    'В отдельных случаях допускается возврат в течение 30 дней с момента получения вами товара.\n\n'
    'Наши сотрудники всегда готовы ответить на все ваши вопросы и помочь вам подобрать нужный товар.\n\n'
    'ИП: Агапов Дмитрий Евгеньевич\n\nИНН: 781425071169'
)

DELIVERY_TEXT = (
    'Срок доставки до нашего основного склада в СПб (21-24 дня)\n\n'
    'Срок доставки по РФ🇷🇺:\n\n'
    '🚛CDEK (2-8 дней)\n\n'
    '🚚 Почта России (3-10 дней)'
)

RETURNS_TEXT = (
    r'☑️ Возврат в течение 14 дней с момента получения вами товара\! В отдельных случаях 30 дней\! '
    r'Возврат допускается только в случае брака или подделки\!\n\n'
    r'☑️ Весь товар проходит через проверку на оригинальность и подтверждается '
    r'[видеофиксацией](https://vk.com/album-227326583_308474149)\!\n\n'
    r'☑️ По всем остальным вопросам обращайтесь к @dm\_agapov или @FedyaLuchkin'
)

JOIN_CLUB_TEXT = (
    'Привет! Рады, что ты хочешь тренироваться в ATLAS!\n\n'
    'Заполни нашу анкету. Это займет не более 5 минут.\n'
    'Вся работа ведется на платформе Microsoft Excel.\n'
    'Для начала максимально честно и развернуто заполни анкету.\n'
    'Это необходимо для хорошего результата. А также очень важно, чтобы ты выполнял(а) тренировки, '
    'соблюдая их количество, объём и самое главное интенсивность (в первую очередь, не завышая!)\n'
    'Мы же, в свою очередь, всегда ответим на все срочные, смешные, важные, глупые, насущные и вообще '
    'любые вопросы! Кстати, вот тебе первое правило:\n'
    'Если вопрос кажется глупым, задавай его в первую очередь!\n\n'
    'Стоимость услуг:\n'
    ' - 9000 рублей онлайн формат работы на месяц\n'
    ' - 2500 рублей офлайн индивидуальное занятие\n'
    ' - 1000 рублей онлайн консультация\n\n'
    'Всё понятно и всё устраивает?\n'
    'Отлично, погнали к вопросам!'
)

FORM_QUESTIONS = [
    "Пожалуйста представься (Фамилия и Имя):",
    "Телефон для СВЯЗИ:",
    "Контактный email:\n(Если есть аккаунт на Final Surge, оставь email с которого регистрировался)",
    "Укажи пожалуйста возраст / рост / вес:",
    "В каком городе ты живешь?",
    "Имеется ли опыт занятий бегом или другими видами спорта?\n(Чем? Сколько лет, месяцев?\n"
    "Самостоятельно или с тренером?)\n(ФИО предыдущего тренера и причина ухода (по желанию))",
    "Расскажи о своих личных рекордах и достижениях в беговых дисциплинах\n"
    "(Укажите официальные личные рекорды и тренировочные результаты)",
    "Основные цели и старты:\n(Укажите какие у вас спортивные цели / ожидания и есть ли запланированные старты)",
    "Оцени свою нынешнюю форму по 10 - бальной шкале:",
    "Ссылка на Strava или любое друго приложение для тренировок:",
]

FORM_STATE_KEY = "form_state"
FORM_ANSWERS_KEY = "form_answers"
FORM_ACTIVE_KEY = "form_active"


def _show_info_section(query, text, parse_mode=None):
    """Заменяет текущее сообщение и отправляет меню инфо-раздела."""
    kwargs = {'parse_mode': parse_mode, 'disable_web_page_preview': True} if parse_mode else {}
    query.edit_message_text(text, **kwargs)
    query.message.reply_text('Выберите раздел информации:', reply_markup=INFO_MARKUP)


def start(update: Update, context: CallbackContext) -> None:
    if update.callback_query:
        update.callback_query.answer()
        chat_id = update.callback_query.message.chat.id
    else:
        chat_id = update.message.chat.id
    context.bot.send_message(chat_id=chat_id, text='Добро пожаловать в Atlas Store!', reply_markup=MAIN_MARKUP)


def info(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    query.edit_message_text('Выберите раздел информации:', reply_markup=INFO_MARKUP)


def about(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    _show_info_section(query, ABOUT_TEXT)


def delivery(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    _show_info_section(query, DELIVERY_TEXT)


def returns(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    _show_info_section(query, RETURNS_TEXT, parse_mode='MarkdownV2')


def faq(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    _show_info_section(query, 'По всем вопросам обращайтесь @dm_agapov')


def payment(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    query.edit_message_text('Выберите способ оплаты:', reply_markup=PAYMENT_MARKUP)


def sbp(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    query.edit_message_text('Выберите банк:', reply_markup=SBP_MARKUP)


def get_payment_image(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    image_path, reply_markup = PAYMENT_IMAGES[query.data]
    try:
        with open(image_path, 'rb') as f:
            query.message.reply_photo(photo=f)
    except Exception as e:
        logger.exception("Не удалось открыть файл изображения: %s", e)

    query.message.reply_text('К другим способам оплаты:', reply_markup=reply_markup)


def measure(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    for image_path in MEASURE_IMAGE_PATHS:
        try:
            with open(image_path, 'rb') as f:
                query.message.reply_photo(photo=InputFile(f))
            time.sleep(0.5)
        except Exception as e:
            logger.exception("Не удалось отправить изображение %s: %s", image_path, e)

    query.message.reply_text('Выберите раздел информации:', reply_markup=MAIN_MARKUP)

def get_coach(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    try:
        with open(COACH_IMAGE, 'rb') as f:
            query.message.reply_photo(photo=InputFile(f))
    except Exception as e:
        logger.exception("Не удалось открыть файл тренера: %s", e)

    query.message.reply_text('Выберите следующий шаг:', reply_markup=InlineKeyboardMarkup([
    [InlineKeyboardButton("Заполнить анкету", callback_data='fill_the_form')],
    [InlineKeyboardButton("Назад", callback_data='back')],
]))


def join_club(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    query.message.reply_text(JOIN_CLUB_TEXT, reply_markup=JOIN_MARKUP)


def fill_the_form(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    context.user_data[FORM_STATE_KEY] = 0
    context.user_data[FORM_ANSWERS_KEY] = []
    context.user_data[FORM_ACTIVE_KEY] = True

    query.edit_message_text(
        "Начинаем анкету. Пожалуйста, отвечайте текстом на каждый вопрос.\n\n"
        "Чтобы прервать заполнение, напишите: стоп"
    )
    context.bot.send_message(chat_id=query.message.chat.id, text=FORM_QUESTIONS[0])


def handle_form_answer(update: Update, context: CallbackContext) -> None:
    if not context.user_data.get(FORM_ACTIVE_KEY):
        return

    text = (update.message.text or "").strip()

    if text.lower() in ("стоп", "stop", "/stop"):
        context.user_data.clear()
        update.message.reply_text(
            "Анкетирование прервано. Если захотите продолжить — нажмите «Хочу в клуб: заполнить анкету».",
            reply_markup=MAIN_MARKUP,
        )
        return

    answers = context.user_data[FORM_ANSWERS_KEY]
    answers.append(text)

    idx = context.user_data[FORM_STATE_KEY] + 1
    context.user_data[FORM_STATE_KEY] = idx

    if idx < len(FORM_QUESTIONS):
        update.message.reply_text(FORM_QUESTIONS[idx])
        return

    context.user_data.clear()

    final_msg = "Новая анкета:\n\n" + "\n\n".join(
        f"{q}\n{a}" for q, a in zip(FORM_QUESTIONS, answers)
    )
    try:
        if ADMIN_ID:
            context.bot.send_message(chat_id=ADMIN_ID, text=final_msg)
        else:
            update.message.reply_text("Внимание: ADMIN_ID не задан. Сообщение админу не отправлено.")
    except Exception as e:
        logger.exception("Ошибка при отправке анкеты админу: %s", e)
        update.message.reply_text("Произошла ошибка при отправке анкеты.")

    update.message.reply_text(
        "Спасибо! Анкета отправлена. Мы свяжемся с вами в ближайшее время.",
        reply_markup=MAIN_MARKUP,
    )


def back(update: Update, context: CallbackContext) -> None:
    start(update, context)


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не задан. Проверьте .env")

    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(info,             pattern='^info$'))
    dp.add_handler(CallbackQueryHandler(about,            pattern='^about$'))
    dp.add_handler(CallbackQueryHandler(delivery,         pattern='^delivery$'))
    dp.add_handler(CallbackQueryHandler(returns,          pattern='^returns$'))
    dp.add_handler(CallbackQueryHandler(faq,              pattern='^faq$'))
    dp.add_handler(CallbackQueryHandler(payment,          pattern='^payment$'))
    dp.add_handler(CallbackQueryHandler(sbp,              pattern='^sbp$'))
    dp.add_handler(CallbackQueryHandler(get_payment_image, pattern='^(vtb|sber|tbank|cash|phone)$'))
    dp.add_handler(CallbackQueryHandler(measure,          pattern='^measure$'))
    dp.add_handler(CallbackQueryHandler(get_coach,          pattern='^get_coach$'))
    dp.add_handler(CallbackQueryHandler(join_club,        pattern='^join_club$'))
    dp.add_handler(CallbackQueryHandler(fill_the_form,    pattern='^fill_the_form$'))
    dp.add_handler(CallbackQueryHandler(back,             pattern='^back$'))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_form_answer))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
