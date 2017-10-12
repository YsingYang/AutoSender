import time
import os
import smtplib
import datetime
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.header import Header
from email.utils import formataddr



class Person:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not isinstance(name, str):
            raise TypeError('Expected a string')
        self._name = name

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        if not isinstance(email, str):
            raise TypeError('Expected a string')
        self._email = email

class Email:
    def __init__(self, path):
        self.message = MIMEMultipart() # 初始化message
        self.path = path

    def add_receiver(self, person):
        if not isinstance(person, Person): #如果person不是person类型, 则抛出异常
            raise Exception
        self.message['To'] = self._format_addr(person)

    def set_content(self): #默认设置内容, 即支付宝图片
        # 添加附件就是加上一个MIMEBase，从本地读取一个图片:
        with open(self.path, 'rb') as f:
            # 设置附件的MIME和文件名，这里是png类型:
            mime = MIMEBase('image', 'jpg', filename='test.png')
            # 加上必要的头信息:
            mime.add_header('Content-Disposition', 'attachment', filename='test.png')
            mime.add_header('Content-ID', '<0>')
            mime.add_header('X-Attachment-Id', '0')
            # 把附件的内容读进来:
            mime.set_payload(f.read())
            # 用Base64编码:
            encoders.encode_base64(mime)
            # 添加到MIMEMultipart:
            self.message.attach(mime)
            self.message.attach(MIMEText('<html><body><h1>水费提醒</h1>' +
                                '<p><img src="cid:0"></p>' +
                                '</body></html>', 'html', 'utf-8'))

    def get_content(self):
        return self.message

    def set_subject(self, subject):
        if not isinstance(subject, str): #如果不是string, 抛出异常
            raise Exception
        self.message['Subject'] = Header(subject, 'utf-8').encode()

    def reset_content(self):
        pass

    def add_content(self):
        pass

    def add_sender(self, person):
        if not isinstance(person, Person): #如果person不是person类型, 则抛出异常
            raise Exception
        self.message['From'] = self._format_addr(person)

    def _format_addr(self, person):
        name, addr = person.name, person.email
        return formataddr((Header(name, 'utf-8').encode(), addr))


class Log:
    def __init__(self, path):
        self.log_path = path

    def _read_time(self):
        try:
            with open(self.log_path, 'r+') as f: # 以w+方式打开会清空所有内容
                return f.read() #读取log记录的时间
        except FileNotFoundError: #捕获没有找到文件
            return str() # 返回空字符串

    def _write_time(self):
        with open(self.log_path, 'w+') as f:
            current_time = datetime.datetime.today()
            current_time_str = current_time.strftime('%Y-%m-%d %I:%M:%S')
            f.write(current_time_str)
            return current_time

    def compare_time(self):
        last_time = self._read_time()
        current_time = self._write_time()

        if(len(last_time) == 0): #未记录过
            return True
        last_time_datetime = datetime.datetime.strptime(last_time, '%Y-%m-%d %I:%M:%S') # 将时间转换为datetime类型
        if(current_time.month != last_time_datetime.month):
            return True #如果月份不一致, 返回True表示可以重新发送
        return False


class Sender:
    def __init__(self, smtp_server, smtp_port, from_addr, password, receive_list, email_object, log):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.from_addr = from_addr
        self.receive_list = receive_list
        self.email_object = email_object
        self.log = log
        self.password = password

    def loop_for_send(self):
        message = self.email_object.get_content()
        while True:
            if(self.log.compare_time()):
                smtp = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
                smtp.login(self.from_addr, self.password)
                smtp.set_debuglevel(1)
                smtp.sendmail(self.from_addr, self.receive_list, message.as_string())
                smtp.quit()
            time.sleep(30)


if __name__ == '__main__':
    smtp_server = 'smtp.qq.com' # 设置smtp服务器
    port = 465 #设置连接的smtp服务器端口
    password = 'Your Password' # 设置password
    email_object = Email('/home/ysing/PycharmProjects/AutoSendingEmail/971059664.jpg') #创建email对象, 并传入收钱码路径
    email_object.set_content() # 设置邮件内容
    email_object.set_subject('交水费邮件') #设置邮件标题
    sd = Person('name', 'address') # 创建发件人对象
    rc_1 = Person('name', 'address') #创建收件人对象1
    rc_2 = Person('name', 'address') # 创建收件人对象2
    email_object.add_receiver(rc_1) #添加收件人对象1进邮件对象中
    email_object.add_receiver(rc_2) # 添加收件人对象2进邮件对象中
    email_object.add_sender(sd) #添加发件人对象仅邮件对象中
    recording_log = Log(os.path.join(os.getcwd(), 'sendingLog')) #创建log对象
    receive_list = [rc_1.email, rc_2.email] #设置收件人列表
    from_addr = sd.email #设置发件人邮箱
    sender = Sender(smtp_server, port, from_addr, password, receive_list, email_object, recording_log) #创建sender对象
    sender.loop_for_send() #循环判断是否发送




