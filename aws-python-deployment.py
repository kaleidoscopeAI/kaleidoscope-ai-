import boto3
import os
import zipfile
import subprocess
import json
from pathlib import Path

def package_dependencies():
    """Package Python dependencies for Lambda."""
    # Create a directory for dependencies
    if not os.path.exists('package'):
        os.makedirs('package')
    
    # Install requirements to package directory
    subprocess.check_call([
        'pip', 'install',
        '-r', 'requirements.txt',
        '-t', 'package/'
    ])
    
    # Add your Python script to package
    subprocess.check_call([
        'cp', 'your_script.py', 
        'package/'
    ])
    
    # Create deployment package
    with zipfile.ZipFile('deployment.zip', 'w') as zf:
        for root, _, files in os.walk('package'):
            for file in files:
                full_path = os.path.join(root, file)
                archive_path = os.path.relpath(full_path, 'package')
                zf.write(full_path, archive_path)

def create_lambda_function():
    """Create or update Lambda function."""
    lambda_client = boto3.client('lambda')
    
    try:
        # Read deployment package
        with open('deployment.zip', 'rb') as f:
            deployment_package = f.read()
        
        try:
            # Try to update existing function
            lambda_client.update_function_code(
                FunctionName='YourAIFunction',
                ZipFile=deployment_package
            )
            print("Updated existing Lambda function")
            
        except lambda_client.exceptions.ResourceNotFoundException:
            # Create new function if it doesn't exist
            lambda_client.create_function(
                FunctionName='YourAIFunction',
                Runtime='python3.9',
                Role='YOUR_LAMBDA_ROLE_ARN',  # Replace with your role ARN
                Handler='your_script.handler',
                Code={'ZipFile': deployment_package},
                Timeout=300,  # 5 minutes
                MemorySize=2048  # 2GB memory
            )
            print("Created new Lambda function")
            
    except Exception as e:
        print(f"Error deploying Lambda: {str(e)}")
        raise

# Example Lambda handler function (your_script.py)
def example_script():
    """Example Lambda function."""
    def handler(event, context):
        try:
            # Get input from event
            input_data = json.loads(event['body'])
            
            # Your AI processing here
            result = process_data(input_data)
            
            # Return result
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'result': result
                })
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': str(e)
                })
            }

def main():
    """Main deployment script."""
    # Create requirements.txt if not exists
    if not os.path.exists('requirements.txt'):
        print("Creating requirements.txt")
        with open('requirements.txt', 'w') as f:
            f.write('\n'.join([
                'numpy',
                'scipy',
                'scikit-learn',
                # Add other dependencies
            ]))
    
    # Package dependencies
    print("Packaging dependencies...")
    package_dependencies()
    
    # Deploy Lambda function
    print("Deploying to Lambda...")
    create_lambda_function()
    
    print("Deployment complete!")

if __name__ == "__main__":
    main()