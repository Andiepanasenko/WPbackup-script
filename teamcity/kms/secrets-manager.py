import os
import base64
import boto3


def encrypt(key, secret):
    """
    Encrypt secret with AWS KWS master key
    :param key: key to use for encryption
    :param secret: string to encrypt
    :return: base64 encoded hash string
    """
    secret_hash_bytes = client.encrypt(
        KeyId=key,
        Plaintext=secret.encode('utf-8')
    )['CiphertextBlob']
    secret_hash_base64_bytes = base64.standard_b64encode(secret_hash_bytes)

    return str(secret_hash_base64_bytes, 'utf-8').replace('\n', '').strip()


def decrypt(secret_hash):
    """
    Decrypt secret with AWS KWS master key
    :param secret_hash: base64 encoded hash string to decrypt
    :return: decoded secret string
    """
    secret_hash_bytes = base64.standard_b64decode(secret_hash)
    secret_plaintext = client.decrypt(
        CiphertextBlob=secret_hash_bytes
    )['Plaintext']
    return str(secret_plaintext, 'utf-8')


if __name__ == "__main__":
    #
    # Set global vars
    #

    # AWS credentials
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    # AWS REGION to be used for script run -- us-east-1
    AWS_REGION = os.environ['AWS_REGION']
    # Encode secret string or Decode secret hash -- encrypt|decrypt
    OPERATION = os.environ['OPERATION']
    # AWS KMS key name alias to be used for encryption -- alias/dev-master-key
    KEY_NAME = os.environ['KEY_NAME']
    # Secret to encode or Hash to decode -- mySecretPass|AQIC4...jAChK
    SECRET = os.environ['SECRET']

    #
    # Return encoded secret
    #

    client = boto3.client('kms', region_name=AWS_REGION)
    if OPERATION == 'encrypt':
        print(encrypt(KEY_NAME, SECRET))
    elif OPERATION == 'decrypt':
        print(decrypt(SECRET))
    else:
        print('Operation is incorrect')

