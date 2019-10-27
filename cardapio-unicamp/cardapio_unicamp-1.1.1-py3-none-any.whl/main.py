#!/usr/bin/env python3

import argparse
import sys
import re
import datetime as dt

from bs4 import BeautifulSoup
import requests

base_url = "https://www.prefeitura.unicamp.br/apps/site/cardapio.php"


def is_valid_date(date):
    date_re = re.compile(r'^20\d\d-(0?[1-9]|1(0|1|2))-(0?[1-9]|[12]\d|3(0|1))$')

    if date and date_re.search(date):
        return True
    else:
        return False


def get_page_content(date):
    date_url = ""

    if date:
        if is_valid_date(date):
            date_url = "?d=" + date
        else:
            print("Data fornecida inválida")
            sys.exit(1)

    try:
        response = requests.get(base_url+date_url)
    except Exception:
        print("Falha ao conectar à página de cardápio da unicamp")

    if response.status_code == requests.codes.ok:
        return response.text
    else:
        print("Erro ao conectar à página de cardápio da unicamp")
        sys.exit(1)


def get_menu(date):
    content = get_page_content(date)

    if date is None:
        date = get_next_day()

    lunch = {'base': [], 'principal': [], 'salada': [], 'sobremesa': [],
             'suco': [], 'obs': []}
    lunch_veg = {'base': [], 'principal': [], 'salada': [], 'sobremesa': [],
                 'suco': [], 'obs': []}
    dinner = {'base': [], 'principal': [], 'salada': [], 'sobremesa': [],
              'suco': [], 'obs': []}
    dinner_veg = {'base': [], 'principal': [], 'salada': [], 'sobremesa': [],
                  'suco': [], 'obs': []}
    meals_dict = {'cafe': '', 'almoco': lunch, 'almoco_veg': lunch_veg,
                  'jantar': dinner, 'jantar_veg': dinner_veg, 'date': date}

    res = {}
    res['principal'] = re.compile(r'PRATO PRINCIPAL:')
    res['salada'] = re.compile(r'SALADA:')
    res['sobremesa'] = re.compile(r'SOBREMESA:')
    res['suco'] = re.compile(r'SUCO:')
    res['obs'] = re.compile(r'Observações:')

    meals_names = ['cafe', 'almoco', 'almoco_veg', 'jantar', 'jantar_veg']

    # parse html and find meals tags
    soup = BeautifulSoup(content, 'html.parser')
    meals_tags = soup.find_all(class_='fundo_cardapio')
    if not meals_tags:
        print("Cardápio não encontrado para esse dia")
        sys.exit(0)

    meals_dict['cafe'] = meals_tags[0].text.strip().capitalize()

    # assemble meals_dict
    for i, meal in enumerate(meals_tags):
        meal_name = meals_names[i]
        dishes = [d.text for d in meal.find_all('td')]
        last_dish = 'base'
        for dish in dishes:
            has_label = False
            for cur_dish in ['principal', 'salada', 'sobremesa', 'suco',
                             'obs']:
                if res[cur_dish].search(dish):
                    dish = res[cur_dish].sub('', dish)
                    dish = dish.strip().capitalize()
                    if dish:
                        meals_dict[meal_name][cur_dish].append(dish)
                    last_dish = cur_dish
                    has_label = True
            if not has_label:
                dish = dish.strip().capitalize()
                if dish:
                    meals_dict[meal_name][last_dish].append(dish)

    # separate obs phrases and format them correctly
    for meal in meals_names[1:]:
        meals_dict[meal]['obs'] = [s.strip('\r\n ').capitalize() for s in
                                   meals_dict[meal]['obs'][0].split('.')]

        meals_dict[meal]['obs'][:-1] = [s+'.' for s in
                                        meals_dict[meal]['obs'][:-1]]

    return meals_dict


def print_dish(meals_dict, meal, dish, args):
    if args.sem_cabecalho:
        if print_dish.has_been_called:
            print()
        print_dish.has_been_called = True
    else:
        print()

    if not args.sem_cabecalho:
        if dish == 'principal':
            print("Prato Principal:")
        if dish == 'salada':
            print("Salada:")
        if dish == 'sobremesa':
            print("Sobremesa:")
        if dish == 'suco':
            print("Suco:")
        if dish == 'obs':
            print("Observações:")

    if meal == 'cafe':
        print(meals_dict['cafe'])
    else:
        if args.primeiro:
            print(meals_dict[meal][dish][0])
        else:
            for line in meals_dict[meal][dish]:
                print(line)


def print_meal(meals_dict, meal, args):
    if print_meal.has_been_called:
        print()
    print_meal.has_been_called = True

    if not args.sem_cabecalho:
        print("### ", end='')
        if meal == 'almoco':
            print("ALMOÇO ", end='')
        elif meal == 'jantar':
            print("JANTAR ", end='')
        elif meal == 'almoco_veg':
            print("ALMOÇO VEGETARIANO ", end='')
        elif meal == 'jantar_veg':
            print("JANTAR VEGETARIANO ", end='')
        elif meal == 'cafe':
            print("CAFÉ DA MANHÃ ", end='')

        print("DIA {} {}ª FEIRA ###".format(meals_dict['date'],
              dt.datetime.strptime(meals_dict['date'],
                                   "%Y-%m-%d").weekday()+2))

    if meal == 'cafe':
        print_dish(meals_dict, meal, None, args)
        return
    if args.base:
        print_dish(meals_dict, meal, 'base', args)
    if args.principal:
        print_dish(meals_dict, meal, 'principal', args)
    if args.salada:
        print_dish(meals_dict, meal, 'salada', args)
    if args.sobremesa:
        print_dish(meals_dict, meal, 'sobremesa', args)
    if args.suco:
        print_dish(meals_dict, meal, 'suco', args)
    if args.obs:
        print_dish(meals_dict, meal, 'obs', args)


def get_next_day(next_weekday=None):
    today = dt.date.today()
    weekday = today.weekday()

    if next_weekday is None:
        if weekday >= 4:
            until_monday = 7 - weekday
            monday = today + dt.timedelta(days=until_monday)

            return monday.isoformat()
        else:
            tomorrow = today + dt.timedelta(days=1)
            return tomorrow.isoformat()
    else:
        if next_weekday > weekday:
            days = next_weekday - weekday
        else:
            days = 7 - (weekday - next_weekday)
        day = today + dt.timedelta(days=days)

        return day.isoformat()


def get_next_meal(meal=''):
    d = dt.datetime.now()
    weekday = d.weekday()
    now = d.hour + d.minute/60
    today = d.date().isoformat()

    next_meal = {'day': None, 'meal': None}

    if meal:
        next_meal['meal'] = meal

    # finds what the next meal is based on meal requested by user, day of week,
    # and time. The regions considered are as follows:
    #       Mon Tue Wed Thu Fri Sat Sun
    #        4   4   4   4   4   1   1
    # 8h30  ---------------------------
    #        3   3   3   3   3   1   1
    # 14h   ---------------------------
    #        2   2   2   2   2   1   1
    # 19h45 ---------------------------
    #        1   1   1   1   1   1   1

    if weekday == 5 or weekday == 6 or now > 19.75: # region 1
        if not meal:
            next_meal['meal'] = 'almoco'
        next_meal['day'] = get_next_day()
    elif now > 14: # region 2
        if not meal:
            next_meal['meal'] = 'jantar'
        if meal == 'cafe' or meal == 'almoco':
            next_meal['day'] = get_next_day()
        else:
            next_meal['day'] = today
    elif now > 8.5: # region 3
        if not meal:
            next_meal['meal'] = 'almoco'
        if meal == 'cafe':
            next_meal['day'] = get_next_day()
        else:
            next_meal['day'] = today
    else: # region 4
        if not meal:
            next_meal['meal'] = 'almoco'
        next_meal['day'] = today

    return next_meal


def display_menu(args):
    print_dish.has_been_called = False
    print_meal.has_been_called = False
    # default behaviour (when no meal is specified) is to print all meals
    if args.dia and not args.cafe and not args.almoco and not args.jantar:
        args.cafe = True
        args.almoco = True
        args.jantar = True

    # default behaviour (when no dish is specified) is to print all dishes
    if not args.base and not args.principal and not args.salada and\
       not args.sobremesa and not args.suco and not args.obs:
        args.base = True
        args.principal = True
        args.salada = True
        args.sobremesa = True
        args.suco = True
        args.obs = True

    # show vegetarian menu if 'vegetariano' flag was used
    veg = ''
    if args.vegetariano:
        veg = '_veg'

    # day specified, show menu for that day
    weekday_re = re.compile(r'^(2|3|4|5|6)a$')
    if args.dia:
        if args.dia == 'proximo':
            args.dia = get_next_day()
        elif args.dia == 'hoje':
            today = dt.date.today()
            args.dia = today.isoformat()
        elif weekday_re.search(args.dia):
            # get day of next given weekday
            args.dia = get_next_day(int(args.dia[0]) - 2)
        menu = get_menu(args.dia)
        if args.cafe:
            print_meal(menu, 'cafe', args)
        for i, meal in enumerate([args.almoco, args.jantar]):
            if meal:
                meals_names = ['almoco', 'jantar']
                print_meal(menu, meals_names[i] + veg, args)
    # day unspecified, show menu for next meal. Any meal if none is
    # specified and for the next meal specified otherwise
    else:
        if not args.almoco and not args.jantar and not args.cafe:
            next_meal = get_next_meal()
            menu = get_menu(next_meal['day'])

            print_meal(menu, next_meal['meal'] + veg, args)
        else:
            if args.cafe:
                next_meal = get_next_meal('cafe')
                menu = get_menu(next_meal['day'])

                print_meal(menu, next_meal['meal'], args)
            if args.almoco:
                next_meal = get_next_meal('almoco')
                menu = get_menu(next_meal['day'])

                print_meal(menu, next_meal['meal'] + veg, args)
            if args.jantar:
                next_meal = get_next_meal('jantar')
                menu = get_menu(next_meal['day'])

                print_meal(menu, next_meal['meal'] + veg, args)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--dia', action='store', help='''seleciona o dia (no
            formato aaaa-mm-dd, ou 'hoje' ou 'proximo' ou '2a', ... ,'6a') do
            cardápio''')
    parser.add_argument('--almoco', action='store_true', help='''mostra o
            cardápio do almoço''')
    parser.add_argument('--jantar', action='store_true', help='''mostra o
            cardápio do jantar''')
    parser.add_argument('--cafe', action='store_true', help='''mostra cardápio
    do café da manhã''')
    parser.add_argument('--vegetariano', action='store_true', help='''mostra o
            cardápio vegetariano''')
    parser.add_argument('--base', action='store_true', help='''mostra a base
            (arroz e feijão) das refeições''')
    parser.add_argument('--principal', action='store_true', help='''mostra o
            prato principal das refeições''')
    parser.add_argument('--salada', action='store_true', help='''mostra a
            salada das refeições''')
    parser.add_argument('--sobremesa', action='store_true', help='''mostra a
            sobremesa das refeições''')
    parser.add_argument('--suco', action='store_true', help='''mostra o suco
            das refeições''')
    parser.add_argument('--obs', action='store_true', help='''mostra as
            observações das refeições''')

    parser.add_argument('--sem-cabecalho', action='store_true', help='''não
            escreve os cabeçalhos para cada prato e dia''')
    parser.add_argument('--primeiro', action='store_true', help='''mostra
            apenas o primeiro item de cada prato''')

    args = parser.parse_args()
    display_menu(args)


if __name__ == "__main__":
    main()
