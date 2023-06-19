# script to take a snapshot of an RDS instance

import boto3
import datetime
import sys
import time
import argparse


# get the current date and time
now = datetime.datetime.now()

if __name__ == '__main__':

    # argparse get inputs
    parser = argparse.ArgumentParser(description='Backup RDS instance')
    parser.add_argument('--instance', help='RDS instance name')
    parser.add_argument('--region', help='AWS region')
    parser.add_argument('--bucket', help='S3 bucket name')
    parser.add_argument('--prefix', help='S3 prefix')
    parser.add_argument('--role', help='IAM role')
    parser.add_argument('--kms', help='KMS key')
    args = parser.parse_args()

    # if args are not passed, throw error
    if None in (args.instance, args.region, args.bucket, args.prefix, args.role, args.kms):
        print('Usage: python backup-rds.py [instance name] [region] [bucket] [prefix] [role] [kms]')
        sys.exit(1)

    # Display all the values given
    print("-"*50)
    print("RDSbackupS3 | Version: 0.0.1 | Github: ")
    print("-"*50)
    for arg in vars(args):
        print("{:<10}: '{}'".format(arg, getattr(args, arg)))
    print("-"*50)


    # set the region and create the RDS client
    rds = boto3.client('rds', region_name=args.region)

    instance_name = args.instance

    # get the instance id from the instance name
    response = rds.describe_db_instances(DBInstanceIdentifier=instance_name)

    if not response['DBInstances']:
        print('No instance found with name: ' + instance_name)
        sys.exit(1)
        
    instance_id = response['DBInstances'][0]['DBInstanceIdentifier']

    # create the snapshot
    year=str(now.year)
    month=str(now.month)
    day=str(now.day)

    snapshot_name = instance_name + '-manual-' + now.strftime('%Y-%m-%d-%H-%M')
    print('Creating snapshot: ' + snapshot_name)
    response = rds.create_db_snapshot(
        DBSnapshotIdentifier=snapshot_name,
        DBInstanceIdentifier=instance_id,
        Tags=[
            {
                'Key': "BackupDateTime",
                'Value': now.strftime('%Y-%m-%d-%H-%M'),
            },
            {
                'Key': "BackupType",
                'Value': "Manual",
            },
        ]
    )

    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        print('Error creating snapshot')
        sys.exit(1)

    # print the snapshot name
    print("Snapshot Initiated successfully: "+snapshot_name)  

    # wait for the snapshot to be created
    waiter = rds.get_waiter('db_snapshot_completed')  

    print('Waiting for snapshot to complete')
    waiter.wait(
        DBSnapshotIdentifier=snapshot_name,
        WaiterConfig={
            'Delay': 30,
            'MaxAttempts': 60
        }
    )

    # print the snapshot status
    response = rds.describe_db_snapshots(DBSnapshotIdentifier=snapshot_name)
    snapshot_status = response['DBSnapshots'][0]['Status']
    print('Snapshot status: ' + snapshot_status)

    # if the snapshot fails, print the status message
    if snapshot_status == 'failed':
        print('Snapshot failed: ' + response['DBSnapshots'][0]['StatusMessage'])
        sys.exit(1)

    # if the snapshot succeeds, print the arn
    print('Snapshot created with arn: ' + response['DBSnapshots'][0]['DBSnapshotArn'])


    # Export the Snapshots to S3
    export_response=rds.start_export_task(
        ExportTaskIdentifier='export-'+snapshot_name,
        SourceArn=response['DBSnapshots'][0]['DBSnapshotArn'],
        S3BucketName=args.bucket,
        IamRoleArn=args.role,
        KmsKeyId=args.kms,
        S3Prefix=args.prefix,
    )

    # print the export status
    response = rds.describe_export_tasks(ExportTaskIdentifier='export-'+snapshot_name)
    export_status = response['ExportTasks'][0]['Status']
    print('Export status: ' + export_status)

    export_status = export_status.lower()

    # wait until the export status changes to 'completed'
    while export_status == 'in_progress' or export_status == 'starting':
        i = 0
        response = rds.describe_export_tasks(ExportTaskIdentifier='export-'+snapshot_name)
        export_status = response['ExportTasks'][0]['Status']
        print('Export status: ' + export_status)
        time.sleep(30)
        i = i + 1

        # Lowercase the export status for comparison
        export_status = export_status.lower()

        # break if no of attempts are more than 30 - 15 minutes
        if i > 30:
            break
        if export_status == 'failed' or export_status == 'failed' or export_status == 'canceled':
            break


    if export_status == 'failed':
        print('Export failed: ' + str(response))
        sys.exit(1)
    
    elif export_status == 'canceled':
        print('Export canceled: ' + str(response))
        sys.exit(1)

    elif export_status == 'complete':
        print('Export completed Successfully: ' + str(response))

    else:
        print('Unhandled Export status: ' + export_status)
        print('Response: ' + str(response))
        print('Not removing the snapshot as the export status is not complete')
        sys.exit(1)

    # Delete the snapshot
    print('Deleting snapshot: ' + snapshot_name)
    response = rds.delete_db_snapshot(
        DBSnapshotIdentifier=snapshot_name
    )

    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        print('Error deleting snapshot')
        sys.exit(1)

    # print the snapshot name
    print("Snapshot deleted successfully: "+snapshot_name)


    

    
  