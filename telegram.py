import telebot
class telegram():
    def send(text):
        TOKEN='1191171470:AAFD2RFpUR0-W_RTqO4uco2WpCAZOCT1b4M'
        bot=telebot.TeleBot(TOKEN)
        bot.send_message('-488020289',text,parse_mode="Markdown")
