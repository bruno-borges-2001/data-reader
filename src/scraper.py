from playwright.sync_api import sync_playwright, Page
from datetime import date
from src.utils.date import select_date
from typing import Callable, Any

BROWSER = 'chromium'

URL = r'https://www.entregasfly.com.br/expresso/loginFuncionarioNovo'

def login(page: Page, credentials: dict[str,str]):
  try:
    page.goto(URL)
    page.get_by_placeholder('Digite seu email').first.fill(credentials['email'])
    page.get_by_placeholder('Digite sua senha').first.fill(credentials['password'])
    page.get_by_text('Logar').first.click()
    page.wait_for_load_state('networkidle')
  except:
    raise ValueError('Credenciais inválidas')
  
def get_user_codes(page: Page) -> list[str]:
  page.locator('xpath=//*[@id="page"]/div/a').click()
  page.wait_for_timeout(1000)
  
  page.get_by_text('Profissionais').first.click()
  page.wait_for_timeout(1000)
  
  page.get_by_text('Lista de profissionais').first.click()
  
  page.wait_for_load_state('networkidle')
  
  return page.locator('td:first-child').all_inner_texts()

def get_user_data(page: Page, user: str):
  input_el = page.locator('id=profissionaltxt')
  input_el.fill(f"{user} -")
  
  item = page.locator(f'div:text-matches("^{user} -.*")').first
  item.wait_for(state='visible')
  item.click()
  
  page.get_by_text('Buscar dados', exact=True).click()
  
  try:
    table = page.wait_for_selector('.table-responsive>div>table', timeout=5000)
    if not table:
      raise ValueError('No values found')
    
    table = page.locator('css=.table-responsive>div>table')
    table.wait_for()
    table.scroll_into_view_if_needed()
    
    data = {}
    
    input_value = input_el.input_value()
    [id, name] = input_value.split(' - ')
    
    data['Código'] = id
    data['Nome'] = name
    
    for row in table.locator('tr').all():
      key = row.locator('td').nth(0).inner_text()
      value = row.locator('td').nth(1).inner_text()
      data[key] = value
    
    return data
  except:
    return

def get_users_info(page: Page, users: list[str], dates: list[date], on_event: Callable[[str, Any], None]):
  page.locator('xpath=//*[@id="page"]/div/a').click()
  page.wait_for_timeout(1000)
  
  page.get_by_text('Serviços', exact=True).click()
  page.wait_for_timeout(1000)
  
  page.locator('id=sidebar_servicos').get_by_text('Relatórios', exact=True).first.click()
  page.wait_for_load_state('networkidle')
  
  # SET FILTER DATES
  select_date(page, page.locator('id=data'), dates[0])
  select_date(page, page.locator('id=dataF'), dates[1])
  
  page.get_by_text('Com dados prof.').locator('id=profissional').click()
  
  parent = page.locator('css=.multiselect-native-select').filter(has=page.locator('id=status'))
  parent.click()
  parent.get_by_role('button', name='Concluídos').click()
  
  page.get_by_text('Por profissional').locator('id=clienteCheck').click()
  
  output = []
  
  for user in users:
    result = get_user_data(page, user)
    if result:
      on_event('user-info', result)
      output.append(result)
  
  return output
  
def scrape(credentials: dict[str, str], dates: list[date], on_event: Callable[[str, Any], None]):
  with sync_playwright() as p:
    browser = p[BROWSER].launch()
    page = browser.new_page()
    
    login(page, credentials)
    
    on_event('authed', None)
    
    users = get_user_codes(page)
    
    on_event('user-loaded', users)
    
    data = get_users_info(page, users, dates, on_event)
        
    page.wait_for_timeout(1000)
    browser.close()
    
    return data
      
      