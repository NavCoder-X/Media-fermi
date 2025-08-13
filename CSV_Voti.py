# csv

def csv():
    import csv
    import os , sys
    import platform
    import subprocess

    # path
    def resource_path(relative_path):
        if hasattr(sys,"_MEIPASS"):
            return os.path.join(sys._MEIPASS,relative_path)
        return os.path.join(os.path.abspath("."),relative_path)

    csv_path = resource_path("example.csv")
    voti_path = resource_path("voti.txt")

    materie_voto={}
    lista=[]
    iter=0
    with open(voti_path,"r") as file:
        context=file.readlines()
        for i in context:
            i=i.strip()
            if iter==0:
                lista.append(i)
                iter=1
            elif len(str(i))>5:
                try:
                    materie_voto[lista[0]]=lista[1:]
                except:
                    continue
                lista=[]
                lista.append(i)
            else:
                lista.append(i)

    with open(csv_path, 'w', newline='') as csvfile:
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
                elif "½" in voto or "ï¿" in voto:
                    voto=voto.replace("½", "")
                    voto=voto.replace("ï¿", "")
                    voto=float(voto)+0.5
                else:
                    voto=float(voto)
                voti[n] = voto  # Convert to float for CSV
                totale+=voto
                m=totale/(len(voti))
            while len(voti)<10:
                voti.append(" ")
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

    if platform.system() == 'Windows':
        os.startfile(csv_path)
    elif platform.system() == 'Darwin':
        subprocess.call(['open', csv_path])
    else:
        subprocess.call(['xdg-open', csv_path])

