from django.shortcuts import render
from django.http import HttpResponse
from playwright.sync_api import sync_playwright
from anticaptchaofficial.recaptchav3proxyless import recaptchaV3Proxyless
from requests.exceptions import RequestException

from .models import Account

def index(request):
    return render(request, 'index.html')

def start(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            # Получение данных аккаунта из модели Account
            account = Account.objects.get(username=username)

            # Инициализация объекта recaptchaV3Proxyless с использованием API ключа
            solver = recaptchaV3Proxyless()
            solver.set_verbose(1)
            solver.set_key('API_KEY') #можно(нужно) вывести в отдельный файл

            # Получение данных капчи
            captcha_id = solver.create_task('https://ru.stripchat.global/login')

            # Ожидание решения капчи
            solver.wait_for_result(captcha_id)

            # Получение результата капчи
            captcha_result = solver.solve_and_return_solution()

            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                page = browser.new_page()

                # Открытие браузера и переход на заданный URL
                page.goto('https://ru.stripchat.global/login')

                # Ввод почты и пароля
                page.fill('input[name="email"]', account.email)
                page.fill('input[name="password"]', account.password)

                # Установка результата капчи
                page.evaluate(f'document.getElementById("g-recaptcha-response").innerHTML = "{captcha_result["gRecaptchaResponse"]}"')

                # Ввод значения из формы и переход по нему
                value = request.POST.get('value')
                page.fill('input[name="search"]', value)
                page.press('input[name="search"]', 'Enter')

                browser.close()

            return HttpResponse('Автоматизация завершена')
        except RequestException as e:
            return HttpResponse('Произошла ошибка при обращении к серверу')
        except Account.DoesNotExist:
            return HttpResponse('Аккаунт не найден')
        except Exception as e:
            return HttpResponse('Произошла непредвиденная ошибка')
    else:
        return HttpResponse('Метод не разрешен')
