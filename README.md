# SMTP服务参考

本地开启SMTP 服务器
[python开启Smtp服务](https://stackoverflow.com/questions/5619914/sendmail-errno61-connection-refused)

本地安装sendmail
[本地安装sendmail](https://gist.github.com/adamstac/7462202)

安装sendmail过程可能会碰到的问题
[sendmail installation hanged](https://askubuntu.com/questions/937666/ubuntu-16-04-command-line-sendmail-installation-hanged)


## AutoSender
* 背景:给良神催交水费, 本想起名叫包租婆, 但是有道搜索包租婆发现404not found...
* 该应用暂时偏定制化, 想要通用的话等我有空再写..
### Requirements
python 3.4

### API使用
#### Person Class
  Person(name, email)
  * property
    - name
    为Person名字, 你起你喜欢的就行, 一般来说是邮件中address前的名字
    
    - email
    为Person邮件地址.
    
#### Email Class
  Email(path)
  * property
    - message : MIMEMultipart对象
    - receiver_list : 为存储Person的列表, 即收件人列表
    - sender : 即发件人, Person类型
    
  * method
    - add_receiver(self, person)
      接受一个person对象, 并将该Person对象中的值添加到message['To']中, 即接收方
      
    - set_content(self, path):
      设置message中的content, 带有一个path, 表示传入的收件码文件地址
      
    - get_content(self):
      返回message
     
    - set_subject(self, subject)
      设置标题, 接受一个string类型, 并设置仅message['Subject']中
    
    - add_sender(self, person)
      设置发送方, 接受一个Person对象, 并添加到message['From']中
    - add_person_by_json(self, path)
      设置发送方与接收方, 传入一个json文件的path路径即可, json文件的每一项要包括
      1. `identity` : 表示身份, 是发送(sender)还是接受(receiver)
      2. `name` : 表示Person name
      3. `email` : 表示邮件地址
    
    - get_receiver_list(self):
      返回接收者列表
    - get_receiver_list_name(self):
      返回接受者name的列表
    - get_receiver_list_email(self):
      返回接收者email的列表
    - get_senderxxx
      (不想再写了)
     
    

#### Log Class
  Log(path)
  * property
    - log_path : 为log存储的路径
  
  * method
    - compare_time(self)
      比较log中的时间与当前时间是否是同一月, 如果是, 则返回false, 如果不是返回true, 另外如果Log不存在, 会抛出一个FileNotFoundError, 在本函数中捕, 并返回true

#### Sender Class
Sender(smtp_server, smtp_port, from_addr, password, receive_list, email_object, log)
* property
   - smtp_server: 你所用到的smtp服务器, 例:如果你用QQ邮箱则使用smtp.qq.com
   - smtp_port: 连接smtp服务器的端口号
   - from_addr: 发件人邮箱地址
   - password: 发件人邮箱密码(通常你的邮箱开启smtp会给你一个通行码)
   - receive_list: 接收人列表, 为list&lt;string&gt; 其中的string为接收人的邮箱地址
   - email_object : 你定义好的Email对象
   - log : 你定义好的log对象

* method
	- loop_for_send(self)
     循环查询该月是否已经发送过邮件, 如果发送了则不发送本月邮件.


### Example

* Example_1
```
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
```

* Example_2
```
if __name__ == '__main__':
    smtp_server = 'smtp.qq.com' # 设置smtp服务器
    port = 465 #设置连接的smtp服务器端口
    password = 'Your password' # 设置password
    email_object = Email() #创建email对象, 并传入收钱码路径
    email_object.set_content('/home/ysing/PycharmProjects/AutoSendingEmail/971059664.jpg') # 设置邮件内容
    email_object.set_subject('交水费邮件') #设置邮件标题
    email_object.add_person_by_json('./person_list.json') #读取json文件, 获取相应的receiver, 与sender
    recording_log = Log(os.path.join(os.getcwd(), 'sendingLog')) #创建log对象
    receive_list = email_object.get_receiver_list_email() #获取收件人列表的email地址
    from_addr = email_object.get_sender_email() #获取发件人email地址
    sender = Sender(smtp_server, port, from_addr, password, receive_list, email_object, recording_log) #创建sender对象
    sender.loop_for_send() #循环判断是否发送
```
相应的json文件
```
[
	{"identity" : "sender", "name" : "ysing", "email" : "594171146@qq.com"},
	{"identity" : "receiver", "name" : "ysing", "email" : "594171146@qq.com"},
	{"identity" : "receiver", "name" : "ysing", "email" : "yangyxemail@163.com"}
]
```