# media voti

# librerie
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
import time
import CSV_Voti
import getpass
from sys import stdout

# chek voti
def chek():
    codice=input("codice: ")
    stdout.write("\033[91mATTENZIONE la password che inserirai non verra visualizzata graficamente ma ogni carattere che scrivi verra contato!\033[0m\n")
    password=getpass.getpass("password: ")
    input(f"hai inserito una password lunga {len(password)} caratteri, invia per proseguire: ")
    # usa in background
    option = Options()
    option.add_argument("--headless")

    # setup driver
    service = Service("chromedriver.exe")  
    driver = webdriver.Chrome(service=service,options=option)

    # applica stealth
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win64",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    # open the website
    driver.get("https://web.spaggiari.eu/home/app/default/login.php")

    # login
    user=driver.find_element(By.ID, "login")
    password_log=driver.find_element(By.ID, "password")
    user.send_keys(codice)
    password_log.send_keys(password)
    bottone = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    bottone.click()

    time.sleep(10)
    try:
        bottone = driver.find_element(By.CSS_SELECTOR, "button[type='button']")
        bottone.click()
    except:
        pass
    try:
        anno_precedente = driver.find_element(By.CSS_SELECTOR, "p[class='handwriting_2 ']")
        anno_precedente.click()
    except:
        pass
    # Passa alla nuova finestra/scheda
    try:
        time.sleep(2)  # attesa breve per apertura finestra
        windows = driver.window_handles
        driver.switch_to.window(windows[-1])
    except:
        print("password errata")

    time.sleep(10)
    # Trova tutte le righe della tabella con classe 'griglia rigtab'
    righe = driver.find_elements(By.CSS_SELECTOR, "tr[align='left']")
    if len(righe) >= 5:
        righe[4].click()  # Indici Python partono da 0, quindi la quinta è [4]
    else:
        stdout.write("\033[91mCredenziali errate!\033[0m\n")
        return
    time.sleep(4)
    # Clicca sul bottone che contiene il testo "Tutto"
    tutto_button = driver.find_element(By.XPATH, "//button[contains(., 'Tutto')]")
    tutto_button.click()

    time.sleep(8)

    # Trova tutti i voti nei paragrafi all'interno della struttura tr>td>div>p
    voti = []
    trs = driver.find_elements(By.TAG_NAME, "tr")
    for tr in trs:
        tcs = tr.find_elements(By.TAG_NAME, "td")
        for tc in tcs:
            if tc.get_attribute("colspan") == "48":
                voti.append(tr.text.strip())
            if tc.get_attribute("colspan") == "2":
                divs = tc.find_elements(By.TAG_NAME, "div")
                for div in divs:
                    if div.get_attribute("class").strip() == "cella_div cella_div f_reg_voto_dettaglio":
                        continue
                    paragrafi = div.find_elements(By.TAG_NAME, "p")
                    for p in paragrafi:
                        testo = p.text.strip()
                        if testo:  # solo paragrafi non vuoti
                            voti.append(testo)
    voti=voti[3:]
    print("Voti trovati:", voti)
    with open("voti.txt", "w") as file:
        for voto in voti:
            file.write(voto + "\n")
        file.write("riga adizzionale")
    driver.quit()
    print("dati aggiornati!")


def media():
    with open("voti.txt", "r") as file:
        voti = file.readlines()
        totale=0
        for voto in voti:
            voto = voto.strip()
            if "-" in voto:
                voto=voto.replace("-", "")
                voto=float(voto)-0.25
            elif "+" in voto:
                voto=voto.replace("+", "")
                voto=float(voto)+0.25
            elif "½" in voto or "ï¿" in voto:
                voto=voto.replace("½", "")
                voto=voto.replace("ï¿", "")
                voto=float(voto)+0.5
            else:
                try:
                    voto=float(voto)
                except:
                    continue
            totale+=voto
            m=totale/(len(voti)-12)
        print("Media dei voti:", m)
    
def main():
    print("""
1) aggiorna lista voti
2) media
3) csv
          """)
    while True:
        try:
            scelta=int(input("Scegli un'opzione: "))
            break
        except ValueError:
            stdout.write("\033[91minserire un numero!\033[0m\n")
    if scelta<1 or scelta>3:
        stdout.write("\033[91mInserisci un numero tra 1 e 3!\033[0m")
    elif scelta==1:
        chek()
    elif scelta==2:
        media()
    elif scelta==3:
        CSV_Voti.csv()

while True:
   main()
