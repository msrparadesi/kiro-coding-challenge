import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as logs from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';
import * as path from 'path';

export class InfrastructureStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // DynamoDB table for events
    const eventsTable = new dynamodb.Table(this, 'EventsTable', {
      tableName: 'EventsTable',
      partitionKey: {
        name: 'eventId',
        type: dynamodb.AttributeType.STRING
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY, // Change to RETAIN for production
      pointInTimeRecoverySpecification: {
        pointInTimeRecoveryEnabled: true,
      },
    });

    // Add GSI for querying by status
    eventsTable.addGlobalSecondaryIndex({
      indexName: 'StatusIndex',
      partitionKey: {
        name: 'status',
        type: dynamodb.AttributeType.STRING
      },
      sortKey: {
        name: 'date',
        type: dynamodb.AttributeType.STRING
      },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    // Create log group for Lambda function
    const logGroup = new logs.LogGroup(this, 'EventsApiLogGroup', {
      logGroupName: '/aws/lambda/EventsApiFunction',
      retention: logs.RetentionDays.ONE_WEEK,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Lambda function for the FastAPI application
    const apiFunction = new lambda.DockerImageFunction(this, 'EventsApiFunction', {
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../backend'), {
        file: 'Dockerfile',
      }),
      memorySize: 512,
      timeout: cdk.Duration.seconds(30),
      environment: {
        DYNAMODB_TABLE_NAME: eventsTable.tableName,
        CORS_ORIGINS: 'https://*,http://localhost:3000,http://localhost:8080',
      },
      logGroup: logGroup,
    });

    // Grant Lambda permissions to access DynamoDB
    eventsTable.grantReadWriteData(apiFunction);

    // Create API Gateway REST API
    const api = new apigateway.RestApi(this, 'EventsApi', {
      restApiName: 'Events API',
      description: 'FastAPI backend for managing events',
      deployOptions: {
        stageName: 'prod',
        throttlingRateLimit: 100,
        throttlingBurstLimit: 200,
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
        metricsEnabled: true,
      },
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: [
          'Content-Type',
          'X-Amz-Date',
          'Authorization',
          'X-Api-Key',
          'X-Amz-Security-Token',
        ],
        allowCredentials: true,
      },
    });

    // Lambda integration
    const lambdaIntegration = new apigateway.LambdaIntegration(apiFunction, {
      proxy: true,
      allowTestInvoke: true,
    });

    // Add root path handler
    api.root.addMethod('ANY', lambdaIntegration);

    // Add proxy resource to handle all paths
    api.root.addProxy({
      defaultIntegration: lambdaIntegration,
      anyMethod: true,
    });

    // Outputs
    new cdk.CfnOutput(this, 'EventsTableName', {
      value: eventsTable.tableName,
      description: 'DynamoDB Events Table Name',
    });

    new cdk.CfnOutput(this, 'EventsTableArn', {
      value: eventsTable.tableArn,
      description: 'DynamoDB Events Table ARN',
    });

    new cdk.CfnOutput(this, 'ApiUrl', {
      value: api.url,
      description: 'API Gateway URL',
      exportName: 'EventsApiUrl',
    });

    new cdk.CfnOutput(this, 'ApiEndpoint', {
      value: `${api.url}events`,
      description: 'Events API Endpoint',
    });

    new cdk.CfnOutput(this, 'ApiDocsUrl', {
      value: `${api.url}docs`,
      description: 'API Documentation (Swagger UI)',
    });

    new cdk.CfnOutput(this, 'LambdaFunctionName', {
      value: apiFunction.functionName,
      description: 'Lambda Function Name',
    });
  }
}
