# media voti

# librerie
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from sys import stdout
import sys, os


# chek voti
def chek():
    
    # path
    def resource_path(relative_path):
        if hasattr(sys,"_MEIPASS"):
            return os.path.join(sys._MEIPASS,relative_path)
        return os.path.join(os.path.abspath("."),relative_path)

    driver_path = resource_path("chromedriver.exe")
    user_path = "login/id.txt"
    pass_path = "login/password.txt"
    voti_path = "voti.txt"
    browser_mode = resource_path("Browser_mode.txt")

    with open(user_path, "r") as file:
        codice = file.read().strip()
    if codice=="":
        print("nessun codice")
        return "nessun id"
    with open(pass_path, "r") as file:
        password = file.read().strip()
    if password=="":
        print("nessuna password trovata")
        return "nessuna password"
    # usa in background
    option = Options()
    with open(browser_mode,"r") as f:
        status = f.read()
    if status=="0":
        option.add_argument("--headless")
    option.add_argument("--no-sandbox")
    option.add_argument("--disable-gpu")
    option.add_argument("--disable-dev-shm-usage")

    # setup driver
    service = Service(driver_path)  
    driver = webdriver.Chrome(service=service,options=option)


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
        driver.quit()
        return "credenziali errate"
        

    time.sleep(10)
    # Trova tutte le righe della tabella con classe 'griglia rigtab'
    righe = driver.find_elements(By.CSS_SELECTOR, "tr[align='left']")
    if len(righe) >= 5:
        righe[4].click()  # Indici Python partono da 0, quindi la quinta ? [4]
    else:
        stdout.write("\033[91mCredenziali errate!\033[0m\n")
        driver.quit()
        return "credenziali errate"
    time.sleep(4)
    try:
    # Clicca sul bottone che contiene il testo "Tutto"
        tutto_button = driver.find_element(By.XPATH, "//button[contains(., 'Tutto')]")
        tutto_button.click()
    except:
        driver.quit()
        return "credenziali errate"

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
    with open(voti_path, "w",encoding="utf-8") as file:
        for voto in voti:
            file.write(voto + "\n")
        file.write("riga adizzionale")
    driver.quit()
    print("dati aggiornati!")
    return "dati aggiornati"


def media():
    voti_path = "voti.txt"


    with open(voti_path, "r",encoding="utf-8") as file:
        n = 0
        voti = file.readlines()
        totale=0
        for voto in voti:
            voto = voto.strip()
            if "EDUCAZIONE CIVICA" in voto:
                break
            if "-" in voto:
                voto=voto.replace("-", "")
                voto=float(voto)-0.25
                n+=1
            elif "+" in voto:
                voto=voto.replace("+", "")
                voto=float(voto)+0.25
                n+=1
            elif "½" in voto:
                voto=voto.replace("½", "")
                voto=float(voto)+0.5
                n+=1
            else:
                try:
                    voto=float(voto)
                    n+=1
                except:
                    continue
            totale+=voto
            m=totale/n
        try:
            print("Media dei voti:", m)
            return m
        except:
            print("Nessun voto trovato o errore nel calcolo della media.")
            return "nessun voto trovato"
    

    # grafico generale da fixare
""" def grafico_generale():
    voti_path = "voti.txt"
    data_x = []
    data_y = [] 
    n=0
    totale=0
    m=0
    with open(voti_path, "r", encoding="utf-8") as file:
        voti = file.readlines()
        for voto in voti:
            voto = voto.strip()
            if "EDUCAZIONE CIVICA" in voto:
                break
            if "-" in voto:
                voto=voto.replace("-", "")
                voto=float(voto)-0.25
                n+=1
            elif "+" in voto:
                voto=voto.replace("+", "")
                voto=float(voto)+0.25
                n+=1
            elif "½" in voto:
                voto=voto.replace("½", "")
                voto=float(voto)+0.5
                n+=1
            else:
                try:
                    voto=float(voto)
                    n+=1
                except:
                    continue
            totale+=voto
            m=totale/n
            data_x.append(n)
            data_y.append(m)
    return data_x , data_y
 """
def graficoXmateria(choice):
    voti_path = "voti.txt"
    data_x = []
    data_y = []
    n=0
    totale=0
    m=0
    flag=False
    with open(voti_path, "r", encoding="utf-8") as file:
        voti = file.readlines()
        dati=[]
        for voto in voti:
            voto = voto.strip()
            if choice in voto:
                flag=True
                continue
            if flag:
                if len(voto)>5:
                    break
                dati.append(voto)
        inverso_dati=[]
        for i in range(len(dati)-1,-1,-1):
            inverso_dati.append(dati[i])
        for voto in inverso_dati:
            if "-" in voto:
                voto=voto.replace("-", "") 
                voto=float(voto)-0.25
                n+=1
            elif "+" in voto:
                voto=voto.replace("+", "")
                voto=float(voto)+0.25
                n+=1
            elif "½" in voto:
                voto=voto.replace("½", "")
                voto=float(voto)+0.5
                n+=1
            else:
                try:
                    voto=float(voto)
                    n+=1
                except:
                    break
            try:
                totale+=voto
                m=totale/n
                data_x.append(n)
                data_y.append(m)
            except:
                pass
    return data_x , data_y 


def materie():
    voti_path = "voti.txt"
    data = []
    with open(voti_path, "r", encoding="utf-8") as file:
        voti = file.readlines()
        for voto in voti:
            voto=voto.strip()       
            if len(voto)>5:
                if voto!="RELIGIONE CATTOLICA/ATTIVITA'ALTERNATIVA":
                    data.append(voto)
    try:
        data.pop()
    except:
        data = "nessun dato"
    return data

    
