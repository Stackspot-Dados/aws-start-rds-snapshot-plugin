import logging
import os
import boto3
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)
rds = boto3.client('rds')

def get_environment_variable(environment_variable_name): 
    logger.setLevel(logging.INFO) 
    
    try: 
        logger.info( "INFO: Obtendo valor da variável de ambiente {}" .format(environment_variable_name) ) 
        environment_variable_value = os.environ[environment_variable_name] 
        return environment_variable_value 
    except Exception as e: 
        logger.error(e)
        raise Exception( "ERROR: A variável de ambiente {} não existe" .format(environment_variable_name))


def delete_snapshot(dbs_instance_identifier_list, sufixo_snapshot): 
    deletion_status = [] 
    for db_instance_identifier in dbs_instance_identifier_list: 
        try: 
            logger.info( "INFO: Deletando snapshot gerado anteriormente - Snapshot: {}" .format(db_instance_identifier + sufixo_snapshot) ) 
            dbSnapshotIdentifier = db_instance_identifier + sufixo_snapshot 
            response = rds.delete_db_cluster_snapshot( DBClusterSnapshotIdentifier=dbSnapshotIdentifier )  
            
            logger.info( "INFO: Deleção do snapshot realizada com sucesso - \ Snapshot: {}".format(db_instance_identifier + sufixo_snapshot) ) 
            deletion_status.append({ 
                'DBClusterSnapshotIdentifier': 
                    response['DBClusterSnapshot'] ['DBClusterSnapshotIdentifier'], 
                'DBClusterSnapshotArn': 
                    response['DBClusterSnapshot'] ['DBClusterSnapshotArn'], 
                'HTTPStatusCode': 
                    response['ResponseMetadata'] ['HTTPStatusCode'] }) 
        except Exception: 
            logger.warning( "WARNING: Erro ao deletar o snapshot pois não existe - \ Snapshot: {}".format(db_instance_identifier + sufixo_snapshot) ) 
            return deletion_status
            
def delete_snapshot_instances(dbs_instance_identifier_list, sufixo_snapshot): 
    deletion_status = [] 
    for db_instance_identifier in dbs_instance_identifier_list: 
        try: 
            logger.info( "INFO: Deletando snapshot gerado anteriormente - Snapshot: {}" .format(db_instance_identifier + sufixo_snapshot) ) 
            dbSnapshotIdentifier = db_instance_identifier + sufixo_snapshot 
            response = rds.delete_db_snapshot( DBSnapshotIdentifier=dbSnapshotIdentifier ) 
            
            logger.info( "INFO: Deleção do snapshot realizada com sucesso - \ Snapshot: {}".format(db_instance_identifier + sufixo_snapshot) ) 
            
            deletion_status.append({ 
                'DBSnapshotIdentifier': 
                    response['DBSnapshot'] ['DBSnapshotIdentifier'], 
                'DBSnapshotArn': 
                    response['DBSnapshot'] ['DBSnapshotArn'], 
                'HTTPStatusCode': 
                    response['ResponseMetadata'] ['HTTPStatusCode'] 
                }) 
        except Exception: 
            logger.warning( "WARNING: Erro ao deletar o snapshot pois não existe - \ Snapshot: {}".format(db_instance_identifier + sufixo_snapshot) ) 
            
            return deletion_status
            
def create_snapshot(dbs_instance_identifier_list, sufixo_snapshot): 
    creation_status = [] 
    for db_instance_identifier in dbs_instance_identifier_list: 
        try: 
            logger.info( "INFO: Iniciada a criação do snapshot - \ Base de dados: {}".format(db_instance_identifier) ) 
            dbSnapshotIdentifier = db_instance_identifier + sufixo_snapshot 
            response = rds.create_db_cluster_snapshot( DBClusterIdentifier=db_instance_identifier, DBClusterSnapshotIdentifier=dbSnapshotIdentifier ) 

            creation_status.append({ 'DBClusterIdentifier': response['DBClusterSnapshot'] ['DBClusterIdentifier'], 'DBClusterSnapshotIdentifier': response['DBClusterSnapshot'] ['DBClusterSnapshotIdentifier'], 'DBClusterSnapshotArn': response['DBClusterSnapshot'] ['DBClusterSnapshotArn'], 'HTTPStatusCode': response['ResponseMetadata'] ['HTTPStatusCode'] }) 
        except Exception as e:
            logger.error(e)
            raise Exception( "ERROR: Erro ao criar snapshot - \ Base de dados: {} | Snapshot: {}" .format( db_instance_identifier, db_instance_identifier + sufixo_snapshot ) ) 

    return creation_status

def create_snapshot_instances(dbs_instance_identifier_list, sufixo_snapshot): 
    creation_status = []

    for db_instance_identifier in dbs_instance_identifier_list: 
        try:
            logger.info( "INFO: Iniciada a criação do snapshot - \ Base de dados: {}".format(db_instance_identifier) ) 

            dbSnapshotIdentifier = db_instance_identifier + sufixo_snapshot 
            response = rds.create_db_snapshot( DBInstanceIdentifier=db_instance_identifier, DBSnapshotIdentifier=dbSnapshotIdentifier )  

            creation_status.append({ 
                'DBInstanceIdentifier': response['DBSnapshot'] ['DBInstanceIdentifier'], 
                'DBSnapshotIdentifier': response['DBSnapshot'] ['DBSnapshotIdentifier'], 
                'DBSnapshotArn': response['DBSnapshot'] ['DBSnapshotArn'], 
                'HTTPStatusCode': response['ResponseMetadata'] ['HTTPStatusCode'] 
            }) 

        except Exception as e:
            logger.error(e)

            raise Exception( "ERROR: Erro ao criar snapshot - \ Base de dados: {} | Snapshot: {}" .format( db_instance_identifier, db_instance_identifier + sufixo_snapshot ) ) 

    return creation_status


def lambda_handler(event, context):
    DBS_SNAPSHOTS = get_environment_variable('DBS_SNAPSHOTS')
    SUFIXO_SNAPSHOT = get_environment_variable('SUFIXO_SNAPSHOT')

    # Cluster snapshots
    DBS_SNAPSHOTS = DBS_SNAPSHOTS.split(";")
    delete_snapshot(DBS_SNAPSHOTS, SUFIXO_SNAPSHOT)
    create_snapshot(DBS_SNAPSHOTS, SUFIXO_SNAPSHOT)

    DBS_INSTANCES_SNAPSHOTS = get_environment_variable(
        'DBS_INSTANCES_SNAPSHOTS')
    DBS_INSTANCES_SNAPSHOTS = DBS_INSTANCES_SNAPSHOTS.split(";")
    delete_snapshot_instances(
        DBS_INSTANCES_SNAPSHOTS, SUFIXO_SNAPSHOT)
    create_snapshot_instances(
        DBS_INSTANCES_SNAPSHOTS, SUFIXO_SNAPSHOT)

    return {
        'dataBases': DBS_SNAPSHOTS + DBS_INSTANCES_SNAPSHOTS,
        'datetime': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'HTTPStatusCode': 201
    }