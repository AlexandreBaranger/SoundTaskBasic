import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import json
import os

# Fichier de sauvegarde des états
FICHIER_SAUVEGARDE = "etat_taches.json"

# Fonction pour lire le fichier txt sélectionné via la boîte de dialogue
def lire_fichier_txt():
    filepath = filedialog.askopenfilename(
        title="Choisissez un fichier .txt",
        filetypes=[("Text files", "*.txt")],
        defaultextension=".txt"
    )
    
    if filepath:
        with open(filepath, 'r') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    else:
        messagebox.showwarning("Aucun fichier sélectionné", "Vous devez sélectionner un fichier .txt pour continuer.")
        return []

# Charger les états des tâches depuis le fichier JSON
def charger_etats():
    if os.path.exists(FICHIER_SAUVEGARDE):
        with open(FICHIER_SAUVEGARDE, 'r') as f:
            return json.load(f)
    else:
        # Si le fichier n'existe pas, créer un nouveau fichier vide
        sauvegarder_etats({})
        return {}

# Sauvegarder les états des tâches dans le fichier JSON
def sauvegarder_etats(etats):
    with open(FICHIER_SAUVEGARDE, 'w') as f:
        json.dump(etats, f, indent=4)

# Initialisation de l'interface graphique
class TacheManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        
        # Stocker l'état des tâches dans un dictionnaire
        self.etats = charger_etats()

        # Configuration du style sombre pour la fenêtre principale
        self.root.configure(bg='#1e1e1e')

        # Créer un cadre pour la liste des tâches avec un canvas pour le scroll
        self.canvas = tk.Canvas(self.root, bg='#1e1e1e', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="Dark.TFrame")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Charger les tâches à partir du fichier txt choisi par l'utilisateur
        self.charger_taches()

    def charger_taches(self):
        taches_principales = lire_fichier_txt()

        if taches_principales:
            col_count = 3  # Nombre de colonnes
            for idx, tache_principale in enumerate(taches_principales):
                row = idx // col_count
                column = idx % col_count
                self.creer_tache_principale(tache_principale, row, column)
        else:
            self.root.quit()

    def creer_tache_principale(self, tache_principale, row, column):
        frame_tache = ttk.LabelFrame(self.scrollable_frame, text=tache_principale, padding=(10, 5), style="Dark.TLabelframe")
        frame_tache.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

        # Initialiser l'état de cette tâche principale dans le dictionnaire
        if tache_principale not in self.etats:
            self.etats[tache_principale] = {}

        # Créer les tâches secondaires
        self.creer_tache_secondaire(frame_tache, tache_principale, "1. Recherche de son dans la bank")
        self.creer_tache_secondaire(frame_tache, tache_principale, "2. Injecter les synthétiseurs dans le projet Wwise")
        self.creer_tache_secondaire(frame_tache, tache_principale, "3. Synchroniser le déclenchement d'event")
        self.creer_tache_secondaire(frame_tache, tache_principale, "4. Ajuster les CSV et mixer")

    def creer_tache_secondaire(self, parent_frame, tache_principale, tache_secondaire):
        frame = ttk.Frame(parent_frame, style="Dark.TFrame")
        frame.pack(fill=tk.X, pady=2)

        # Vérifier si la tâche secondaire a un état dans le fichier JSON, sinon l'initialiser
        if tache_principale not in self.etats:
            self.etats[tache_principale] = {}
        if tache_secondaire not in self.etats[tache_principale]:
            self.etats[tache_principale][tache_secondaire] = {"etat": "ToDo", "checkbox": False}

        etat_bouton = self.etats[tache_principale][tache_secondaire]

        var = tk.BooleanVar(value=etat_bouton["checkbox"])  # État de la case à cocher

        # Créer une checkbox pour valider la tâche secondaire
        checkbox = tk.Checkbutton(frame, text=tache_secondaire, variable=var, bg='#1e1e1e', fg='white', selectcolor='#1e1e1e', activebackground='#1e1e1e', activeforeground='white')
        checkbox.pack(side=tk.LEFT)

        # Créer un bouton pour marquer la tâche en cours
        btn = ttk.Button(frame, text=etat_bouton["etat"], command=lambda: self.toggle_en_cours(btn, tache_principale, tache_secondaire), style="Dark.TButton")
        self.update_button_style(btn, etat_bouton["etat"])
        btn.pack(side=tk.RIGHT)

        # Sauvegarder l'état de la case à cocher et du bouton lors du changement d'état
        var.trace_add("write", lambda *args: self.update_etat(tache_principale, tache_secondaire, var.get(), btn))
        btn.bind("<Button-1>", lambda event: self.toggle_en_cours(btn, tache_principale, tache_secondaire))

    def toggle_en_cours(self, btn, tache_principale, tache_secondaire):
        # Toggle l'état du bouton entre "ToDo", "En cours" et "Terminé"
        current_state = self.etats[tache_principale][tache_secondaire]
        etat_bouton = current_state["etat"]

        if etat_bouton == "ToDo":
            self.etats[tache_principale][tache_secondaire]["etat"] = "En cours"
            btn.config(text="En cours")
        elif etat_bouton == "En cours":
            self.etats[tache_principale][tache_secondaire]["etat"] = "Terminé"
            btn.config(text="Terminé")
        else:
            self.etats[tache_principale][tache_secondaire]["etat"] = "ToDo"
            btn.config(text="ToDo")
        
        self.update_button_style(btn, self.etats[tache_principale][tache_secondaire]["etat"])
        sauvegarder_etats(self.etats)

    def update_button_style(self, btn, etat):
        if etat == "En cours":
            btn.configure(style="EnCours.TButton")
        elif etat == "Terminé":
            btn.configure(style="Termine.TButton")
        else:
            btn.configure(style="Dark.TButton")

    def update_etat(self, tache_principale, tache_secondaire, checkbox_state, btn):
        # Mettre à jour l'état de la case à cocher dans le dictionnaire et sauvegarder
        self.etats[tache_principale][tache_secondaire]["checkbox"] = checkbox_state
        sauvegarder_etats(self.etats)

# Création de l'application
if __name__ == "__main__":
    root = tk.Tk()

    # Configurer le style sombre pour tous les éléments
    style = ttk.Style()
    style.theme_use("clam")

    # Personnaliser le style pour chaque type de widget (fond sombre et texte blanc)
    style.configure("Dark.TLabelframe", background="#1e1e1e", foreground="white")
    style.configure("Dark.TLabelframe.Label", background="#1e1e1e", foreground="white")
    style.configure("Dark.TFrame", background="#1e1e1e")
    style.configure("Dark.TCheckbutton", background="#1e1e1e", foreground="white")
    style.configure("Dark.TButton", background="#1e1e1e", foreground="white")

    # Styles spécifiques pour les boutons d'état
    style.configure("EnCours.TButton", background='#F5F5DC', foreground='black')
    style.configure("Termine.TButton", background='#4A90E2', foreground='white')

    # Lancer l'application
    app = TacheManagerApp(root)
    root.mainloop()
