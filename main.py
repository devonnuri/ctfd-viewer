import requests
from bs4 import BeautifulSoup
from typing import List
from markdown import markdown

URL = ''

session = requests.Session()

def login(name: str, password: str) -> None:
    global session

    text = session.get(URL + '/login').text
    soup = BeautifulSoup(text, 'html.parser')
    nonce = soup.find('input', {'name': 'nonce'})['value']
    res = session.post(URL + '/login', data={'name': name, 'password': password, 'nonce': nonce})
    if 'incorrect' in res.text:
        print('[*] Incorrect credentials')
        exit()
    print('[*] Login Successfully')

def challenges() -> List[dict]:
    global session

    challs = session.get(URL + '/chals').json()['game']
    challs = [{k: v for k, v in d.items() if k in ['category', 'name', 'id', 'value']} for d in challs]
    
    solves = session.get(URL + '/solves').json()['solves']
    return [dict(list(d.items()) + [['solved', any(s['chalid'] == d['id'] for s in solves)]]) for d in challs]

def main():
    global URL
    with open('config', 'r') as f:
        URL, name, password = f.readlines()
        URL = URL.strip()
        login(name.strip(), password.strip())
    
    prev_category = ''
    for chall in sorted(challenges(), key=lambda x: x['category']):
        if prev_category != chall['category']:
            print('\n = ' + chall['category'])
            prev_category = chall['category']
        
        solved_emoji = '✅' if chall['solved'] else '☑️'
        print('  {}  | {:3} | {:4}pt | {}'.format(solved_emoji, chall['id'], chall['value'], chall['name']))
    
    prev = None
    while True:
        choice = input('\ncommand > ').strip()
        if choice == 'd':
            if not prev:
                print('No previous chall')
            print('Unavailable')
        else:
            chall = session.get(URL + '/chals/' + choice).json()
            prev = chall

            description = markdown(chall['description'])
            soup = BeautifulSoup(description, 'html.parser')
            for tags in soup(['script', 'style']):
                tags.extract()

            print('\n'+soup.text.strip())

if __name__ == "__main__":
    main()