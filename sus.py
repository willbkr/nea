import customtkinter as ctk
import tkinter as tk  # Still needed for Menu and MessageBox
from tkinter import messagebox
from captcha.image import ImageCaptcha
from PIL import Image, ImageTk, ImageOps
import random
import string
import sqlite3
import hashlib
import os
import datetime
from pathlib import Path

# --- CONFIGURATION ---
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# Adjust this path if necessary. currently set to script location
BASE_DIR = Path(__file__).parent 
DB_PATH = BASE_DIR / "application.db"

# --- DATABASE SETUP ---
def init_db():
    connect = sqlite3.connect(DB_PATH)
    c = connect.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (userid INTEGER PRIMARY KEY AUTOINCREMENT, 
              username TEXT UNIQUE, 
              password TEXT,
              joindate DATE,
              lastlogin DATE,   
              saveme INTEGER DEFAULT 0)''')

    c.execute('''CREATE TABLE IF NOT EXISTS albums
                 (albumid INTEGER PRIMARY KEY AUTOINCREMENT,
              title TEXT, 
              artistid INTEGER, 
              date YEAR,
              rating INTEGER,
              genre TEXT,
              coverpath TEXT,
              dateadded DATE,
              FOREIGN KEY(artistid) REFERENCES artists(artistid))''')

    c.execute('''CREATE TABLE IF NOT EXISTS artists (
            artistid INTEGER PRIMARY KEY AUTOINCREMENT,
            profilepicpath TEXT,
            name TEXT UNIQUE
            )''')
    connect.commit()
    connect.close()

init_db()

# --- SECURITY & UTILS ---
def hash_password(password):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return (salt + key).hex()

def verify_password(stored_hex, provided_password):
    try:
        stored_bytes = bytes.fromhex(stored_hex)
        salt = stored_bytes[:32]
        stored_key = stored_bytes[32:]
        new_key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
        return new_key == stored_key
    except:
        return False

def captchagenerate(letters=string.ascii_lowercase + string.digits, length=5):
    return ''.join(random.choices(letters, k=length))

def captchaimage(captcha_text):
    image = ImageCaptcha(width=280, height=90)
    # image.generate returns data, but image.write saves it. 
    # We will save to a temp file to load into CTk
    fp = BASE_DIR / "captcha.png"
    image.write(captcha_text, str(fp)) 
    return captcha_text

def resolve_cover(raw):
    placeholder = BASE_DIR / "assets" / "placeholder.png"
    # Ensure assets dir exists
    if not (BASE_DIR / "assets").exists():
        (BASE_DIR / "assets").mkdir(parents=True, exist_ok=True)
        # Create a dummy placeholder if it doesn't exist to prevent crash
        if not placeholder.exists():
            img = Image.new('RGB', (250, 250), color='gray')
            img.save(placeholder)

    if not raw:
        return placeholder
    
    raw = raw.strip()
    candidate = Path(raw)
    
    if candidate.is_absolute():
        resolved = candidate
    else:
        resolved = BASE_DIR / raw.lstrip(r'\/')
        
    return resolved if resolved.exists() else placeholder

def bubblesort(data, key_index, reverse=False):
    arr = list(data)
    n = len(arr)
    for i in range(n - 1):
        for j in range(n - 1 - i):
            a = arr[j][key_index]
            b = arr[j + 1][key_index]
            should_swap = a < b if reverse else a > b
            if should_swap:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

# --- DATABASE LOGIC ---
def registeruser(username, password):
    if not username or not password:
        messagebox.showerror("Oops.", "Please actually enter something.")
        return
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            joindate = datetime.date.today()
            secure_password = hash_password(password)
            c.execute("INSERT INTO users (username, password, joindate, lastlogin) VALUES (?, ?, ?, ?)",
                      (username, secure_password, joindate, joindate))
            conn.commit()
            messagebox.showinfo("Success", "Account created successfully!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "An account already exists with that username.")

def listusersnids():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT userid, username FROM users ORDER BY userid")
        return [(row[0], row[1]) for row in c.fetchall()]

def getuserdetails(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT userid, username, password, joindate, lastlogin, saveme FROM users WHERE userid = ?", (user_id,))
        return c.fetchone()

def artistcheckregister(conn, artist_name):
    c = conn.cursor()
    c.execute("SELECT artistid FROM artists WHERE name = ?", (artist_name,))
    result = c.fetchone()
    if result: return result[0]
    c.execute("INSERT INTO artists (name) VALUES (?)", (artist_name,))
    conn.commit()
    return c.lastrowid

def addalbum(title, artist_name, date, rating, genre, coverpath):
    try:
        date = int(date)
        rating = int(rating)
        conn = sqlite3.connect(DB_PATH)
        artistid = artistcheckregister(conn, artist_name)
        dateadded = datetime.date.today()
        c = conn.cursor()
        c.execute(
            "INSERT INTO albums (title, artistid, date, rating, genre, coverpath, dateadded) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, artistid, date, rating, genre, coverpath, dateadded)
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"Album '{title}' added!")
    except ValueError:
        messagebox.showerror("Error", "Year and Rating must be integers.")

def credscheck(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    if user and verify_password(user[2], password):
        return user

def updatelastlogin(username):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE users SET lastlogin = ? WHERE username = ?", (datetime.date.today(), username))

def passwordsaved(answer, username):
    val = 1 if answer else 0
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE users SET saveme = ? WHERE username = ?", (val, username))

def getsaveduser():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE saveme = 1")
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def searchalbums(title=None, artist=None, genre=None, year=None, min_rating=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    query = """
        SELECT albums.albumid, albums.title, artists.name, albums.date, 
               albums.rating, albums.genre, albums.coverpath
        FROM albums JOIN artists ON albums.artistid = artists.artistid
    """
    conditions = []
    params = []

    if title:
        conditions.append("albums.title LIKE ?"); params.append(f"%{title}%")
    if artist:
        conditions.append("artists.name LIKE ?"); params.append(f"%{artist}%")
    if genre:
        conditions.append("albums.genre LIKE ?"); params.append(f"%{genre}%")
    if year:
        conditions.append("albums.date = ?"); params.append(int(year))
    if min_rating:
        conditions.append("albums.rating >= ?"); params.append(int(min_rating))

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    c.execute(query, params)
    res = c.fetchall()
    conn.close()
    return res

def get_unique_genres():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT DISTINCT genre FROM albums ORDER BY RANDOM()")
    rows = c.fetchall()
    conn.close()
    unique = set()
    for row in rows:
        if row[0]:
            parts = [p.strip() for p in str(row[0]).split('/')]
            for p in parts: unique.add(p)
    lst = list(unique)
    random.shuffle(lst)
    return lst[:10]

def generate_recommendations(targetgenre, prioritiserecent=False):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM albums")
    all_albums = c.fetchall()
    conn.close()
    
    scored = []
    for album in all_albums:
        db_genre = str(album[5]).lower()
        target = targetgenre.lower()
        if target not in db_genre: continue
        
        score = 50
        try: score += (int(album[4]) * 2)
        except: score += 10
        
        try:
            year = int(album[3])
            if prioritiserecent:
                if year >= 2023: score += 30
                elif year >= 2018: score += 10
        except: pass
        scored.append((score, album))
    
    scored = bubblesort(scored, 0) # Sort by score (index 0 of tuple)
    return [item[1] for item in scored[:8]]

# --- GUI CLASSES ---

class Application(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("NEA Album Manager")
        self.geometry("1200x800") # slightly smaller default than 1080p for compatibility
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Fonts
        self.defaultFont = ctk.CTkFont(family="Consolas", size=14)
        self.boldFont = ctk.CTkFont(family="Consolas", size=14, weight="bold")
        self.headingFont = ctk.CTkFont(family="Consolas", size=24, weight="bold")

        # Main Container
        self.content = ctk.CTkFrame(self)
        self.content.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        # Attach helper methods to content for frames to access
        self.content.shownewframe = self.shownewframe
        self.content.app = self
        self.content.captchawindow = self.captchawindow
        
        # Navigation Menu (Standard TK Menu is best for top-level dropdowns, or custom logic)
        self.page_menu = tk.Menu(self, tearoff=False)
        self.page_menu.add_command(label="Home", command=lambda: self.shownewframe(Home))
        self.page_menu.add_command(label="Search", command=lambda: self.shownewframe(Search))
        self.page_menu.add_command(label="Recommendations", command=lambda: self.shownewframe(Recommendations))
        self.page_menu.add_separator()
        
        self.admin_menu_index = None
        self.loggedinuser = None

        if getsaveduser() == "admin":
            self.show_admin_menu()
        
        self.page_menu.add_command(label="Sign out", command=self.signout)
        self.page_menu.add_command(label="Exit", command=self.destroy)

        # Menu Button (Floating)
        self.navbutton = ctk.CTkButton(self, text="☰", width=40, height=40, font=self.boldFont, command=self.openmenu)
        
        # Initial State Check
        saved = getsaveduser()
        if saved:
            self.loggedinuser = saved
            self.content.loggedinuser = saved
            self.shownewframe(AreYouSure)
        else:
            self.create_widgets()
            self.captchawindow()

    def create_widgets(self):
        self.LoginPage = LoginPage(self.content)
        self.LoginPage.grid(row=0, column=0, sticky="nsew")

    def openmenu(self):
        # Position menu at button location
        try:
            x = self.navbutton.winfo_rootx()
            y = self.navbutton.winfo_rooty() + self.navbutton.winfo_height()
            self.page_menu.tk_popup(x, y)
        finally:
            self.page_menu.grab_release()

    def shownewframe(self, frame_class):
        # Destroy children of content
        for widget in self.content.winfo_children():
            widget.destroy()
            
        frame = frame_class(self.content)
        frame.grid(row=0, column=0, sticky="nsew")

        # Hide menu button on login pages
        if isinstance(frame, (LoginPage, AreYouSure)):
            self.navbutton.place_forget()
        else:
            self.navbutton.place(x=20, y=20)

    def captchawindow(self):
        if hasattr(self, 'captcha_popup') and self.captcha_popup.winfo_exists():
            self.captcha_popup.destroy()

        ctext = captchaimage(captchagenerate())
        
        popup = ctk.CTkToplevel(self)
        popup.title("Captcha")
        popup.geometry("300x150")
        popup.attributes("-topmost", True)
        
        # Load image into CTkImage
        pil_img = Image.open(BASE_DIR / "captcha.png")
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(280, 90))
        
        lbl = ctk.CTkLabel(popup, text="", image=ctk_img)
        lbl.pack(pady=10)
        
        self.captcha = ctext
        self.captcha_popup = popup
        return ctext

    def signout(self):
        passwordsaved(False, self.loggedinuser)
        self.loggedinuser = None
        self.content.loggedinuser = None
        if hasattr(self, 'captcha_popup') and self.captcha_popup.winfo_exists():
            self.captcha_popup.destroy()
        self.hide_admin_menu()
        self.shownewframe(LoginPage)
        self.captchawindow()

    def show_admin_menu(self):
        if self.admin_menu_index is None:
            self.page_menu.insert_command(3, label="Admin", command=lambda: self.shownewframe(AdminPage))
            self.admin_menu_index = 3

    def hide_admin_menu(self):
        if self.admin_menu_index is not None:
            self.page_menu.delete(self.admin_menu_index)
            self.admin_menu_index = None

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        app = getattr(self.master, 'app', self.master)

        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.center_frame, text="welcome", font=app.headingFont).pack(pady=(0, 20))

        # Form
        form = ctk.CTkFrame(self.center_frame)
        form.pack(pady=10, padx=20)

        ctk.CTkLabel(form, text="user:", font=app.defaultFont).grid(row=0, column=0, padx=10, pady=10)
        self.userentry = ctk.CTkEntry(form, font=app.defaultFont, width=200)
        self.userentry.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(form, text="password:", font=app.defaultFont).grid(row=1, column=0, padx=10, pady=10)
        self.passentry = ctk.CTkEntry(form, show="*", font=app.defaultFont, width=200)
        self.passentry.grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkLabel(form, text="captcha:", font=app.defaultFont).grid(row=2, column=0, padx=10, pady=10)
        self.captchaentry = ctk.CTkEntry(form, font=app.defaultFont, width=200)
        self.captchaentry.grid(row=2, column=1, padx=10, pady=10)

        # Buttons
        btns = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        btns.pack(pady=20)
        
        ctk.CTkButton(btns, text="Login", font=app.boldFont, command=self.trylogin).pack(side="left", padx=10)
        ctk.CTkButton(btns, text="Register", font=app.boldFont, 
                      command=lambda: registeruser(self.userentry.get(), self.passentry.get())).pack(side="left", padx=10)

    def trylogin(self):
        app = self.master.app
        u = self.userentry.get()
        p = self.passentry.get()
        
        if not u or not p:
            messagebox.showerror("Oops", "Enter credentials.")
            return

        user_data = credscheck(u, p)
        if user_data and self.captchaentry.get() == getattr(app, 'captcha', None):
            app.loggedinuser = u
            updatelastlogin(u)
            if hasattr(app, 'captcha_popup'): app.captcha_popup.destroy()
            self.master.loggedinuser = u
            
            if u == "admin": app.show_admin_menu()
            else: app.hide_admin_menu()
            
            app.shownewframe(AreYouSure)
        else:
            app.captchawindow()
            messagebox.showerror('Error', 'Incorrect credentials or captcha.')

class AreYouSure(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        app = self.master.app
        username = getattr(app, 'loggedinuser', "User")

        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(wrapper, text=f"Wait! Is {username} the only user?", font=app.headingFont).pack(pady=10)
        
        warn_text = ("If you save your password here, others could:\n"
                     "- Ruin your search history\n"
                     "- Favourite bad music\n"
                     "- Leave awful reviews")
        ctk.CTkLabel(wrapper, text=warn_text, font=app.defaultFont, justify="left").pack(pady=10)

        btns = ctk.CTkFrame(wrapper, fg_color="transparent")
        btns.pack(pady=20)
        
        ctk.CTkButton(btns, text="Save Password", command=lambda: [passwordsaved(True, username), app.shownewframe(Home)]).pack(side="left", padx=10)
        ctk.CTkButton(btns, text="Don't Save", fg_color="transparent", border_width=2, command=lambda: [passwordsaved(False, username), app.shownewframe(Home)]).pack(side="left", padx=10)

class Home(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        app = self.master.app
        
        ctk.CTkLabel(self, text="Recently Added", font=app.headingFont).pack(pady=20)

        # Replaced manual Canvas with CTkScrollableFrame
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Get data
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("SELECT title, coverpath FROM albums ORDER BY dateadded DESC LIMIT 20")
            albums = c.fetchall()

        if not albums:
            ctk.CTkLabel(self.scroll_frame, text="No albums found.", font=app.defaultFont).pack(pady=20)
        else:
            self.populate_grid(albums)

    def populate_grid(self, albums):
        row = 0
        col = 0
        per_row = 4
        
        self.scroll_frame.grid_columnconfigure((0,1,2,3), weight=1)

        for title, coverpath in albums:
            card = ctk.CTkFrame(self.scroll_frame)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            # Image Handling
            img_path = resolve_cover(coverpath)
            try:
                pil_img = Image.open(img_path)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(200, 200))
                lbl_img = ctk.CTkLabel(card, text="", image=ctk_img)
            except Exception as e:
                lbl_img = ctk.CTkLabel(card, text="[IMG ERR]")
            
            lbl_img.pack(pady=5)
            ctk.CTkLabel(card, text=title, wraplength=180, font=("Consolas", 12, "bold")).pack(pady=(0,5))

            col += 1
            if col >= per_row:
                col = 0
                row += 1

class Search(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        app = self.master.app
        
        ctk.CTkLabel(self, text="Search", font=app.headingFont).pack(pady=10)

        # Controls
        form = ctk.CTkFrame(self)
        form.pack(pady=10)

        fields = [("Title:", "title"), ("Artist:", "artist"), ("Genre:", "genre"), 
                  ("Year:", "year"), ("Min Rating:", "rating")]
        
        self.entries = {}
        for i, (lbl, key) in enumerate(fields):
            ctk.CTkLabel(form, text=lbl).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            ent = ctk.CTkEntry(form, width=200)
            ent.grid(row=i, column=1, padx=10, pady=5)
            self.entries[key] = ent

        ctk.CTkLabel(form, text="Sort by:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
        self.sort_menu = ctk.CTkComboBox(form, values=["Title (A-Z)", "Year (New-Old)", "Rating (High-Low)"])
        self.sort_menu.grid(row=5, column=1, padx=10, pady=5)
        self.sort_menu.set("Rating (High-Low)")

        ctk.CTkButton(form, text="Search", command=self.runsearch).grid(row=6, column=0, columnspan=2, pady=15)

        # Results Area (Scrollable)
        self.results_area = ctk.CTkScrollableFrame(self)
        self.results_area.pack(fill="both", expand=True, padx=20, pady=10)

    def runsearch(self):
        # Clear previous
        for w in self.results_area.winfo_children(): w.destroy()

        res = searchalbums(
            title=self.entries["title"].get().strip(),
            artist=self.entries["artist"].get().strip(),
            genre=self.entries["genre"].get().strip(),
            year=self.entries["year"].get().strip(),
            min_rating=self.entries["rating"].get().strip()
        )

        mode = self.sort_menu.get()
        if "Title" in mode: res = bubblesort(res, 1)
        elif "Year" in mode: res = bubblesort(res, 3, True)
        else: res = bubblesort(res, 4, True)

        if not res:
            ctk.CTkLabel(self.results_area, text="No matches.").pack(pady=10)
            return

        for item in res:
            # item: (id, title, artist, year, rating, genre, cover)
            text = f"{item[1]}  //  {item[2]}  //  {item[3]}  //  ★ {item[4]}"
            card = ctk.CTkFrame(self.results_area)
            card.pack(fill="x", pady=2)
            ctk.CTkLabel(card, text=text, anchor="w").pack(padx=10, pady=5, fill="x")

class Recommendations(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        app = self.master.app
        
        ctk.CTkLabel(self, text="Find Your Sound", font=app.headingFont).pack(pady=20)
        
        controls = ctk.CTkFrame(self)
        controls.pack(pady=10)
        
        self.recent_switch = ctk.CTkSwitch(controls, text="Prioritise Recent (2023+)")
        self.recent_switch.pack(side="left", padx=20, pady=10)

        # Genre Buttons
        btn_box = ctk.CTkFrame(self, fg_color="transparent")
        btn_box.pack(pady=10)
        
        genres = get_unique_genres()
        if not genres:
            ctk.CTkLabel(btn_box, text="No genres available.").pack()
        else:
            # Simple flow layout logic using a text-wrap style or grid
            r, c = 0, 0
            for g in genres:
                ctk.CTkButton(btn_box, text=g, width=80, 
                              command=lambda x=g: self.show_recs(x)).grid(row=r, column=c, padx=5, pady=5)
                c += 1
                if c > 4: 
                    c = 0
                    r += 1

        self.rec_view = ctk.CTkScrollableFrame(self, orientation="horizontal", height=280)
        self.rec_view.pack(fill="x", expand=False, padx=20, pady=20)

    def show_recs(self, genre):
        for w in self.rec_view.winfo_children(): w.destroy()
        
        recs = generate_recommendations(genre, self.recent_switch.get())
        if not recs:
            ctk.CTkLabel(self.rec_view, text="No recommendations found.").pack(pady=50)
            return

        for album in recs:
            # album structure from DB select *
            # title=1, cover=6
            card = ctk.CTkFrame(self.rec_view, width=220)
            card.pack(side="left", padx=10, fill="y")
            
            p = resolve_cover(album[6])
            try:
                pil = Image.open(p)
                cimg = ctk.CTkImage(pil, pil, (200, 200))
                ctk.CTkLabel(card, text="", image=cimg).pack(pady=5)
            except: pass
            
            ctk.CTkLabel(card, text=album[1], font=("Consolas", 12, "bold"), wraplength=200).pack()
            ctk.CTkLabel(card, text=f"Score: {album[4]*2}").pack()

class AdminPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        app = self.master.app
        
        ctk.CTkLabel(self, text="Admin Dashboard", font=app.headingFont).pack(pady=10)
        
        # Tabs for better organization
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        tab_add = self.tabview.add("Add Album")
        tab_users = self.tabview.add("Manage Users")

        # --- ADD ALBUM ---
        form = ctk.CTkFrame(tab_add)
        form.pack(pady=20)
        
        self.add_entries = []
        labels = ["Title", "Artist", "Year", "Rating", "Genre", "Cover Path"]
        for i, l in enumerate(labels):
            ctk.CTkLabel(form, text=l).grid(row=i, column=0, padx=10, pady=5)
            e = ctk.CTkEntry(form, width=250)
            e.grid(row=i, column=1, padx=10, pady=5)
            self.add_entries.append(e)

        ctk.CTkButton(form, text="Submit Album", command=self.do_add).grid(row=6, column=0, columnspan=2, pady=20)

        # --- MANAGE USERS ---
        m_frame = ctk.CTkFrame(tab_users)
        m_frame.pack(pady=20)
        
        self.user_map = {}
        self.user_combo = ctk.CTkComboBox(m_frame, width=250, command=self.load_user)
        self.user_combo.grid(row=0, column=0, columnspan=2, pady=10)
        
        self.m_vars = {}
        keys = ["userid", "username", "password", "lastlogin", "saveme"]
        for i, k in enumerate(keys):
            ctk.CTkLabel(m_frame, text=k).grid(row=i+1, column=0, padx=5, pady=5, sticky="e")
            e = ctk.CTkEntry(m_frame, width=200)
            if k == "userid": e.configure(state="disabled")
            e.grid(row=i+1, column=1, padx=5, pady=5)
            self.m_vars[k] = e
            
        ctk.CTkButton(m_frame, text="Update User", command=self.update_user).grid(row=7, column=0, columnspan=2, pady=10)
        
        self.refresh_users()

    def do_add(self):
        vals = [e.get() for e in self.add_entries]
        addalbum(*vals)

    def refresh_users(self):
        users = listusersnids()
        vals = []
        self.user_map = {}
        for uid, uname in users:
            s = f"{uid} - {uname}"
            vals.append(s)
            self.user_map[s] = uid
        self.user_combo.configure(values=vals)
        if vals: self.user_combo.set(vals[0])

    def load_user(self, selection):
        uid = self.user_map.get(selection)
        if not uid: return
        data = getuserdetails(uid) # id, user, pass, join, last, save
        if data:
            self.update_entry(self.m_vars["userid"], str(data[0]))
            self.update_entry(self.m_vars["username"], data[1])
            self.update_entry(self.m_vars["password"], "") # Don't show hash
            self.update_entry(self.m_vars["lastlogin"], str(data[4]))
            self.update_entry(self.m_vars["saveme"], str(data[5]))

    def update_entry(self, entry, text):
        entry.configure(state="normal")
        entry.delete(0, "end")
        entry.insert(0, text)
        if entry == self.m_vars["userid"]: entry.configure(state="disabled")

    def update_user(self):
        uid = self.m_vars["userid"].get()
        if not uid: return
        
        uname = self.m_vars["username"].get()
        pwd = self.m_vars["password"].get()
        last = self.m_vars["lastlogin"].get()
        save = self.m_vars["saveme"].get()
        
        try:
            with sqlite3.connect(DB_PATH) as conn:
                if pwd:
                    hashed = hash_password(pwd)
                    conn.execute("UPDATE users SET username=?, password=?, lastlogin=?, saveme=? WHERE userid=?", 
                                 (uname, hashed, last, save, uid))
                else:
                    conn.execute("UPDATE users SET username=?, lastlogin=?, saveme=? WHERE userid=?", 
                                 (uname, last, save, uid))
            messagebox.showinfo("Success", "User updated.")
            self.refresh_users()
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = Application()
    app.mainloop()