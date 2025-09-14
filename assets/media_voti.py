# librerie
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from sys import stdout
import sys, os
import platform
import subprocess
import os
from openpyxl import workbook 
from openpyxl.styles import PatternFill , Font ,Alignment ,Border ,Side
from openpyxl.formatting.rule import CellIsRule
import json
from datetime import date
import keyring as ky
import fpdf as fp
import matplotlib.pyplot as plt
import matplotlib as mpl


def resource_path(relative_path):
    if hasattr(sys,"_MEIPASS"):
        return os.path.join(sys._MEIPASS,relative_path)
    return os.path.join(os.path.abspath("."),relative_path)

excel_path = "voti.xlsx"
numer_materie_path = "archivio/n_materie.txt"
grafico_gen_path = "archivio/dati_grafico.json"
service_name_id = "Classeviva-Medie-id"
service_name_password = "Classeviva-Medie-password"
nome_path = "archivio/nome.txt"
path_logo_1 = resource_path("assets/logo.png")
path_logo_2 = resource_path("assets/dashboard.png")
path_grafico = resource_path("assets/grafico.png")
path_ciambella = resource_path("assets/ciambella.png")
path_qr_code = [resource_path("assets/qrcode_discord.png"),resource_path("assets/qrcode_github.png"),resource_path("assets/qrcode_instagram.png")]
path_report = "archivio/report.pdf"


# chek voti
def login():

    browser_mode = resource_path("assets/Browser_mode.txt")

    #controllo credenziali
    codice = ky.get_password(service_name_id,"user")
    if codice=="" or codice==None:
        print("nessun codice")
        return "nessun id"
    password = ky.get_password(service_name_password,"user")
    if password=="" or password==None:
        print("nessuna password trovata")
        return "nessuna password"
    
    # usa in background e altre opzioni
    option = Options()
    with open(browser_mode,"r") as f:
        status = f.read()
    if status=="0":
        option.add_argument("--headless")
    option.add_argument("--no-sandbox")
    option.add_argument("--disable-gpu")
    option.add_argument("--disable-dev-shm-usage")
    option.add_experimental_option("detach", True) # non chiude il browser

    # setup driver
    driver = webdriver.Chrome(options=option)


    # open the website
    driver.get("https://web.spaggiari.eu/home/app/default/login.php")

    # login
    user=driver.find_element(By.ID, "login")
    password_log=driver.find_element(By.ID, "password")
    user.send_keys(codice)
    password_log.send_keys(password)
    bottone = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    bottone.click()

    return "ok"

def chek(anno):

    browser_mode = resource_path("assets/Browser_mode.txt")

    #controllo credenziali
    codice = ky.get_password(service_name_id,"user")
    if codice=="" or codice==None:
        print("nessun codice")
        return "nessun id"
    password = ky.get_password(service_name_password,"user")
    if password=="" or password==None:
        print("nessuna password trovata")
        return "nessuna password"
    
    # usa in background e altre opzioni
    option = Options()
    with open(browser_mode,"r") as f:
        status = f.read()
    if status=="0":
        option.add_argument("--headless")
    option.add_argument("--no-sandbox")
    option.add_argument("--disable-gpu")
    option.add_argument("--disable-dev-shm-usage")

    # setup driver
    driver = webdriver.Chrome(options=option)


    # open the website
    driver.get("https://web.spaggiari.eu/home/app/default/login.php")

    # login
    user=driver.find_element(By.ID, "login")
    password_log=driver.find_element(By.ID, "password")
    user.send_keys(codice)
    password_log.send_keys(password)
    bottone = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    bottone.click()

    # naviga fino al anno precedente
    time.sleep(5)
    if anno=="precedente":
        try:
            wait = WebDriverWait(driver, 10)
            bottone = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='button']")))
            bottone.click()
        except:
            pass
        try:
            wait = WebDriverWait(driver, 10)
            anno_precedente = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "p.voce_menu_colonna_sx")))
            anno_precedente.click()
            time.sleep(2)
        except:
            pass
        # Passa alla nuova finestra/scheda
        try:
            windows = driver.window_handles
            driver.switch_to.window(windows[-1])
        except:
            driver.quit()
            return "credenziali errate"
        
        time.sleep(20) # attesa per caricamento pagina

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

    time.sleep(4)

    # Trova tutti i voti nei paragrafi all'interno della struttura tr>td>div>p
    date=[]
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
                        try:
                            date.pop()
                        except:
                            pass
                        continue
                    paragrafi = div.find_elements(By.TAG_NAME, "p")
                    for p in paragrafi:
                        testo = p.text.strip()
                        if testo:  # solo paragrafi non vuoti
                            voti.append(testo)
            if tc.get_attribute("colspan") == "5": # colonna data
                ps = tc.find_elements(By.TAG_NAME, "p")
                for par in ps:
                    spans = par.find_elements(By.TAG_NAME, "span")
                    for span in spans:
                        testo = span.text.strip()
                        if testo:  # solo paragrafi non vuoti
                            if testo!="Orale" and testo!="Scritto/Grafico" and testo!="Pratico" and testo!="Scritto" and testo!="Grafico" and testo!="Voto Test":
                                date.append(testo)
                
    voti=voti[3:]
    driver.quit()

    # scrittura dati grafico generale
    l=[]
    n=0
    flag=False
    for i in voti:
        if len(i)>5:
            l.append([i,""])
        else:
            if i in "ODBSN":
                pass
            elif "-" in i:
                i=i.replace("-", "")
                i=float(i)-0.25
            elif "+" in i:
                i=i.replace("+", "")
                i=float(i)+0.25
            elif "½" in i or "�" in i:
                i=i.replace("½", "")
                i=i.replace("�", "")
                i=float(i)+0.5
            else:
                i=float(i)
            l.append([i,date[n]])
            n+=1
    date_processate = []
    for i in l:
        voto = i[0]
        if len(str(voto))>5:
            if voto=="EDUCAZIONE CIVICA" or voto=="RELIGIONE CATTOLICA/ATTIVITA'ALTERNATIVA":
                flag=True
            else:
                flag=False
        elif flag:
            continue
        else:
            date_processate.append(i)
    with open(grafico_gen_path,"w") as f:
        json.dump(date_processate,f)


    # scrittura voti in excel file 
    materie_voto={}
    lista=[]
    iter=0

    # rendere tutti i voti float ed escludere religione
    for i in voti:
        i=i.strip()
        if i=="RELIGIONE CATTOLICA/ATTIVITA'ALTERNATIVA" or i in "ODBSN":
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
            if "EDUCAZIONE CIVICA" in i:
                break
            if "-" in i:
                i=i.replace("-", "")
                i=float(i)-0.25
            elif "+" in i:
                i=i.replace("+", "")
                i=float(i)+0.25
            elif "½" in i:
                i=i.replace("½", "")
                i=float(i)+0.5
            else:
                try:
                    i=float(i)
                except:
                    continue
            lista.append(i)

    # scrittura di ed civica
    voti_coronologici = lista[1:]
    voti_coronologici.reverse()  # Inverti l'ordine dei voti
    materie_voto[lista[0]]=voti_coronologici

    # scrittura numero materie
    numero_materie = len(materie_voto.keys())
    with open(numer_materie_path,"w") as f:
        f.write(str(numero_materie))

   # creazione excel file
    wb = workbook.Workbook()
    ws = wb.active
    ws.title = "Voti"

    ws.append(['Materia', 'Voto_1','Voto_2','Voto_3','Voto_4','Voto_5','Voto_6','Voto_7','Voto_8','Voto_9','Voto_10', 'Media'])

    riga = 2
    for i in materie_voto.keys():
        voti=materie_voto[i]
        ws.append([i]+voti)
        ws[f"L{riga}"] = f"=AVERAGE(B{riga}:K{riga})"
        riga += 1

    # stile excel
    stile_allineamento = Alignment(horizontal="center",vertical="center")
    bold = Font(bold=True)
    fieldnames_background_color = PatternFill(start_color="99D6FB",fill_type="solid")
    materie_background_color = PatternFill(start_color="F6FE9F",fill_type="solid")
    voti_background_color = PatternFill(start_color="B6B6B6",fill_type="solid")
    medie_background_color = PatternFill(start_color="FFAFE1",fill_type="solid")
    thin = Side(style="thin",color="000000")
    bordo = Border(left=thin,top=thin,right=thin,bottom=thin)
    for row in ws.iter_rows(min_row=1,max_row=len(materie_voto.keys())+1,min_col=1,max_col=12):
        for cell in row:
            cell.alignment = stile_allineamento
            cell.border = bordo
            if cell.row==1:
                cell.fill = fieldnames_background_color
                cell.font = bold
            elif cell.row>1 and cell.column==1:
                cell.fill = materie_background_color
                cell.font = bold
            elif cell.row>1 and cell.column==12:
                cell.fill = medie_background_color
            else:
                cell.fill = voti_background_color
            
    ws.column_dimensions["A"].width = 55

    # formattazione celle 
    font = Font(bold=True,color="ff0000")
    celle_da_formattare = f"B2:L{numero_materie+1}"
    rule = CellIsRule(operator="lessThan",formula=["6"],font=font)
    ws.conditional_formatting.add(celle_da_formattare,rule)

    wb.save(excel_path)
    return "dati aggiornati"

def media():
    # calcolo media senza inculedere ed civica
    voti_processati = []
    flag = 0
    totale=0
    voti = get_data()
    if voti == "nessun voto trovato" or voti=="nessun file":
        return voti

    for k in voti:
        for voto in k[0:len(k)-1]:
            if voto=="EDUCAZIONE CIVICA":
                flag=11
            elif flag>0:
                flag-1
                continue
            if len(str(voto))>5:
                continue
            elif voto==None:
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
    if data=="nessun file" or data=="nessun voto trovato":
        return data
    l = []

    for i in data:
        materia = i[0]
        media = round(i[-1],2)
        totale = 0
        esito = ""
        n = 1
        for j in i[1:-1]:
            if j == None:
                continue
            totale += float(j)
            n += 1
        target = n * 6
        v = target - totale
        if v < 6:
            esito = f"puoi prendere: {v:.2f}"
        else:
            esito = f"devi prendere: {v:.2f}"
        l.append(f"{materia} | media:{media} | {esito}")
    return l

def grafico_generale():
    data_x=[]
    data_y=[]
    n=0
    totale=0
    with open(grafico_gen_path,"r") as f:
        dati=json.load(f)
        dati=list(dati)
    for i in dati:
        data = i[1]
        giorno , mese , anno = map(int,data.split("/"))
        data = date(anno,mese,giorno)
        i[1]=data
    dati.sort(key=lambda x:x[1])
    for i in dati:
        voto=i[0]
        totale+=voto
        n+=1
        m=round(totale/n,2)
        
        data_x.append(n)
        data_y.append(m)

    return data_x,data_y

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
            try:
                voto = voto.strip()
            except:
                pass
            if choice==voto:
                flag=True
                continue
            if flag:
                if len(str(voto))>5 or voto==None:
                    break
                dati.append(voto)

    for voto in dati:
        n+=1
        totale+=voto
        m=totale/n
        data_x.append(n) # numero del voto
        data_y.append(m) # media progressiva
    return data_x , data_y 

def materie():

    data = []
    voti = get_data()
    if voti=="nessun file" or voti=="nessun voto trovato":
        return voti

    for materia in voti:
        materia=materia[0]       
        data.append(materia)
    try:
        data.pop()
    except:
        data = "nessun dato"
    return data

def excel():
    if platform.system() == 'Windows':
        os.startfile(excel_path)
    elif platform.system() == 'Darwin':
        subprocess.call(['open', excel_path])
    else:
        subprocess.call(['xdg-open', excel_path])

def get_data():

    with open(numer_materie_path,"r") as f:
        try:
            numero_materie = int(f.read())
        except ValueError:
            return "nessun file"

    lista_voti=[]
    voti=[]

    from openpyxl import load_workbook

    wb = load_workbook(excel_path,data_only=True)
    ws = wb.active

    for row in ws.iter_rows(min_row=1,max_row=numero_materie,min_col=1,max_col=12):
        for cell in row:
            if cell.row==1:
                continue
            voti.append(cell.value)
            if cell.column==12:
                lista_voti.append(voti)
                voti=[]
    # calcolo manulae della media in quanto excel restituisce una formula
    for r in lista_voti:
        totale = 0
        n = 0
        for j in r[1:-1]:
            if j==None:
                continue
            totale+=j
            n+=1
        try:
            m=totale/n
        except ZeroDivisionError:
            return "nessun voto trovato"
        r[-1]=m
    return lista_voti

def report():
    # varibili di supporto
    cord_x=0
    cord_y=0
    codice = ky.get_password(service_name_id,"user")
    with open(nome_path,"r") as f:
        nome = f.read()
    m = media()
    if m=="nessun voto trovato":
        return "nessun voto trovato"
    dati = get_data()
    if dati=="nessun file" or dati=="nessun voto trovato":
        return dati
    materie_insufficenti=0
    totale_verifiche = 0
    totale_insufficenze = 0
    totale_dieci = 0
    materia_media = []
    for i in dati:
        materia_media.append([i[0],[i][-1]])
    
    for i in materia_media: # calcolo info
        for j in i[-1][1:-1]:
            if j==None or str(j).strip()=="":
                continue
            totale_verifiche+=1
            if j<6:
                totale_insufficenze+=1
            elif j==10:
                totale_dieci+=1
            

    # crea pdf vuoto (orientazione,formato,unita di misura)
    pdf = fp.FPDF("portrait",format=(220, 300),unit="mm")

    # aggiungi pagina
    pdf.add_page()

    # imposta font (nome,size,stile="BUI")
    pdf.set_font("Arial", size=16,style='B')

    # immagine (cordinate,width)
    pdf.image(path_logo_1, x=0, y=0, w=50)
    pdf.image(path_logo_2, x=180 , y=4, w=30)

    # aggiungi testo (width,height,text,ln,align,bordo,fill,x,y)
    pdf.cell(200, 10, txt="Report Voti", ln=1, align="C")

    # linea
    pdf.line(10, 26, 210, 26)


    pdf.set_font("Arial", size=12,style='')
    pdf.cell(100, 20, txt=f"Studente: {nome}    ID:{codice}", ln=False, align="L")


    # istogramma a linee orizzontali
    pdf.set_xy(10, 40)
    cord_x = 10
    cord_y = 40
    cord_y_area_istogrammi = 0
    materia_media.sort(key=lambda x:x[-1][-1],reverse=1)
    for i in materia_media:
        cord_y+=10
        cord_y_area_istogrammi+=10
        materia = i[0]
        m_materia = round(i[-1][-1],2)
        width_cella = int(m_materia*10)
        m_materia_formattato = f"**{m_materia}**"

        if m_materia<6:
            pdf.set_fill_color(255,0,0) #rosso
            materie_insufficenti+=1
        else:
            pdf.set_fill_color(0, 100, 200) # blue

        pdf.set_font("Arial", size=10)
        pdf.cell(100, 4, txt=materia, ln=True, align="L")
        pdf.set_text_color(255, 255, 255)
        pdf.cell(width_cella, 5, txt=m_materia_formattato, ln=True, align="R", fill=True,markdown=True)
        pdf.set_font("Arial", size=12,style='')
        pdf.set_text_color(0, 0, 0)

    # ciambella
    cord_y_area_istogrammi = 120
    m = m*10
    if m<60:
        colore = "#ff0000"
    else:
        colore = "#00FF4C"
    plt.figure(figsize=(6,6))
    plt.pie(
        [m,100-m],
        colors=[colore,'#FFFFFF'],
        startangle=90,
        counterclock=False,
        wedgeprops={'edgecolor':'black','linewidth':0.3,"width":0.3}
    )
    plt.text(0,0,str(round(m/10,2)),ha="center",va="center",fontsize=40,color="black")
    plt.axis('equal')
    plt.savefig(path_ciambella,transparent=True)

    pdf.image(path_ciambella, x=160, y=cord_y_area_istogrammi/4, w=50)

    cord_y_area_istogrammi = cord_y_area_istogrammi/2+40
    pdf.set_xy(160,cord_y_area_istogrammi)
    pdf.set_fill_color(36, 182, 184)
    pdf.set_font("Arial", size=12,style='I')
    pdf.set_text_color(255,255,255)
    pdf.cell(60, 8, txt=f"totale verifiche con peso:{totale_verifiche} ", ln=1, align="L",fill=True)
    cord_y_area_istogrammi+=10

    pdf.set_xy(165,cord_y_area_istogrammi)
    pdf.set_fill_color(255, 72, 78)
    pdf.set_font("Arial", size=12,style='I')
    pdf.set_text_color(0,0,0)
    pdf.cell(55, 8, txt=f"totale materie insufficenti:{materie_insufficenti} ", ln=1, align="L",fill=True)
    cord_y_area_istogrammi+=10

    pdf.set_xy(180,cord_y_area_istogrammi)
    pdf.set_fill_color(255, 72, 78)
    pdf.set_font("Arial", size=12,style='I')
    pdf.set_text_color(0,0,0)
    pdf.cell(40, 8, txt=f"totale insufficenze:{totale_insufficenze} ", ln=1, align="L",fill=True)
    cord_y_area_istogrammi+=10

    pdf.set_xy(190,cord_y_area_istogrammi)
    pdf.set_fill_color(36, 182, 184)
    pdf.set_font("Arial", size=12,style='I')
    pdf.set_text_color(255,255,255)
    pdf.cell(30, 8, txt=f"totale '10':{totale_dieci} ", ln=1, align="L",fill=True)
    cord_y_area_istogrammi+=10

    pdf.set_font("Arial", size=12,style='')
    # grafico
    if cord_y<=150:
        cord_y=150
        size=50
    else:
        size = 35
    x,y = grafico_generale()
    mpl.rcParams["figure.facecolor"] = "#FFFFFF"
    mpl.rcParams["axes.facecolor"] = "#4D4D4D"
    fig = plt.figure(figsize=(12,4))
    plt.plot(x,y)
    plt.savefig(path_grafico , transparent=True)
    plt.close()

    pdf.line(cord_x, cord_y, 210, cord_y)
    pdf.set_xy(cord_x,cord_y)
    pdf.cell(200, 10, txt="Grafico Andamento Voti", ln=1, align="L")
    pdf.image(path_grafico, x=5, y=cord_y+5, w=200)

    cord_y+=70
    cord_x=10
    spazio_tra_code = int((200-size*3)/2)
    pdf.line(cord_x, cord_y, 210, cord_y)
    for i in path_qr_code:
        pdf.image(i, cord_x, y=cord_y+5, w=size)
        cord_x+=spazio_tra_code+size

    # salva pdf nome
    pdf.output(path_report)
    return "ok"
