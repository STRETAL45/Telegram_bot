import telebot
import sqlite3
from telebot import types

bot = telebot.TeleBot('7081305312:AAGx0HTcYPTBBezWTp3O1Q6SoWYoFa5Gvuc')
name = None
age = None
place = None
adress = None
kategor = None
num = None
city = None
otzv_obj =None


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "Привет, если ты запустил это приложение, то значит тебе нужна помощь по поиску подходящего места для досуга. В этом я точно смогу тебе помочь! Регистрируйся и вперед! ")
    bot.send_message(message.chat.id, "Как я могу к тебе обращаться?")
    bot.register_next_step_handler(message, user_name)


def user_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, f"{name}, добро пожаловать! Введите свой возраст.")
    bot.register_next_step_handler(message, user_age)


def user_age(message):
    global age
    age = message.text.strip()
    bot.send_message(message.chat.id, f"Cпасибо! Осталось лишь ввести нужный вам город.")
    bot.register_next_step_handler(message, user_savedate)


def user_savedate(message):
    global city
    city = message.text.strip()
    conn = sqlite3.connect("db_tg.sql")

    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    c = 0
    for i in users:
        if name in i:
            if age in i:
                if city in i:
                    c += 1
    if c:
        bot.send_message(message.chat.id, "Такой пользователь уже есть в системe!")
    else:
        cur.execute(f"INSERT INTO users (name, age, city) VALUES ('%s', '%s', '%s')" % (name, age, city))
        conn.commit()
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("Список", callback_data='users'))
        bot.send_message(message.chat.id, "Теперь вы в системе!", reply_markup=markup)
    cur.close()
    conn.close()


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    conn = sqlite3.connect("db_tg.sql")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    info = ""
    for i in users:
        info += f"Имя: {i[1]}, Возраст: {i[2]}, Город: {i[3]}\n"
    cur.close()
    conn.close()
    bot.send_message(call.message.chat.id, info)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🏢 Добавить место")
    btn2 = types.KeyboardButton("📝 Оставить отзыв")
    btn3 = types.KeyboardButton("💎 ТОП мест")
    btn4 = types.KeyboardButton("❌ Удалить аккаунт")
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(call.message.chat.id,
                     text="Выберите нужную вам задачу.".format(
                         call.from_user), reply_markup=markup)


@bot.message_handler(content_types=['text'])
def func(message):
    global city
    if message.text == "🏢 Добавить место":
        bot.send_message(message.chat.id, text="Название места:")
        bot.register_next_step_handler(message, user_place)
    if message.text == "💎 ТОП мест":
        bot.send_message(message.chat.id, text="А вот и топ мест обязательных для посещений!")
        conn = sqlite3.connect('db_tg.sql')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM place WHERE city=? ORDER BY num DESC", (city,))
        rows = cursor.fetchall()
        for i in range(len(rows)):
            bot.send_message(message.chat.id, text=f"{i + 1} - Название: {rows[i][2]}, Адрес: {rows[i][3]}")
        conn.close()
    if message.text == "📝 Оставить отзыв":
        conn = sqlite3.connect("db_tg.sql")
        cur = conn.cursor()
        cur.execute("SELECT kategor FROM place WHERE city=?", (city,))
        users = cur.fetchall()
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, text="Чтобы выбрать нужную вам категорию, введите ее номер.")
        # на данный момент, чтобы код работал нужно вводить категорию целиком, а не ее номер
        for i in range(len(users)):
            bot.send_message(message.chat.id, text=f"{i + 1} - {users[i][0]}")
        bot.register_next_step_handler(message, otziv)


def otziv(message):
    num_kat = message.text.strip()
    print(num_kat)
    conn = sqlite3.connect("db_tg.sql")
    cur = conn.cursor()
    cur.execute("SELECT * FROM place WHERE city=? AND kategor=?", (city, num_kat,))
    place_kat = cur.fetchall()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, text="Чтобы выбрать нужное вам место, введите ее номер.")
    for i in range(len(place_kat)):
        bot.send_message(message.chat.id, text=f"{i + 1} - Название: {place_kat[i][2]}, Адрес: {place_kat[i][3]}")
    bot.register_next_step_handler(message, update_otzv)


def update_otzv(message):
    global otzv_obj
    place_otzv = message.text.strip()
    conn = sqlite3.connect("db_tg.sql")
    cur = conn.cursor()
    cur.execute("SELECT * FROM review WHERE user_review=?", (place_otzv,))
    otzv_obj = cur.fetchall()
    cur.close()
    conn.close()
    for i in range(len(otzv_obj)):
        bot.send_message(message.chat.id, text=f"{otzv_obj[i][2]}")
    bot.send_message(message.chat.id, text="Вы можете добавить и свой отзыв!")
    bot.register_next_step_handler(message, update_otzv2)


def update_otzv2(message):
    global otzv_obj
    text_otzv = message.text.strip()
    print(text_otzv)
    print(otzv_obj)
    conn = sqlite3.connect("db_tg.sql")
    cur = conn.cursor()
    cur.execute("INSERT INTO review(user_review, place_review) VALUES (?, ?)",
                (otzv_obj[0][1], text_otzv,))
    conn.commit()
    cur.close()
    conn.close()



def user_place(message):
    global place
    place = message.text
    bot.send_message(message.chat.id, "Какой адрес у места?")
    bot.register_next_step_handler(message, user_adress)


def user_adress(message):
    global adress
    adress = message.text.strip()
    bot.send_message(message.chat.id, "Какая категория?")
    bot.register_next_step_handler(message, user_kat)


def user_kat(message):
    global kategor
    kategor = message.text
    bot.send_message(message.chat.id, "Поставьте оценку!")
    bot.register_next_step_handler(message, user_num)


def user_num(message):
    global num
    num = message.text
    bot.send_message(message.chat.id, "Добавить картинку")
    bot.register_next_step_handler(message, handle_photo)


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    global city
    global place
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path
    downloaded_file = bot.download_file(file_info.file_path)
    with open(f'photos/{file_id}.jpg', 'wb') as new_file:
        new_file.write(downloaded_file)
    conn = sqlite3.connect("db_tg.sql")
    cur = conn.cursor()
    print(file_path)
    cur.execute("UPDATE place SET picture=? WHERE city=? AND name_place=?", (file_path, city, place))
    conn.commit()
    # Тут проблемы с картинками
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, "Изображение успешно добавлено!")
    bot.send_message(message.chat.id, "Спасибо, что добавили новое место!")
    conn = sqlite3.connect("db_tg.sql")
    cur = conn.cursor()
    cur.execute("SELECT picture FROM place WHERE city=? AND name_place=?", (city, place))
    row = cur.fetchone()
    conn.close()

    if row:
        photo_path = row[0]
        with open(f'photos/file_id_retrieved.jpg', 'wb') as retrieved_file:
            retrieved_file.write(bot.download_file(photo_path))
        bot.send_photo(message.chat.id, open(f'photos/file_id_retrieved.jpg', 'rb'))
    else:
        bot.send_message(message.chat.id, "Изображение не найдено.")

    conn = sqlite3.connect("db_tg.sql")
    cur = conn.cursor()
    cur.execute("INSERT INTO place(city, name_place, adress, kategor, num) VALUES (?, ?, ?, ?, ?)",
                (city, place, adress, kategor, num))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, f"Название: {place} "
                                      f"Адрес: {adress} "
                                      f"Категория: {kategor} "
                                      f"Оценка: {num}")


bot.polling(none_stop=True)
