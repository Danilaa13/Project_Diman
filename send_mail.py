import smtplib
import os
import schedule
import time
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication



def send_email(file_path_1,  file_path_2):
    load_dotenv()
    # Заполните свои данные
    sender_email = os.getenv("SENDER_EMAIL")
    receiver_email = os.getenv("RECEIVER_EMAIL")
    subject = "Актуальные остатки"
    body = "Актуальные остатки"
    pass_for_email = os.getenv("PASS_FOR_MAIL")

    # Создаем объект MIMEMultipart
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # Открываем и добавляем файл вложения
    with open(file_path_1, "rb") as file:
        part = MIMEApplication(file.read(), Name=file_path_1)
        part["Content-Disposition"] = f"attachment; filename={file.name}"
        message.attach(part)

    with open(file_path_2, "rb") as file:
        part = MIMEApplication(file.read(), Name=file_path_2)
        part["Content-Disposition"] = f"attachment; filename={file.name}"
        message.attach(part)

    # Подключение к SMTP-серверу и отправка письма
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, pass_for_email)
        server.sendmail(sender_email, receiver_email, message.as_string())

    print("Письмо успешно отправлено.")





