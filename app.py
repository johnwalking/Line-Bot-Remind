from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from datetime import timedelta

from linebot import (
    LineBotApi, WebhookHandler,
)
import json

from linebot.exceptions import(
    InvalidSignatureError,
)

from linebot.models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
# channel access token 
line_bot_api = LineBotApi(your own chaennel access token)
# channel Secret
handler = WebhookHandler( your own channel Secret)
 
 
 
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default= datetime.utcnow())
    day_to_do = db.Column(db.String(20) , default = "2/29" ) 
    time_to_do  = db.Column(db.String(20) , default = "9:00")

    def __repr__(self):
        return '<Task %r>' % self.id


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


 
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print(event.message.text+"---------")
    new_list = event.message.text.split(" ")
    if len(new_list) == 3:
        new_task = Todo(content=new_list[0], day_to_do = new_list[1],time_to_do=new_list[2])
        db.session.add(new_task)
        db.session.commit()
        line_bot_api.push_message( your_user_id , TextSendMessage(text='Add new item to '+new_list[0]+" at "+new_list[1]+"/"+new_list[2]+" Successfully !"))
                     
    elif  "today"  in str(event.message.text) or  "今天" in str(event.message.text) :
    
        print("today 觸發")
        tasks = Todo.query.order_by(Todo.day_to_do).all()
        date = str(datetime.now()) 
        today = str(int(date.split(" ")[0].split("-")[1]))+"/" + str(int(date.split(" ")[0].split("-")[2] ))
        
        ret = "" 
        if len(tasks) >=1:
            for task in tasks:
                if task.day_to_do == today:
                    ret += ( str(task.content)+" at "+ str(task.time_to_do)+"\n")            
        if ret != "": 
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=ret)
            )
    elif  "所有"  in str(event.message.text) or  "All" in str(event.message.text) or  "all" in str(event.message.text) : 
        tasks = Todo.query.order_by(Todo.day_to_do).all()
        date = str(datetime.now()) 
        today = str(int(date.split(" ")[0].split("-")[1]))+"/"+date.split(" ")[0].split("-")[2]
        
        ret = "" 
        if len(tasks) >=1:
            for task in tasks:
                ret += ( str(task.content)+" in "+ str(task.day_to_do)+" "+str(task.time_to_do)+ '\n')            
        if ret != "": 
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=ret)
            )    


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        task_day = request.form['day_to_do']
        task_time = request.form['time_to_do']
        new_task = Todo(content=task_content, day_to_do = task_day,time_to_do=task_time)
        

        try:
            db.session.add(new_task)
            db.session.commit()
            
            line_bot_api.push_message( your_user_id , TextSendMessage(text='Add new item to '+task_content+" at "+task_day+"/"+task_time+" Successfully !"))
             
            return redirect('/')
        except:
            # line_bot_api.reply_message(
            #     event.reply_token,
            #     TextSendMessage(text="你對資料庫的改動成功")
            # ) 
            return 'There was an issue adding your task'

    else:
        tasks = Todo.query.order_by(Todo.day_to_do).all()
        
        if len(tasks) >=1:
            for task in tasks:
                time = "2021/"+str(task.day_to_do)+"/"+str(task.time_to_do) 
                print(time)
                print(datetime.strptime(time, "%Y/%m/%d/%H:%M").timestamp(), datetime.now().timestamp()  + 3600 )
                if  datetime.strptime(time, "%Y/%m/%d/%H:%M").timestamp() <  datetime.now().timestamp() + 3600 :
                    line_bot_api.push_message( your_user_id, TextSendMessage(text="It's time to "+str(task.content)+" afte about an hour."))
                    task_to_delete = Todo.query.get_or_404(task.id)
                    db.session.delete(task_to_delete)
                    db.session.commit()
        tasks = Todo.query.order_by(Todo.day_to_do).all() 
        return render_template('index.html', tasks=tasks)


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']
        task.day_to_do = request.form['day_to_do']
        task.time_to_do = request.form['time_to_do']

        try:
            db.session.commit()
            
        
            return redirect('/')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('update.html', task=task)


if __name__ == "__main__":
    app.run(debug=True,port = 7776)
