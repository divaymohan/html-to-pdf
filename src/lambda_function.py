import pdfkit
import boto3 as boto
from jinja2 import Environment

s3 = boto.client('s3')
env = Environment()

def getTemplateFromS3(bucket_name, template):
    # Get the S3 bucket and file name from the event
    s3_response = s3.get_object(Bucket=bucket_name, Key=template)
    html_content = s3_response['Body'].read().decode('utf-8')
    return html_content

def putPdfToS3(bucket_name, file_name, pdf_content):
    # Put file to s3 bucket
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=pdf_content)

def get_s3_object_url(bucket_name, object_key):
    object_url = f"https://{bucket_name}.s3.{s3.meta.region_name}.amazonaws.com/{object_key}"
    return object_url

def lambda_handler(event, context):
    path = "/opt/bin/wkhtmltopdf"
    pdf_path = event['pdf_path']
    template_bucket_name = event["template_bucket_name"]
    template_path = event["template_path"]
    asset_bucket_name = event["asset_bucket_name"]
   
    template = getTemplateFromS3(bucket_name = template_bucket_name, template=template_path)
    template_string = env.from_string(template)
    template_vars = event["data"]
        
    html_string = template_string.render(template_vars)
    config = pdfkit.configuration(wkhtmltopdf=path)

    options = {
        'page-size': 'A4',
        "enable-local-file-access": "",
        'encoding': "UTF-8",
    }

    pdf = pdfkit.from_string(html_string, False, configuration=config, options = options)
    putPdfToS3(bucket_name=asset_bucket_name, file_name=pdf_path, pdf_content=pdf)

    return get_s3_object_url(asset_bucket_name, pdf_path)
    
   
    

