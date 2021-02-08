# Install required Linux packages

```
1. [sudo] pip3 install -r req.txt
```
```
2. [sudo] pip3 install -U awscli
```
# If you have the AWS CLI installed, then you can use it to configure your credentials file:
# Alternatively, you can create the credential file yourself. By default, its location is at ~/.aws/credentials:

example:
```
3. vim .aws/credentials 

[marketing]  => [default]

aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY 
```
```
4. python3 ./our_script.py {link1} {link2} {linkN}
```
