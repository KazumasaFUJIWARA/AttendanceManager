import tkinter as tk

def hide_button_a():
    button_a.grid_remove()

# Tkinterウィンドウの作成
window = tk.Tk()
window.title("Hide Button Example")

# ボタンの作成
button_a = tk.Button(window, text="Button A", command=hide_button_a)
button_a.grid(row=0, column=0, padx=10, pady=10)

# イベントループの開始
window.mainloop()

