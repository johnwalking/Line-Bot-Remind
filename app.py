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
line_bot_api = LineBotApi("3ZRPiUoXnoLf+TjLgiq0Dkhi52kFxjSdMLpWxHPw/4fpJNHJCWPfZh5TjWWbMeotxxzuyf2k3uG0pU7gjzCYIet4eKR7z4QlaVRLF9Q8E//+iOUKj8ZImu/W7DpOGfhpnaScxvLUJOSBDYm6sqMMXgdB04t89/1O/w1cDnyilFU=")
# channel Secret
handler = WebhookHandler("ef4938f6e2b3adde11d7a99d32a5ebad")
 
 
 
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default= datetime.utcnow())
    day_to_do = db.Column(db.String(20) , default = "2/29" ) 
    time_to_do  = db.Column(db.String(20) , default = "9:00")

    def __repr__(self):
        return '<Task %r>' % self.id


@app.route('/callback', methods=['POST'])
def callback():
    signature = request.header['X-Line-Signature']
    
    #get request body as text
    body = request.get_data(as_text = True)
    d = json.loads(body)
    reid = d['events'][0]["message"]["id"]
    print("R_ID: ", end = "")
    print(reid)
    User_id = d['events'][0]["source"]["userId"]
    print("UserID: ", end = "")
    print(User_id)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    
    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
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
            
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="你對資料庫的改動成功")
            )
             
            return redirect('/')
        except:
            return 'There was an issue adding your task'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
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
