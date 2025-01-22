
"""
WARNING:

Please make sure you install the bot dependencies with `pip install --upgrade -r requirements.txt`
in order to get all the dependencies on your Python environment.

Also, if you are using PyCharm or another IDE, make sure that you use the SAME Python interpreter
as your IDE.

If you get an error like:
```
ModuleNotFoundError: No module named 'botcity'
```

This means that you are likely using a different Python interpreter than the one used to install the dependencies.
To fix this, you can either:
- Use the same interpreter as your IDE and install your bot with `pip install --upgrade -r requirements.txt`
- Use the same interpreter as the one used to install the bot (`pip install --upgrade -r requirements.txt`)

Please refer to the documentation for more information at
https://documentation.botcity.dev/tutorials/python-automations/web/
"""


from botcity.web import WebBot, Browser, By
# Import for integration with BotCity Maestro SDK
from botcity.maestro import *

from webdriver_manager.firefox import GeckoDriverManager

# Disable errors if we are not connected to Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False


def main(env):

    
    # Runner passes the server url, the id of the task being executed,
    # the access token and the parameters that this task receives (when applicable).
    maestro = BotMaestroSDK.from_sys_args()
    ## Fetch the BotExecution with details from the task, including parameters
    execution = maestro.get_execution()
    import os

    login = os.environ.get('LOGIN')
    key = os.environ.get('KEY')
    server = os.environ.get('SERVER')

    # Uncomment this if you will deploy this automation.
    maestro.login(
        server=server, 
        login=login, 
        key=key)


    print(f"Task ID is: {execution.task_id}")
    print(f"Task Parameters are: {execution.parameters}")

    bot = WebBot()

    if env == 'test':
        test_process(maestro,bot,execution)
    else:
        orquestration_process(maestro,bot, execution)


def not_found(label):
    print(f"Element not found: {label}")


def get_stock_price(bot):
    price = bot.find_element(".NprOob", By.CSS_SELECTOR).text
    stock_price = f"R${price}"
    return stock_price


def test_process(maestro, bot, execution):

    # Configure whether or not to run on headless mode
    bot.headless = False

    # Uncomment to change the default Browser to Firefox
    bot.browser = Browser.FIREFOX

    # Uncomment to set the WebDriver path
    bot.driver_path = GeckoDriverManager().install()

    # Opens the BotCity website.
    bot.browse("https://www.google.com/")

    # Implement here your logic...
    bot.wait(2000)

    barra_pesquisa = bot.find_element("#APjFqb", By.CSS_SELECTOR)
    barra_pesquisa.click()

    bot.paste("Cotacao B3SA3")
    bot.enter()

    bot.maximize_window()

    # Extrair valor da ação:
    price = get_stock_price(bot)
    
    stock_info = {
        "stock": "B3SA3",
        "price": price
    }

    print(stock_info)

    stocks = ['PETR4', 'VALE3', 'ITUB4', 'RADL3']
    for stock in stocks:
        limpador = bot.find_element(".ExCKkf", By.CSS_SELECTOR)
        limpador.click()
        bot.wait(500)
        bot.paste(f"Cotacao {stock}")
        bot.enter()

        bot.wait(1000)

        price = get_stock_price(bot)
    
        stock_info = {
            "stock": f"{stock}",
            "price": f"R${price}"
        }

        print(stock_info)


    # Finish and clean up the Web Browser
    # You MUST invoke the stop_browser to avoid
    # leaving instances of the webdriver open
    
    bot.stop_browser()

    # Uncomment to mark this task as finished on BotMaestro
    maestro.finish_task(
        task_id=execution.task_id,
        status=AutomationTaskFinishStatus.SUCCESS,
        message="Task Finished OK."
    )


def orquestration_process(maestro, bot, execution):

    # Ler dados do datapool:
    datapool = maestro.get_datapool(label="stocks-pool")

    # Configure whether or not to run on headless mode
    bot.headless = False

    # Uncomment to change the default Browser to Firefox
    bot.browser = Browser.FIREFOX

    # Uncomment to set the WebDriver path
    bot.driver_path = GeckoDriverManager().install()

    # Opens the BotCity website.
    bot.browse("https://www.google.com/")

    # Implement here your logic...
    bot.wait(2000)
    try:
        barra_pesquisa = bot.find_element("#APjFqb", By.CSS_SELECTOR)
        barra_pesquisa.click()
    except Exception as error:
        filepath = 'resources/screenshot.png'
        bot.save_screenshot(filepath)
        attachments = ['resources/error.png', '/resources/test.txt']

        maestro.error(task_id=execution.task_id, exception=error, tags={"custom": "tag"}, screenshot=filepath, attachments=attachments)

    bot.paste("Cotacao ")
    bot.enter()

    bot.maximize_window()

    while datapool.has_next():
        # Buscar o próximo item do Datapool
        item = datapool.next(task_id=execution.task_id)
        if item is None:
            # O item pode ser None se outro processo o consumiu antes
            break
        
        stock = item["stock"]
        try:
            limpador = bot.find_element(".ExCKkf", By.CSS_SELECTOR)
            limpador.click()
            bot.wait(500)
            bot.paste(f"Cotacao {stock}")
            bot.enter()

            bot.wait(1000)

            price = get_stock_price(bot)
        
            stock_info = {
                "stock": f"{stock}",
                "price": price
            }

            print(stock_info)

            item["price"] = price

            maestro.new_log_entry(
                activity_label="stock-quotation",
                values={
                    "stock": stock,
                    "price": price,
                    "status": "Informations about Stock were collected SUCCESSFULLY."
                    }
                )

            # Finalizando como 'DONE' após processamento
            item.report_done()

        except Exception as error:

            maestro.new_log_entry(
                activity_label="stock-quotation",
                values={
                    "stock": stock,
                    "price": "",
                    "status": "ERROR while processing item"
                    }
                )
            filepath = 'resources/screenshot.png'
            bot.save_screenshot(filepath)
            attachments = ['resources/error.png', '/resources/test.txt']

            maestro.error(task_id=execution.task_id, exception=error, tags={"custom": "tag"}, screenshot=filepath, attachments=attachments)



if __name__ == '__main__':
    env='test'
    main(env)
