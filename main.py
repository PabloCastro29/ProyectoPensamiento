import requests
from decimal import Decimal
from random import randint
from app.AWSConnections import AWSConnections
from time import time

API_KEY = "dc66e9efc2ec4234a259b73530453cdb"

aws = AWSConnections()
awsSession = aws.getSession()


def saveUserDynamoDB(session, user):
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table('Users')
    response = table.put_item(Item=user)
    return response

def saveInvestmentDynamoDB(session, investment):
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table('Inversiones')
    response = table.put_item(Item=investment)
    return response

def get_action_price(symbol):
    url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    if "price" in data:
        return float(data["price"])
    else:
        print("No se pudo obtener el precio de la acción:", data)
        return None

def menu():
    print("=== Registro de Inversión ===")

    while True:
        email = input("Ingrese su correo Gmail: ")
        if email.endswith("@gmail.com"):
            break
        else:
            print("El correo debe ser de Gmail. Intente de nuevo.")

    name = input("Ingrese su nombre: ")

    while True:
        identification = input("Ingrese su número de identificación (UUID o DPI): ")
        if identification.strip():
            break
        else:
            print("Debe ingresar un número de identificación válido.")

    while True:
        try:
            age = int(input("Ingrese su edad: "))
            break
        except ValueError:
            print("Edad inválida. Debe ser un número.")

    usuario = {
        "email": email,
        "name": name,
        "age": age,
        "identificacion": identification
    }
    saveUserDynamoDB(awsSession, usuario)

    # Datos de inversión
    while True:
        try:
            total_amount = float(input("¿Con cuánto dinero cuentas en total? Q: "))
            break
        except ValueError:
            print("Debe ingresar un número válido.")

    while True:
        try:
            investment_amount = float(input("¿Cuánto deseas invertir? Q: "))
            if investment_amount > total_amount:
                print("No puedes invertir más de lo que tienes.")
            else:
                break
        except ValueError:
            print("Debe ingresar un número válido.")

    available_actions = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    print("Acciones disponibles:")
    for i, action in enumerate(available_actions, 1):
        print(f"{i}. {action}")
    while True:
        try:
            option = int(input("Elige el número de la acción que deseas comprar: "))
            if 1 <= option <= len(available_actions):
                chosen_action = available_actions[option - 1]
                break
            else:
                print("Opción inválida. Intente de nuevo.")
        except ValueError:
            print("Debe ingresar un número válido.")

    current_price = get_action_price(chosen_action)
    if current_price is None:
        print("No se puede continuar sin conocer el precio de la acción.")
        return

    actions_amount = round(investment_amount / current_price, 2)

    print(f"Precio actual de {chosen_action}: ${current_price}")
    print(f"Con Q{investment_amount} puedes comprar aproximadamente {actions_amount} acciones.")

    
    investment = {
        "inversion": str(int(time())), 
        "email": email,
        "name": name,
        "age": age,
        "monto_total": Decimal(str(total_amount)),
        "monto_invertido": Decimal(str(investment_amount)),
        "accion": chosen_action,
        "precio_unitario": Decimal(str(current_price)),
        "acciones_compradas": Decimal(str(actions_amount))
    }

    print(" OBJETO A GUARDAR:")
    print(investment)

    response = saveInvestmentDynamoDB(awsSession, investment)
    print("¡Inversión guardada exitosamente en DynamoDB!")
    print("Respuesta de AWS:", response)


if __name__ == "__main__":
    menu()

