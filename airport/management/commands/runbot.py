import functools
import os

import telebot
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from airport.models import Ticket

bot = telebot.TeleBot(os.environ["TELEGRAM_BOT_TOKEN"])


def check_if_user_exist(func):
    @functools.wraps(func)
    def wrapper(message, *args, **kwargs):
        try:
            return func(message, *args, **kwargs)
        except get_user_model().DoesNotExist:
            bot.send_message(
                message.chat.id,
                "Before using this command "
                "you should connect your telegram account to airport profile",
            )

    return wrapper


def get_main_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_profile = telebot.types.KeyboardButton("👤 Profile")
    btn_tickets = telebot.types.KeyboardButton("🎫 Tickets")
    markup.add(btn_profile, btn_tickets)
    return markup


@bot.message_handler(commands=["start"])
def handle_start(message):
    parts = message.text.split()
    if len(parts) > 1:
        user = get_user_model().objects.get(telegram_token=parts[1])
        user.telegram_token = None

        if user.telegram_id is None:
            user.telegram_id = message.chat.id

        user.save()
        bot.send_message(
            message.chat.id,
            "Welcome to airport api system",
            reply_markup=get_main_keyboard(),
        )
    else:
        bot.send_message(
            message.chat.id,
            "To get access to bot you should authenticate and receive link in api/user/me/telegram-link/",
        )


@bot.message_handler(func=lambda message: message.text == "👤 Profile")
@check_if_user_exist
def handle_profile(message):
    user = get_user_model().objects.get(telegram_id=message.chat.id)
    bot.send_message(
        message.chat.id,
        f"Your info: \n"
        f"Email: {user.email}\n"
        f"First name: {user.first_name}\n"
        f"Last name: {user.last_name}\n"
        f"Is staff: {user.is_staff}",
    )


@bot.message_handler(func=lambda message: message.text == "🎫 Tickets")
@check_if_user_exist
def handle_tickets(message):
    user = get_user_model().objects.get(telegram_id=message.chat.id)
    tickets = Ticket.objects.filter(order__user=user.pk)
    bot.send_message(
        message.chat.id,
        ("-" * 10).join(
            [
                f"\nrow: {ticket.row}"
                f"\nseat: {ticket.seat}"
                f"\nflight: {str(ticket.flight.route)}\n"
                for ticket in tickets
            ]
        ),
    )


@bot.message_handler(func=lambda message: message.text)
def handle_incorrect_value(message):
    bot.send_message(
        message.chat.id,
        "You should write appropriate command",
    )


class Command(BaseCommand):
    help = "Command to run Telegram bot"

    def handle(self, *args, **options):
        self.stdout.write("Telegram bot is running...")
        bot.infinity_polling()
