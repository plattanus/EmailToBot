import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 邮件信息
smtp_server = '127.0.0.1'
smtp_port = 18025
sender = 'sender@example.com'
password = 'password'
recipient = 'recipient@example.com'
subject = 'Test email'
content = 'This is a test email. Please ignore it.'

# 创建邮件对象
msg = MIMEText(content, 'plain', 'utf-8')
msg['From'] = Header(sender, 'utf-8')
msg['To'] = Header(recipient, 'utf-8')
msg['Subject'] = Header(subject, 'utf-8')

# 发送邮件
try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, [recipient], msg.as_string())
    print('Email sent successfully!')
except Exception as e:
    print('Failed to send email:', e)
finally:
    server.quit()

'''
swaks --to recipient@example.com --from sender@example.com --server 127.0.0.1 --port 18025 --auth-user sender@example.com --auth-password password --tls --data "Subject: Test Email\r\n\r\nThis is a test email."
'''