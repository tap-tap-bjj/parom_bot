��� ������� ������ ��������� ��� 2 �������. (��� ����� test ��������� testbot, ��� inputform - inputform)

systemctl enable parombot
systemctl start parombot

���� ��� �� ��������, ��������� ������ � ����:

systemctl status parombot  # ������
journalctl -u  parombot.service  # ����
sudo journalctl -u parombot.service -n 100 #��� ������� ��������� 100 ������� �� ������� ������ ParomBot.
