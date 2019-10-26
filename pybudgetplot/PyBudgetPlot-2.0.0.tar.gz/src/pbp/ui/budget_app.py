import tkinter as tk

from tkinter import filedialog

from pbp.core import accountant, plotter
from pbp.core.budget import Budget

FONT = ("Consolas", 14, "bold")


class BudgetApp:

    def __init__(self):
        self.budget = Budget.sample()

        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.title("PyBudgetPlot")

        self.description_var = tk.StringVar(self.root)
        self.amount_var = tk.IntVar(self.root)
        self.frequency_var = tk.StringVar(self.root)

        self._create_menus()
        self._create_header()
        self._create_body()

        self.update_ui_list()

    def _create_menus(self):
        top = tk.Menu(self.root)

        # create File menu
        file_menu = tk.Menu(top, tearoff=0)
        file_menu.add_command(label="Load Budget", command=self.cmd_load_budget)
        file_menu.add_separator()
        file_menu.add_command(label="Save Budget", command=self.cmd_save_budget)
        file_menu.add_command(label="Save Daily Breakdown", command=self.cmd_save_daily)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.root.quit)
        top.add_cascade(label="File", menu=file_menu)

        # bind the menu
        self.root.config(menu=top)

    def _create_header(self):
        header = tk.LabelFrame(self.root, text="  Item details  ")

        desc_frame = tk.LabelFrame(header, text=" Description ")
        tk.Entry(desc_frame, width=20, textvariable=self.description_var).pack(padx=5, pady=5)
        desc_frame.pack(side=tk.LEFT, padx=5, pady=10)

        amount_frame = tk.LabelFrame(header, text=" Amount ")
        tk.Entry(amount_frame, width=10, textvariable=self.amount_var).pack(padx=5, pady=5)
        amount_frame.pack(side=tk.LEFT, padx=5, pady=10)

        freq_frame = tk.LabelFrame(header, text=" Frequency ")
        tk.Entry(freq_frame, width=40, textvariable=self.frequency_var).pack(padx=5, pady=5)
        freq_frame.pack(side=tk.LEFT, padx=5, pady=10)

        buttons_frame = tk.LabelFrame(header, text=" Actions ")
        tk.Button(buttons_frame, text="Add", command=self.cmd_add_item).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="Plot", command=self.cmd_plot_budget).pack(side=tk.RIGHT, padx=5)
        buttons_frame.pack(side=tk.LEFT, padx=5, pady=10)

        header.pack(side=tk.TOP, fill=tk.X, expand=True, anchor=tk.N, padx=5, pady=5)

    def _create_body(self):
        items_frame = tk.LabelFrame(self.root, text=" Budget items ")

        scroll_bar = tk.Scrollbar(items_frame)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        self.items_list_box = tk.Listbox(items_frame, height=15, width=80, yscrollcommand=scroll_bar.set,
                                         font=FONT)
        self.items_list_box.bind("<Double-1>", self.cmd_edit_item)

        scroll_bar.config(command=self.items_list_box.yview)
        self.items_list_box.pack(side=tk.LEFT, fill=tk.BOTH)

        items_frame.pack(side=tk.TOP, fill=tk.BOTH)

    def update_ui_list(self):
        self.items_list_box.delete(0, tk.END)
        for item in self.budget:
            self.items_list_box.insert(tk.END, str(item))

    def cmd_load_budget(self):
        file = filedialog.askopenfilename(title="Select budget file", filetypes=[("Budget files", ".yaml")])
        if file:
            self.budget = Budget.load(file)
            self.update_ui_list()

    def cmd_save_budget(self):
        file = filedialog.asksaveasfilename(title="Select budget file", filetypes=[("Budget files", ".yaml")])
        self.budget.save(file)

    def cmd_save_daily(self):
        file = filedialog.asksaveasfilename(title="Select daily breakdown file", filetypes=[("CSV file", ".csv")])
        data = accountant.calculate_data(self.budget)
        data.to_csv(file)

    def cmd_plot_budget(self):
        data = accountant.calculate_data(self.budget)
        plotter.plot_data(data)

    def cmd_add_item(self):
        desc = self.description_var.get()
        self.description_var.set("")

        amount = self.amount_var.get()
        self.amount_var.set(0)

        freq = self.frequency_var.get()
        self.frequency_var.set("")

        self.budget.add_item(desc, amount, freq)
        self.update_ui_list()

    def cmd_edit_item(self, ev=None):
        item_idx = self.items_list_box.curselection()[0]
        current_item = self.budget[item_idx]
        self.description_var.set(current_item.description)
        self.amount_var.set(current_item.amount)
        self.frequency_var.set(current_item.frequency)

        del self.budget[item_idx]
        self.update_ui_list()


def main():
    app = BudgetApp()
    app.root.mainloop()


if __name__ == '__main__':
    main()
