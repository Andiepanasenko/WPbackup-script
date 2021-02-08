
**Mandatory variables**

* host
* s3_file_name
* aws_profile=dev
* GITHUB_USER
* GITHUB_TOKEN

**Installation to remote host**

* install with build modules
```
ansible-playbook php71-install.yml -i ../hosts -e "host=web02 s3_file_name=web-php71-artifacts.tgz aws_profile=dev GITHUB_USER=SKozlovsky GITHUB_TOKEN=66189884fd78239d5olololsometocken"
```
* install without bild (get artifacts from s3)

```
ansible-playbook php71-install.yml -i ../hosts -e "host=web02 s3_file_name=web-php71-artifacts.tgz aws_profile=dev GITHUB_USER=SKozlovsky GITHUB_TOKEN=66189884fd78239d5olololsometocken" --skip-tags "build_php_modules"
```
* only packages install
```
ansible-playbook php71-install.yml -i ../hosts -e "host=prod-web-servers " --tags "packages"
```