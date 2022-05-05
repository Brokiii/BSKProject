import threading
import tkinter as tk
from Client import write2, receive


def gui(client):
    root = tk.Tk()
    root.title("Chatbox 1.0")

    canvas = tk.Canvas(root, width=700, height=450)
    canvas.grid(columnspan=4, rowspan =16)

    #chatbox
    label = tk.Label(root, text="Chatbox")
    label.grid(columnspan = 2, column = 2, row = 0)

    chatbox = tk.Text(root, height=20, width=30, padx=15, pady=15)
    chatbox.grid(columnspan=2, column=2, row=1, rowspan=14)

    #nick użytkownika
    label4 = tk.Label(root, text="Enter your nickname")
    label4.grid(columnspan=2, column=0, row=0)
    nickname = tk.Entry(root, width=30)
    nickname.grid(columnspan=2, column=0, row=1)
    nickname.insert(tk.END, "Default nickname")

    # radiobuttony
    label3 = tk.Label(root, text="Choose encryption mode")
    label3.grid(columnspan=2, column=0, row=2)

    var1 = tk.StringVar()
    radio1 = tk.Radiobutton(root, text="CBC", variable=var1, value="CBC")
    radio2 = tk.Radiobutton(root, text="ECB", variable=var1, value="ECB")
    radio1.grid(column=0, row=3)
    radio2.grid(column=1, row=3)
    radio1.invoke()


    #pole na wiadomosc
    label2 = tk.Label(root, text="Enter your message")
    label2.grid(columnspan=2, column=0, row=4)
    message = tk.Entry(root, width=55)
    message.grid(columnspan=2, column=0, row=5)

    #przycisk
    button_text = tk.StringVar()
    button_text.set("Send")
    send_button = tk.Button(root, textvariable=button_text, bg="red", fg="white", height=2, width=15,
                                    command=lambda: write2(client, message.get(), var1.get(), nickname.get(), chatbox))
    send_button.grid(columnspan=2, column=0, row=6)

    receive_thread = threading.Thread(target=receive, args=(client, chatbox))
    receive_thread.start()

    root.mainloop()