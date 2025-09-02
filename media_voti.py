# media voti

# librerie
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from sys import stdout
import sys, os
import platform
import subprocess
import os
csv_path = "example.csv"


# chek voti
def chek():

    import csv  
    
    # path
    def resource_path(relative_path):
        if hasattr(sys,"_MEIPASS"):
            return os.path.join(sys._MEIPASS,relative_path)
        return os.path.join(os.path.abspath("."),relative_path)

    driver_path = resource_path("chromedriver.exe")
    user_path = "login/id.txt"
    pass_path = "login/password.txt"
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
    # scrittura voti in csv file 
    materie_voto={}
    lista=[]
    iter=0

    for i in voti:
        i=i.strip()
        if i=="RELIGIONE CATTOLICA/ATTIVITA'ALTERNATIVA" or i=="O":
            continue
        if iter==0:
            lista.append(i)
            iter=1
        elif len(str(i))>5:
            try:
                voti_coronologici = lista[1:]
                voti_coronologici.reverse()  # Inverti l'ordine dei voti
                materie_voto[lista[0]]=voti_coronologici
            except:
                continue
            lista=[]
            lista.append(i)
        else:
            lista.append(i)
    # scrittura di ed civica
    voti_coronologici = lista[1:]
    voti_coronologici.reverse()  # Inverti l'ordine dei voti
    materie_voto[lista[0]]=voti_coronologici

    with open(csv_path, 'w', newline='',encoding="utf-8") as csvfile:
        fieldnames = ['materia', 'voto_1','voto_2','voto_3','voto_4','voto_5','voto_6','voto_7','voto_8','voto_9','voto_10', 'media']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for i in materie_voto.keys():
            voti=materie_voto[i]
            totale=0 
            for n in range(len(voti)):
                voto = voti[n].strip()
                if "-" in voto:
                    voto=voto.replace("-", "")
                    voto=float(voto)-0.25
                elif "+" in voto:
                    voto=voto.replace("+", "")
                    voto=float(voto)+0.25
                elif "�" in voto or "½" in voto:
                    voto=voto.replace("�", "")
                    voto=voto.replace("½", "")
                    voto=float(voto)+0.5
                else:
                    voto=float(voto)
                voti[n] = voto  # Convert to float for CSV
                totale+=voto
                m=totale/(len(voti))
            while len(voti)<10:
                voti.append("")
            writer.writerow({'materia': i,
                            fieldnames[1]:voti[0],
                            fieldnames[2]:voti[1],
                            fieldnames[3]:voti[2],
                            fieldnames[4]:voti[3],
                            fieldnames[5]:voti[4],
                            fieldnames[6]:voti[5],
                            fieldnames[7]:voti[6],
                            fieldnames[8]:voti[7],
                            fieldnames[9]:voti[8],
                            fieldnames[10]:voti[9],
                            fieldnames[11]:"{:.2f}".format(m).replace('.', ',')
                            })
    driver.quit()
    return "dati aggiornati"


def media():
    voti_processati = []
    flag = 0
    totale=0
    voti = get_data()
    for k in voti:
        for voto in k[0:len(k)-1]:
            if voto=="EDUCAZIONE CIVICA":
                flag=11
            elif flag>0:
                flag-1
                continue
            if len(str(voto))>5:
                continue
            elif voto=="":
                continue
            voti_processati.append(voto)
    n = len(voti_processati)
    for voto in voti_processati:
        try:
            voto = float(voto)
        except:
            print(f"Errore di conversione per il voto: {voto}")
            continue
        totale+=voto
        m=totale/n
    try:
        print("Media dei voti:", m)
        return m
    except:
        print("Nessun voto trovato o errore nel calcolo della media.")
        return "nessun voto trovato"
    
def quanto_posso_prendere():
    data = get_data()
    l = []
    for i in data:
        materia = i[0]
        media = i[-1]
        totale = 0
        esito = ""
        n = 1
        for j in i[1:-1]:
            if j == "":
                continue
            try:
                totale += float(j.replace(",", "."))
            except:
                print(f"Errore di conversione per il voto: {j}")
            n += 1
        target = n * 6
        v = target - totale
        if v < 6:
            esito = f"puoi prendere: {v:.2f}"
        else:
            esito = f"devi prendere: {v:.2f}"
        l.append(f"{materia} | media:{media} | {esito}")
    return l

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
    data_x = []
    data_y = []
    n=0
    totale=0
    m=0
    flag=False
    voti = get_data()
    dati=[]
    for categoria in voti:
        for voto in categoria:
            voto = voto.strip()
            if choice==voto:
                flag=True
                continue
            if flag:
                if len(voto)>5 or voto=="":
                    break
                dati.append(voto)
    for voto in dati:
        voto=float(voto)
        n+=1
        totale+=voto
        m=totale/n
        data_x.append(n)
        data_y.append(m)
    return data_x , data_y 


def materie():
    data = []
    voti = get_data()
    for materia in voti:
        materia=materia[0]       
        data.append(materia)
    try:
        data.pop()
    except:
        data = "nessun dato"
    return data

def csv():
    if platform.system() == 'Windows':
        os.startfile(csv_path)
    elif platform.system() == 'Darwin':
        subprocess.call(['open', csv_path])
    else:
        subprocess.call(['xdg-open', csv_path])

def get_data():
    import csv
    with open(csv_path, "r", encoding="utf-8") as file:
        voti = csv.reader(file)
        voti = list(voti)
        voti = voti [1:]
    return voti

