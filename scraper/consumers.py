# consumers.py
import json
import time
from channels.generic.websocket import AsyncWebsocketConsumer
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from channels.db import database_sync_to_async

class MarketDataConsumer(AsyncWebsocketConsumer):
    
    
    async def connect(self):
        import asyncio
        Authorization = "691b0ba70730e772997d9446e1378b9e65bb94fa"
        self.user = await self.authenticate_user(Authorization)
        if self.user is None:
            await self.close(code=4003)  # Unauthorized
            return

        self.room_group_name = "market_data"
        self.is_connected = True
        self.driver = None  # مقدار اولیه برای درایور
        self.monitor_task = asyncio.create_task(self.monitor_connection())

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        self.is_connected = False  # به‌روزرسانی وضعیت اتصال
        print("WebSocket disconnected.")

        # بستن منابع
        if hasattr(self, "driver") and self.driver is not None:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None

        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

        # لغو تسک نظارت
        if hasattr(self, "monitor_task"):
            self.monitor_task.cancel()

    async def receive(self, text_data):
        count = int(text_data)
        if not self.is_connected:
            return

        try:
            data = await self.get_market_data(count)
            if self.is_connected:  # اطمینان از اینکه اتصال هنوز برقرار است
                await self.send(text_data=json.dumps(data))
        except Exception as e:
            print(f"Error during data scraping: {e}")
            if self.is_connected:
                await self.send(text_data=json.dumps({"error": str(e)}))

    async def get_market_data(self, count):
        from selenium.webdriver.chrome.service import Service
        import asyncio  # برای زمان‌بندی دقیق و مدیریت غیرهمزمان
    
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # برای جلوگیری از تشخیص خودکار
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        driver_path = "C:\chromedriver-win64\chromedriver.exe"
    
        print("Launching browser...")
        await self.send(text_data=json.dumps({"message": "Launching browser..."}))
        await asyncio.sleep(1)
    
        self.driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
        self.driver.get("https://cointelegraph.com/tags/markets")
        if not self.is_connected:
            print("Connection is closed, exiting browser launch.")
            self.driver.quit()
            return
    
        print("Opened main page. Waiting for elements...")
        await self.send(text_data=json.dumps({"message": "Opened main page. Waiting for elements..."}))
    
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".tag-page__posts-col li")))
        time.sleep(3)
        height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_step = height // 5  # تقسیم صفحه به سه قسمت برابر

        # اسکرول به پایین صفحه در سه مرحله
        for i in range(1, 6):
            scroll_position = scroll_step * i
            self.driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            time.sleep(1)
        time.sleep(3)
        if not self.is_connected:
            print("Connection lost during page load.")
            self.driver.quit()
            return
        
        print("Fetching posts...")
        await self.send(text_data=json.dumps({"message": "Fetching posts..."}))
        await asyncio.sleep(1)
    
        posts = self.driver.find_elements(By.CSS_SELECTOR, ".tag-page__posts-col li")
        print(posts)
        print(f"Found {len(posts)} posts.")
        await self.send(text_data=json.dumps({"message": f"Found {len(posts)} posts."}))
        
        data = []
    
        for idx, post in enumerate(posts[:count]):
            if not self.is_connected:
                print("Disconnected during data scraping. Exiting loop...")
                self.driver.quit()
                break
    
            try:
                print(f"Processing post {idx + 1}/{count}...")
                await self.send(text_data=json.dumps({"message": f"Processing post {idx + 1}/{count}..."}))
                if not self.is_connected:
                    print("Connection lost during page load.")
                    self.driver.quit()
                    return
                await asyncio.sleep(1)
                
    
                title = post.find_element(By.CLASS_NAME, "post-card-inline__title").text
                title_link = post.find_element(By.CLASS_NAME, "post-card-inline__title-link").get_attribute("href")
                text = post.find_element(By.CLASS_NAME, "post-card-inline__text").text
                image_element = WebDriverWait(post, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "lazy-image__img"))
                )
                image_url = image_element.get_attribute("src")
    
                print(f"Post title: {title}")
                await self.send(text_data=json.dumps({"message": f"Post title: {title}"}))
                if not self.is_connected:
                    print("Disconnected during data scraping. Exiting loop...")
                    break
                await asyncio.sleep(1)
    
                print(f"Navigating to link: {title_link}")
                await self.send(text_data=json.dumps({"message": f"Navigating to link: {title_link}"}))
                if not self.is_connected:
                    print("Disconnected during data scraping. Exiting loop...")
                    break
                await asyncio.sleep(1)
    
                self.driver.execute_script("window.open('');")
                self.driver.switch_to.window(self.driver.window_handles[-1])
    
                try:
                    self.driver.get(title_link)
                    print("Opened post page.")
                    if not self.is_connected:
                        print("Disconnected during data scraping. Exiting loop...")
                        break
                    await self.send(text_data=json.dumps({"message": "Opened post page."}))
                    await asyncio.sleep(1)
    
                    article_element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "post__article"))
                    )
                    content_element = article_element.find_element(By.CLASS_NAME, "post-content")
                    paragraphs = content_element.find_elements(By.TAG_NAME, "p")
                    paragraph_texts = [p.text for p in paragraphs if p.text.strip()]
    
                    print(f"Found {len(paragraph_texts)} paragraphs.")
                    await self.send(text_data=json.dumps({"message": f"Found {len(paragraph_texts)} paragraphs."}))
                    await asyncio.sleep(1)
    
                    data.append({
                        "title": title,
                        "title_link": title_link,
                        "text": text,
                        "image_url": image_url,
                        "paragraphs": paragraph_texts,
                    })
    
                except Exception as e:
                    print(f"Error processing link {title_link}: {e}")
                    await self.send(text_data=json.dumps({"message": f"Error processing link {title_link}: {e}"}))
    
                finally:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
    
            except Exception as e:
                print(f"Error processing post {idx + 1}: {e}")
                await self.send(text_data=json.dumps({"message": f"Error processing post {idx + 1}: {e}"}))
    
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
    
        self.driver.quit()
        print("Browser closed.")
        if data:  # اگر داده‌ها خالی نبودند
            await self.save_data_to_db(data)
        return {
            "scraped_count": len(data),
            "data": data
        }
        
        
        
    @database_sync_to_async
    def authenticate_user(self, token):
        from rest_framework.authtoken.models import Token
        try:
            # بررسی صحت توکن و دیکود کردن آن
            token_obj = Token.objects.get(key=token)  # گرفتن توکن از دیتابیس
            user = token_obj.user  # دریافت کاربر مرتبط با توکن
            return user
        except Token.DoesNotExist:
            print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! تAuthentication error: Token does not exist.")
            return None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
        
    async def monitor_connection(self):
        import asyncio
        while self.is_connected:
            await asyncio.sleep(1)  # بررسی وضعیت اتصال هر ۱ ثانیه
            if not self.is_connected:
                print("Connection lost. Closing resources...")
                if self.driver is not None:  # اگر درایور وجود دارد، آن را ببندید
                    try:
                        self.driver.quit()
                    except Exception as e:
                        print(f"Error closing WebDriver in monitor: {e}")
                    finally:
                        self.driver = None
                break
    
    @database_sync_to_async
    def save_data_to_db(self, data):
        from .models import MarketData
        if data:
            for entry in data:
                try:
                    market_data = MarketData.objects.create(
                        title=entry['title'],
                        title_link=entry['title_link'],
                        text=entry['text'],
                        image_url=entry['image_url'],
                        paragraphs=entry['paragraphs']
                    )
                    print(f"Data saved to database: {market_data.title}")
                except Exception as e:
                    print(f"Error saving data to database: {e}")

	