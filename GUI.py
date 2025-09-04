import customtkinter as ctk
import tkinter as tk
import sys,os
from media_voti import chek,media,graficoXmateria,materie,quanto_posso_prendere,csv
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# path
def resource_path(relative_path):
    if hasattr(sys,"_MEIPASS"):
        return os.path.join(sys._MEIPASS,relative_path)
    return os.path.join(os.path.abspath("."),relative_path)

nome_path = "login/nome.txt"
user_path = "login/id.txt"
pass_path = "login/password.txt"
icona_path = resource_path("icona.ico")
browser_mode = resource_path("Browser_mode.txt")


class ModernGUI:
    def __init__(self):
        # Configura il tema e la modalità di colore
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Crea la finestra principale
        self.root = ctk.CTk()
        self.root.title("Medie-Fermi")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Imposta l'icona 
        try:
            self.root.iconbitmap(icona_path)  
        except:
            pass  
        
        # Configura il grid layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(0, weight=0)  # Label saluto
        self.root.grid_rowconfigure(1, weight=1)  # Output area
        self.root.grid_rowconfigure(2, weight=0)  # Checkbox
        self.root.grid_rowconfigure(3, weight=0)  # Entry e bottoni
        
        # Variabili per le animazioni
        self.animation_running = False
        # varibile contente i comandi usati dal inizio del programma
        self.comandi_usati = []
        self.indice_comandi = -1

        self.setup_gui()
        
    def setup_gui(self):
        # Label di saluto in alto
        with open(nome_path, "r") as file:
            nome = file.read() # ricava nome
        self.saluto_label = ctk.CTkLabel(
            self.root,
            text=f"💻 Ciao {nome} 💻",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#00D4FF"
        )
        self.saluto_label.grid(row=0, column=0, columnspan=3, pady=(20, 30), padx=20, sticky="ew")

        
        # Label centrale per l'output
        self.output_frame = ctk.CTkFrame(self.root)
        self.output_frame.grid(row=1, column=0, columnspan=3, pady=(0, 20), padx=20, sticky="nsew")
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.output_frame.grid_rowconfigure(0, weight=1)
        
        self.output_label = ctk.CTkLabel(
            self.output_frame,
            text="L'output del programma apparirà qui...",
            font=ctk.CTkFont(size=12,family="Rubik",weight="bold"),
            wraplength=500,
            justify="left",
            anchor="nw"
        )
        self.output_label.grid(row=0, column=0, pady=20, padx=20, sticky="nsew")

        # bottone togle 
        switch_var = ctk.IntVar(value=0)
        self.switch=ctk.CTkSwitch(
            master=self.root,text="Light mode",
            variable=switch_var,
            onvalue=1,
            offvalue=0,
            width=100,
            height=20,
            command=self.mode,
            bg_color="transparent"
        )
        self.switch.grid(row=2, column=2, columnspan=1, pady=(0, 5), padx=10)

        # grafico
        self.canvas = None
    
        # Checkbox
        self.checkbox_var = ctk.BooleanVar()
        self.checkbox = ctk.CTkCheckBox(
            self.root,
            text="Browser visibile",
            variable=self.checkbox_var,
            font=ctk.CTkFont(size=12),
            command=self.on_checkbox_change,
            bg_color="transparent",
        )
        self.checkbox.grid(row=2, column=0, columnspan=3, pady=(0, 5))
        
        # Frame per i controlli in basso
        self.bottom_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.bottom_frame.grid(row=3, column=0, columnspan=3, pady=(0, 20), padx=20, sticky="ew")
        self.bottom_frame.grid_columnconfigure(1, weight=1)
        
        # Bottone di aiuto
        self.help_button = ctk.CTkButton(
            self.bottom_frame,
            text="❓ Aiuto",
            width=100,
            height=35,
            command=self.show_help,
            fg_color="#2B2B2B",
            hover_color="#404040",
            border_width=2,
            border_color="#27F602"
        )
        self.help_button.grid(row=0, column=0, padx=(0, 10), pady=5)
        
        # Entry centrale
        self.entry = ctk.CTkEntry(
            self.bottom_frame,
            placeholder_text="Inserisci il tuo comando qui...",
            height=35,
            font=ctk.CTkFont(size=12),
            border_width=2,
            border_color="#00D4FF",
            fg_color=("#F0F0F0", "#2B2B2B"),
            text_color=("#000000", "#FFFFFF")
        )
        self.entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        # Bottone di invio
        self.submit_button = ctk.CTkButton(
            self.bottom_frame,
            text="🚀 Invia",
            width=100,
            height=35,
            command=self.process_input,
            fg_color="#1F1F1F",
            hover_color="#333333",
            border_width=2,
            border_color="#3C06DD"
        )
        self.submit_button.grid(row=0, column=2, padx=(10, 0), pady=5)
        
        # Focus sull'entry
        self.entry.focus()
    
        # keybinds

        self.entry.bind("<Return>", lambda event: self.process_input())
        self.entry.bind("<FocusIn>", self.on_entry_focus_in)
        self.entry.bind("<FocusOut>", self.on_entry_focus_out)

        self.root.bind("<Shift-R>",self.ripulisci)

        self.root.bind("<Up>",self.riprendi_comando_up)
        self.root.bind("<Down>",self.riprendi_comando_down)

    def on_entry_focus_in(self, event):
        """Effetto glow quando l'entry riceve il focus"""
        self.entry.configure(border_color="#FF0000", border_width=2)
        
    def on_entry_focus_out(self, event):
        """Rimuove l'effetto glow quando l'entry perde il focus"""
        self.entry.configure(border_color="#00D4FF", border_width=2)

    def ripulisci(self,key):
        self.distruggi_grafico()
        self.update_output(" ")

    def riprendi_comando_up(self,key):
        if -len(self.comandi_usati)<self.indice_comandi:
            self.indice_comandi-=1
        try:
            commando = self.comandi_usati[self.indice_comandi]
            self.entry.delete(0, tk.END)  # Pulisce l'entry
            self.entry.insert(0,commando)
        except:
            print("lista comandi vuota")

    def riprendi_comando_down(self,key):
        if -1>self.indice_comandi:
            self.indice_comandi+=1
        try:
            commando = self.comandi_usati[self.indice_comandi]
            self.entry.delete(0, tk.END)  # Pulisce l'entry
            self.entry.insert(0,commando)
        except:
            print("lista comandi vuota")

    def distruggi_grafico(self):
        try:
            self.canvas.get_tk_widget().destroy()  # Rimuove il grafico precedente
        except:
            pass
        try:
            self.dropdown.destroy()
        except:
            pass

    def process_input(self):
        """Processa l'input dall'utente"""
        self.distruggi_grafico()
        user_input = self.entry.get()
        if not user_input.strip():
            self.update_output("⚠️ Inserisci un comando prima di inviare!")
            return
        elif "/nome" in user_input:
            content = user_input[6::]
            with open(nome_path, "w") as file:
                file.write(content)
            output_text = "nome aggiornato!"
            self.saluto_label.configure(text=f"💻 Ciao {content} 💻")
        elif "/id" in user_input:
            content = user_input[4::]
            with open(user_path, "w") as file:
                file.write(content)
            output_text = "id aggiornato!"
        elif "/pass" in user_input:
            content = user_input[6::]
            with open(pass_path, "w") as file:
                file.write(content)
            output_text = "password aggiornata!"
        elif user_input=="/upd":
            self.update_output("📡Aggiornamento in corso...\n🕓ci potrebbero volere alcuni minuti\n🛜assicurati di avere una buona conessione.")
            self.root.update_idletasks()
            esito = chek()
            if esito=="nessuna password":
                output_text="⚠️Nessuna password trovata! Inserisci '/pass' per aggiungerla."
            elif esito=="nessun id":
                output_text="⚠️Nessun id trovato! Inserisci '/id' per aggiungerlo."
            elif esito=="credenziali errate":
                output_text="⚠️Credenziali errate, perfavore metti quelle giuste"
            elif esito=="dati aggiornati":
                output_text="Dati aggiornati!🙆‍♂️"
        elif user_input=="/m":
            esito = media()
            if esito=="nessun voto trovato":
                output_text="⚠️Nessun voto trovato!"
            else:
                output_text=f"📈Media Generale: {esito:.2f}"
        elif user_input=="/csv":
            self.update_output("📂 Il file si sta aprendo...")
            self.root.update_idletasks()
            csv()
            output_text = "File CSV aperto con successo!👌"   
        elif user_input=="/r":
            output_text="L'output del programma apparirà qui..."
        elif user_input=="/q":
            l = quanto_posso_prendere()
            output_text = "\n".join(l) if l else "⚠️ Nessun risultato trovato."

        elif user_input=="/gm":
            def menuHandle(choice):
                try:
                    self.canvas.get_tk_widget().destroy()
                except:
                    pass
                self.canvas=None
                x,y=graficoXmateria(choice)
                mpl.rcParams["figure.facecolor"] = "#2B2B2B"
                mpl.rcParams["axes.facecolor"] = "#4D4D4D"
                fig = plt.figure()
                ax = fig.add_subplot()
                ax.plot(x,y)
                self.canvas = FigureCanvasTkAgg(fig,master=self.output_label)
                self.canvas.draw()
                self.canvas.get_tk_widget().grid(row=0, column=0, pady=20, padx=20, sticky="nsew")
            output_text="Grafico x Materia:"
            valori = materie()
            if valori=="nessun dato":
                output_text="⚠️ Nessun dato trovato"
            else:
                self.dropdown = ctk.CTkOptionMenu(
                    master=self.output_frame,
                    values=valori,
                    command=menuHandle,
                    bg_color="transparent"
                )
                self.dropdown.grid(row=1, column=0, pady=(0, 20), padx=20, sticky="nsew")
        else:
            output_text="non so cosa hai scritto...😵‍💫"
        if output_text!="non so cosa hai scritto...😵‍":
            self.comandi_usati.append(user_input)
            self.indice_comandi = 0
        # Simula l'elaborazione del comando
        self.update_output(output_text)
        self.entry.delete(0, tk.END)  # Pulisce l'entry
        
    def mode(self):
        value = self.switch.get()
        if value==0:
            ctk.set_appearance_mode("dark")
        elif value==1:
            ctk.set_appearance_mode("light")

    def update_output(self, text):
        """Aggiorna il testo nell'area di output"""
        self.output_label.configure(text=text)
        
    def on_checkbox_change(self):
        """Gestisce il cambiamento della checkbox"""
        status = "attivato" if self.checkbox_var.get() else "disattivato"
        with open(browser_mode, "w") as file:
            file.write("1" if self.checkbox_var.get() else "0")
        self.update_output(f"🔄 Browser visibile {status}")
        
    def show_help(self):
        """Mostra la finestra di aiuto"""
        self.distruggi_grafico()

        help_text = """
🔷 GUIDA ALL'UTILIZZO:

• Usa la checkbox per vedere l attivita su chrome quando usi /upd

🔷 Comandi:

• '/nome' <-- per mettere il tuo nome                        
• '/id'   <-- per mettere il tuo id di classeviva            
• '/pass' <-- per mettere la tua password di classeviva      
• '/upd'  <-- per aggiornare i dati sui tuoi voti            
• '/m'    <-- per visualizzare la tua media generale         
• '/csv'  <-- per aprire un file excel con i tuoi voti       
• '/q'    <-- per sapere quanto puoi prendere in ogni materia
• '/r'    <-- per ripulire il output box                     
• '/gm'   <-- per vedere il grafico del andamento per materia                     

"""
        
        # Mostra l'aiuto nel label centrale
        self.update_output(help_text)

    def run(self):
        """Avvia l'applicazione"""
        self.root.mainloop()

# Crea e avvia l'applicazione
if __name__ == "__main__":
    app = ModernGUI()
    app.run()



