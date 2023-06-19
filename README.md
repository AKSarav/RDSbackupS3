# RDS BACKUP TO S3 

This project is a simple script to backup RDS databases to S3. It uses the boto SDK to connect to AWS and create a snapshot of the database. The snapshot is then copied to S3 and the snapshot is deleted.

To Summarize the script does the following:

1. Connects to AWS using boto
2. Creates a snapshot of the database
3. Copies the snapshot to S3
4. Deletes the snapshot

## How to use this tool

1. Clone git repository
2. Create a virtual environment
``` 
python3 -m venv venv 
```
3. Install the requirements using the following command
```
pip install -r requirements.txt
```
4. Run the script
 ```
 python3 rds_backup_to_s3.py [--instance INSTANCE] [--region REGION][--bucket BUCKET] [--prefix PREFIX] [--role ROLE] [--kms KMS]
 ```


5. Check the S3 bucket for the snapshot


## prequisites

The script expects the following arguments.



`--instance` RDS instance name to backup*

`--region` AWS region of RDS instance

`--bucket` S3 bucket name to copy the snapshot to

`--prefix` S3 prefix ( folder ) to copy the snapshot to

`--role` IAM role to use to copy the snapshot to S3

`--kms`  key to use to copy the snapshot to S3


### Further References

Please checkout my blog for further reference 



> Feedbacks and Contributions are welcome


### Sample run and output

```bash
$ python3 backup-rds.py  – instance mysqlproddb – region us-east-1 – bucket gritfy-backup-drive – prefix databases/mysql/2023/06/18 – kms arn:aws:kms:us-east-1:XXXXXXXXXXX:key/zzzzzzz-1313-4091-xxxx-z18c81001zz – role arn:aws:iam::XXXXXXXXXXX:role/rds-s3-export-support-role
--------------------------------------------------
RDSbackupS3 | Version: 0.0.1 | Github: https://github.com/AKSarav/RDSbackupS3
--------------------------------------------------
instance  : 'mysqlproddb'
region    : 'us-east-1'
bucket    : 'gritfy-backup-drive'
prefix    : 'databases/mysql/2023/06/18'
role      : 'arn:aws:iam::XXXXXXXXXXX:role/rds-s3-export-support-role'
kms       : 'arn:aws:kms:us-east-1:XXXXXXXXXXX:key/zzzzzzz-1313-4091-xxxx-z18c81001zz'
--------------------------------------------------
Creating snapshot: mysqlproddb-manual-2023-06-18-21-00
Snapshot Initiated successfully: mysqlproddb-manual-2023-06-18-21-00
Waiting for snapshot to complete
Snapshot status: available
Snapshot created with arn: arn:aws:rds:us-east-1:XXXXXXXXXXX:snapshot:mysqlproddb-manual-2023-06-18-21-00
Export status: STARTING
Export status: STARTING
Export status: STARTING
Export status: STARTING
Export status: STARTING
Export status: STARTING
Export status: INPROGRESS
Export status: COMPLETE
Export completed Successfully:
Deleting snapshot: mysqlproddb-manual-2023-06-18-21-00
Snapshot deleted successfully: mysqlproddb-prime-manual-2023-06-18-21-00
```


### To do

- [ ] Add support and test with Aurora - In Progress
- [ ] Creating an interface for backup management - In Progress
- [ ] Adding a scheduler to run periodically 
- [ ] Integration with Terraform and Pulumi 
