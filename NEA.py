import tkinter as tk 
from tkinter import ttk, font, messagebox
from captcha.image import ImageCaptcha
from PIL import Image, ImageTk, ImageOps
import random
import string
import sqlite3
import datetime
from pathlib import Path

#test uhhhhhhhhhhhhhhhh
BASE_DIR = Path("/home/willy/Documents/NEA")
DB_PATH = BASE_DIR / "application.db"

#Connecting to the database file, and if it doesnt exist it'll be created
connect = sqlite3.connect(DB_PATH)
c = connect.cursor()

#Creating the table for Users, if it isnt already there.
c.execute('''CREATE TABLE IF NOT EXISTS users
             (userid INTEGER PRIMARY KEY AUTOINCREMENT, 
          username TEXT UNIQUE, 
          password TEXT,
          joindate DATE,
          lastlogin DATE,   
          saveme INTEGER DEFAULT 0)''')

#Creating the albums table, if it isnt there already.
#The artist ID is foreign, so4fjryehcxvgyt7yl65oihghtr67hy5  h j,yyubhyuj6tuj9f8ngrvh ydf6th67rvh4ujg7okvyhji5gtmjt6gfffffffe76ducvjm, we can add info about artists later on
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

#Making the artists table
c.execute('''CREATE TABLE IF NOT EXISTS artists (
        artistid INTEGER PRIMARY KEY AUTOINCREMENT,
        profilepicpath TEXT,
        name TEXT UNIQUE
        )''')

#Closing the global connection
c.close()

#This function inserts data into the SQL database, and generates the information regarding logins and account creation date.
def registeruser(username, password):

    if not username or not password:
        messagebox.showerror("Oops.", "Please actually enter something.")
        return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        joindate = datetime.date.today()
        lastlogin = joindate
        c.execute(
                "INSERT INTO users (username, password, joindate, lastlogin) VALUES (?, ?, ?, ?)",
                (username, password, joindate, lastlogin)
        )
        conn.commit()
        messagebox.showinfo("Success", "Account created successfully!")


    except sqlite3.IntegrityError: # this makes sure the user's input is unique, to maintain database integrity
        messagebox.showerror("Error", "An account already exists with that username.")


    conn.close()

#This function returns every username, so in the Admin Panel the dropdown stays populated with results from the database.
def listusersnids(): #List USERS N IDS (it sounded better in my head)
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT userid, username FROM users ORDER BY userid")
        return [(row[0], row[1]) for row in c.fetchall()]

#kinda self explanatory 
def getuserdetails(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(
            """
            SELECT userid, username, password, joindate, lastlogin, saveme
            FROM users
            WHERE userid = ?
            """,
            (user_id,),
        )
        return c.fetchone()

#This function checks to see if an artist is already inside of the database, (as of artist potentially having multiple albums) and if its already there- it links the album to the right artistid. If not it just creates a new record for the artist.
def artistcheckregister(conn, artist_name):
    c = conn.cursor()
    c.execute("SELECT artistid FROM artists WHERE name = ?", (artist_name,))
    result = c.fetchone()
    if result:
        return result[0]
    c.execute("INSERT INTO artists (name) VALUES (?)", (artist_name,))
    conn.commit()
    return c.lastrowid  # This Says Last Row ID, not lastrowid ik it looks confusing

#This function inserts data about albums, and it also calls the checking function to make sure it actually links it to an artist.
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
    except ValueError:
        messagebox.showerror("Error", "Year and Rating must be integers.")
        return


    conn.close()
    messagebox.showinfo("Success", f"Album '{title}' by '{artist_name}' added successfully!")

def getalbum(albumid):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # access columns by name
    c = conn.cursor()
    c.execute(
        """
        SELECT title, date, rating, genre, coverpath
        FROM albums
        WHERE albumid = ?
        """,
        (albumid,)
    )
    row = c.fetchone()
    conn.close()

    if row is None:
        print('No album found with that ID.')
        return None  # Cant find an album!!!
    

    
    cover = row["coverpath"]

    return row["title"], row["date"], row["rating"], row["genre"], cover

#addalbum("Icedancer", "Bladee", 2018, 6, "Cloud Rap", "assets/icedancer.jpg")
#addalbum("Revengeseekerz", "Jane Remover", 2025, 10, "Hyperpop", "assets/revengeseekerz.jpg")
#addalbum("Toxicity", "System of a Down", 2001, 9, "Alternative Metal", "assets/toxicity.jpg")
#addalbum("Nothing Was the Same", "Drake", 2013, 8, "Hip Hop / R&B", "assets/nothing_was_the_same.jpg")
#addalbum("OK Computer", "Radiohead", 1997, 10, "Alternative Rock", "assets/ok_computer.jpg")
#addalbum("Ghostholding", "Venturing", 2024, 9, "Alternative", "assets/ghostholding.png")
#addalbum("Die Lit", "Playboi Carti", 2018, 9, "Trap / Experimental Hip Hop", "assets/die_lit.jpg")
#addalbum("The Boy Who Played the Harp", "Dave", 2025, 9, "UK Rap / Peak", "assets/the_boy_who_played_the_harp.jpg")
#addalbum("Graduation", "Kanye West", 2007, 9, "Hip Hop", "assets/graduation.jpg")
#addalbum("The Money Store", "Death Grips", 2012, 10, "Industrial / Experimental", "assets/money_store.jpg")
#addalbum("AM", "Arctic Monkeys", 2013, 8, "Indie Rock", "assets/am.jpg")
#addalbum("Good Kid, M.A.A.D City", "Kendrick Lamar", 2012, 10, "Hip Hop", "assets/gkmc.jpg")
# addalbum("Frailty", "Jane Remover", 2021, 10, "Hyperpop / Shoegaze", "assets/frailty.jpg")
# addalbum("Rodeo", "Travis Scott", 2015, 10, "Trap / Hip Hop", "assets/rodeo.jpg")
# addalbum("Astroworld", "Travis Scott", 2018, 9, "Trap / Hip Hop", "assets/astroworld.jpg")
# addalbum("The College Dropout", "Kanye West", 2004, 10, "Hip Hop / Soul", "assets/the_college_dropout.jpg")
# addalbum("Birds in the Trap Sing McKnight", "Travis Scott", 2016, 9, "Trap / Hip Hop", "assets/birds_in_the_trap.jpg")
# addalbum("dariacore", "leroy", 2021, 9, "Dariacore / Mashcore", "assets/dariacore.jpg")
# addalbum("dariacore 2: enter here, never leave", "leroy", 2021, 9, "Dariacore / Mashcore", "assets/dariacore2.jpg")
# addalbum("dariacore 3: is it really a joke if no one laughs?", "leroy", 2022, 9, "Dariacore / Mashcore", "assets/dariacore3.jpg")
# addalbum("Scary Monsters and Nice Sprites", "Skrillex", 2010, 10, "Dubstep / EDM", "assets/scary_monsters.jpg")




#This function checks to see whether the info a user has entered, matches with a username and password from the database.
def credscheck(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

def updatelastlogin(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        today = datetime.date.today()
        c.execute("UPDATE users SET lastlogin = ? WHERE username = ?", (today, username))
        conn.commit()
    finally:
        conn.close()

def passwordsaved(answer, username):
        if answer == True:
                savemevalue = 1
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("UPDATE users SET saveme = ? WHERE username = ?", (savemevalue, username))
                print(username, "remains the saved user")
                conn.commit()
                conn.close()

        elif answer == False:
                savemevalue = 0
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("UPDATE users SET saveme = ? WHERE username = ?", (savemevalue, username))
                print(username, "is no longer saved")
                conn.commit()
                conn.close()

def getsaveduser():
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT username, password FROM users WHERE saveme = 1")
        result = c.fetchone()
        conn.close()
        return result[0] if result else None

def searchalbums(title=None, artist=None, genre=None, year=None, min_rating=None):
    """
    Returns: (albumid, title, artist_name, year, rating, genre, coverpath)
    Matches optional search filters.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    query = """
        SELECT albums.albumid,
               albums.title,
               artists.name,
               albums.date,
               albums.rating,
               albums.genre,
               albums.coverpath
        FROM albums
        JOIN artists ON albums.artistid = artists.artistid
    """

    conditions = []
    params = []

    if title:
        conditions.append("albums.title LIKE ?")
        params.append(f"%{title}%")

    if artist:
        conditions.append("artists.name LIKE ?")
        params.append(f"%{artist}%")

    if genre:
        conditions.append("albums.genre LIKE ?")
        params.append(f"%{genre}%")

    if year:
        conditions.append("albums.date = ?")
        params.append(int(year))

    if min_rating:
        conditions.append("albums.rating >= ?")
        params.append(int(min_rating))

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    c.execute(query, params)
    results = c.fetchall()
    conn.close()
    return results

def bubblesort(data, key_index, reverse=False):
    
    # Implementation of bubble sort instead of reusing ORDER BY
    # data: list of tuples
    # key_index: which element we're sorting by (e.g. 1 being the title and so on)
    # reverse: if true then DSC and false then ASC ykyk
    
    arr = list(data) # make a python variable of wtv we sorting
    n = len(arr) # sees how many things r in the list (how many items we sorting)

    for i in range(n - 1): #sees how many passes r gna be needed
        for j in range(n - 1 - i): #compares neighbours!!!!!
            a = arr[j][key_index] # pull out the item
            b = arr[j + 1][key_index] # pull out the next one

            if reverse: # deciding whether to swap!!!!!
                should_swap = a < b
            else:
                should_swap = a > b

            if should_swap: #swap em!!!!!!!
                arr[j], arr[j + 1] = arr[j + 1], arr[j]

    return arr

def showcovers(parent):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT title, coverpath FROM albums ORDER BY dateadded DESC LIMIT 20")
        albums = c.fetchall()

    frame = tk.Frame(parent)
    frame.pack(pady=10)

    images = [] # creates a list to store album cover images
    placeholder = BASE_DIR / "assets" / "placeholder.png"
    coversize = (250, 250)
    per_row = 4

    def resolve_cover(raw):
        if not raw: # if the coverpath is empty, default image is subbed in
            return placeholder
        raw = raw.strip()
        candidate = Path(raw)
        if candidate.is_absolute():
            if str(candidate).startswith(str(BASE_DIR)): # Makes sure its within the base directory
                resolved = candidate #the absolute path of the image
            else:
                return placeholder # If not then it returns the default image
        else:
            resolved = BASE_DIR / raw.lstrip('\/') # it shows the relative path of the image
        return resolved if Path(resolved).exists() else placeholder # if the path exists, it returns it- and if not it returns the default 

    if not albums: # If there isnt anything in the database, it just replaces the grid with a message saying that
        empty_label = tk.Label(frame, text="No albums yet", font=getattr(parent.master, "defaultFont", None)) # Oh no!!
        empty_label.pack(pady=20)
        return frame

    for index, (title, coverpath) in enumerate(albums):
        candidate = resolve_cover(coverpath)
        try:
            image = Image.open(candidate).convert("RGBA") # It tries to open the image
        except (FileNotFoundError, OSError): #If the file isnt found, or it cant load for some reason- it just smashes the placeholder in there
            image = Image.open(placeholder).convert("RGBA")

        image = ImageOps.fit(image, coversize, Image.LANCZOS) # Resizing the image to make all the pics the same on the home screen
        photo = ImageTk.PhotoImage(image) # making it a tk image
        images.append(photo) # doing it

        row, col = divmod(index, per_row) # Creation of the grid
        album_frame = tk.Frame(frame) # Each album gets its own frame
        album_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        cover_label = tk.Label(album_frame, image=photo)
        cover_label.grid(row=0, column=0)

        title_font = getattr(app, "defaultFont") # Grabs the font from inside the tk app
        title_label = tk.Label(album_frame, text=title, font=title_font, wraplength=coversize[0])
        title_label.grid(row=1, column=0, pady=(5, 0))

    for col in range(per_row):
        frame.grid_columnconfigure(col, weight=1)
    frame.images = images  # Keep references so images stay visible.
    return frame

def captchagenerate( # Generating a string of random letters and numbers when called
        letters = string.ascii_lowercase + string.digits, #Defining what the string consists of
        length = 5
    ):
    return ''.join(random.choices(letters, k=length))

def captchaimage(captcha_text):
    image = ImageCaptcha(width = 280, height = 90)
    data = image.generate(captcha_text)  
    image.write(captcha_text, BASE_DIR / "captcha.png")
    return(captcha_text)  #Saving it to a file so it can be used in the window (BASE DIR USED!! absolute path)



# DIVIDER



class Application(tk.Tk):
    def __init__(self):
        super().__init__()
    
        self.admin_menu_index = None

        #configuration of all the apps settings overall
        self.title("Login")
        self.resizable(0,0)
        self.defaultFont = font.nametofont("TkDefaultFont")
        self.defaultFont.configure(family="Consolas")
        self.boldFont = self.defaultFont.copy()
        self.boldFont.configure(weight="bold")
        self.headingFont = self.boldFont.copy()
        self.headingFont.configure(size=20)
        self.geometry("1920x1080")
        

        #This is going to define the environment for all pages, essentual the central content frame.
        self.content = tk.Frame(self, bg="#FFFFFF")


        # Copying over the fonts into the container, so it actually works.
        self.content.defaultFont = self.defaultFont
        self.content.boldFont = self.boldFont
        self.content.headingFont = self.headingFont

        self.content.captchawindow = self.captchawindow
        self.content.shownewframe = self.shownewframe
        self.content.app = self

        #Dropdown menu
        self.page_menu = tk.Menu(self, tearoff=False)
        self.page_menu.add_command(label="Home", command=lambda:self.shownewframe(Home))
        self.page_menu.add_command(label="Search", command=lambda:self.shownewframe(Search))
        self.page_menu.add_command(label="Rankings", command=lambda:self.shownewframe(Home))


        # lol its seperated in the code tooo!!! hahahahaha lo lolololol
        self.page_menu.add_separator() 
        
        saveduser = getsaveduser()
        if getsaveduser() == "admin":
            self.show_admin_menu()
        else:
            self.hide_admin_menu()

        self.page_menu.add_command(label="Sign out", command=lambda:self.signout())
        self.page_menu.add_command(label="Exit", command=self.destroy)
        

        #The Button that Opens said menu!?!?!?!
        self.navbutton = tk.Button(self, text="☰", font=self.boldFont, command=self.openmenu)
        self.navbutton.place_forget()

        #Start the Log In Screean!!! (Ignore the saved user part) 
        #self.shownewframe(LoginPage)




        self.content.pack(fill="both", expand=True)

        #The check to see if the user needs to log in - or whether they saved their info so the login screen is ignored.

        print(saveduser, "is the saved user")

        if saveduser:
            self.loggedinuser = saveduser
            # if self.loggedinuser == "admin":
            #     self.page_menu.add_command(label="Admin", command=lambda:self.shownewframe(AdminPage))
            self.content.loggedinuser = saveduser
            self.shownewframe(AreYouSure)

        else:
            self.create_widgets()
            self.captchawindow()

        # self.create_widgets()
        # self.captchawindow()


        
    def create_widgets(self):
        self.LoginPage = LoginPage(self.content)
        self.LoginPage.pack(fill='both', expand=True)

    def openmenu(self):
        x = self.navbutton.winfo_rootx()
        y = self.navbutton.winfo_rooty() + self.navbutton.winfo_height()
        
        self.page_menu.tk_popup(x, y)
        self.page_menu.grab_release()

    def shownewframe(self, frame_class):
        # Destroy all frames in the window
        for widget in self.content.winfo_children():
            widget.destroy()
        # Create the new frame
        frame = frame_class(self.content)
        frame.pack(fill='both', expand=True)


        if isinstance(frame, (LoginPage, AreYouSure)):
            self.navbutton.place_forget()
        else:
            self.navbutton.place(x=10, y=10)

    def captchawindow(self):
        if hasattr(self, 'captcha_popup') and self.captcha_popup.winfo_exists():
            self.captcha_popup.destroy()

        ctext = captchaimage(captchagenerate())
        print(ctext)
        popup = tk.Toplevel(self)
        popup.title("Captcha")
        popup.resizable(0, 0)
        img = tk.PhotoImage(file=str(BASE_DIR / "captcha.png"))
        captchapicture = tk.Label(popup, image=img)
        captchapicture.image = img
        captchapicture.pack()
        self.captcha = ctext
        self.captcha_popup = popup
        return ctext

    def signout(self):
        passwordsaved(False, self.loggedinuser)
        self.loggedinuser = None
        if hasattr(self.content, "loggedinuser"):
            self.content.loggedinuser = None

        if hasattr(self, 'captcha_popup') and self.captcha_popup.winfo_exists():
            self.captcha_popup.destroy()
        self.hide_admin_menu()
        self.shownewframe(LoginPage)
        self.captchawindow()

    def show_admin_menu(self):
        if self.admin_menu_index is not None:
            return
        # insert near top (index 3) or just append
        self.page_menu.add_command(label="Admin", command=lambda: self.shownewframe(AdminPage))
        self.admin_menu_index = self.page_menu.index("end")  # remember location

    def hide_admin_menu(self):
        if self.admin_menu_index is None:
            return
        self.page_menu.delete(self.admin_menu_index)
        self.admin_menu_index = None

class LoginPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.label = tk.Label(self, text="welcome", font=self.master.headingFont)
        self.label.pack(pady=0)

        form_frame = tk.Frame(self)
        form_frame.pack(pady=20)



        tk.Label(form_frame, text="user:", font=self.master.defaultFont).grid(row=0, column=0, padx=(10))
        self.userentry = tk.Entry(form_frame, font=self.master.defaultFont)
        self.userentry.grid(row=0, column=1, sticky="w", padx=(10))
        #username = self.userentry.get()


        tk.Label(form_frame, text="password:", font=self.master.defaultFont).grid(row=1, column=0, padx=(10))
        self.passentry = tk.Entry(form_frame, font=self.master.defaultFont)
        self.passentry.grid(row=1, column=1, sticky="w", padx=(10))
        #password = self.passentry.get()


        tk.Label(form_frame, text="captcha:", font=self.master.defaultFont).grid(row=2, column=0, padx=(10))
        self.captchaentry = tk.Entry(form_frame, font=self.master.defaultFont)
        self.captchaentry.grid(row=2, column=1, sticky="w", padx=(10))

        buttons_frame = tk.Frame(self)
        buttons_frame.pack(pady=10)
        
        login = tk.Button(buttons_frame, text="login", font=self.master.boldFont, command=lambda: trylogin(self))
        register = tk.Button(buttons_frame, text="register", font=self.master.boldFont, command=lambda: registeruser(self.userentry.get(), self.passentry.get()))

        login.pack(side="left", padx=10)
        register.pack(side="left", padx=10)
        
        def trylogin(self):
            app = getattr(self.master, 'app', self.master)
            username = self.userentry.get()
            password = self.passentry.get()
            if not username or not password:
                messagebox.showerror("Oops.", "Please actually enter something.")
                return
            app = getattr(self.master, 'app', self.master)
            if credscheck(username, password) and self.captchaentry.get() == getattr(app, 'captcha', None):
                app.loggedinuser = username
                updatelastlogin(username)
                print(app.loggedinuser, 'logged in')
                if hasattr(app, 'captcha_popup') and app.captcha_popup.winfo_exists():
                    app.captcha_popup.destroy()
                self.loggedinuser = app.loggedinuser
                app.content.loggedinuser = self.loggedinuser
                if username == "admin":
                    app.show_admin_menu()
                else:
                    app.hide_admin_menu()
                app.shownewframe(AreYouSure)
            else:
                app.shownewframe(LoginPage)
                messagebox.showerror('Error', 'Incorrect credentials.')
       
class AreYouSure(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        app = getattr(self.master, 'app', self.master) 
        username = getattr(app, 'loggedinuser', None)



        self.label = tk.Label(self, text="wait!!!! do other people use this computer", font=self.master.headingFont)
        self.label.pack(pady=0)

        tk.Label(self, text=(username, "is logged in"), font=self.master.defaultFont).pack(pady=5)

        self.label = tk.Label(self, text="If you save your password here, anyone who uses this computer could access your account. \nthey could:", font=self.master.defaultFont)
        self.label.pack(pady=5)
        
        self.label = tk.Label(self, text="- ruin your search history\n- favourite really bad music\n- leave awful reviews\n- make it seem as if you have really bad taste \n- be silly")
        self.label.pack(pady=5)


        buttons_frame = tk.Frame(self)
        buttons_frame.pack(pady=10)
        yes = tk.Button(buttons_frame, text="Save password", font=self.master.boldFont, command=lambda: [passwordsaved(True, username), app.shownewframe(Home)])
        no = tk.Button(buttons_frame, text="Don't", font=self.master.boldFont, command=lambda: [passwordsaved(False, username), app.shownewframe(Home)])
        yes.pack(side="left", padx=10)
        no.pack(side="left", padx=10)
        form_frame = tk.Frame(self)
        form_frame.pack(pady=20)
        
class Home(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack_propagate(False)
        self.label = tk.Label(self, text="Recently Added", font=self.master.headingFont)
        self.label.pack(pady=0)

        wrapper = tk.Frame(self)
        wrapper.pack(fill="both", expand=True)

        canvas = tk.Canvas(wrapper)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(wrapper, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        inner = tk.Frame(canvas)
        inner_window = canvas.create_window((0, 0), window=inner, anchor="n")
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-int(e.delta/120), "units")) # allows fr mouse wheel scrolling


        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.coords(inner_window, e.width / 2, 0))

        self.recent_covers = showcovers(inner)

class Search(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        tk.Label(self, text="Search", font=self.master.headingFont).pack(pady=10)

        form = tk.Frame(self)
        form.pack(pady=10)

        # TITLE
        tk.Label(form, text="Title:", font=self.master.defaultFont).grid(row=0, column=0, sticky="e")
        self.titleentry = tk.Entry(form, font=self.master.defaultFont)
        self.titleentry.grid(row=0, column=1, padx=10)

        # ARTIST
        tk.Label(form, text="Artist:", font=self.master.defaultFont).grid(row=1, column=0, sticky="e")
        self.artistentry = tk.Entry(form, font=self.master.defaultFont)
        self.artistentry.grid(row=1, column=1, padx=10)

        # GENRE
        tk.Label(form, text="Genre:", font=self.master.defaultFont).grid(row=2, column=0, sticky="e")
        self.genreentry = tk.Entry(form, font=self.master.defaultFont)
        self.genreentry.grid(row=2, column=1, padx=10)

        # YEAR
        tk.Label(form, text="Year:", font=self.master.defaultFont).grid(row=3, column=0, sticky="e")
        self.yearentry = tk.Entry(form, font=self.master.defaultFont)
        self.yearentry.grid(row=3, column=1, padx=10)

        # MIN RATING
        tk.Label(form, text="Min rating:", font=self.master.defaultFont).grid(row=4, column=0, sticky="e")
        self.minratingentry = tk.Entry(form, font=self.master.defaultFont)
        self.minratingentry.grid(row=4, column=1, padx=10)

        # SORT OPTIONS
        tk.Label(form, text="Sort by:", font=self.master.defaultFont).grid(row=5, column=0, sticky="e")

        self.sort_var = tk.StringVar(value="Rating (high→low)")
        self.sort_menu = ttk.Combobox(
            form,
            textvariable=self.sort_var,
            state="readonly",
            width=20,
            values=[
                "Title (A→Z)",
                "Year (new→old)",
                "Rating (high→low)",
            ]
        )
        self.sort_menu.grid(row=5, column=1, padx=10)

        tk.Button(
            form,
            text="Search",
            font=self.master.boldFont,
            command=self.runsearch
        ).grid(row=6, column=0, columnspan=2, pady=15)

        # RESULTS AREA
        self.results_frame = tk.Frame(self)
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.results_canvas = tk.Canvas(self.results_frame)
        self.results_canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=self.results_canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.results_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.inner_results = tk.Frame(self.results_canvas)
        self.results_window = self.results_canvas.create_window((0, 0), window=self.inner_results, anchor="nw")

        self.inner_results.bind("<Configure>", lambda e: self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all")))
        self.results_canvas.bind("<Configure>", lambda e: self.results_canvas.coords(self.results_window, 0, 0))

    def runsearch(self):
        title = self.titleentry.get().strip() or None
        artist = self.artistentry.get().strip() or None
        genre = self.genreentry.get().strip() or None
        year = self.yearentry.get().strip() or None
        min_rating = self.minratingentry.get().strip() or None

        raw_results = searchalbums(
            title=title,
            artist=artist,
            genre=genre,
            year=year,
            min_rating=min_rating,
        )

        sort_choice = self.sort_var.get()

        if sort_choice == "Title (A→Z)":
            sorted_results = bubblesort(raw_results, key_index=1)
        elif sort_choice == "Year (new→old)":
            sorted_results = bubblesort(raw_results, key_index=3, reverse=True)
        else:
            sorted_results = bubblesort(raw_results, key_index=4, reverse=True)

        self.display_results(sorted_results)

    def display_results(self, results):
        for widget in self.inner_results.winfo_children():
            widget.destroy()

        if not results:
            tk.Label(self.inner_results, text="No results found.", font=self.master.defaultFont).pack(pady=10)
            return

        for (albumid, title, artist_name, year, rating, genre, coverpath) in results:
            text = f"{title} – {artist_name} ({year})  [{rating}/10]  ({genre})"
            tk.Label(self.inner_results, text=text, font=self.master.defaultFont, anchor="w", justify="left").pack(
                fill="x", padx=5, pady=2
            )

class AdminPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.label = tk.Label(self, text="Dashboard", font=self.master.headingFont)
        self.label.pack(pady=0)

        addframe = tk.Frame(self)
        addframe.pack(pady=20)

        tk.Label(addframe, text="Title:", font=self.master.defaultFont).grid(row=0, column=0, padx=10)
        self.titleentry = tk.Entry(addframe, font=self.master.defaultFont)
        self.titleentry.grid(row=0, column=1, sticky="w", padx=10)

        tk.Label(addframe, text="Artist:", font=self.master.defaultFont).grid(row=1, column=0, padx=10)
        self.artistentry = tk.Entry(addframe, font=self.master.defaultFont)
        self.artistentry.grid(row=1, column=1, sticky="w", padx=10)

        tk.Label(addframe, text="Year:", font=self.master.defaultFont).grid(row=2, column=0, padx=10)
        self.yearentry = tk.Entry(addframe, font=self.master.defaultFont)
        self.yearentry.grid(row=2, column=1, sticky="w", padx=10)

        tk.Label(addframe, text="Rating:", font=self.master.defaultFont).grid(row=3, column=0, padx=10)
        self.ratingentry = tk.Entry(addframe, font=self.master.defaultFont)
        self.ratingentry.grid(row=3, column=1, sticky="w", padx=10)

        tk.Label(addframe, text="Genre:", font=self.master.defaultFont).grid(row=4, column=0, padx=10)
        self.genreentry = tk.Entry(addframe, font=self.master.defaultFont)
        self.genreentry.grid(row=4, column=1, sticky="w", padx=10)

        tk.Label(addframe, text="Coverpath:", font=self.master.defaultFont).grid(row=5, column=0, padx=10)
        self.coverentry = tk.Entry(addframe, font=self.master.defaultFont)
        self.coverentry.grid(row=5, column=1, sticky="w", padx=10)

        tk.Button(
            addframe,
            text="Add Album",
            font=self.master.boldFont,
            command=lambda: addalbum(
                self.titleentry.get(),
                self.artistentry.get(),
                self.yearentry.get(),
                self.ratingentry.get(),
                self.genreentry.get(),
                self.coverentry.get(),
            ),
        ).grid(row=6, column=0, columnspan=2, pady=10)

        manageframe = tk.Frame(self)
        manageframe.pack(pady=20)

        tk.Label(manageframe, text="Account Manager", font=self.master.headingFont).grid(
            row=0, column=0, columnspan=2, pady=(0, 10)
        )

        self.uservar = tk.StringVar()
        self.userdropdown = ttk.Combobox(
            manageframe,
            textvariable=self.uservar,
            state="readonly",
            width=25,
        )
        self.userdropdown.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")
        self.userdropdown.bind("<<ComboboxSelected>>", self.populateuserinfo)

        tk.Label(manageframe, text="User ID:", font=self.master.defaultFont).grid(row=3, column=0, sticky="w")
        self.userid_var = tk.StringVar()
        tk.Entry(manageframe, textvariable=self.userid_var, state="readonly").grid(row=3, column=1, padx=10, sticky="ew")

        tk.Label(manageframe, text="Username:", font=self.master.defaultFont).grid(row=4, column=0, sticky="w")
        self.username_var = tk.StringVar()
        tk.Entry(manageframe, textvariable=self.username_var).grid(row=4, column=1, padx=10, sticky="ew")

        tk.Label(manageframe, text="Password:", font=self.master.defaultFont).grid(row=5, column=0, sticky="w")
        self.password_var = tk.StringVar()
        tk.Entry(manageframe, textvariable=self.password_var).grid(row=5, column=1, padx=10, sticky="ew")

        tk.Label(manageframe, text="Join date:", font=self.master.defaultFont).grid(row=6, column=0, sticky="w")
        self.joindate_var = tk.StringVar()
        tk.Entry(manageframe, textvariable=self.joindate_var, state="readonly").grid(row=6, column=1, padx=10, sticky="ew")

        tk.Label(manageframe, text="Last login:", font=self.master.defaultFont).grid(row=7, column=0, sticky="w")
        self.lastlogin_var = tk.StringVar()
        tk.Entry(manageframe, textvariable=self.lastlogin_var).grid(row=7, column=1, padx=10, sticky="ew")

        tk.Label(manageframe, text="Saved?", font=self.master.defaultFont).grid(row=8, column=0, sticky="w")
        self.saveme_var = tk.StringVar()
        tk.Entry(manageframe, textvariable=self.saveme_var).grid(row=8, column=1, padx=10, sticky="ew")

        tk.Button(
            manageframe,
            text="Save changes",
            font=self.master.boldFont,
            command=self.saveuserchanges,
        ).grid(row=9, column=0, columnspan=2, pady=10)

        self.user_display_map = {}
        self.refreshuserdropdown()

    def refreshuserdropdown(self, selected_id=None):
        pairs = listusersnids()
        self.user_display_map = {}
        values = []
        for uid, uname in pairs:
            label = f"{uid} – {uname}"
            self.user_display_map[label] = uid
            values.append(label)
        self.userdropdown["values"] = values
        if selected_id is not None:
            for label, uid in self.user_display_map.items():
                if uid == selected_id:
                    self.uservar.set(label)
                    break
        else:
            self.uservar.set("")

    def populateuserinfo(self, _event=None):
        display = self.uservar.get()
        user_id = self.user_display_map.get(display)
        if not user_id:
            self.clearuserfields()
            return

        record = getuserdetails(user_id)
        if not record:
            self.clearuserfields()
            return

        userid, username, password, joindate, lastlogin, saveme = record
        self.userid_var.set(userid)
        self.username_var.set(username or "")
        self.password_var.set(password or "")
        self.joindate_var.set(joindate or "")
        self.lastlogin_var.set(lastlogin or "")
        self.saveme_var.set("Yes" if saveme else "No")

    def clearuserfields(self):
        self.userid_var.set("")
        self.username_var.set("")
        self.password_var.set("")
        self.joindate_var.set("")
        self.lastlogin_var.set("")
        self.saveme_var.set("")

    def saveuserchanges(self):
        display = self.uservar.get()
        user_id = self.user_display_map.get(display)
        if not user_id:
            messagebox.showerror("Error", "Select a user first.")
            return

        new_username = self.username_var.get()
        new_password = self.password_var.get()
        new_lastlogin = self.lastlogin_var.get()
        new_saveme = 1 if self.saveme_var.get().strip().lower() == "yes" else 0

        try:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute(
                    """
                    UPDATE users
                    SET username = ?, password = ?, lastlogin = ?, saveme = ?
                    WHERE userid = ?
                    """,
                    (new_username, new_password, new_lastlogin, new_saveme, user_id),
                )
                conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "That username is already taken.")
            return

        messagebox.showinfo("Saved", f"Updated user #{user_id}.")
        self.refreshuserdropdown(selected_id=user_id)
        self.populateuserinfo()

app = Application()
app.mainloop()
