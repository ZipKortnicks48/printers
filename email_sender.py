import smtplib
from email.mime.text import MIMEText
from email.header    import Header
class email_sender():
    def send_email(self, text): 
        to_addr="sirokvasov.av@rkvv.ru"
        from_addr="vodokanal482019@gmail.com"
        msg = MIMEText(text, 'plain', 'utf-8')
        msg['Subject'] = Header('Заявка на ремонт принетра. ОГУП "Липецкий областной водоканал"', 'utf-8')
        msg['From'] = from_addr     
        msg['To'] = to_addr
        server = smtplib.SMTP_SSL("smtp.gmail.com",port=465)
        server.login('vodokanal482019@gmail.com','Djljrfyfk48')
        server.sendmail(from_addr, to_addr, msg.as_string())
        server.quit()
# if __name__ == "__main__":
#     sender=email_sender()
#     sender.send_email("text") 