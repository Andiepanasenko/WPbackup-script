pdffiller_dev = [
    'das',
    'dev-as-smtp0',
    'dev-smtp1',
    'dev-smtp2',
    'rabbitmq-dev',
    'dev-zabbix',
    'awseb-e-a2mnycuwda-stack-AWSEBAutoScalingGroup-16XD3NPT1U5A8', #Default-enviroment
    'dev-grafana-docker',
    'monitoring', # Haven't  SSH key `worker-dev`
    'nodepdf-pdfworker-word-1', # Haven't  SSH key `worker-dev`
    'nodepdf-test - pdfworker-word-1', # Haven't  SSH key `worker-dev`
    'qa-dev', # Windows VMs, zabbix-agent setup manually
    'sharepoint', # Windows VM, zabbix-agent setup manually
    'signnow_web_dev', # Haven't  SSH key `deployer-key`
    'websocket-dev',
    'ws2-native',
    'dev-bastion', # Another user with sudo. Manually will be faster
    'marketing-solr-yandex-tank', # Something wrong with host
    'aws-opsworks-cm-instance-Chef-Test',
    'dev-as',
    'dev-ecs-elk-test', # Daimon cluster for destroy
    'dev-grafana2', # Pysarenko cluster in work
    'dev-pmm', # Rogachov cluster for destroy
    'dev-dfs3', # Cluster
    'dev-api2', # Cluster
    'dev-tmp-elcsch', # Cluster
    'dev-to-delete-tmp-test-module', # Cluster
    'dev-airslate', # Cluster
    'dev-mas-elasticsearch', # Cluster
    'dev-jsfiller-trueedit3', # Cluster
    'dev-rabbitmq-js', # Cluster
    'dev-jsfiller-desk5', # Cluster
    'OpenVPN', # test instance
    'dev-grafana5', # Cluster
    'dev-pinba_cluster', # Cluster
    'dev-js-pdas', # Cluster
    'dev-marketing-signnow', # Cluster
    'nodepdf-as-test', # Airslate
    'nodepdf-test - nodepdf-test-web2', # Can't connect

]

pdffiller_prod = [
    'prod-smtp', # Clusters
    'prod-as-terrahost',
    'qa', # Windows machines
    'mail-api-dev', # GO HOME
    'prod-zabbix', # Cluster
    'prod-bastion', # Another user with sudo. Manually will be faster
    'prod-as', # GO HOME
    'dev-pdf', # GO HOME
    'mail-analytic-dev', # GO HOME
    'ws2-dev1', # GO HOME
    'ios-denise', # GO HOME
    'sharepoint', # Windows
    'SQL Server 2014 [sharepoint] prod', # Windows
    'Sharepoint Server 2016  [sharepoint] prod', # Windows
    'message-manager-dev', # GO HOME
    'modx-dev' # GO HOME
    'denise perf', # GO HOME
    'api-dev', # GO HOME
    'ws2-dev', # GO HOME
    'marketing-php7-dev', # GO HOME
    'denise_new dev-pdf', # GO HOME
    'aerospike-dev01', # GO HOME
    'dev-api-docker-instance', # GO HOME
    'blog-dev', # GO HOME
    'tasks - blog', # Very old, have not VPC, ca't work w/ Ansible from bastion
    'ios', # Very old, have not VPC, ca't work w/ Ansible from bastion
    'stats', # Very old, have not VPC, ca't work w/ Ansible from bastion
    'socket-server', # Very old, have not VPC, ca't work w/ Ansible from bastion
    'gitlab', # Very old, have not VPC, ca't work w/ Ansible from bastion
    'pdf-worker-stage-windows', # Windows
    'pdf-worker-windows', # Windows
    'noc zabbix vpc', # ec2-user
    'static', # ec2-user
    'nautilus10', # Can't connect
    'lb-redis', # Can't connect
    'bpm', # Can't connect
    'fillable-vpc hvm', # ubuntu 12
    'pdffillers', # Dev
]

airslate_dev = [
    'dev-', # PDFfiller
    'jsfiller3', # PDFfiller
    'das-smtp', # Cluster
    'api-test-server', # PDFfiller
    'marketing-sas', # PDFfiller
    'jsfocr-dev', # PDFfiller
    'ws-mongo',  # PDFfiller
    'e-file', # PDFfiller
    'forms-processing',
    'das-pinba', # Cluster
    'artifactory',
    'nodepdf-test', # PDFfiller
    'marketing-solr-yandex-tank', # PDFfiller
    'docker-build-server', # PDFfiller
    'korax-chef-test', # PDFfiller
    'salesforce-deploy', # PDFfiller
    'solr-dev', # PDFfiller
    'snfiller', # PDFfiller
    'marketing-sas-sandbox', # PDFfiller
    'flat experiments', # PDFfiller
    'qa', # PDFfiller
    'awseb-e-a2mnycuwda-stack-AWSEBAutoScalingGroup-16XD3NPT1U5A8',
    'aws-opsworks-cm-instance-Chef-Test',
    'OpenVPN',  # PDFfiller
    'test mylo-ref-image', # PDFfiller
    'sharepoint', # PDFfiller
    'websocket-dev', # PDFfiller
    'ws2-native', # PDFfiller
    'nodepdf-pdfworker-word-1', # PDFfiller
    'das-pmm', # Cluster
    'Chef_Test', # PDFfiller
    'monitoring', # PDFfiller
    '172', # PDFfiller
]
