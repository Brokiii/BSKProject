import threading
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk
import time

from Client import write, receive, send_file


def create_chatbox(root):
    label = tk.Label(root, text="Chatbox")
    label.grid(columnspan=2, column=2, row=0)

    chatbox = tk.Text(root, height=20, width=30, padx=15, pady=15)
    chatbox.grid(columnspan=2, column=2, row=1, rowspan=14)

    return chatbox


def create_nickname_label(root):
    label = tk.Label(root, text="Enter your nickname")
    label.grid(columnspan=2, column=0, row=0)
    nickname = tk.Entry(root, width=30)
    nickname.grid(columnspan=2, column=0, row=1)
    nickname.insert(tk.END, "Default nickname")

    return nickname


def create_radio_buttons(root):
    label = tk.Label(root, text="Choose encryption mode")
    label.grid(columnspan=2, column=0, row=2)

    var1 = tk.StringVar()
    radio1 = tk.Radiobutton(root, text="CBC", variable=var1, value="CBC")
    radio2 = tk.Radiobutton(root, text="ECB", variable=var1, value="ECB")
    radio1.grid(column=0, row=3)
    radio2.grid(column=1, row=3)
    radio1.invoke()

    return var1


def create_message_label(root):
    label = tk.Label(root, text="Enter your message")
    label.grid(columnspan=2, column=0, row=4)
    message = tk.Entry(root, width=55)
    message.grid(columnspan=2, column=0, row=5)

    return message


def select_file(client, storage, progress_bar, nickname, mode, chatbox):
    filetypes = (
        ('text files', '*.txt'),
        ('photo files', '*.png'),
        ('pdf files', '*.pdf'),
        ('video files', '*.avi')
    )

    filename = fd.askopenfilename(
        title='Choose a file',
        filetypes=filetypes
    )

    send_file_thread = threading.Thread(target=send_file,
                                        args=(client, filename, storage, progress_bar, nickname, mode, chatbox))
    send_file_thread.start()


def gui(client, storage):
    root = tk.Tk()
    root.title("Chatbox 1.0")

    canvas = tk.Canvas(root, width=700, height=450)
    canvas.grid(columnspan=4, rowspan=16)

    chatbox = create_chatbox(root)
    nickname = create_nickname_label(root)
    radio_mode = create_radio_buttons(root)
    message = create_message_label(root)

    # Send button
    button_text = tk.StringVar()
    button_text.set("Send")
    send_button = tk.Button(root, textvariable=button_text, bg="red", fg="white", height=2, width=15,
                            command=lambda: write(client, message.get(), radio_mode.get(), nickname.get(), chatbox,
                                                  storage))
    send_button.grid(columnspan=2, column=0, row=6)

    receive_thread = threading.Thread(target=receive, args=(client, chatbox, storage))
    receive_thread.start()

    file_button = tk.Button(root, text="Choose a file and send it PYCZ", bg="red", fg="white", height=2, width=30,
                            command=lambda: select_file(client, storage, progress_bar, nickname.get(), radio_mode.get(),
                                                        chatbox))
    file_button.grid(columnspan=2, column=0, row=10)

    progress_bar = ttk.Progressbar(root, orient='horizontal', mode='determinate', length=350)
    progress_bar.grid(columnspan=2, column=0, row=11)
    progress_bar_label = tk.Label(root, text="Uploading file progress bar")
    progress_bar_label.grid(columnspan=2, column=0, row=12)

    root.mainloop()
