"""Punto de entrada de la aplicación MD <-> LaTeX."""

import tkinter as tk
from view.main_window import MainWindow
from controller.app_controller import AppController


def main():
    root = tk.Tk()
    view = MainWindow(root)
    AppController(view)  # conecta vista y modelo
    root.mainloop()


if __name__ == "__main__":
    main()
