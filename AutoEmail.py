import time
import os
import smtplib
import datetime
import json
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
    def __init__(self):
        self.sender = None
        self.receiver_list = []
        self.message = MIMEMultipart() # 初始化message
        self.image_id = []
        self.content = None

    def add_receiver(self, person):
        if not isinstance(person, Person): #如果person不是person类型, 则抛出异常
            raise Exception
        self.receiver_list.append(person)
        self.message['To'] = self._format_addr(person)

    def set_content(self, path): #默认设置内容, 即支付宝图片
        # 添加附件就是加上一个MIMEBase，从本地读取一个图片:
        with open(path, 'rb') as f:
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
            self.message.attach(MIMEText('<html><body><h1>这是一封正经的邮件</h1>' +
                                '<p><img src="cid:0"></p>' +
                                '大家记得交水费啊~'+
                                '</body></html>', 'html', 'utf-8'))

    def add_image_to_attach(self, path, postfix, name='test'):  # 添加附件
        with open(path, 'rb') as f:
            mime = MIMEBase('image', postfix, filename=name)
            mime.add_header('Content-Disposition', 'attachment', filename=name)
            mime.add_header('Content-ID', name)

            # 读入附件内容
            mime.set_payload(f.read())
            encoders.encode_base64(mime)
            self.message.attach(mime)

            #记录图片id
            self.image_id.append(name)

    def add_content(self, content):
        self.content = content

    def create_email(self):
        prefix = '<html><body><p>'
        current_time = datetime.datetime.today()
        current_time_str = current_time.strftime('%Y-%m-%d %I:%M:%S')
        content = '<b>' + current_time_str + '</b><br>' + self.content
        for image in self.image_id:
            content += '<img src="cid:' + image + '">'
        postfix = '</p></body></html>'
        self.message.attach(MIMEText(prefix + content + postfix, 'html', 'utf-8'))

    def get_content(self):
        return self.message

    def set_subject(self, subject):
        if not isinstance(subject, str): #如果不是string, 抛出异常
            raise Exception
        self.message['Subject'] = Header(subject, 'utf-8').encode()

    def reset_content(self):
        pass

    def add_sender(self, person):
        if not isinstance(person, Person): #如果person不是person类型, 则抛出异常
            raise Exception
        self.sender = person
        self.message['From'] = self._format_addr(person)

    def add_person_by_json(self, path):
        try:
            with open(path, 'r') as f:
                person_content = json.load(f)
                for person in person_content:
                    if(not self._check_format(person)): #如果所需的3项属性不在, 则输出错误, 继续下一项
                        print('json文件内容格式不正确')
                        continue
                    if(person['identity'] == 'sender'): #如果是发送者
                        self.add_sender(Person(person['name'], person['email']))
                    else:
                        self.add_receiver(Person(person['name'], person['email']))


        except FileNotFoundError:
            print('json file not found')
            exit(0)
        pass

    def get_sender(self):
        return self.sender

    def get_receiver_list(self):
        return self.receiver_list

    def get_reciver_list_name(self):
        return [receiver.name for receiver in self.receiver_list]

    def get_receiver_list_email(self):
        return [receiver.email for receiver in self.receiver_list]

    def get_sender_name(self):
        return self.sender.name

    def get_sender_email(self):
        return self.sender.email

    def _format_addr(self, person):
        name, addr = person.name, person.email
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def _check_format(self, content):
        if 'identity' not in content or 'name' not in content or 'email' not in content:
            return False
        return True


class Log:
    def __init__(self, path):
        self.log_path = path
        if(not os.path.exists(path)):
            with open(self.log_path, 'w') as f:
                pass

    def _read_time(self):
        with open(self.log_path, 'r+') as f: # 以w+方式打开会清空所有内容
            return f.read() #读取log记录的时间

    def write_time(self):
        with open(self.log_path, 'w+') as f:
            current_time = datetime.datetime.today()
            current_time_str = current_time.strftime('%Y-%m-%d %I:%M:%S')
            f.write(current_time_str)

    def compare_time(self):
        last_time = self._read_time()
        current_time = datetime.datetime.today()
        print(current_time.strftime('%Y-%m-%d %I:%M:%S') + '开始检测')
        last_time_datetime = datetime.datetime.strptime(last_time, '%Y-%m-%d %I:%M:%S') if len(last_time) != 0 else datetime.datetime(1970, 1, 1, 0, 0, 0)# 将时间转换为datetime类型
        print(last_time_datetime, current_time)
        print(last_time_datetime.day, current_time.day)
        if(current_time.day != last_time_datetime.day):
            print('返回True')
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
                # smtp.set_debuglevel(1)
                smtp.sendmail(self.from_addr, self.receive_list, message.as_string())
                print('发送本月邮件')
                smtp.quit()
            self.log.write_time()
            time.sleep(30)





