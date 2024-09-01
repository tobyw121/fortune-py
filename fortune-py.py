#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
import sqlite3
import random

# Datenbankoperationen in eine eigene Klasse auslagern
class DatabaseManager:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()  
  

        self.add_sample_fortunes()
        self.set_default_settings()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS fortunes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                language TEXT,
                text TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS fish_settings (
                id INTEGER PRIMARY KEY,
                fish_name TEXT,
                fish_color TEXT DEFAULT "black"
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY,
                gui_name TEXT
            )
        ''')

        # Sicherstellen, dass es immer genau einen Eintrag in den Einstellungs-Tabellen gibt
        self.cursor.execute('INSERT OR IGNORE INTO settings (id) VALUES (1)')
        self.cursor.execute('INSERT OR IGNORE INTO fish_settings (id) VALUES (1)')
        self.conn.commit()

    def add_sample_fortunes(self):
        sample_fortunes = [
            # Füge hier deine eigenen Sprüche hinzu
            #("Deutsch", "Ein Lächeln ist die schönste Sprache der Welt."),
            #("Englisch", "A smile is the prettiest language in the world.")
        ]
        for language, text in sample_fortunes:
            self.cursor.execute('INSERT INTO fortunes (language, text) VALUES (?, ?)', (language, text))
        self.conn.commit()  

    def set_default_settings(self):
        if not self.get_setting("gui_name"):
            self.set_setting("gui_name", "Glückskekse")
        if not self.get_fish_setting("fish_name"):             
            self.set_fish_setting("fish_name", "TUX der Weise")

    def get_fortune(self, language):
        self.cursor.execute('SELECT text FROM fortunes WHERE language = ?', (language,))
        fortunes = self.cursor.fetchall()
        if fortunes:
            return random.choice(fortunes)[0]
        else:
            return "Keine Sprüche in dieser Sprache verfügbar."

    def get_setting(self, setting_name):
        self.cursor.execute(f'SELECT {setting_name} FROM settings WHERE id = 1')
        result = self.cursor.fetchone()
        return result[0] if result else None

    def set_setting(self, setting_name, value):
        self.cursor.execute(f'UPDATE settings SET {setting_name} = ? WHERE id = 1', (value,))
        self.conn.commit()

    def get_fish_setting(self, setting_name):
        self.cursor.execute(f'SELECT {setting_name} FROM fish_settings WHERE id = 1')
        result = self.cursor.fetchone()
        return result[0] if result else None

    def set_fish_setting(self, setting_name, value):
        self.cursor.execute(f'UPDATE fish_settings SET {setting_name} = ? WHERE id = 1', (value,))
        self.conn.commit()

    def add_fortune(self, language, text):
        self.cursor.execute('INSERT INTO fortunes (language, text) VALUES (?, ?)', (language, text))
        self.conn.commit()

    def close(self):
        self.conn.close()

# GUI-Logik 
class FortuneGUI:
    def __init__(self, db_manager):
        self.db = db_manager
        self.window = tk.Tk()
        self.window.title(self.db.get_setting("gui_name"))
        self.window.configure(bg="#F5F5DC")

        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Helvetica", 12), background="#F5F5DC")
        self.style.configure("TButton", font=("Helvetica", 10), background="#F0E68C")
        self.style.configure("TFrame", background="#F5F5DC")
        self.style.configure("TLabelframe", background="#F5F5DC", relief="groove", borderwidth=2)
        self.style.configure("TLabelframe.Label", font=("Georgia", 14, "bold"))

        self.language_var = tk.StringVar(value="Deutsch")
        self.fortune_text = tk.StringVar()
        self.new_language_var = tk.StringVar(value="Deutsch")

        self.fish_name = self.db.get_fish_setting("fish_name")
        self.fish_color = self.db.get_fish_setting("fish_color")

   
        self.status_label = ttk.Label(self.window, text="", foreground="black", background="#F5F5DC")
        self.status_label.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.create_widgets()

        # Zeige einen ersten Spruch beim Start
        self.show_next_fortune()

    def create_widgets(self):
        # Frame für den Anzeigebereich 
        display_frame = ttk.LabelFrame(self.window, text="Spruch anzeigen")
        display_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew") 

        ttk.Label(display_frame, text="Wähle deine Sprache:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        language_frame = ttk.Frame(display_frame)
        language_frame.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ttk.Radiobutton(language_frame, text="Deutsch", variable=self.language_var, value="Deutsch", command=self.show_next_fortune).pack(side="left")
        ttk.Radiobutton(language_frame, text="Englisch", variable=self.language_var, value="Englisch", command=self.show_next_fortune).pack(side="left")

        # Scrollfenster für den Spruch
        fortune_scroll = tk.Scrollbar(display_frame)
        fortune_scroll.grid(row=2, column=1, sticky="ns")

        self.fortune_label = tk.Text(display_frame, wrap="word", yscrollcommand=fortune_scroll.set,
                                     height=10, width=90, font=("Helvetica", 14, "bold")) 
        self.fortune_label.grid(row=2, column=0, padx=10, pady=20, sticky="nsew") 

        fortune_scroll.config(command=self.fortune_label.yview)

        # Wende die geladene Farbe auf das Label an
        self.fortune_label.config(foreground=self.fish_color)

        ttk.Button(display_frame, text="Einen neuen Spruch!", command=self.show_next_fortune).grid(row=3, column=0, padx=10, pady=10)

        # Frame für den Bereich zum Hinzufügen neuer Sprüche 
        add_frame = ttk.LabelFrame(self.window, text="Spruch hinzufügen")
        add_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew") 

        ttk.Label(add_frame, text="Teile deinen eigenen Spruch:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.new_fortune_entry = ttk.Entry(add_frame, width=40)
        self.new_fortune_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew") 

        ttk.Label(add_frame, text="In welcher Sprache ist dein Spruch?").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        new_language_frame = ttk.Frame(add_frame)
        new_language_frame.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        ttk.Radiobutton(new_language_frame, text="Deutsch", variable=self.new_language_var, value="Deutsch").pack(side="left")
        ttk.Radiobutton(new_language_frame, text="Englisch", variable=self.new_language_var, value="Englisch").pack(side="left")

        # "Spruch hinzufügen!"-Button 
        ttk.Button(add_frame, text="Spruch hinzufügen!", command=self.add_fortune).grid(row=4, column=0, padx=10, pady=10) 


    # Rechtsklick-Menü zum Ändern des GUI-Namens
        self.window.bind("<Button-3>", lambda event: self.show_change_name_dialog())

    # Button zum Öffnen des Dialogs zum Ändern des Fischnamens und der Farbe
        ttk.Button(self.window, text="Fischnamen & Farbe ändern", command=self.show_change_fish_dialog).grid(row=3, column=0, padx=10, pady=10)

    # Konfiguriere das Hauptfenster, um die Größenänderung der Widgets zu ermöglichen - NACH dem Erstellen aller Widgets
        self.window.columnconfigure(0, weight=1) 
        self.window.rowconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1) 

    def show_change_name_dialog(self):
        global new_name_entry
        dialog = tk.Toplevel(self.window)
        dialog.title("GUI-Namen ändern")

        ttk.Label(dialog, text="Neuer Name:").pack(padx=10, pady=5)
        new_name_entry = ttk.Entry(dialog)
        new_name_entry.pack(padx=10, pady=5)

        ttk.Button(dialog, text="Ändern", command=lambda: [self.change_gui_name(), dialog.destroy()]).pack(padx=10, pady=10)

    def show_next_fortune(self):
        language = self.language_var.get()
        fortune = self.db.get_fortune(language)

        # Hole den aktuellen Fischnamen aus der Datenbank
        self.fish_name = self.db.get_fish_setting("fish_name")

        # Füge den Fischnamen vor dem Spruch hinzu, wenn die Sprache Deutsch oder Englisch ist
        if language.lower() in ["deutsch", "englisch"]:
            full_text = self.fish_name + " sagt:    " + fortune
        else:
            full_text = fortune

        # Lösche den vorherigen Text und füge den neuen Text ein
        self.fortune_label.delete("1.0", tk.END)
        self.fortune_label.insert(tk.END, full_text)

    def add_fortune(self):
        language = self.new_language_var.get()
        text = self.new_fortune_entry.get()

        if language and text:
            # Speichere nur den eigentlichen Spruch ohne Fischnamen in der Datenbank
            self.db.add_fortune(language, text)

            self.new_fortune_entry.delete(0, tk.END)
            self.status_label.config(text="Spruch hinzugefügt!", foreground="green")
        else:
            self.status_label.config(text="Bitte Sprache und Text eingeben.", foreground="red")

    def change_gui_name(self):
        new_name = new_name_entry.get()
        if new_name:
            self.db.set_setting("gui_name", new_name)
            self.window.title(new_name)
            self.status_label.config(text="GUI-Name geändert!", foreground="green")
        else:
            self.status_label.config(text="Bitte einen neuen Namen eingeben.", foreground="red")

    def change_fish_name_and_color(self):
        new_fish_name = new_fish_name_entry.get()
        new_color = new_color_entry.get()

        if new_fish_name:
            self.db.set_fish_setting("fish_name", new_fish_name)

        if new_color:
            try:
                # Versuche, die Farbe auf das Label anzuwenden, um zu überprüfen, ob sie gültig ist
                self.fortune_label.config(foreground=new_color)

                # Speichere die neue Farbe in der Datenbank, nachdem sie erfolgreich angewendet wurde
                self.db.set_fish_setting("fish_color", new_color)
                print("Farbe in Datenbank gespeichert:", new_color) 

                # Aktualisiere die lokale Variable self.fish_color
                self.fish_color = new_color

                self.status_label.config(text="Farbe geändert!", foreground="green")
            except tk.TclError:
                self.status_label.config(text="Ungültige Farbe!", foreground="red")

        # Aktualisiere den aktuellen Spruch, um den neuen Fischnamen anzuzeigen
        self.show_next_fortune()

        # Wenn entweder der Name oder die Farbe geändert wurden, zeige eine Erfolgsmeldung an
        if new_fish_name or new_color:
            self.status_label.config(text="Fischname und/oder Farbe geändert!", foreground="green")

    def show_change_fish_dialog(self):
        global new_fish_name_entry, new_color_entry
        dialog = tk.Toplevel(self.window)
        dialog.title("Fischnamen & Farbe ändern")

        ttk.Label(dialog, text="Neuer Fischname:").pack(padx=10, pady=5)
        new_fish_name_entry = ttk.Entry(dialog)
        new_fish_name_entry.pack(padx=10, pady=5)

        ttk.Label(dialog, text="Neue Farbe (z.B. 'red', 'blue', '#FF0000'):").pack(padx=10, pady=5)
        new_color_entry = ttk.Entry(dialog)
        new_color_entry.pack(padx=10, pady=5)

        ttk.Button(dialog, text="Ändern", command=lambda: [self.change_fish_name_and_color(), dialog.destroy()]).pack(padx=10, pady=10)

    def run(self):
        self.window.mainloop()
        self.db.close()

if __name__ == "__main__":
    db_manager = DatabaseManager('sprueche.db')
    gui = FortuneGUI(db_manager)
    gui.run() 

