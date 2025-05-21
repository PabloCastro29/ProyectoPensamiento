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

# Guardar en la tabla Inversiones
def saveInversionDynamoDB(session, inversion):
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table('Inversiones')
    response = table.put_item(Item=inversion)
    return response

# Obtener precio actual desde Twelve Data
def obtener_precio_accion(simbolo):
    url = f"https://api.twelvedata.com/price?symbol={simbolo}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    if "price" in data:
        return float(data["price"])
    else:
        print("No se pudo obtener el precio de la acción:", data)
        return None

# Menú principal
def menu():
    print("=== Registro de Inversión ===")

    while True:
        email = input("Ingrese su correo Gmail: ")
        if email.endswith("@gmail.com"):
            break
        else:
            print("El correo debe ser de Gmail. Intente de nuevo.")

    nombre = input("Ingrese su nombre: ")

    while True:
        identificacion = input("Ingrese su número de identificación (UUID o DPI): ")
        if identificacion.strip():
            break
        else:
            print("Debe ingresar un número de identificación válido.")

    while True:
        try:
            edad = int(input("Ingrese su edad: "))
            break
        except ValueError:
            print("Edad inválida. Debe ser un número.")

    
    usuario = {
        "email": email,
        "name": nombre,
        "age": edad,
        "identificacion": identificacion
    }
    saveUserDynamoDB(awsSession, usuario)

    # Datos de inversión
    while True:
        try:
            monto_total = float(input("¿Con cuánto dinero cuentas en total? Q: "))
            break
        except ValueError:
            print("Debe ingresar un número válido.")

    while True:
        try:
            monto_invertir = float(input("¿Cuánto deseas invertir? Q: "))
            if monto_invertir > monto_total:
                print("No puedes invertir más de lo que tienes.")
            else:
                break
        except ValueError:
            print("Debe ingresar un número válido.")

    acciones_disponibles = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    print("Acciones disponibles:")
    for i, accion in enumerate(acciones_disponibles, 1):
        print(f"{i}. {accion}")
    while True:
        try:
            opcion = int(input("Elige el número de la acción que deseas comprar: "))
            if 1 <= opcion <= len(acciones_disponibles):
                accion_elegida = acciones_disponibles[opcion - 1]
                break
            else:
                print("Opción inválida. Intente de nuevo.")
        except ValueError:
            print("Debe ingresar un número válido.")

    
    precio_actual = obtener_precio_accion(accion_elegida)
    if precio_actual is None:
        print("No se puede continuar sin conocer el precio de la acción.")
        return

    cantidad_acciones = round(monto_invertir / precio_actual, 2)

    print(f"\nPrecio actual de {accion_elegida}: ${precio_actual}")
    print(f"Con Q{monto_invertir} puedes comprar aproximadamente {cantidad_acciones} acciones.")

    
    inversion = {
        "Inversiones": int(time()),
        "email": email,
        "name": nombre,
        "age": edad,
        "monto_total": Decimal(str(monto_total)),
        "monto_invertido": Decimal(str(monto_invertir)),
        "accion": accion_elegida,
        "precio_unitario": Decimal(str(precio_actual)),
        "acciones_compradas": Decimal(str(cantidad_acciones))
    }

    print("DEBUG - OBJETO A GUARDAR:")
    print(inversion)

    respuesta = saveInversionDynamoDB(awsSession, inversion)
    print("¡Inversión guardada exitosamente en DynamoDB!")
    print("Respuesta de AWS:", respuesta)

if __name__ == "__main__":

    menu()

