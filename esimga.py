import chromedriver_autoinstaller
chromedriver_autoinstaller.install()
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from telethon import TelegramClient, events
import phonenumbers
from phonenumbers import geocoder
from datetime import datetime
import re
import requests
import websocket
import threading
import time
import json
from telethon.tl.types import ReplyInlineMarkup, KeyboardButtonRow, InputKeyboardButtonUserProfile, KeyboardButtonCopy,  KeyboardButtonUrl
from telethon.tl.custom import Button
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
import os

# ───────────────────────────
# CONFIG
# CONFIG
api_id = 20348321
api_hash = "f6e0f6c94aaca0670619dbb17ca0e1e4"
bot_token = "8382938163:AAHrHTM16st8LjGiuQsGYJ5t2mNUk4PdN9U"
chat_id = -1002993082859

panels = {
    "1": {
        "name": "Panel 1",
        "url": "http://217.182.195.194",
        "user": "mustafa2202ee",
        "pwd": "mustafa2202ee",
        "type": "selenium"
    }
}
# ───────────────────────────

def parseX(data, start, end):
    try:
        star = data.index(start) + len(start)
        last = data.index(end, star)
        return data[star:last]
    except ValueError:
        return "None"

class seleSession:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Linux; Android 10; K) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/140.0.7339.80 Mobile Safari/537.36"
        )
        self.driver = webdriver.Chrome(options=chrome_options)
        self.logged_in = False

    def login(self, username: str, password: str):
        if self.logged_in:
            return
        self.driver.get(self.base_url + "/ints/login")
        page_source = self.driver.page_source
        try:
            cap_text = page_source.split("What is ")[1].split(" = ?")[0]
            n1, n2 = cap_text.split(" + ")
            capt = int(n1) + int(n2)
        except Exception:
            print("Failed to parse captcha.")
            self.driver.quit()
            return
        self.driver.find_element(By.NAME, "username").send_keys(username)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.NAME, "capt").send_keys(str(capt))
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.login100-form-btn"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        page_sourcee = self.driver.page_source
        print(f"[{self.base_url}] Login successful!")
        self.logged_in = True

    def fetch_page(self, path: str, refresh: bool = False):
        if not self.logged_in:
            raise Exception("Must login first!")
        url = self.base_url + path
        if refresh and self.driver.current_url == url:
            self.driver.refresh()
        else:
            self.driver.get(url)
        WebDriverWait(self.driver, 10).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "table tr")) > 1
        )
        with open("login1.html", "w") as f:
            f.write(self.driver.page_source)
        return self.driver.page_source

    def close(self):
        self.driver.quit()

def mask_number(num: str) -> str:
    if len(num) > 10:
        return num[:5] + "⁕⁕⁕⁕" + num[-4:]
    elif len(num) > 6:
        return num[:3] + "⁕⁕⁕⁕" + num[-3:]
    return num

def get_country(num: str) -> str:
    try:
        if num.startswith("+"):
            parsed = phonenumbers.parse(num, None)
        else:
            parsed = phonenumbers.parse("+"+num, None)
        if not phonenumbers.is_valid_number(parsed):
            return "🌍 Unknown"

        region_name = geocoder.description_for_number(parsed, "en")
        country_code = phonenumbers.region_code_for_number(parsed)

        if region_name and country_code:
            flag = "".join(chr(127397 + ord(c)) for c in country_code.upper())
            return f"{flag} {region_name}"
        elif region_name:
            return region_name
        else:
            return "🌍 Unknown"
    except phonenumbers.NumberParseException:
        return "🌍 Unknown"

def style(otp):
    masked = mask_number(otp['num'])
    country = get_country(otp['num'])
    return (
        f"<b>✨ {otp['svc'].upper()} 𝐎𝐓𝐏 𝐑𝐄𝐂𝐈𝐕𝐄𝐃 ✨</b>\n"
        f"┏━━━━━━━━━━━━━━━\n"
        f"┃ ᴛɪᴍᴇ - <b>{otp['time']}</b>\n"
        f"┃ ᴘᴀɴᴇʟ - <b>{otp['panel']}</b>\n"
        f"┃ ᴄᴏᴜɴᴛʀʏ - <b>{country}</b>\n"
        f"┃ ɴᴜᴍʙᴇʀ - <code>{masked}</code>\n"
        f"┃ sᴇʀᴠɪᴄᴇ - {otp['svc']}\n"
        f"┃ ᴏᴛᴘ - <b><code>{otp['code']}</code></b>\n"
        f"┗━━━━━━━━━━━━━━━\n"
        f"<blockquote>{otp['msg']}</blockquote>"
    )

def extract_otp(message):
    ignore_list = {
        "login", "code", "password", "hello", "service", "otp",
        "your", "number", "verify", "verification", "id", "pin"
    }
    numeric_pattern = r"\b\d{2,4}(?:[-\s]?\d{2,4})+\b"
    numeric_matches = [
        m for m in re.findall(numeric_pattern, message)
        if m.lower() not in ignore_list
    ]
    if numeric_matches:
        return numeric_matches
    plain_numeric_pattern = r"\b\d{4,8}\b"
    plain_numeric_matches = [
        m for m in re.findall(plain_numeric_pattern, message)
        if m.lower() not in ignore_list
    ]
    if plain_numeric_matches:
        return plain_numeric_matches
    alnum_pattern = r"\b[A-Z0-9]{4,10}\b"
    alnum_matches = [
        m for m in re.findall(alnum_pattern, message, flags=re.IGNORECASE)
        if any(c.isdigit() for c in m) and m.lower() not in ignore_list
    ]
    if alnum_matches:
        return alnum_matches
    return []

# Scraper
async def fetch_otp(session, panel_name):
    try:
        print("fetch_otp triggered")
        loop = asyncio.get_running_loop()
        html = await loop.run_in_executor(
            None, session.fetch_page, "/ints/agent/SMSCDRStats", True
        )
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.find_all("tr")

        # Check if the table has any data rows
        if len(rows) < 2:
            print(f"[{panel_name}] No data rows found in table.")
            return None

        cols = rows[1].find_all("td")
        
        # Check if the row has enough columns (at least 6 for the message)
        if len(cols) < 6:
            print(f"[{panel_name}] Row does not have enough columns.")
            return None

        now = cols[0].text.strip()
        number = cols[2].text.strip()
        service = cols[3].text.strip()
        message = cols[5].text.strip()
        code = extract_otp(message)

        return {
            "panel": panel_name,
            "num": number,
            "svc": service,
            "code": code[0] if code else "N/A",
            "msg": message,
            "time": now
        }
    except Exception as e:
        # This will now catch any errors and print them without crashing
        print(f"[{panel_name}] An error occurred in fetch_otp: {e}")
        # Optionally, write the error to your log file
        #with open(panel_name.replace(" ", "-") +'.txt', "a") as f:
        #    f.write(f"[{panel_name}] Error: {str(e)}\n\n")
        return None
# Telethon Bot
bot = TelegramClient("bot3", api_id, api_hash).start(bot_token=bot_token)

@bot.on(events.NewMessage(pattern="/getlogs"))
async def send_logs(event):
    sender = await event.get_sender()
    user_id = sender.id
    for pid, panel in panels.items():
        filename = f"{panel['name'].replace(' ', '-')}.txt"
        if os.path.exists(filename):
            await bot.send_file(user_id, filename, caption=f"Logs for {panel['name']}")
        else:
            await bot.send_message(user_id, f"No logs found for {panel['name']}")

#@bot.on(events.ChatAction())
#async def welcome_new_user(event):
#    if event.chat_id == -1002972723766:
#        if (event.user_joined and not event.user_added) or (event.user_added and not event.user_joined):
#            user = await event.get_user()
#            await bot.send_message(
#                event.chat_id,
#                f"👋 Welcome {user.first_name}",
#                buttons=[
#                    [Button.url("👑 Owner", "https://t.me/cryptixbits"), Button.url("👨‍💻 Developer", "https://t.me/+22893624413")],
#                    [Button.url("📞 Numbers", "https://t.me/+o0h2ZrgT8ooxMGU0"), Button.url("⏳ OTPS", "https://t.me/+4NzzQda-26dlODVk")],
#                ]
#            )
#            await event.delete()

async def panel_loop(session, panel_name):
    last_code = None
    while True:
        otp = await fetch_otp(session, panel_name)
        #print(otp)
        if otp and otp["code"] != last_code:
            last_code = otp["code"]
            await bot.send_message(
                -1002993082859,
                style(otp),
                parse_mode="html",
                buttons=ReplyInlineMarkup([
                    KeyboardButtonRow([
                        KeyboardButtonCopy("Copy OTP Code", otp["code"])
                    ]),
                    KeyboardButtonRow([
                        KeyboardButtonUrl("👑 Owner", "https://t.me/xion_ensigma"),
                        KeyboardButtonUrl("👨‍💻 Developer", "https://t.me/CrazyTha")
                    ]),
                    KeyboardButtonRow([
                        KeyboardButtonUrl("📞 Numbers", "https://t.me/+zGBLO8pOSylmODMx"),
                        KeyboardButtonUrl("⏳ OTPS", "https://t.me/xion_otps"),
                    ])
                ])
            )
        await asyncio.sleep(1)

# ───────── PANEL 3 (IVASMS) ─────────
async def sendmsg(text, buttons=None, panel={"name": "No"}):
    try:
        await bot.send_message(
            chat_id,
            text,
            parse_mode="html",
            buttons=buttons
        )
    except Exception as e:
        with open(f"{panel['name'].replace(' ', '-')}.txt", 'a') as f:
            f.write(f"[{panel['name']}] Error: {str(e)}\n\n")
        print(f"[Panel 3] Send error:", e)

def login_ivasms(email, password):
    r = requests.Session()
    req1 = r.get('https://www.ivasms.com/login')
    tok = parseX(req1.text, '<input type="hidden" name="_token" value="', '"')
    data = {
        '_token': tok,
        'email': email,
        'password': password,
        'remember': 'on',
        'submit': 'register',
    }
    r.post('https://www.ivasms.com/login', data=data)
    req3 = r.get('https://www.ivasms.com/portal/live/my_sms')
    r3txt = req3.text
    token = parseX(r3txt, "token: '", "',")
    user = parseX(r3txt, 'user:"', '"')
    return token, user

def start_panel3(panel, loop):
    while True:
        try:
            connected = {"value": False}
            token, user = login_ivasms(panel["email"], panel["password"])
            url = f"wss://ivasms.com:2087/socket.io/?token={token}&user={user}&EIO=4&transport=websocket"

            def on_message(ws, message):
                if message == "2":
                    ws.send("3")
                    if not connected["value"]:
                        print(f"[{panel['name']}] CONNECTED")
                        connected["value"] = True
                    return

                if message.startswith("42/livesms,"):
                    try:
                        payload = message[len("42/livesms,"):]
                        data = json.loads(payload)
                        sms = data[1]

                        number = sms.get("recipient", "Unknown")
                        msg = sms.get("message", "")
                        service = sms.get("originator", "Unknown")
                        code = extract_otp(msg)

                        otp = {
                            "panel": panel["name"],
                            "num": number,
                            "svc": service,
                            "code": code[0] if code else "N/A",
                            "msg": msg,
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }

                        buttons = ReplyInlineMarkup([
                            KeyboardButtonRow([
                                KeyboardButtonCopy("Copy OTP Code", otp["code"])
                            ]),
                            KeyboardButtonRow([
                                KeyboardButtonUrl("👑 Owner", "https://t.me/cryptixbits"),
                                KeyboardButtonUrl("👨‍💻 Developer", "https://t.me/+22893624413")
                            ]),
                            KeyboardButtonRow([
                                KeyboardButtonUrl("📞 Numbers", "https://t.me/+o0h2ZrgT8ooxMGU0"),
                                KeyboardButtonUrl("⏳ OTPS", "https://t.me/+4NzzQda-26dlODVk")
                            ])
                        ])

                        # Use the main loop explicitly
                        asyncio.run_coroutine_threadsafe(
                            bot.send_message(
                                -1002993082859,
                                style(otp),
                                buttons=buttons,
                                parse_mode="html"
                            ),
                            loop
                        )

                        # Save OTP log
                        with open(panel['name'].replace(" ", "-") + '.txt', "a") as f:
                            f.write(f"[{panel['name']}] OTP - {number} - {service} - {code} - {msg}\n\n")

                    except Exception as e:
                        print(f"[{panel['name']}] Parse error:", e, message)

            def on_open(ws):
                ws.send("40/livesms")
                print(f"[{panel['name']}] Connected to IVASMS")

            ws = websocket.WebSocketApp(
                url,
                on_message=on_message,
                on_open=on_open,
                header=[
                    "Origin: https://www.ivasms.com",
                    "User-Agent: Mozilla/5.0 (Linux; Android 10; K) "
                                 "AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/137.0.0.0 Mobile Safari/537.36",
                ],
            )
            ws.run_forever()

        except Exception as e:
            print(f"[{panel['name']}] Error: {e}, restarting in 5s...")
            time.sleep(5)

# ───────── MAIN ─────────
async def main():
    sessions_to_close = []
    tasks = []
    loop = asyncio.get_running_loop()

    for pid, panel in panels.items():
        filename = f"{panel['name'].replace(' ', '-')}.txt"
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                f.write("")
            print(f"[{panel['name']}] logs file created.")
        
        if panel["type"] == "selenium":
            try:
                s = seleSession(panel["url"])
                s.login(panel["user"], panel["pwd"])
                sessions_to_close.append(s)
                tasks.append(panel_loop(s, panel["name"]))
            except Exception as e:
                print(f"Failed to initialize session for {panel['name']}: {e}")
        
        elif panel["type"] == "ivasms":
            threading.Thread(
                target=start_panel3,
                kwargs={"panel": panel, "loop": loop},
                daemon=True
            ).start()
    if tasks:
        await asyncio.gather(*tasks)

    if not tasks and any(p["type"] == "ivasms" for p in panels.values()):
        while True:
            await asyncio.sleep(3600) # Keep main thread alive

#async info()
#    botinfo = await bot.get_me()
#    print(f"Started, User: {botinfo.username} | Firstname: {botinfo.first_name}")

if __name__ == "__main__":
    with bot:
        #bot.loop.run_until_complete(info())
        bot.loop.run_until_complete(
            bot.send_message(
                -1002993082859,
                "<blockquote><b>OTP RECEIVER ON!</b></blockquote>\n🤖 Bot is watching for SMS...",
                buttons=[
                    [Button.url("👑 Owner", "https://t.me/xion_ensigma")],
                    [Button.url("👨‍💻 Developer", "https://t.me/CrazyTha")],
                    [Button.url("📞 Numbers", "https://t.me/+zGBLO8pOSylmODMx"),
                    Button.url("⏳ OTPS", "https://t.me/xion_otps")],
                ],
                parse_mode="html"
            )
        )

        bot.loop.run_until_complete(main())
