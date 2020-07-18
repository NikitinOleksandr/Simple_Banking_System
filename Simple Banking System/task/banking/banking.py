import random
import sys
from luhn import *
import sqlite3
from checkdigit import luhn

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS card (
        id INTEGER,
        number TEXT,
        pin TEXT,
        balance INTEGER DEFAULT 0);
        """)
conn.commit()

card_number = ""
pin = ""
balance = int

initial_menu = """
1. Create an account
2. Log into account
0. Exit
"""

logged_menu = """
1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit
"""


def create_account():
    global balance
    i = 1
    balance = 0
    generated_account = append("400000" + str(random.randint(000000000, 999999999)).rjust(9, '0'))
    generated_pin = str(random.randint(0, 9999)).rjust(4, '0')
    print("Your card has been created")
    print("Your card number:")
    print(generated_account)
    print("Your card PIN:")
    print(generated_pin)
    cur.execute("""
        INSERT INTO card (id, number, pin, balance)
        VALUES ({}, {}, {}, {});""".format(i, generated_account, generated_pin, balance))
    conn.commit()
    i += 1


def log_into_account():
    global card_number
    global pin
    cur.execute("""
        SELECT number, pin
        FROM card; 
    """)
    output = dict(cur.fetchall())
    card_number = input("Enter your card number:\n")
    pin = input("Enter your PIN:\n")
    if card_number in output.keys() and output[card_number] == pin:
        print("\nYou have successfully logged in!")
        inner_menu()
    else:
        print("\nWrong card number or PIN!")


def add_income():
    add_value = input("Enter income:\n")
    cur.execute("""UPDATE card SET balance = balance + {} 
                WHERE number = {} and pin = {};""".format(add_value, card_number, pin))
    conn.commit()
    print("Income was added!")


def do_transfer():
    cur.execute("""SELECT number FROM card;""")
    list_of_cards = cur.fetchall()
    formatted_list = []
    for element in list_of_cards:
        formatted_item = str(element).replace("[", "").replace("]", "").replace("(", "").replace(")", "").replace(",", "").replace("'", "")
        formatted_list.append(formatted_item)
    print("Transfer")
    target_card = input("Enter card number:\n")
    while True:
        if not luhn.luhn_validate(target_card):
            print("Probably you made mistake in the card number. Please try again!")
            break
        if target_card not in formatted_list:
            print("Such a card does not exist.")
            break
        if target_card == card_number:
            print("You can't transfer money to the same account!")
            break
        money_for_transfer = input("Enter how much money you want to transfer:\n")
        if money_for_transfer > get_balance():
            print("Not enough money!")
            break
        else:
            cur.execute("UPDATE card SET balance = balance - {} WHERE number = {};".format(money_for_transfer, card_number))
            cur.execute("UPDATE card SET balance = balance + {} WHERE number = {};".format(money_for_transfer, target_card))
            conn.commit()
            print("Success!")
            break


def close_account():
    cur.execute("DELETE FROM card WHERE number = {}".format(card_number))
    conn.commit()
    print("The account has been closed!")


def get_balance():
    global balance
    cur.execute("""
            SELECT balance FROM card
            WHERE number = {} and pin = {};""".format(card_number, pin))
    balance = str(cur.fetchall()).replace("[", "").replace("]", "").replace("(", "").replace(")", "").replace(",", "")
    return balance


def inner_menu():
    while True:
        print(logged_menu)
        choice = int(input())
        if choice == 1:
            print("Balance:", get_balance())
        elif choice == 2:
            add_income()
        elif choice == 3:
            do_transfer()
        elif choice == 4:
            close_account()
            break
        elif choice == 5:
            print("\nYou have successfully logged out!")
            break
        elif choice == 0:
            print("\nBye!")
            sys.exit(0)


def upper_menu():
    while True:
        print(initial_menu)
        command = int(input())
        if command == 1:
            create_account()
        elif command == 2:
            log_into_account()
            continue
        elif command == 0:
            print("\nBye!")
            break


upper_menu()
