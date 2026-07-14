# PHREEQC_database helper
import tkinter as tk
import re
import pandas as pd
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox
from tkinter.messagebox import showinfo
from .build_database import clean_tables as ct
from .build_database import utils as ut
from . import database_editor as de
import importlib.resources as pkg_resources

def load_tables():
    """
    Load and compile the Solution Species, Solution Master Species, and
    Phases tables from the bundled PHREEQC databases.

    Returns
    -------
    tuple[pandas.DataFrame, pandas.DataFrame, pandas.DataFrame]
        The solution_species, sms, and phase tables.
    """
    database_list = pkg_resources.files('pqcdbchk.build_database.databases')
    database_list = ut.phreeqc_database_list(database_list)

    # create and normalize Solution Species table
    solution_species = ct.compile_solution_species_table(database_list)
    solution_species.iloc[:, 0] = solution_species.iloc[:, 0].str.replace(' ', '')
    ones = re.compile(r'\b1(?!\d)')
    solution_species.iloc[:, 0] = solution_species.iloc[:, 0].str.replace(ones, '', regex=True)

    # create Solution Master Species table
    sms = ct.compile_master_solution_table(database_list, analysis=True)

    # create phases table
    phase = ct.compile_phase_table(database_list)

    return solution_species, sms, phase

# Class for searching values
class DatabaseSearcher:
    def __init__(self, ss_df, sms_df, phase_df):
        self.ss = ss_df
        self.sms = sms_df
        self.phase = phase_df

    # function to find the values
    def search(self, category, query, exact=False):
        if not query: return pd.DataFrame()
        
        if category == "equation":
            df, col = self.ss, 'equation'
            query = query.replace(" ", "")
        elif category == "species":
            df, col = self.sms, 'species'
        elif category == "phase":
            df, col = self.phase, 'phase_name'
        else: return pd.DataFrame()

        if exact:
            return df[df[col].astype(str) == query]
        else:
            return df[df[col].astype(str).str.contains(query, case=False, na=False)]

# Sort the results numerically and alphabetically
def treeview_sort_column(tree, col, reverse):
    l = [(tree.set(k, col), k) for k in tree.get_children('')]
    try: 
        l.sort(key=lambda t: float(t[0]), reverse=reverse)
    except ValueError: 
        l.sort(reverse=reverse)
    for index, (val, k) in enumerate(l):
        tree.move(k, '', index)
    tree.heading(col, command=lambda: treeview_sort_column(tree, col, not reverse))

# function to exit the program
def quit_program():
    root.destroy()

# Class for searching values in Find Values page
class SearchPageBase(tk.Frame):
    def __init__(self, master, title, category):
        super().__init__(master)
        self.category = category
        self.searcher = master.searcher

        tk.Label(self, text=title, font=("DejaVu Sans Mono", 20, "bold")).pack(pady=10)
        
        search_frame = tk.Frame(self)
        search_frame.pack(pady=5)
        self.entry = tk.Entry(search_frame, width=40)
        self.entry.pack(side="left", padx=5)
        
        self.exact_var = tk.BooleanVar()
        tk.Checkbutton(search_frame, text="Exact Match", variable=self.exact_var).pack(side="left")

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Search", command=self.perform_search, width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Export Selected to Excel", command=self.export_to_excel, width=22).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Back", command=lambda: master.show_frame(FindValuesPage), width=10).pack(side="left", padx=5)

        self.tree_frame = tk.Frame(self)
        self.tree_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        yscroll = ttk.Scrollbar(self.tree_frame, orient="vertical")
        yscroll.pack(side='right', fill='y')

        self.tree = ttk.Treeview(self.tree_frame, selectmode="extended", yscrollcommand=yscroll.set)
        self.tree.pack(side="left", fill="both", expand=True)

        yscroll.config(command=self.tree.yview)

    # function to perform the actual search
    def perform_search(self):
        """
        Perform search based on user query and display results in treeview.

        Retrieves the search query from the entry field, executes the search
        using the DatabaseSearcher with the specified category and exact match
        option, and populates the treeview with the results. If no results are
        found, displays an informational message box.

        The treeview columns are dynamically configured based on the result
        DataFrame, with sortable headings. Each row is inserted into the
        treeview for display.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Attributes
        ----------
        result_df : pandas.DataFrame
            Stores the resulting DataFrame from the search.
        tree : ttk.Treeview
            The treeview widget updated with search results.

        Notes
        -----
        This method modifies the GUI state by updating the treeview and
        storing the result DataFrame for potential export.
        """
        query = self.entry.get().strip()
        self.result_df = self.searcher.search(self.category, query, self.exact_var.get())
        
        self.tree.delete(*self.tree.get_children())
        if self.result_df.empty:
            messagebox.showinfo("No Results", "No matching data found.")
            return

        self.tree["columns"] = list(self.result_df.columns)
        self.tree["show"] = "headings"
        for c in self.result_df.columns:
            self.tree.heading(c, text=c, command=lambda _c=c: treeview_sort_column(self.tree, _c, False))
            self.tree.column(c, anchor="center", width=100)
        for _, row in self.result_df.iterrows():
            self.tree.insert("", "end", values=list(row))
            
    # function for exporting the result into an excel file
    def export_to_excel(self):
        selected_items = self.tree.selection()
        if not selected_items:
            if hasattr(self, 'result_df') and not self.result_df.empty:
                if not messagebox.askyesno("Export", "No items selected. Export all results?"): return
                df_to_export = self.result_df
            else:
                messagebox.showwarning("No data", "Search first and select items.")
                return
        else:
            data = [self.tree.item(item)['values'] for item in selected_items]
            df_to_export = pd.DataFrame(data, columns=self.result_df.columns)

        file_path = fd.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            df_to_export.to_excel(file_path, index=False)
            messagebox.showinfo("Exported", f"Data saved to:\n{file_path}")

# Pages to find equation, species, and phases
class FindEquationsPage(SearchPageBase):
    def __init__(self, master): super().__init__(master, "Find Species Equation", "equation")

class FindSpeciesPage(SearchPageBase):
    def __init__(self, master): super().__init__(master, "Find Solution Master Species", "species")

class FindPhasesPage(SearchPageBase):
    def __init__(self, master): super().__init__(master, "Find Phases", "phase")

# main class
class Main(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text="PHREEQC Menu", font=("DejaVu Sans Mono", 24, "bold")).pack(pady=20)
        tk.Button(self, text="Edit Database", width=25, bg="#4F8FC0", command=lambda: master.show_frame(EditDatabasePage)).pack(pady=10)
        tk.Button(self, text="Find Values", width=25, bg="#53DEDC", command=lambda: master.show_frame(FindValuesPage)).pack(pady=10)

# page for finding different values
class FindValuesPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text="Find Values", font=("DejaVu Sans Mono", 20, "bold")).pack(pady=20)
        for text, page in [("Find Equation", FindEquationsPage), ("Find Species", FindSpeciesPage), ("Find Phase", FindPhasesPage)]:
            tk.Button(self, text=text, width=20, command=lambda p=page: master.show_frame(p)).pack(pady=5)
        tk.Button(self, text="Back", command=lambda: master.show_frame(Main)).pack(pady=20)

# class that enables scrolling
class ScrollableFrame(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.canvas = tk.Canvas(self, highlightthickness=0, width=800, height=500)
        self.vscrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vscrollbar.grid(row=0, column=1, sticky="ns")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.inner = tk.Frame(self.canvas)
        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.window_id, width=e.width))
        self.canvas.configure(yscrollcommand=self.vscrollbar.set)

# page for editing values in existing databases
class EditDatabasePage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
    
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        scroll = ScrollableFrame(self)
        scroll.grid(row=0, column=0, sticky="nsew")
        inner = scroll.inner

        tk.Label(
            inner,
            text="Edit Existing Database",
            font=("DejaVu Sans Mono", 20, "bold"),
            anchor="center"
        ).pack(pady=10, fill="x")

        tk.Label(inner, text="Select Database").pack()
        self.entry_db = tk.Entry(inner, width=50)
        self.entry_db.pack()
        tk.Button(
            inner,
            text="Browse",
            command=lambda: self.browse_file(self.entry_db)
        ).pack()

        tk.Label(inner, text="New Database").pack()
        self.entry_new = tk.Entry(inner, width=50)
        self.entry_new.pack()
        tk.Button(
            inner,
            text="Browse",
            command=lambda: self.browse_save(self.entry_new)
        ).pack()

        tk.Label(inner, text="Solution Species").pack(pady=(15, 0))

        tk.Label(inner, text="Equation").pack()
        self.entry_eq = tk.Entry(inner, width=50)
        self.entry_eq.pack()

        tk.Label(inner, text="log K").pack()
        self.entry_logk = tk.Entry(inner, width=50)
        self.entry_logk.pack()

        tk.Label(inner, text="delta H (kcal/mol)").pack()
        self.entry_dh = tk.Entry(inner, width=50)
        self.entry_dh.pack()

        tk.Button(
            inner,
            text="Add/Edit Species",
            command=self.add_species,
            bg="#DFF0D8"
        ).pack(pady=5)

        tk.Label(inner, text="Solution Master Species").pack(pady=(20, 0))

        tk.Label(inner, text="Element").pack()
        self.entry_sms_element = tk.Entry(inner, width=50)
        self.entry_sms_element.pack()

        tk.Label(inner, text="Master species").pack()
        self.entry_sms_species = tk.Entry(inner, width=50)
        self.entry_sms_species.pack()

        tk.Label(inner, text="Alk").pack()
        self.entry_sms_alk = tk.Entry(inner, width=50)
        self.entry_sms_alk.pack()

        tk.Label(inner, text="Element gfw").pack()
        self.entry_sms_gfw = tk.Entry(inner, width=50)
        self.entry_sms_gfw.pack()

        tk.Button(
            inner,
            text="Add/Edit Master Species",
            command=self.add_master_species,
            bg="#DFF0D8"
        ).pack(pady=5)

        tk.Label(inner, text="Phase").pack(pady=(20, 0))

        tk.Label(inner, text="Phase name").pack()
        self.entry_phase_name = tk.Entry(inner, width=50)
        self.entry_phase_name.pack()

        tk.Label(inner, text="Equation").pack()
        self.entry_phase_eq = tk.Entry(inner, width=50)
        self.entry_phase_eq.pack()

        tk.Label(inner, text="log K").pack()
        self.entry_phase_logk = tk.Entry(inner, width=50)
        self.entry_phase_logk.pack()

        tk.Label(inner, text="delta H (kcal/mol)").pack()
        self.entry_phase_dh = tk.Entry(inner, width=50)
        self.entry_phase_dh.pack()

        tk.Button(
            inner,
            text="Add/Edit Phase",
            command=self.add_phase,
            bg="#DFF0D8"
        ).pack(pady=5)

        tk.Button(
            inner,
            text="Back",
            command=lambda: master.show_frame(Main),
            bg="#F2DEDE"
        ).pack(pady=10)

    # find database file
    def browse_file(self, entry):
        filename = fd.askopenfilename(
            filetypes=[("Database files", "*.dat"), ("All files", "*.*")]
        )
        if filename:
            entry.delete(0, tk.END)
            entry.insert(0, filename)

    # save new database file
    def browse_save(self, entry):
        filename = fd.asksaveasfilename(defaultextension=".dat")
        if filename:
            entry.delete(0, tk.END)
            entry.insert(0, filename)

    # add user input values to species
    def add_species(self):
        eq = de.normalize_equation(self.entry_eq.get().strip())
        logk = self.entry_logk.get().strip()
        dh = self.entry_dh.get().strip()
        db_path = self.entry_db.get().strip()
        new_path = self.entry_new.get().strip()

        if not eq or not logk or not dh or not db_path or not new_path:
            messagebox.showwarning("Error", "Check the file location again.")
            return

        lines = de.load_database(db_path)
        index = de.find_species(lines, eq)

        new_entry = (
        f"    {eq}\n"
        f"    log_k {logk}\n"
        f"    delta_h {dh} kcal/mol\n\n"
        )

        new_lines = new_entry.splitlines(keepends=True)
        for j, nl in enumerate(new_lines):
            if not nl.endswith('\n'):
                new_lines[j] = nl + '\n'

        if index != -1:
            choice = messagebox.askyesno(
                "Duplicate found",
                f"Species '{eq}' already exists.\nChange?"
            )
            if choice:
                end = index + 1
                while end < len(lines) and lines[end].strip():
                    end += 1
                del lines[index:end]
                lines.insert(index, new_entry)
                messagebox.showinfo("Edited", f"{eq} is now edited.")
            else:
                return
        else:
            de.insert_into_section(lines, "SOLUTION_SPECIES", new_entry)
            messagebox.showinfo("Added", f"{eq} is now added.")

        de.save_database(lines, new_path)

    # add user input values to solution master species
    def add_master_species(self):
        element = self.entry_sms_element.get().strip()
        species = self.entry_sms_species.get().strip()
        alk = self.entry_sms_alk.get().strip()
        gfw = self.entry_sms_gfw.get().strip()
        db_path = self.entry_db.get().strip()
        new_path = self.entry_new.get().strip()

        if not element or not species or not alk or not gfw or not db_path or not new_path:
            messagebox.showwarning("Error", "Check the file location again.")
            return

        lines = de.load_database(db_path)
        index = de.find_master_species_line(lines, element)

        new_line = f"{element}    {species}    {alk}    {gfw}\n"

        if index != -1:
            choice = messagebox.askyesno(
                "Duplicate found",
                f"Element '{element}' already exists in SOLUTION_MASTER_SPECIES.\nChange?"
            )
            if choice:
                lines[index] = new_line
                messagebox.showinfo("Edited", f"{element} master species is now edited.")
            else:
                return
        else:
            de.insert_into_section(lines, "SOLUTION_MASTER_SPECIES", new_line)
            messagebox.showinfo("Added", f"{element} master species is now added.")

        de.save_database(lines, new_path)

    # add user input to phase block
    def add_phase(self):
        name = self.entry_phase_name.get().strip()
        eq = de.normalize_equation(self.entry_phase_eq.get().strip())
        logk = self.entry_phase_logk.get().strip()
        dh = self.entry_phase_dh.get().strip()
        db_path = self.entry_db.get().strip()
        new_path = self.entry_new.get().strip()

        if not name or not eq or not logk or not dh or not db_path or not new_path:
            messagebox.showwarning("Error", "Check the file location again.")
            return

        lines = de.load_database(db_path)
        index = de.find_phase_line(lines, name)

        new_entry = (
        f"{name}\n"
        f"    {eq}\n"
        f"    log_k {logk}\n"
        f"    delta_h {dh} kcal/mol\n\n"

        )

        if index != -1:
            choice = messagebox.askyesno(
                "Duplicate found",
                f"Phase '{name}' already exists.\nChange?"
            )
            if choice:
                end = index + 1
                while end < len(lines) and lines[end].strip():
                    end += 1
                new_lines = new_entry.splitlines(keepends=True)
                lines[index:end] = new_lines
                messagebox.showinfo("Edited", f"{name} phase is now edited.")
            else:
                return
        else:
            de.insert_into_section(lines, "PHASES", new_entry)
            messagebox.showinfo("Added", f"{name} phase is now added.")

        de.save_database(lines, new_path)



# main app
class App(tk.Tk):
    def __init__(self, solution_species=None, sms=None, phase=None):
        super().__init__()
        self.title("PHREEQC Database Helper")
        self.geometry("1000x750")

        # enables scrolling even when the window size is small
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        if solution_species is None or sms is None or phase is None:
            solution_species, sms, phase = load_tables()

        self.searcher = DatabaseSearcher(solution_species, sms, phase)
        self.frames = {}

        for F in (Main, EditDatabasePage, FindValuesPage, FindEquationsPage, FindSpeciesPage, FindPhasesPage):
            frame = F(self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(Main)
        
        # Exit button
        exit_btn = ttk.Button(self, text='Exit Program', command=quit_program)
        exit_btn.grid(row=1, column=0, pady=10)

    def show_frame(self, page_class):
        self.frames[page_class].tkraise()

if __name__ == "__main__":
    root = App()
    root.mainloop()
