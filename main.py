# main.py
import discord  # Discordのライブラリをインポート
import os  # 環境変数を扱うためのライブラリ
import json  # JSON形式のデータを扱うためのライブラリ
from keep_alive import keep_alive  # RenderでBotを常時稼働させるための関数

# 🔧 Botの権限設定
intents = discord.Intents.default()  # デフォルトの権限を設定
intents.voice_states = True  # ボイスチャンネルの状態を監視する権限
intents.messages = True  # メッセージを読み取る権限
intents.message_content = True  # メッセージの内容を読み取る権限（重要！）
intents.members = True  # メンバー情報を読み取る権限

# Discordクライアントを作成
client = discord.Client(intents=intents)

# 🔧 自己紹介チャンネルのIDを設定（ここを変更！）
INTRODUCTION_CHANNEL_ID = 1300659373227638794  # 自己紹介チャンネルのID

# 📂 自己紹介リンクを保存する辞書
introduction_links = {}

# 💾 リンクをファイルに保存する関数
def save_links():
    # introduction_links辞書をJSON形式でファイルに保存
    with open("introduction_links.json", "w") as f:
        json.dump(introduction_links, f)

# 📥 リンクをファイルから読み込む関数
def load_links():
    try:
        # introduction_links.jsonファイルからデータを読み込む
        with open("introduction_links.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # ファイルが存在しない場合は空の辞書を返す
        return {}

# 🚀 Botが起動したときの処理
@client.event
async def on_ready():
    global introduction_links
    # 起動時にリンクを読み込む
    introduction_links = load_links()
    print(f'✅ Botがログインしました: {client.user}')
    print(f"📜 読み込まれたリンク数: {len(introduction_links)}")

    # 自己紹介チャンネルを取得
    channel = client.get_channel(INTRODUCTION_CHANNEL_ID)
    
    # 過去のメッセージを最大100件取得
    async for message in channel.history(limit=100):
        if message.author.bot:  # Botのメッセージは無視
            continue
        # メッセージリンクを生成
        message_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
        # ユーザーIDをキーにしてリンクを保存
        introduction_links[str(message.author.id)] = message_link
    
    # リンクを保存
    save_links()
    print(f"📜 過去のメッセージを読み込みました。総リンク数: {len(introduction_links)}")

# 💬 メッセージが送信されたときの処理
@client.event
async def on_message(message):
    # 自己紹介チャンネルでのみ反応
    if message.channel.id == INTRODUCTION_CHANNEL_ID and not message.author.bot:
        # メッセージリンクを作成
        message_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
        
        # ユーザーIDをキーにしてリンクを保存
        introduction_links[str(message.author.id)] = message_link
        save_links()  # リンクを保存
        
        print(f"📝 {message.author} のリンクを保存: {message_link}")

# 🎧 ボイスチャンネルの状態が変わったときの処理
@client.event
async def on_voice_state_update(member, before, after):
    # ボイスチャンネルに入室したときのみ反応
    if before.channel is None and after.channel is not None:
        # 入室したボイスチャンネルを取得
        voice_channel = after.channel
        
        # ボイスチャンネルに関連するテキストチャンネルを取得
        text_channel = discord.utils.get(voice_channel.guild.text_channels, name=voice_channel.name)
        
        # テキストチャンネルが見つからない場合はデフォルトのチャンネルを使用
        if text_channel is None:
            text_channel = voice_channel.guild.system_channel  # サーバーのデフォルトチャンネル
        
        # ユーザーの自己紹介リンクを取得
        user_link = introduction_links.get(str(member.id))
        
        # メッセージを作成
        if user_link:
            msg = (
                f"{member.mention} さんが入室しました。\n"  # ここを変更！
                f"📌 自己紹介はこちら → {user_link}"
            )
        else:
            msg = (
                f"{member.mention} さんが入室しました。\n"  # ここを変更！
                "❌ 自己紹介がまだありません"
            )
        
        # テキストチャンネルにメッセージを送信
        if text_channel:
            await text_channel.send(msg)
        else:
            print(f"❌ テキストチャンネルが見つかりません: {voice_channel.name}")

# 🌐 RenderでBotを常時稼働させるための関数を呼び出す
keep_alive()

# 🔑 TOKENを使ってBotを起動
client.run(os.getenv("TOKEN"))
