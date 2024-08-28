from playwright.sync_api import Page, Locator
from datetime import date

MONTH_MAP = [
  '',
  'Janeiro',
  'Fevereiro',
  'Março',
  'Abril',
  'Maio',
  'Junho',
  'Julho',
  'Agosto',
  'Setembro',
  'Outubro',
  'Novembro',
  'Dezembro'
]

def select_date(page: Page, trigger: Locator, date: date):
  trigger.click()
  
  dialog = page.locator('id=ui-datepicker-div')
  
  before_btn = dialog.get_by_title('<Anterior')
  after_btn = dialog.get_by_title('Próximo>')
  
  year_el = dialog.locator('css=.ui-datepicker-year')
  month_el = dialog.locator('css=.ui-datepicker-month')
  
  while int(year_el.inner_text()) != date.year:
    if int(year_el.inner_text()) < date.year:
      after_btn.click()
    else:
      before_btn.click()
      
  while month_el.inner_text() != MONTH_MAP[date.month]:
    if MONTH_MAP.index(month_el.inner_text()) < date.month:
      after_btn.click()
    else:
      before_btn.click()
  
  dialog.locator(f'a:has-text("{date.day}")').click()
