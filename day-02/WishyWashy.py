
import random

def generate_minutes():
    minutes = random.randint(30, 180)
    return minutes

def calc_amount(machine_type, minutes):

    hours = minutes / 60

    if machine_type == "A":
        initial_cost = 50.00
        hourly_rate = 30.00

    elif machine_type == "B":
        initial_cost = 62.50
        hourly_rate = 36.25

    elif machine_type == "C":
        initial_cost = 74.87
        hourly_rate = 40.50

    amount = initial_cost + (hourly_rate * hours)

    return amount

def calc_total_amount(amount):

    vat = amount * 0.14
    total = amount + vat

    return vat, total

def display_summary(payments):

    number_of_customers = len(payments)

    total_payments = sum(payments)

    average_payment = total_payments / number_of_customers

    highest_payment = max(payments)

    lowest_payment = min(payments)

    print("\n========== DAILY SUMMARY ==========")

    print("Number of customers:", number_of_customers)
    print(f"Combined amount payable: R{total_payments:.2f}")
    print(f"Average payment: R{average_payment:.2f}")
    print(f"Highest payment: R{highest_payment:.2f}")
    print(f"Lowest payment: R{lowest_payment:.2f}")

    print("===================================")

def process_payments():

    payments = []

    customers = int(input("Enter number of customers: "))

    for count in range(customers):

        print("\nCustomer", count + 1)

        name = input("Enter customer name: ")

        machine_type = input("Enter machine type (A, B or C): ").upper()

        minutes = generate_minutes()

        amount = calc_amount(machine_type, minutes)

        vat, total = calc_total_amount(amount)

        payments.append(total)

        print("\n========== CUSTOMER INVOICE ==========")

        print("Customer name:", name)
        print("Machine type:", machine_type)
        print("Minutes used:", minutes)

        print(f"Amount before VAT: R{amount:.2f}")
        print(f"VAT (14%): R{vat:.2f}")
        print(f"Total payable: R{total:.2f}")

        print("======================================")

    display_summary(payments)

process_payments()
