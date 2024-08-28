import tkinter as tk
import tkinter.ttk as ttk

from tkinter import messagebox as mb, filedialog as fd

from src.ui.calendar_dialog import CalendarPicker
from src.scraper import scrape
from src.export import export_data
from src.utils.download import get_download_folder

from datetime import date, timedelta

class GUI:
  def __init__(self):
    self.root = tk.Tk()
    
    self.state = {}
    self.components = {}
    
    s = ttk.Style(self.root)
    s.theme_use('clam') 
    
    self.initial_value: date = date.today() - timedelta(days=7)
    self.end_value: date = date.today()
    
    self.header = ttk.Frame(self.root, padding=(10, 10))
    
    self.credentials = ttk.Frame(self.header, padding=(0, 5))
    
    ttk.Label(self.credentials, text="Email: ", anchor="w").grid(row=0, column=0)
    ttk.Label(self.credentials, text="Senha: ", anchor="w").grid(row=1, column=0)
    
    self.email_input = ttk.Entry(self.credentials)
    self.password_input = ttk.Entry(self.credentials, show="*")
    
    self.email_input.grid(row=0, column=1)
    self.password_input.grid(row=1, column=1)
    
    self.period = ttk.Frame(self.header)
    
    self.button_start = ttk.Button(self.period, text="Data Inicial", command=self.get_initial_date)
    self.button_start.grid(row=0, sticky="ew")
    
    self.period.grid_columnconfigure(0, weight=1)
    self.period.grid_columnconfigure(1, weight=1)
    
    self.start_label = ttk.Label(self.period, text=self.initial_value.strftime('%d/%m/%Y'))
    self.start_label.grid(row=0, column=1)
    
    self.end_label = ttk.Label(self.period, text=self.end_value.strftime('%d/%m/%Y'))
    self.end_label.grid(row=1, column=1)
    
    self.button_end = ttk.Button(self.period, text="Data Final", command=self.get_end_date)
    self.button_end.grid(row=1, sticky="ew")
    
    self.credentials.grid(row=0, column=0)
    self.period.grid(row=1, column=0, sticky='ew')
    
    self.header.columnconfigure(1, weight=1, minsize=20)
    
    self.run_button= ttk.Button(self.header, text="Executar", command=self.run)
    self.run_button.grid(column=2, row=0, rowspan=2, sticky='nsw')
    
    self.header.pack(fill='x')
    
    tree_frame = ttk.Frame(self.root)
    
    columns = ('Código', 'Nome', 'Total de serviços', 'Valor total dos serviços', 'Valor total do profissional', 'Valor ganho')
    
    self.tree = ttk.Treeview(
      tree_frame,
      show='headings', 
      columns=columns
    )
    
    for c in columns:
      self.tree.heading(c, text=c)
    
    self.tree.pack(fill='both')
    tree_frame.pack(fill='both')
    
    self.root.mainloop()    
    
  def get_initial_date(self):
    popup = CalendarPicker(self.root, self.initial_value)
    result = popup.show()
    if result:
      self.initial_value = result
      self.start_label.config(text=result.strftime('%d/%m/%Y'))
    
  def get_end_date(self):
    popup = CalendarPicker(self.root, self.end_value)
    result = popup.show()
    if result:
      self.end_value = result
      self.end_label.config(text=result.strftime('%d/%m/%Y'))
  
  def insert_value_on_tree(self, data):
    values = (
      data['Código'],
      data['Nome'], 
      data['Total de serviços'], 
      data['Valor total dos serviços'], 
      data['Valor total do profissional'], 
      data['Valor ganho']
    )
    self.tree.item(data['Código'], text=data['Código'], values=values)
    self.tree.update()
    
  def handle_event(self, event, payload):
    match event:
      case 'authed':
        self.run_button.config(text='Recuperando Usuários')
        self.run_button.update()
        return
      case 'user-loaded':
        for cod in payload:
          default_value = (cod, '','','','','')
          self.tree.insert('', 'end', cod, text=cod, values=default_value)
          self.tree.update()
        self.run_button.config(text='Carregando Dados')
        self.run_button.update()
        return
      case 'user-info':
        self.insert_value_on_tree(payload)
        self.run_button.config(text='Dados Carregados')
        self.run_button.update()
        return
  
  def run(self):
    date_start = self.initial_value
    date_end = self.end_value
    
    email = self.email_input.get()
    password = self.password_input.get()
    
    if not email or not password:
      mb.showerror("Erro", "Email e senha são obrigatórios")
      return
    
    if not date_start or not date_end:
      mb.showerror("Erro", "Data inicial e data final são obrigatórios")
      return
    
    if date_start > date_end:
      mb.showerror("Erro", "Data inicial não pode ser maior que a data final")
      return
    
    credentials = {
      'email': email,
      'password': password
    }
    
    for i in self.tree.get_children():
      self.tree.delete(i)
    self.tree.update()
    
    try:
      self.run_button.config(state='disabled', text='Autenticando')
      self.run_button.update()
      
      scraped_data = scrape(credentials, [date_start, date_end], self.handle_event)
      
      destination = fd.askdirectory(initialdir=get_download_folder())
      
      export_data(destination, scraped_data)
      
      mb.showinfo("Sucesso", "Arquivo exportado com sucesso")
    except ValueError as error:
      mb.showerror("Erro", str(error.args[0]))
    except Exception as error:
      mb.showerror("Erro", str(error))
    finally:
      self.run_button.config(state='normal', text='Executar')
      self.run_button.update()