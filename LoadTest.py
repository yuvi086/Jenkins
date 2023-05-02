import sqlite3
import requests
import datetime
import json
import time
import schedule
import smtplib
import os
import base64
import csv
from email.message import EmailMessage


# *******************|Sense BoT Part|***********************************
def main():
    with open('mycsv.csv', 'w', newline='') as f:
        thewriter = csv.writer(f)
        thewriter.writerow(['EMAIL', 'MESSAGE'])
    date_time = datetime.datetime.now()
    reg_date = date_time.strftime("%Y-%m-%d %H:%M:%S")
    print(reg_date)
    x = []
    z = []
    k = []
    q = []
    url = 'https://reqres.in/api/login'
    payload = {
         'email': 'eve.holt@reqres.in',
        'password': 'cityslicka'
        }
    with requests.session() as session:
        post = session.post(url, data=payload)
        print(post.content)
        print('Login successfull')
    with open(r"data.json.txt") as f:
         data = json.load(f)
    #print(data)
    fo = open("sensebotdata.txt", "w")
    for i in data['data']:
        fo.write("%i    %s    %s    %s     %s\n" % (i['id'], i['email'], i['first_name'], i['last_name'], reg_date))
    fo.close()

    # ********* |Response Bot Part |*****************************
    db = sqlite3.connect('temp.db')
    cursor = db.cursor()
    with open('sensebotdata.txt') as f:
        for line in f:
            id1, email2, first_name, last_name, date1, time1 = line.strip().split()
            k.append(email2)
    print(k)
    for j in k:
        status_flag4 = 'Y'
        g = cursor.execute('select * from info where email_id=? AND status_flag =?', (str(j), status_flag4))
        for row2 in g:
            id4, email4, status_flag5 = row2
            q.append(email4)

    print(q)
    for j in k:
        status_flag2 = 'N'
        d = cursor.execute('select * from info where email_id=? AND status_flag =?', (str(j), status_flag2))
        for row in d:
            id, email1, status_flag1 = row
            x.append(email1)
    print(x)
    for j in k:
        f = cursor.execute('select * from info where email_id=?', [str(j)])
        for row1 in f:
            id3, email3, status_flag3 = row1
            z.append(email3)
    print(z)
    length = len(z)
    id = length + 1
    # ***************|Updating flag of the user|****************
    for y in k:
        if y in x:
            status_flag1 = 'Y'
            cursor.execute('update info set status_flag = ? where email_id = ?', (status_flag1, y))
            db.commit()
            rec_mail = y
            message = "Editor role has been enabled"
            mailing(rec_mail, message)
            csv_report(rec_mail, message)
            # *************|Sending mail if account is already present |*************
        elif y in q:
            rec_mail = y
            message = "Person already has editor access"
            mailing(rec_mail, message)
            csv_report(rec_mail, message)
            # with open('mycsv.csv', 'a') as f:
            #   thewriter = csv.writer(f)
            #  thewriter.writerow({rec_mail,message})

            # *********************|Inserting data in database|*****************
        elif y not in z:
            email2 = y
            status_flag1 = 'Y'
            cursor.execute('insert into info(id,email_id,status_flag) values(?,?,?)', (id, str(email2), status_flag1))
            db.commit()
            id = id + 1
            rec_mail = y
            message = 'Person Account Created and editor role has been granted'
            mailing(rec_mail, message)
            csv_report(rec_mail, message)
    mail_team()


# *****************|Scheduling the sense bot|*********************


def mailing(mail_id, msg):
    sender_mail = 'yatin.rana1997@gmail.com'
    password_me = base64.b64decode("WXV2aTA4NlI=").decode("utf-8")
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_mail, password_me)
    print('Successfully Login')
    server.sendmail(sender_mail, mail_id, msg)
    print('Mail sent to ', mail_id)


def csv_report(rec_id, msg1):
    with open('mycsv.csv', 'a+', newline='') as f:
        fieldnames = ['Email', 'Message']
        thewriter = csv.DictWriter(f, fieldnames=fieldnames)
        # thewriter.writeheader()
        thewriter.writerow({"Email": rec_id, "Message": msg1})


def mail_team():
    sender_mail = 'yatin.rana1997@gmail.com'
    password_me = base64.b64decode("WXV2aTA4NlI=").decode("utf-8")
    receiver_mail = 'yuvi.vicku@gmail.com'
    subject = 'Daily Report'
    msg9 = EmailMessage()
    msg9['FROM'] = sender_mail
    msg9['TO'] = receiver_mail
    msg9['Subject'] = subject
    msg9.set_content('Attached is the list of Incidents resolved')
    with open('mycsv.csv', 'rb') as f:
        file_data = f.read()
    filename = 'mycsv.csv'
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    msg9.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=filename)
    server.login(sender_mail, password_me)
    print('Successfully Login')
    server.send_message(msg9)
    print('Mail sent to ', receiver_mail)
    os.remove('mycsv.csv')

main()
schedule.every(500).seconds.do(main)
#schedule.every().day.at("08:35").do(mail_team)
while True:
    schedule.run_pending()
    time.sleep(1)