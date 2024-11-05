from datetime import datetime, time

import telebot
from telebot import types

from DataService import DataService
from YaContestService import YaContestService
from LoggerService import LoggerService


class TelegramService:
    def __init__(self, bot_token: str,
                 db_service: DataService,
                 contest_service: YaContestService,
                 logger: LoggerService,
                 num_of_daily_attempts: int = 5):
        self.__bot_token = bot_token
        self.__tg_bot = telebot.TeleBot(token=self.__bot_token)

        self.__db_service = db_service
        self.__contest_service = contest_service
        self.__logger = logger

        self.__num_of_daily_attempts = num_of_daily_attempts

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("/help")
        btn2 = types.KeyboardButton("/get_test")
        btn3 = types.KeyboardButton("/count_free_attempts")
        markup.add(btn1, btn2, btn3)

        @self.__tg_bot.message_handler(commands=['start'])
        def reply_start_message(message: telebot.types.Message):
            self.__logger.log(str(message.from_user.id),
                             self.__get_name_message(message),
                              datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S'),
                              "ok",
                              "started dialogue with bot with command / start")
            self.__tg_bot.reply_to(message, self.__get_greetings_message(message.from_user.first_name),
                                   reply_markup=markup)

        @self.__tg_bot.message_handler(commands=['help'])
        def reply_help_message(message: telebot.types.Message):
            self.__logger.log(str(message.from_user.id),
                              self.__get_name_message(message),
                              datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S'),
                              "ok",
                              "sent command /help")
            self.__tg_bot.reply_to(message, self.__get_help_message(), reply_markup=markup)

        @self.__tg_bot.message_handler(commands=['count_free_attempts'])
        def reply_free_attempts_message(message: telebot.types.Message):
            tg_id = str(message.from_user.id)
            total_attempts_today = self.__db_service.count_user_responses(tg_id,
                                                                          datetime.combine(datetime.now(), time.min),
                                                                          datetime.combine(datetime.now(), time.max))

            self.__logger.log(str(message.from_user.id),
                              self.__get_name_message(message),
                              datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S'),
                              "ok",
                              f"sent message /count_free_attempts. Bot answered: {self.__num_of_daily_attempts - total_attempts_today}   (user has now {total_attempts_today} attempts)")

            self.__tg_bot.reply_to(message, self.__get_free_attempts_message(
                self.__num_of_daily_attempts - total_attempts_today), reply_markup=markup)

        @self.__tg_bot.message_handler(commands=['get_test'])
        def reply_get_test_message(message: telebot.types.Message):
            self.__logger.log(str(message.from_user.id),
                              self.__get_name_message(message),
                              datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S'),
                              "ok",
                              f"sent command /get_test")

            self.__tg_bot.reply_to(message,
                                   "Введите данные в следующем формате:\nIDКонтеста IDПосылки НомерТеста\nДля получения справки нажмите /help")
            self.__tg_bot.register_next_step_handler(message, inner_get_test_message)

        def inner_get_test_message(message: telebot.types.Message):
            splitted_message = message.text.split()
            self.__logger.log(str(message.from_user.id),
                              self.__get_name_message(message),
                              datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S'),
                              "info",
                              f" tried to get input data. user's input: {message.text}")
            if len(splitted_message) != 3:
                self.__logger.log(str(message.from_user.id),
                                  self.__get_name_message(message),
                                  datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S'),
                                  "wrong data",
                                  f"inputted wrong data (got {len(splitted_message)} tags, need = 3)")

                self.__tg_bot.reply_to(message, "Неправильный ввод :( повторите еще раз.", reply_markup=markup)
            else:
                tg_id = str(message.from_user.id)
                count_already = self.__db_service.count_user_responses(tg_id,
                                                                       datetime.combine(datetime.now(), time.min),
                                                                       datetime.combine(datetime.now(), time.max))
                if count_already >= self.__num_of_daily_attempts:
                    self.__logger.log(str(message.from_user.id),
                                      self.__get_name_message(message),
                                      datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S'),
                                      "no attempts",
                                      f"has no attempts to got input data")

                    self.__tg_bot.reply_to(message, "У тебя закончились попытки. Возвращайся позже",
                                           reply_markup=markup)
                else:
                    try:
                        data = self.__contest_service.get_input_file(*splitted_message)

                        self.__db_service.insert_new_response(tg_id, datetime.now(), *splitted_message)

                        self.__logger.log(str(message.from_user.id),
                                          self.__get_name_message(message),
                                          datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S'),
                                          "ok",
                                          f"got his input data for test {splitted_message[2]} in contest {splitted_message[0]}, attempt = {splitted_message[1]}")

                        self.__tg_bot.reply_to(message,
                                               f"Входные данные к тесту {splitted_message[2]} в контесте № {splitted_message[0]}:\n\n{data}")
                    except Exception as e:
                        self.__tg_bot.reply_to(message, f"Произошла ошибка: {e}")

        @self.__tg_bot.message_handler(content_types=['text'])
        def default_handler(message: telebot.types.Message):
            inner_get_test_message(message)

    def start(self):
        self.__tg_bot.polling(non_stop=True, interval=1)

    def __get_greetings_message(self, user_name: str):
        return f"""
        {user_name}, привет!
        Данный бот предназначен для получения входных данных какого-либо теста из задачи в системе Яндекс.Контест. 
        
        Опишу некоторые правила пользования:
        1. У тебя будет всего {self.__num_of_daily_attempts} запросов в день. По истечению лимита необходимо будет подождать следующего дня, тогда тебе снова будут доступны {self.__num_of_daily_attempts} попыток.
        2. Для получения входных данных тебе необходимо будет отправить боту сообщение следующего вида:
        IDКонтеста IDПосылки НомерТеста
        
        Обращаю внимание на то, что для получения данных тебе необходимо иметь хотя бы одну посылку по данной задаче в данном соревновании. Статус посылки не важен (WA, RE, PE, OK и т.д.)
        
        Для более детальной информации отправь команду /help
        """

    def __get_help_message(self):
        return f"""
        Правила использования бота:
        1. У тебя будет всего {self.__num_of_daily_attempts} запросов в день. По истечению лимита необходимо будет подождать следующего дня, тогда тебе снова будут доступны {self.__num_of_daily_attempts} попыток.
        2. Для получения входных данных тебе необходимо будет отправить боту сообщение следующего вида:
        IDКонтеста IDПосылки НомерТеста

        Обращаю внимание на то, что для получения данных тебе необходимо иметь хотя бы одну посылку по данной задаче в данном соревновании. Статус посылки не важен (WA, RE, PE, OK и т.д.)

        Давай приведем пример использования. Допустим, тебе необходимо узнать входные данные к тесту 3 в посылке 12345 в контесте 78903. Тогда тебе необходимо отослать боту следующее сообщение:
        ```
        78903 12345 3
        ```
        
        Для получения оставшегося количества попыток отправь команду /count_free_attempts
        """

    def __get_free_attempts_message(self, free_attempts):
        return f"""
        У Вас осталось {free_attempts} попыток на сегодня. Всего в день доступно {self.__num_of_daily_attempts} попыток.
        """

    @staticmethod
    def __get_name_message(message):
        name = ''
        if message.from_user.first_name is not None:
            name += str(message.from_user.first_name)
        if message.from_user.last_name is not None:
            name += str(message.from_user.last_name)
        if len(name) > 0:
            return name
        return 'Unknown user'


    @staticmethod
    def __get_log_header(message: telebot.types.Message):
        return f"(tg_id = {message.from_user.id}, {message.from_user.first_name} {message.from_user.last_name}, {datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')}) => "
