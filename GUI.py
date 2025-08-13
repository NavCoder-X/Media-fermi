import customtkinter as ctk
from PIL import Image
from media_voti import chek,media
from CSV_Voti import csv
import sys, os

# path
def resource_path(relative_path):
    if hasattr(sys,"_MEIPASS"):
        return os.path.join(sys._MEIPASS,relative_path)
    return os.path.join(os.path.abspath("."),relative_path)

immagine_2 = resource_path("assets/image_2.png")
nome_path = resource_path("login/nome.txt")
user_path = resource_path("login/id.txt")
pass_path = resource_path("login/password.txt")
icona_path = resource_path("icona.ico")


# Impostazioni CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Finestra principale
window = ctk.CTk()
window.geometry("700x450")
window.configure(fg_color="#343333")
window.title("Media-Fermi")
window.iconbitmap(icona_path)

# short cut
window.bind("<Return>", lambda event: send_button.invoke())  # Invoca handler quando si preme Invio

# Barra superiore: width/height nel costruttore (errore risolto)
top_bar = ctk.CTkFrame(
    master=window,
    fg_color="#6F5E6F",
    corner_radius=20,
    width=600,
    height=35
)
top_bar.place(x=50, y=10) # NON mettere width/height qui

with open(nome_path, "r") as file:
    nome = file.read()

title_label = ctk.CTkLabel(
    master=top_bar,
    text=f"Ciao {nome}",
    font=("KumarOne Regular", 18),
    text_color="white"
)
# uso place interno o pack; ho usato place per posizionare il testo vicino al bordo
title_label.place(x=10, y=3)

# Area grigia centrale (width/height nel costruttore)
center_frame = ctk.CTkLabel(
    master=window,
    fg_color="#636363",
    corner_radius=25,
    width=562,
    height=286,
    text=" ",
    font=("Courier",14),
    
)
center_frame.place(x=72, y=77)


# Immagine piccola a sinistra (se presente)
try:
    img2 = Image.open(immagine_2)
    ctki2 = ctk.CTkImage(light_image=img2, dark_image=img2, size=(50, 50))
    image_label_2 = ctk.CTkLabel(master=window, image=ctki2, text="")
    image_label_2.place(x=16, y=77)
except Exception as e:
    print("Immagine image_2.png non trovata o errore:", e)

# Campo di testo: width nel costruttore (CTkEntry non sempre accetta height)
entry_1 = ctk.CTkEntry(
    master=window,
    placeholder_text="Scrivi qui...",
    font=("ariel",16),
    width=500,
    fg_color="#636363",
    text_color="white",
    height=35,
    corner_radius=15
)
entry_1.place(x=103, y=388) # nessun width/height qui

# funzione help
def help():
    center_frame.configure(text="""
Comandi:                                             
'/nome' <-- per mettere il tuo nome                  
'/id'   <-- per mettere il tuo id di classeviva      
'/pass' <-- per mettere la tua password di classeviva
'/upd'  <-- per aggiornare i dati sui tuoi voti      
'/m'    <-- per visualizzare la tua media generale   
'/csv'  <-- per aprire un file excel con i tuoi voti 
"""
)




# Bottone Help (width/height nel costruttore)
help_button = ctk.CTkButton(
    master=window,
    text="/Help",
    fg_color="#636363",
    hover_color="#000000",
    text_color="white",
    corner_radius=10,
    border_width=2,
    border_color="#3AE22E",
    width=80,
    font=("impact",14),
    height=35,
    command=help
)
help_button.place(x=10, y=388)


# handler dei comandi
def handler():
    testo = entry_1.get()
    entry_1.delete(0, 'end')  # Pulisce il campo di testo dopo l'invio
    if "/nome" in testo:
        content = testo[6::]  
        with open(nome_path, "w") as file:
            file.write(content)
        center_frame.configure(text="Nome aggiornato!.")
        title_label.configure(text=f"Ciao {content}")
    elif "/id" in testo:
        content = testo[4::]  
        with open(user_path, "w") as file:
            file.write(content)
        center_frame.configure(text="id impostato!.")
    elif "/pass" in testo:
        content = testo[6::]  
        with open(pass_path, "w") as file:
            file.write(content)
        center_frame.configure(text="password impostata!.")
    elif testo=="/upd":
        center_frame.configure(text="Aggiornamento in corso...\nci potrebbero volere alcuni minuti\nassicurati di avere una buona conessione.")
        window.update_idletasks()
        esito = chek()
        if esito=="nessuna password":
            center_frame.configure(text="Nessuna password trovata! Inserisci '/pass' per aggiungerla.")
        elif esito=="nessun id":
            center_frame.configure(text="Nessun id trovato! Inserisci '/id' per aggiungerlo.")
        elif esito=="credenziali errate":
            center_frame.configure(text="Credenziali errate, perfavore metti quelle giuste")
        elif esito=="dati aggiornati":
            center_frame.configure(text="Dati aggiornati!")
    elif testo=="/m":
        esito = media()
        if esito=="nessun voto trovato":
            center_frame.configure(text="Nessun voto trovato!")
        else:
            center_frame.configure(text=f"Media dei voti: {esito:.2f}")
    elif testo=="/csv":
        center_frame.configure(text=f"il file si sta aprendo...")
        csv()


# Bottone invio
send_button = ctk.CTkButton(
    master=window,
    text="→",
    fg_color="#636363",
    text_color="white",
    hover_color="#000000",
    corner_radius=10,
    border_width=2,
    border_color="#2BCBE8",
    width=35,
    height=35,
    command=handler
)
send_button.place(x=620, y=388)

window.resizable(False, False)
window.mainloop()

