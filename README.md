# status-bot

Slackで特定のステータスに変更された場合に特定のチャンネルに通知してくれるbotです。  

# Installation
Githubからクローンしてきます
```
$ git clone https://github.com/yokensei/status-bot
```
```
$ cd status-bot
```
  
ライブラリのインストールを行います
```
$ pip install -r requirements.txt
```

# Usage
config.iniに必要な情報を記述します
```
token={your slack token or bot token}
room={room name that you want to nortificate like general}
status_start={start status emoji name that you want to notify change}
status_end={end status emoji name that you want to notify change}
message_format_start={bot message without user name when start status set}
message_format_end={bot message without user name when end status set}
```
token ・・・ユーザーのtoken、あるいはbot用のトークンを指定します  
room ・・・通知を行いたいSlackのチャンネル名を指定します(トークンの持ち主が所属するチャンネルである必要があります)
status_start ・・・通知を発生させるステータスの名前
status_end ・・・通知を発生させるステータスの名前。変更後に当該ステータスをクリアする(未実現)
message_format_start ・・・status_start にステータスが変更された場合に通知されるメッセージのフォーマット。{} を指定することでユーザー名を含められます。
message_format_end ・・・end_start にステータスが変更された場合に通知されるメッセージのフォーマット。{} を指定することでユーザー名を含められます。

スクリプトを実行し、botを立ち上げます。
```
$ python channel-bot.py
```
`config.ini`でbot用のtokenを使用した場合は、そのbotを`config.ini`のroomで指定したroomに招待してください。

# Remark

前述の通り、 status_end は変更後に該当ステータスをクリアする処理を含めていますが、うまく動作していないため現状では status_start と同じ動きとなっています。
