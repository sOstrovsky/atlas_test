import logging, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

VK_GROUP_URL = "https://vk.com/market-227326583?screen=group"
TOKEN = '8485397631:AAG6d4vshtusF4qhs5t0B8NVJPifVLiWoYk'

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

keyboard = [
    [InlineKeyboardButton("Каталог", url=VK_GROUP_URL)],
    [InlineKeyboardButton("Оплата", callback_data='payment')],
    [InlineKeyboardButton("Определить размер", callback_data='measure')],
    [InlineKeyboardButton("Информация", callback_data='info')]
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

def start(update: Update, context: CallbackContext) -> None:
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        update.message.reply_text('Добро пожаловать в Atlas Store!', reply_markup=reply_markup)
    elif update.callback_query:
        context.bot.send_message(chat_id=update.callback_query.message.chat.id, 
                                 text='Добро пожаловать в Atlas Store!', 
                                 reply_markup=reply_markup)

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

    back_buttons = [[InlineKeyboardButton("Выбрать другой банк", callback_data='sbp')], [InlineKeyboardButton("Выбрать другой способ оплаты", callback_data='payment')]]

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
    
    query.message.reply_photo(photo=photo)
    reply_markup = InlineKeyboardMarkup(back_buttons)
    
    query.message.reply_text('К другим способам оплаты:', reply_markup=reply_markup)

 

def about(update: Update, context: CallbackContext):
    query = update.callback_query
    if query:
        query.answer()
        query.edit_message_text('Вас приветствует команда интернет-магазина «Atlas Store»!\n\nМы импортируем оригинальные товары из Европы, Азии и США.\n\nШиповки и кроссовки, а также спортивная одежда для легкой атлетики по самым низким ценам в России!\n\nРаботаем с организациями по договору.\n\nВ случае брака или подделки мы вернём вам деньги. Возврат допускается только в этих двух случаях в течение 14 дней с момента получения вами товара при условии сохранения товарного вида. В отдельных случаях допускается возврат в течение 30 дней с момента получения вами товара.\n\nНаши сотрудники всегда готовы ответить на все ваши вопросы и помочь вам подобрать нужный товар.\n\nИП: Агапов Дмитрий Евгеньевич\n\nИНН: 781425071169')
        
        keyboard = secondary_keyboard
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text('Выберите раздел информации:', reply_markup=reply_markup)

def delivery(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query:
        query.answer()
        query.edit_message_text('Срок доставки до нашего основного склада в СПб (21-24 дня)\n\nСрок доставки по РФ🇷🇺:\n\n🚛CDEK (2-8 дней)\n\n🚚 Почта России (3-10 дней)')

        keyboard = secondary_keyboard
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text('Выберите раздел информации:', reply_markup=reply_markup)

def returns(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query:
        query.answer()
        query.edit_message_text(
            '☑️ Возврат в течение 14 дней с момента получения вами товара\! В отдельных случаях 30 дней\! Возврат допускается только в случае брака или подделки\!\n\n☑️ Весь товар проходит через проверку на оригинальность и подтверждается [видеофиксацией](https://vk.com/album-227326583_308474149)\!\n\n☑️ По всем остальным вопросам обращайтесь к @dm\_agapov или @FedyaLuchkin',
            parse_mode='MarkdownV2',
            disable_web_page_preview=True
        )
        keyboard = secondary_keyboard
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text('Выберите раздел информации:', reply_markup=reply_markup)

def faq(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query:
        query.answer()
        query.edit_message_text('По всем вопросам обращайтесь @dm_agapov')

        keyboard = secondary_keyboard
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text('Выберите раздел информации:', reply_markup=reply_markup)


def back(update: Update, context: CallbackContext) -> None:
    start(update, context)


def measure(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    if query.data == 'measure':
        for image_path in image_paths:
            with open(image_path, 'rb') as image_file:
                query.message.reply_photo(photo=InputFile(image_file))
                time.sleep(0.5)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text('Выберите раздел информации:', reply_markup=reply_markup)

def main():
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(info, pattern='info'))
    dp.add_handler(CallbackQueryHandler(measure, pattern='measure'))
    dp.add_handler(CallbackQueryHandler(payment, pattern='payment'))
    dp.add_handler(CallbackQueryHandler(sbp, pattern='sbp'))
    dp.add_handler(CallbackQueryHandler(get_sbp_qr, pattern='vtb|sber|tbank|cash|phone'))
    dp.add_handler(CallbackQueryHandler(about, pattern='about'))
    dp.add_handler(CallbackQueryHandler(delivery, pattern='delivery'))
    dp.add_handler(CallbackQueryHandler(returns, pattern='returns'))
    dp.add_handler(CallbackQueryHandler(faq, pattern='faq'))
    dp.add_handler(CallbackQueryHandler(back, pattern='back'))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()