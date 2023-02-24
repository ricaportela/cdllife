from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep
import pandas as pd
import re


def grab_data(driver):
    data = []
    for div in driver.find_elements(
        By.XPATH, '//*[contains(@class, "lightCard lightCardSizeDeskTop")]'
    ):
        # jobs = driver.find_elements(By.XPATH,'//*[contains(@class, "lightCard lightCardSizeDeskTop")]')
        descricao = div.find_element(
            By.XPATH, './/div[contains(@class, "description truncate")]'
        ).text
        descricao_list = descricao.split(" • ")
        if descricao_list[-1].strip() == "&nbsp;️️":
            descricao_list = descricao_list[:-1]

        descricao_string = " • ".join(descricao_list)
        descricao_string = descricao_string.replace("\n", "").replace("\r", "")

        # bonusTag = div.find_elements(By.XPATH, './/div[contains(@class, "bonusTags-tag")]')
        # if bonusTag:
        #     bonusTag = bonusTag
        # else:
        #     bonusTag = "-"

        nomeEmpresa = div.find_element(
            By.XPATH, './/div[contains(@class, "companyNameLightCard")]'
        ).text
        tipoMotorista = div.find_element(
            By.XPATH, './/div[contains(@class, "tagWrapper is-bottom")]//div'
        ).text
        headline = div.find_element(
            By.XPATH, './/div[contains(@class, "headLine")]'
        ).text
        # bonusTag = bonusTag
        descricao = descricao_string
        
        data.append([nomeEmpresa, tipoMotorista, headline, descricao])

    return data


def top(driver):
    sleep(0.5)
    driver.execute_script("window.scrollTo(0, 0);")


def bottom(driver):
    sleep(0.5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def page_down(driver):
    actions = ActionChains(driver)
    actions.pause(0.3)
    actions.send_keys(Keys.PAGE_DOWN)
    actions.perform()


def page_up(driver):
    actions = ActionChains(driver)
    actions.pause(0.3)
    actions.send_keys(Keys.PAGE_UP)
    actions.perform()


def atualizar(driver, html):
    bottom(driver)
    top(driver)
    for _ in range(0, 18):
        page_up(driver)

    for _ in range(0, 258):
        page_down(driver)


def get_tot_results(driver):
    elements = driver.find_elements(
        By.XPATH, "//*[@id='svelte']/main/div[2]/div[3]/span/div/span"
    )
    current_value = []

    for element in elements:
        text = element.text  # Aqui está pegando o texto dentro do elemento
        resultado = re.search(r"\d+", text)
        if resultado:
            current_value.append(int(resultado.group(0)))
        else:
            current_value.append(0)

    prev_total = sum(current_value)
    return prev_total


if __name__ == "__main__":

    driver = webdriver.Chrome()

    driver.get("https://jobs.cdllife.com/search/listings")

    driver.maximize_window()

    sleep(0.9)

    html = driver.find_element(By.XPATH, "//body")
    previous_value = 0

    while True:
        elements = driver.find_elements(
            By.XPATH, "//*[@id='svelte']/main/div[2]/div[3]/span/div/span"
        )
        current_value = []

        for element in elements:
            text = element.text  # Aqui está pegando o texto dentro do elemento
            resultado = re.search(r"\d+", text)

            if resultado:
                current_value.append(int(resultado.group(0)))
            else:
                current_value.append(0)

        current_total = sum(current_value)
        print(f'Current total = {current_total}')
        print(f'Current value = {current_value}')

        if previous_value == current_total:
            list_jobs = grab_data(driver)
            df = pd.DataFrame(
                list_jobs,
                columns=["Nome da Empresa", "Tipo de Motorista", "Título", "Descrição"],
            )
            df.to_csv("trucksjobs.csv", index=False)

            input(f"Total {current_total} registro(s) ")
            break

        previous_value = current_total
        html = driver.find_element(By.XPATH, "//body")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        bottom(driver)
        atualizar(driver, html)
        current_total = get_tot_results(driver)
