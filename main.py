# Imports
from tkinter import messagebox
from connection import initialize_db
from data_entry_gui import DataEntry
from eval_entry_gui import eval_search_update_duplicate
from query_gui import QuerySearch
from data_manipulate_func import clear_data, create_tables
from tkinter import *
import mysql.connector
from context import context


SERVER = '127.0.0.1'

# Spawns the initial window
root = Tk()

# Sets the size for the window
root.geometry("350x150")

# GLOBAL VARIABLES
tracker = 'empty'

# Creates a canvas to use initialy
canvas = Canvas(root)
canvas.pack()

# --------------------------------------------
#  Login Screen
#     This screen stays till the user signs
#     into the SQL server.
# --------------------------------------------


def login():
    global canvas
    try:
        context.db = initialize_db(server=SERVER,
                                   username=i2.get(),
                                   password=i3.get(),
                                   database_name=i1.get())
        context.cursor = context.db.cursor()
    except ValueError as e:
        return messagebox.showerror("Error", str(e))
    except mysql.connector.Error as e:
        feedback.config(text='Incorrect Creds/Server')
        print(e)
        return messagebox.showerror("Error", str(e))
    canvas.destroy()
    create_tables(context.cursor)
    context.db.commit()
    myOptions()


title = Label(canvas, text='SQL Login')
title.grid(row=0, column=1)
server = Label(canvas, text='SQL database')
server.grid(row=1, column=0)
username = Label(canvas, text='username')
username.grid(row=2, column=0)
password = Label(canvas, text='password')
password.grid(row=3, column=0)
feedback = Label(canvas)
feedback.grid(row=4, column=0)

i1 = Entry(canvas)
i1.grid(row=1, column=1)
i2 = Entry(canvas)
i2.grid(row=2, column=1)
i3 = Entry(canvas)
i3.grid(row=3, column=1)
i3.config(show='*')

Button(canvas, text='LOGIN', command=login).grid(row=4, column=1)

# End

# --------------------------------------------
#  Options
#     Spawn windows based on selections
# --------------------------------------------


def confirm_clear():
    confirm = messagebox.askyesno(
        "Confirm Clear Table", "Clear all the data from the table. Once cleared, the data cannot be recovered. Do you want to proceed?")
    if not confirm:
        return
    messages = clear_data(context.cursor)
    for message in messages:
        if "error" in message:
            messagebox.showerror("Error", message["error"])
        elif "message" in message:
            messagebox.showinfo("Success", message["message"])
        context.db.commit()


def myOptions():
    root.geometry("250x200")
    canvas = Canvas(root)
    canvas.pack()
    Button(canvas, text='Enter Data', command=DataEntry).pack(pady=5)
    Button(canvas, text='Enter Update Evaluation',
           command=eval_search_update_duplicate).pack(pady=5)
    Button(canvas, text='Enter Query', command=QuerySearch).pack(pady=5)
    Button(canvas, text="Clear Table", command=confirm_clear).pack(pady=5)

# End


mainloop()
