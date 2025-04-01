import tkinter as tk

def hide_button_a():
    button_a.grid_remove()

# Tkinter$B%&%#%s%I%&$N:n@.(B
window = tk.Tk()
window.title("Hide Button Example")

# $B%\%?%s$N:n@.(B
button_a = tk.Button(window, text="Button A", command=hide_button_a)
button_a.grid(row=0, column=0, padx=10, pady=10)

# $B%$%Y%s%H%k!<%W$N3+;O(B
window.mainloop()

