from tkcalendar import Calendar
import tkinter as tk
import tkinter.ttk as ttk

from datetime import date

class CalendarPicker(tk.Toplevel):
    def __init__(self, parent, value):
        super().__init__(parent)

        self.cal = Calendar(
          self,
          font="Arial 14", 
          selectmode='day',
        )
        
        self.cal.selection_set(value)
        
        self.cal.pack(fill="both", expand=True)
        tk.Button(self, text="ok", command=self.destroy).pack()

    def show(self) -> date:
        self.deiconify()
        self.wm_protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window(self)
        return self.cal.selection_get() or date.today()