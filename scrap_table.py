import requests
import boto3
import uuid

def lambda_handler(event, context):

    # URL de la API del IGP
    url = "https://ultimosismo.igp.gob.pe/api/ultimo-sismo/ajaxb/2026"

    # Realizar la solicitud HTTP
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    if response.status_code != 200:
        return {
            'statusCode': response.status_code,
            'body': 'Error al acceder a la API del IGP'
        }

    # Obtener los datos JSON
    rows = response.json()

    # Conectar con DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('TablaWebScrapping')

    # Eliminar los registros anteriores
    scan = table.scan()

    with table.batch_writer() as batch:
        for each in scan['Items']:
            batch.delete_item(
                Key={
                    'id': each['id']
                }
            )

    # Insertar los nuevos registros
    i = 1

    with table.batch_writer() as batch:
        for row in rows:

            row['#'] = i
            row['id'] = str(uuid.uuid4())

            batch.put_item(Item=row)

            i += 1

    # Retornar resultado
    return {
        'statusCode': 200,
        'body': f'Se insertaron {len(rows)} reportes sísmicos'
    }
