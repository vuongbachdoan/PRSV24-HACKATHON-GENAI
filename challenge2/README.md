### Understanding the Architecture

#### Data Flow
- DynamoDB: Stores data with a contactId partition key.
- Glue: Extracts data from DynamoDB, likely transforms it, and loads it into S3.
- S3: Stores the transformed data with a contactId partition key.

#### Setting Up IAM Roles
1. Create an IAM Role for Glue
- Navigate to the IAM console.
- Go to Roles and click "Create Role".
- Select "AWS Service" as the trusted entity and choose "Glue" as the service.
- Attach the following policies:
```
AmazonS3FullAccess
AmazonDynamoDBFullAccess
AWSGlueServiceRole
```
2. Create an IAM Role for EC2 (if running Glue job on EC2)
- Follow the same steps as above, but select "EC2" as the trusted entity.
- Attach the same policies as for the Glue role.

#### Creating the Glue Job
1. Create a Glue Database and Table
- In the Glue console, create a database to store the metadata for your job.
- Create a table in the database to define the schema of your data.
2. Create a Glue Crawler
- Create a crawler to discover the schema of your DynamoDB table. This is optional but recommended for automatic schema discovery.
3. Create a Glue Job
- In the Glue console, create a new job.
- Paste the provided Python script into the job editor.
- Save the job.
- Running the Glue Job

> You can run the job manually from the Glue console or schedule it to run automatically.