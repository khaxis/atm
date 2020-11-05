#!/usr/bin/env python
from dataclasses import dataclass, field
from typing import List


@dataclass
class Card:
    card_id: str
    pin: str


@dataclass
class Account:
    account_number: str
    balance: int
    cards: List[Card] = field(default_factory=list)


@dataclass
class Test:
    action: str
    args: list
    expect_exception: bool = False
    result: 'typing.Any' = None


class ATMError(Exception):
    def __init__(self, *args, **kwargs):
        super(ATMError, self).__init__(*args, **kwargs)


class ATM(object):
    def __init__(self, accounts):
        self.account_id_to_account = {
            account.account_number: account for account in accounts
        }
        self.card_id_to_account_id = {}
        self.card_id_to_card = {}
        for account in accounts:
            for card in account.cards:
                self.card_id_to_account_id[card.card_id] = account.account_number
                self.card_id_to_card[card.card_id] = card

        self.card_id = None

    def __get_account(self, account_id):
        return self.account_id_to_account[account_id]

    def insert(self, card_id, pin):
        if self.card_id:
            raise ATMError('Card is already in ATM')
        if self.card_id_to_card[card_id].pin != pin:
            raise ATMError('Wrong pin')
        self.card_id = card_id

    def remove(self):
        if not self.card_id:
            raise ATMError('No card in ATM')
        self.card_id = None

    def balance(self):
        if not self.card_id:
            raise ATMError('No card in ATM')
        return self.__get_account(self.card_id_to_account_id[self.card_id]).balance

    def deposit(self, money):
        if not self.card_id:
            raise ATMError('No card in ATM')
        if money < 0:
            raise ATMError('Could not deposit negative amount')
        self.__get_account(self.card_id_to_account_id[self.card_id]).balance += money

    def withdraw(self, money):
        if not self.card_id:
            raise ATMError('No card in ATM')
        bal = self.__get_account(self.card_id_to_account_id[self.card_id]).balance
        if bal - money < 0:
            raise ATMError('Not enough balance')
        self.__get_account(self.card_id_to_account_id[self.card_id]).balance -= money
        return money


# TESTS:

accounts = [
    Account(
        account_number='0',
        balance=100,
        cards=[
            Card(
                card_id='12345678',
                pin='1234',
            )
        ]
    ),
]

atm = ATM(accounts)

TESTS = [
    Test('insert', ['12345678', 'fake'], True),
    Test('insert', ['12345678', '1234'], False),
    Test('insert', ['12345678', '1234'], True),
    Test('balance', [], False, 100),
    Test('balance', [], True, 200),
    Test('deposit', [100], False),
    Test('balance', [], False, 200),
    Test('withdraw', [1000], True),
    Test('withdraw', [200], False, 200),
    Test('balance', [], False, 0),
]

for test in TESTS:
    try:
        result = getattr(atm, test.action)(*test.args)
        if (result or test.result) and result != test.result:
            raise ATMError("Unexpected result")
    except ATMError as e:
        if test.expect_exception:
            continue
        else:
            raise
