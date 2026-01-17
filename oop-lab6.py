from typing import List, Union, Optional

##################################################################################
# Instruction for Students:
# 1. จงเขียน Class Diagram เพื่อออกแบบ Class ต่างๆ ให้รองรับการทำงานของ Code ส่วนล่าง
# 2. จงเขียน Class Definition (Bank, User, Account, ATM_Card, ATM_machine, Transaction)
#    เพื่อให้สามารถรัน Function run_test() ได้โดยไม่เกิด Error
# 3. ห้ามแก้ไข Code ในส่วนของ create_bank_system() และ run_test() โดยเด็ดขาด
# 4. ต้องมีการ Validate ข้อมูลตามเงื่อนไขที่กำหนดในเอกสาร Lab (เช่น เงินไม่พอ, PIN ผิด)
#    และทำการ Raise Exception เมื่อเกิดข้อผิดพลาด
##################################################################################

# --- พื้นที่สำหรับเขียน Class ของนักศึกษา (เขียนต่อจากตรงนี้) ---

class Bank:
    def __init__(self, name_bank):
        self.__name_bank = name_bank
        self.__users = []
        self.__atm_machines = []

    def add_user(self, user):
        self.__users.append(user) 

    def add_atm_machine(self, atm_machine):
        self.__atm_machines.append(atm_machine)

    def get_atm_by_id(self, atm_id):
        for atm in self.__atm_machines:
            if atm.atm_id == atm_id:
                return atm
        return None
    
    def search_account_from_atm(self, atm_card_no: str):
        for user in self.__users:
            for account in user.accounts:
                if account.atm_card and account.atm_card.card_no == atm_card_no:
                    return account
        return None
    
class User:
    def __init__(self, citizen_id, name):
        self.citizen_id = citizen_id
        self.name = name
        self.accounts = []

    def add_account(self, account):
        self.accounts.append(account)

    def get_account_num(self, account_no):
        for account in self.accounts:
            if account.account_no == account_no:
                return account
        return None
    
class Account:
    DAILY_LIMIT = 40000
    ANNUAL_FEE = 150

    def __init__(self, account_no, user, amount):
        self.account_no = account_no
        self.user = user
        self.amount = amount
        self.atm_card = None
        self.transaction_history = []
        self.daily_used = 0

    def add_atm_card(self, atm_card):
        self.atm_card = atm_card

    def reset_daily_limit(self):
        self.daily_used = 0

    def pay_annual_fee(self):
        if self.amount < self.ANNUAL_FEE:
            raise Exception("Insufficient balance for annual fee")
        self.amount -= self.ANNUAL_FEE
        self.transaction_history.append(
            Transaction("Annual Fee", self.ANNUAL_FEE)
        )

    def _check_amount(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")

    def _check_daily_limit(self, amount):
        if self.daily_used + amount > self.DAILY_LIMIT:
            raise Exception("Daily limit exceeded")

    def deposit(self, atm_machine, amount):
        atm_machine._validate_card(self)
        self._check_amount(amount)

        self.amount += amount
        self.transaction_history.append(Transaction("Deposit", amount))

    def withdraw(self, atm_machine, amount):
        atm_machine._validate_card(self)
        self._check_amount(amount)
        self._check_daily_limit(amount)

        if amount > self.amount:
            raise Exception("Insufficient balance")

        if amount > atm_machine.balance:
            raise Exception("ATM has insufficient cash")

        self.amount -= amount
        atm_machine.balance -= amount
        self.daily_used += amount

        self.transaction_history.append(Transaction("Withdraw", amount))

    def transfer(self, atm_machine, amount, to_account):
        atm_machine._validate_card(self)
        self._check_amount(amount)
        self._check_daily_limit(amount)

        if amount > self.amount:
            raise Exception("Insufficient balance")

        self.amount -= amount
        to_account.amount += amount
        self.daily_used += amount

        self.transaction_history.append(Transaction("Transfer", amount))

    def print_transactions(self):
        for t in self.transaction_history:
            print(f"{t.type}: {t.amount}")

class ATM_Card:
    def __init__(self, card_no, account_no, pin):
        self.card_no = card_no
        self.account_no = account_no
        self.pin = pin
    
class ATM_machine:
    def __init__(self, atm_id, balance):
        self.atm_id = atm_id
        self.balance = balance
        self.current_card = None

    def insert_card(self, card, pin):
        if card.pin != pin:
            return False
        self.current_card = card
        return True

    def eject_card(self):
        self.current_card = None

    def _validate_card(self, account):
        if self.current_card is None:
            raise Exception("No ATM card inserted")

        if self.current_card.account_no != account.account_no:
            raise Exception("ATM card does not match this account")


    
class Transaction:
    def __init__(self, type, amount):
        self.type = type
        self.amount = amount
        
##################################################################################
# Test Case & Setup : ห้ามแก้ไข Code ส่วนนี้
# ใช้สำหรับตรวจสอบว่า Class ที่ออกแบบมาถูกต้องตาม Requirement หรือไม่
##################################################################################

def create_bank_system() -> Bank:
    print("--- Setting up Bank System ---")
    
    # 1. กำหนดชื่อธนาคาร
    scb = Bank("SCB")
    
    # 2. สร้าง User, Account, ATM_Card
    # Data format: CitizenID: [Name, AccountNo, ATM Card No, Balance]
    user_data = {
       '1-1101-12345-12-0': ['Harry Potter', '1000000001', '12345', 20000],
       '1-1101-12345-13-0': ['Hermione Jean Granger', '1000000002', '12346', 1000]
    }
    
    for citizen_id, detail in user_data.items():
        name, account_no, atm_no, amount = detail
        
        user_instance = User(citizen_id, name)
        user_account = Account(account_no, user_instance, amount)
        atm_card = ATM_Card(atm_no, account_no, '1234')
        
        user_account.add_atm_card(atm_card)
        user_instance.add_account(user_account)
        scb.add_user(user_instance)

    # 3. สร้างตู้ ATM
    scb.add_atm_machine(ATM_machine('1001', 1000000))
    scb.add_atm_machine(ATM_machine('1002', 200000))

    return scb

def run_test():
    scb = create_bank_system()
    
    atm_machine1 = scb.get_atm_by_id('1001')
    atm_machine2 = scb.get_atm_by_id('1002')
    
    harry_account = scb.search_account_from_atm('12345')
    hermione_account = scb.search_account_from_atm('12346')
    
    # ตรวจสอบว่าหา Account เจอหรือไม่
    if not harry_account or not hermione_account:
        print("Error: Could not find accounts. Check your search_account_from_atm method.")
        return

    harry_card = harry_account.atm_card
    hermione_card = hermione_account.atm_card
    
    print("\n--- Test Case #1 : Insert Card (Harry) ---")
    print(f"Harry's Account No : {harry_account.account_no}")

    atm_machine2.insert_card(hermione_card, "1234") 

    if atm_machine1.insert_card(harry_card, "1234"):
        print("Success: ATM accepted valid card and PIN")
    else:
        print("Error: ATM rejected valid card")

    print("\n--- Test Case #2 : Deposit 1000 to Hermione ---")
    print(f"Before: {hermione_account.amount}")

    try:
        hermione_account.deposit(atm_machine2, 1000)
        print(f"After: {hermione_account.amount}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n--- Test Case #3 : Deposit -1 (Expect Error) ---")
    try:
        hermione_account.deposit(atm_machine2, -1)
        print("Error: Failed to catch negative deposit")
    except ValueError as e: # คาดหวัง ValueError หรือ Exception ที่เหมาะสม
        print(f"Pass: System correctly raised error -> {e}")
    except Exception as e:
        print(f"Pass: System raised error -> {e}")

    print("\n--- Test Case #4 : Withdraw 500 from Hermione ---")
    print(f"Before: {hermione_account.amount}")

    try:
        hermione_account.withdraw(atm_machine2, 500)
        print(f"After: {hermione_account.amount}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n--- Test Case #5 : Withdraw Excess Balance (Expect Error) ---")
    try:
        hermione_account.withdraw(atm_machine2, 30000)
        print("Error: Failed to catch overdraft")
    except Exception as e:
        print(f"Pass: System correctly raised error -> {e}")

    harry_card = harry_account.atm_card
    atm_machine2.insert_card(harry_card, "1234") 
    
    print("\n--- Test Case #6 : Transfer 10000 from Harry to Hermione ---")
    print(f"Harry Before: {harry_account.amount}")
    print(f"Hermione Before: {hermione_account.amount}")

    try:
        harry_account.transfer(atm_machine2, 10000, hermione_account)
        print(f"Harry After: {harry_account.amount}")
        print(f"Hermione After: {hermione_account.amount}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n--- Test Case #7 : Transaction History ---")

    print("Harry Transactions:")
    harry_account.print_transactions()
    print("Hermione Transactions:")
    hermione_account.print_transactions()

    print("\n--- Test Case #8 : Wrong PIN (Expect Error) ---")
    if not atm_machine1.insert_card(harry_card, "9999"):
        print("Pass: ATM correctly rejected wrong PIN")
    else:
        print("Error: ATM accepted wrong PIN")
        
    print("\n--- Test Case #9 : Exceed Daily Limit (Expect Error) ---")
    # Harry ถอนไปแล้ว 0, โอน 10000 (นับรวม) = ใช้ไป 10000
    # Limit = 40000. ลองถอนอีก 35000 (รวมเป็น 45000) ต้อง Error
    try:
        print("Attempting to withdraw 35,000 (Total daily: 45,000)...")
        harry_account.withdraw(atm_machine1, 35000)
        print("Error: Daily limit exceeded but not caught")
    except Exception as e:
        print(f"Pass: System correctly raised error -> {e}")

    print("\n--- Test Case #10 : ATM Insufficient Cash (Expect Error) ---")
 
    poor_atm = ATM_machine('9999', 100) 
    scb.add_atm_machine(poor_atm)
    try:
        print("Attempting to withdraw 500 from ATM with 100 THB...")
        harry_account.withdraw(poor_atm, 500)
        print("Error: ATM insufficient cash but not caught")
    except Exception as e:
        print(f"Pass: System correctly raised error -> {e}")

if __name__ == "__main__":
    run_test()