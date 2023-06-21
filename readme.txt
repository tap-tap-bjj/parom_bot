Для запуска службы выполните эти 2 команды.

systemctl enable parombot
systemctl start parombot

Если бот не отвечает, проверьте статус и логи:

systemctl status parombot  # статус
journalctl -u  parombot.service  # логи
sudo journalctl -u parombot.service -n 100 #Это покажет последние 100 записей из журнала службы ParomBot.
