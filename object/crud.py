from urllib.request import urlopen
import io
import logging
from hashlib import md5
from time import localtime
from botocore.exceptions import ClientError

def get_objects(aws_s3_client, bucket_name) -> str:
  for key in aws_s3_client.list_objects(Bucket=bucket_name)['Contents']:
    print(f" {key['Key']}, size: {key['Size']}")


def download_file_and_upload_to_s3(aws_s3_client,
                                   bucket_name,
                                   url,
                                   keep_local=False) -> str:
  file_name = f'image_file_{md5(str(localtime()).encode("utf-8")).hexdigest()}.jpg'
  with urlopen(url) as response:
    content = response.read()
    aws_s3_client.upload_fileobj(Fileobj=io.BytesIO(content),
                                 Bucket=bucket_name,
                                 ExtraArgs={'ContentType': 'image/jpg'},
                                 Key=file_name)
  if keep_local:
    with open(file_name, mode='wb') as jpg_file:
      jpg_file.write(content)

  # public URL
  return "https://s3-{0}.amazonaws.com/{1}/{2}".format('us-west-2',
                                                       bucket_name, file_name)


def upload_file(aws_s3_client, filename, bucket_name):
  response = aws_s3_client.upload_file(filename, bucket_name, "hello.txt")
  status_code = response["ResponseMetadata"]["HTTPStatusCode"]
  if status_code == 200:
    return True
  return False


def upload_file_obj(aws_s3_client, filename, bucket_name):
  with open(filename, "rb") as file:
    aws_s3_client.upload_fileobj(file, bucket_name, "hello_obj.txt")


def upload_file_put(aws_s3_client, filename, bucket_name):
  with open(filename, "rb") as file:
    aws_s3_client.put_object(Bucket=bucket_name,
                             Key="hello_put.txt",
                             Body=file.read())


def delete_file_from_s3(aws_s3_client, file_name, bucket_name):
    try:

      object = aws_s3_client.get_object(Bucket=bucket_name, Key=file_name)
      if object["Body"] is not None:

        response = aws_s3_client.delete_object(Bucket=bucket_name, Key=file_name)
        print(response)
        print(f'The file {file_name} has been deleted from the bucket {bucket_name}.')

    except ClientError as e:
        logging.error(e)
        return False
    return True
