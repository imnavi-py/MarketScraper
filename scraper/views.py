from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework import generics
from .models import MarketData
from .serializers import MarketDataSerializer

# View برای لاگین و دریافت توکن
@api_view(['POST'])
def login(request):
    # دریافت نام کاربری و رمز عبور از body درخواست
    username = request.data.get('username')
    password = request.data.get('password')

    # تایید اعتبار کاربر
    user = authenticate(request, username=username, password=password)
    if user is not None:
        # ایجاد توکن برای کاربر (اگر توکنی از قبل نداشته باشد)
        token, created = Token.objects.get_or_create(user=user)

        # برگرداندن توکن
        return Response({
            'token': token.key
        })
    else:
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# API برای گرفتن تمام داده‌ها
class MarketDataListView(generics.ListAPIView):
    queryset = MarketData.objects.all()
    serializer_class = MarketDataSerializer

# API برای گرفتن یک داده خاص بر اساس id
class MarketDataRetrieveView(generics.RetrieveAPIView):
    queryset = MarketData.objects.all()
    serializer_class = MarketDataSerializer
    lookup_field = 'id'  # استفاده از id برای جستجو



# import json
# import time
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from django.http import JsonResponse

# def get_market_data(request):
#     count = int(request.GET.get('count', 10))
#     print(f"Scraping {count} posts.")

#     chrome_options = Options()
#     chrome_options.add_argument('--headless')  # اجرا به صورت headless
#     chrome_options.add_argument('--disable-gpu')  # غیرفعال کردن GPU
#     chrome_options.add_argument('--no-sandbox')  # غیرفعال کردن sandbox
#     chrome_options.add_argument('--disable-dev-shm-usage')  # جلوگیری از مشکلات shared memory
#     chrome_options.add_argument('--disable-extensions')  # غیرفعال کردن افزونه‌ها
#     chrome_options.add_argument('--remote-debugging-port=9222')  # رفع مشکلات شبیه‌سازی headless

#     chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
#     chrome_options.add_argument('--disable-blink-features=AutomationControlled')

#     driver_path = '/usr/bin/chromedriver' 

#     try:
#         driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
        
#         driver.get("https://cointelegraph.com/tags/markets")  

#         print("Waiting for the page to load...")
#         WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".tag-page__posts-col li")))
        
#         time.sleep(3)
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(3)
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        
        
#         # for _ in range(3):
            
#         #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         #     time.sleep(3)
#         #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         #     time.sleep(3)
#         #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

#         print("Searching for posts...")
#         posts = driver.find_elements(By.CSS_SELECTOR, ".tag-page__posts-col li")
#         print(f"Found {len(posts)} posts.")
        
#         data = []
#         for post in posts[:count]:
#             try:
#                 title = post.find_element(By.CLASS_NAME, "post-card-inline__title").text
#                 title_link = post.find_element(By.CLASS_NAME, "post-card-inline__title-link").get_attribute("href")
#                 text = post.find_element(By.CLASS_NAME, "post-card-inline__text").text

#                 image_element = WebDriverWait(post, count).until(
#                     EC.presence_of_element_located((By.CLASS_NAME, "lazy-image__img"))
#                 )
#                 image_url = image_element.get_attribute("src")
                
#                 data.append({
#                     "title": title,
#                     "title_link": title_link,
#                     "text": text,
#                     "image_url": image_url
#                 })
#             except Exception as e:
#                 print(f"Error in processing post: {e}")

#         information = {
#             "scraped_count": len(data),
#             "data": data
#         }

#         driver.save_screenshot("screenshot.png")
        
#         return JsonResponse(information)

#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=400)

#     finally:
#         driver.quit()









