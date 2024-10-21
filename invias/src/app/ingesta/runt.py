import psycopg2

def getDataRunt(placa):
    conn = psycopg2.connect(
        host="psql-prod-001.postgres.database.azure.com",
        database="cco_lite",
        user="adminazure@psql-prod-001",
        password="UsPt7eKmGQ"
    )
    cur = conn.cursor()
    cur.execute('SELECT * FROM "RUNT".runt_data WHERE "PLACA" = %s', (placa,))
    rows = cur.fetchall()
    # records = []
    
    dataNew = {}
    for row in rows:
        # record = {}
        for i, column in enumerate(cur.description):
            # print(column)
            if(column.name == 'EJES'):
                dataNew['axles'] = row[i]
            if(column.name == 'EJES_CALCULADO'):
                axles = 0
                if(row[i] != None):
                    axles = row[i]
                dataNew['calculated_axles'] = axles
            if(column.name == 'CAPACIDAD_CARGA'):
                dataNew['load_capacity'] = row[i]
            if(column.name == 'CLASE'):
                dataNew['class'] = row[i]
            # record[column.name] = row[i]
        # records.append(record)
    conn.close()
    
    return dataNew