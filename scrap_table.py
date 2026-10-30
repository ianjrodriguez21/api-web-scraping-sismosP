
import requests
import boto3
import uuid

def lambda_handler(event, context):

    # URL de los reportes sísmicos del IGP
    url = "https://ultimosismo.igp.gob.pe/api/ultimo-sismo/ajaxb/2026"

    # Obtener información de la página
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    if response.status_code != 200:
        return {
            'statusCode': response.status_code,
            'body': 'Error al acceder a la API del IGP'
        }

    # Convertir la respuesta a JSON
    rows = response.json()

    # Conectarse a DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('TablaWebScrapping-SismosP')

    # Eliminar registros anteriores
    scan = table.scan()

    with table.batch_writer() as batch:
        for each in scan['Items']:
            batch.delete_item(
                Key={'id': each['id']}
            )

    # Insertar los nuevos reportes sísmicos
    i = 1

    with table.batch_writer() as batch:
        for row in rows:
            row['#'] = i
            row['id'] = str(uuid.uuid4())

            batch.put_item(Item=row)
            i += 1

    return {
        'statusCode': 200,
        'body': f'Se insertaron {len(rows)} reportes sísmicos'
    }

