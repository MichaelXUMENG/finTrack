import smtplib

subject = "This is a test"
text = "Sending email from python."
message = 'Subject: {}\n\n{}'.format(subject, text)

server = smtplib.SMTP_SSL('smtp.qq.com', 465)
server.login("342049327@qq.com", "FamilyHappy1989")
server.sendmail("342049327@qq.com", "xumenglove@icloud.com", message)
server.quit()