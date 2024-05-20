import boto3

def add_vehicle(table_name, vehicle_id, status):
    # Ensure that status is either 'blacklisted' or 'whitelisted'
    if status not in ['blacklisted', 'whitelisted']:
        return "Invalid status. Please use 'blacklisted' or 'whitelisted'."

    # Create a DynamoDB client using boto3
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    # Put item in the table
    try:
        response = table.put_item(
            Item={
                'VehicleID': vehicle_id,
                'Status': status,
            }
        )
        return f"Successfully added vehicle {vehicle_id} with status {status}."
    except Exception as e:
        return f"Error adding vehicle: {str(e)}"

if __name__ == '__main__':
    table_name = 'VehicleTable-s2110849'
    print(add_vehicle(table_name, '10652 OC 22', 'blacklisted'))
    print(add_vehicle(table_name, '8740 NV 12', 'whitelisted'))
