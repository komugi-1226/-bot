import discord  # Discordのライブラリをインポート
import os  # 環境変数を扱うためのライブラリ
import json  # JSON形式のデータを扱うためのライブラリ
from dotenv import load_dotenv  # 環境変数を読み込むためのライブラリ
from flask import Flask  # Flaskをインポート
import threading  # スレッドを扱うためのライブラリ

# 環境変数をロード
load_dotenv()

# Flaskアプリケーションのセットアップ
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    """
    Flaskサーバーを指定されたポートで実行します。
    Render.com は環境変数 'PORT' を使用してポートを指定します。
    """
    port = int(os.getenv("PORT", 8080))  # Render.comが指定するポートを取得（デフォルトは8080）
    app.run(host='0.0.0.0', port=port)

# 別スレッドでFlaskアプリを実行
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

# 🔧 Botの権限設定
intents = discord.Intents.default()  # デフォルトの権限を設定
intents.voice_states = True  # ボイスチャンネルの状態を監視する権限
intents.messages = True  # メッセージを読み取る権限
intents.message_content = True  # メッセージの内容を読み取る権限（重要！）
intents.members = True  # メンバー情報を読み取る権限

# Discordクライアントを作成
client = discord.Client(intents=intents)

# 🔧 自己紹介チャンネルのIDを設定
INTRODUCTION_CHANNEL_ID = 1300659373227638794  # 自己紹介チャンネルのID（実際のIDに置き換えてください）

# 🔧 通知用テキストチャンネルのIDを設定
NOTIFICATION_CHANNEL_ID = 1331177944244289598  # 通知用テキストチャンネルのID（実際のIDに置き換えてください）

# 🔧 対象のボイスチャンネルIDのリスト
TARGET_VOICE_CHANNELS = [
    1300291307750559754,  # ボイスチャンネル1のID
    1302151049368571925,  # ボイスチャンネル2のID
    1302151154981011486,  # ボイスチャンネル3のID
    1306190768431431721,  # ボイスチャンネル4のID
    1306190915483734026,  # ボイスチャンネル5のID
]

# 📂 自己紹介リンクを保存する辞書
introduction_links = {}

# 💾 リンクをファイルに保存する関数
def save_links():
    """
    introduction_links辞書をJSON形式でファイルに保存します。
    """
    try:
        with open("introduction_links.json", "w", encoding='utf-8') as f:
            json.dump(introduction_links, f, ensure_ascii=False, indent=4)
        print("✅ introduction_links.json にリンクを保存しました。")
    except Exception as e:
        print(f"❌ リンクの保存中にエラーが発生しました: {e}")

# 📥 リンクをファイルから読み込む関数
def load_links():
    """
    introduction_links.jsonファイルからデータを読み込みます。
    ファイルが存在しない場合は空の辞書を返します。
    """
    try:
        with open("introduction_links.json", "r", encoding='utf-8') as f:
            print("✅ introduction_links.json を読み込みました。")
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ introduction_links.json が存在しません。新規作成します。")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ introduction_links.json の読み込み中にJSONエラーが発生しました: {e}")
        return {}
    except Exception as e:
        print(f"❌ introduction_links.json の読み込み中にエラーが発生しました: {e}")
        return {}

# 🚀 Botが起動したときの処理
@client.event
async def on_ready():
    global introduction_links
    # 起動時にリンクを読み込む
    introduction_links = load_links()
    print(f'✅ Botがログインしました: {client.user}')
    print(f"📜 読み込まれたリンク数: {len(introduction_links)}")
    print(f"📢 監視対象ボイスチャンネル: {TARGET_VOICE_CHANNELS}")
    print(f"📢 通知用テキストチャンネル: {NOTIFICATION_CHANNEL_ID}")

    # 自己紹介チャンネルを取得
    channel = client.get_channel(INTRODUCTION_CHANNEL_ID)
    
    if channel is None:
        print(f"⚠️ 自己紹介チャンネルが見つかりません: {INTRODUCTION_CHANNEL_ID}")
        return
    
    # 過去のメッセージを最大1000件取得（必要に応じて増やしてください）
    async for message in channel.history(limit=1000):
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
    print(f"🔄 Voice state updated: {member} - before: {before.channel}, after: {after.channel}")
    # ボイスチャンネルに入室したときのみ反応
    if before.channel is None and after.channel is not None:
        voice_channel_id = after.channel.id
        # 対象のボイスチャンネルか確認
        if voice_channel_id in TARGET_VOICE_CHANNELS:
            print(f"✅ {member} が対象のボイスチャンネルに参加しました: {after.channel.name} (ID: {voice_channel_id})")
            # 通知用テキストチャンネルを取得
            notify_channel = client.get_channel(NOTIFICATION_CHANNEL_ID)
            
            if notify_channel is None:
                print(f"⚠️ 通知チャンネルが見つかりません: {NOTIFICATION_CHANNEL_ID}")
                return
            
            # ユーザーの自己紹介リンクを取得
            user_link = introduction_links.get(str(member.id))
            
            # メッセージを作成
            if user_link:
                msg = (
                    f"{member.display_name} さんが`{after.channel.name}` に入室しました！\n"
                    f"📌 自己紹介はこちら → {user_link}"
                )
                print(f"📨 {member} の自己紹介リンクを見つけました: {user_link}")
            else:
                msg = (
                    f"{member.display_name} さんが`{after.channel.name}` に入室しました！\n"
                    "❌ 自己紹介がまだありません"
                )
                print(f"⚠️ {member} の自己紹介リンクが見つかりません。")
            
            # メッセージ送信前にログを出力
            print(f"📨 通知メッセージを送信します: {msg}")
            
            # メッセージ送信
            try:
                await notify_channel.send(msg)
                print(f"✅ {member} の入室通知を送信しました。")
            except discord.Forbidden:
                print(f"❌ Botが通知チャンネルにメッセージを送信する権限がありません: {NOTIFICATION_CHANNEL_ID}")
            except discord.HTTPException as e:
                print(f"❌ メッセージ送信中にHTTPエラーが発生しました: {e}")
            except Exception as e:
                print(f"❌ メッセージ送信中に予期しないエラーが発生しました: {e}")

# 🔑 TOKENを使ってBotを起動
token = os.getenv("TOKEN")
if not token:
    print("❌ TOKENが設定されていません。環境変数を確認してください。")
    exit()

try:
    client.run(token)
except Exception as e:
    print(f"❌ Botの起動中にエラーが発生しました: {e}")
