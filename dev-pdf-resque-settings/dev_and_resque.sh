#!/bin/bash
# Example usage:
# script.sh DB_NUM DEV_NUM DEV_NUM_STOP
# Where:
# DB_NUM - integer. Redis DB number, which will be use for dev Resques
# DEV_NUM - integer. Create devs/resques/etc from this number (inclusive)
# DEV_NUM_STOP - integer. Create devs/resques/etc to this number (inclusive)
# SERVER_NAME - string. Route53 3 level domain for this server. For example, in 'dev-pdf.pdffiller.com' - 'dev-pdf'

function download_example_files {
        DEV_EXAMPLE_PATH=/mnt/www/devEXAMPLE

        su - developer -c "git clone git@github.com:pdffiller/pdffiller.git ${DEV_EXAMPLE_PATH}"
        su - developer -c "ln -s /var/www/projects ${DEV_EXAMPLE_PATH}/projects"
        su - developer -c "mkdir -p ${DEV_EXAMPLE_PATH}/include"
        su - developer -c "mkdir -p ${DEV_EXAMPLE_PATH}/templates_c"
        su - developer -c "mkdir -p ${DEV_EXAMPLE_PATH}/tmp"
        su - developer -c "mkdir -p ${DEV_EXAMPLE_PATH}/logs"
        su - developer -c "mkdir -p ${DEV_EXAMPLE_PATH}/admin/templates_c"

        su - developer -c "git clone git@github.com:pdffiller/system-utils.git ~/system-utils"

        CONFIG_PATH=/home/developer/system-utils/dev-pdf-resque-settings
        mv ${CONFIG_PATH}/define.php /mnt/www/devEXAMPLE/include/
        mv ${CONFIG_PATH}/php-resque-scheduler.conf.example /etc/supervisor/conf.d/
        mv ${CONFIG_PATH}/resque.conf.example /etc/supervisor/conf.d/
        mv ${CONFIG_PATH}/resque-web.conf.example /etc/supervisor/conf.d/
        mv ${CONFIG_PATH}/resque-web-example/ /opt/node-resque/
        mv ${CONFIG_PATH}/dev.pdffiller.conf.example /etc/nginx/sites-available/
        mv ${CONFIG_PATH}/server.pdffiller.conf.example /etc/nginx/sites-available/
        rm -rf /home/developer/system-utils/
        echo
}


function update_configs {
        DEV_PATH=/mnt/www/devEXAMPLE
        su - developer -c "cd ${DEV_PATH}; git pull; composer install"
        su - developer -c "cd ${DEV_PATH}/angular; npm i; gulp production"
        echo "Compress JS & CSS"
        su - developer -c "cd ${DEV_PATH}/compress/css/; php update.php"
        echo
        su - developer -c "cd ${DEV_PATH}/compress/js/; php update.php"
        echo
}

function create_dev {
        ## Params start ##
        DEV_NUM=$1
        ### Params end ###

        # Original script: vi /etc/nginx/sites-available/gen.sh
        DEV_PATH=/mnt/www/dev${DEV_NUM}
        su - developer -c "cp -R /mnt/www/devEXAMPLE ${DEV_PATH}"

        su - developer -c "mkdir -p ${DEV_PATH}/templates_c"
        su - developer -c "mkdir -p ${DEV_PATH}/tmp"
        su - developer -c "mkdir -p ${DEV_PATH}/logs"
        su - developer -c "mkdir -p ${DEV_PATH}/admin/templates_c"
}

function create_resque_settings {
        ## Params start ##
        DB_NUM=$1
        DEV_NUM=$2
        ### Params end ###

        SUPERVISOR_PATH=/etc/supervisor/conf.d
        sed s/DEV_NUM/${DEV_NUM}/g ${SUPERVISOR_PATH}/resque.conf.example > ${SUPERVISOR_PATH}/resque_${DEV_NUM}.conf
        sed -i s/DB_NUM/${DB_NUM}/g ${SUPERVISOR_PATH}/resque_${DEV_NUM}.conf

        # Change PHP settings for Resque
        sed -i s/DEV_NUM/${DEV_NUM}/g  /mnt/www/dev${DEV_NUM}/include/define.php
        sed -i s/DB_NUM/${DB_NUM}/g /mnt/www/dev${DEV_NUM}/include/define.php
}

function create_resque_scheduler_settings {
        ## Params start ##
        DB_NUM=$1
        DEV_NUM=$2
        ### Params end ###

        SUPERVISOR_PATH=/etc/supervisor/conf.d
        sed s/DEV_NUM/${DEV_NUM}/g ${SUPERVISOR_PATH}/php-resque-scheduler.conf.example > ${SUPERVISOR_PATH}/php-resque-scheduler_${DEV_NUM}.conf
        sed -i s/DB_NUM/${DB_NUM}/g ${SUPERVISOR_PATH}/php-resque-scheduler_${DEV_NUM}.conf
}

function create_resque_web_settings {
        ## Params start ##
        DB_NUM=$1
        DEV_NUM=$2
        ### Params end ###

        SUPERVISOR_PATH=/etc/supervisor/conf.d
        sed s/DEV_NUM/${DEV_NUM}/g ${SUPERVISOR_PATH}/resque-web.conf.example > ${SUPERVISOR_PATH}/resque-web-${DEV_NUM}.conf

        NODE_RESQUE_PATH=/opt/node-resque
        cp -r ${NODE_RESQUE_PATH}/resque-web-example ${NODE_RESQUE_PATH}/resque-web-${DEV_NUM}
        sed -i s/DB_NUM/${DB_NUM}/g ${NODE_RESQUE_PATH}/resque-web-${DEV_NUM}/config.ru
        sed -i s/DEV_NUM/${DEV_NUM}/g ${NODE_RESQUE_PATH}/resque-web-${DEV_NUM}/config.ru

        # Create nginx configs
        NGINX_PATH=/etc/nginx/sites-available
        cp ${NGINX_PATH}/dev.pdffiller.conf.example ${NGINX_PATH}/dev${DEV_NUM}.pdffiller.conf
        sed -i s/DEV_NUM/${DEV_NUM}/g ${NGINX_PATH}/dev${DEV_NUM}.pdffiller.conf
        # Activate configuration
        ln -s ${NGINX_PATH}/dev${DEV_NUM}.pdffiller.conf /etc/nginx/sites-enabled/dev${DEV_NUM}.pdffiller.conf
}

function remove_example_configs {
        rm -rf /mnt/www/devEXAMPLE
        rm -rf /etc/supervisor/conf.d/php-resque-scheduler.conf.example
        rm -rf /etc/supervisor/conf.d/resque.conf.example
        rm -rf /etc/supervisor/conf.d/resque-web.conf.example
        rm -rf /opt/node-resque/resque-web-example/
        rm -rf /etc/nginx/sites-available/dev.pdffiller.conf.example
        rm -rf /etc/nginx/sites-available/server.pdffiller.conf.example

}


function change_host_name {
        ## Params start ##
        SERVER_NAME=$1
        ### Params end ###

        echo ${SERVER_NAME} > /etc/hostname
        echo "127.0.0.1 ${SERVER_NAME}" >> /etc/hosts
        hostname ${SERVER_NAME}
}



function generate_resque_hide_locations {
        ## Params start ##
        SERVER_NAME=$1
        ### Params end ###

        HIDE_VHOST=/etc/nginx/sites-available/resque-hide-locations.conf

        cat << HEREDOC > ${HIDE_VHOST}
server {
        listen 127.0.0.1:4181;

        # Resque list
        location /resque-login {
                alias /mnt/www/resque-login;
                index resque-login.html;
        }

HEREDOC

        for I in $(ls -la /etc/supervisor/conf.d | egrep -o 'resque-web-[0-9]+' | egrep -o '[0-9]+'); do
                echo "
        # Resque web interface
        location /${I}/resque {
                proxy_set_header  X-Real-IP        \$remote_addr;
                proxy_set_header  X-Forwarded-For  \$proxy_add_x_forwarded_for;
                proxy_set_header  Host             \$http_host;
                proxy_redirect    off;
                proxy_pass        http://localhost:39${I};
        }

        location ~* ^/${I}/resque/(.+\.(jpg|jpeg|gif|css|png|js|ico|html|xml|txt))$ {
                proxy_pass http://localhost:39${I};
        }" >> ${HIDE_VHOST}
        done

        echo '}' >> ${HIDE_VHOST}

        # Activate configuration
        ln -s ${HIDE_VHOST} /etc/nginx/sites-enabled/resque-hide-locations.conf
}

function generate_resque_login_page {
        ## Params start ##
        SERVER_NAME=$1
        ### Params end ###

        test -d /mnt/www/resque-login/ || mkdir /mnt/www/resque-login/
        LOGIN_PAGE_PATH=/mnt/www/resque-login/resque-login.html

        cat << HEREDOC > ${LOGIN_PAGE_PATH}
<html>
    <style>
        * {margin: 0; padding: 0;}

        h3 {
            font: bold 25px/1.5 Helvetica, Verdana, sans-serif;
        }

        li {
            padding: 10px;
            overflow: auto;
            float: left;
            margin: 10px;
            height: 40px;
        }

        li p {
            font: 200 14px/1.5 Georgia, Times New Roman, serif;
        }

        li:hover {
            background: #eee;
            cursor: pointer;  
        }

        a {
            color: black;
            text-decoration: none;
        }
    </style>
    <div>
        <ul>
HEREDOC

        for I in $(ls -la /etc/supervisor/conf.d | egrep -o 'resque-web-[0-9]+' | egrep -o '[0-9]+'); do
                echo "            <a href=\"https://${SERVER_NAME}.pdffiller.com/${I}/resque\">"\
                     "<li><h3>Resque ${I}</h3></li></a>" >> ${LOGIN_PAGE_PATH}
        done

        cat << HEREDOC >> ${LOGIN_PAGE_PATH}
        </ul>
    </div>
</html>
HEREDOC

}

function create_server_oauth_settings {
        ## Params start ##
        SERVER_NAME=$1
        ### Params end ###

        # Create nginx configs
        NGINX_PATH=/etc/nginx/sites-available
        cp ${NGINX_PATH}/server.pdffiller.conf.example ${NGINX_PATH}/${SERVER_NAME}.pdffiller.conf
        sed -i s/SERVER_NAME/${SERVER_NAME}/g ${NGINX_PATH}/${SERVER_NAME}.pdffiller.conf
        # Activate configuration
        ln -s ${NGINX_PATH}/${SERVER_NAME}.pdffiller.conf /etc/nginx/sites-enabled/${SERVER_NAME}.pdffiller.conf
}

function route53_reminder {
        ## Params start ##
        DEV_NUM=$1
        DEV_NUM_STOP=$2
        ### Params end ###

        echo -e "\n\e[43m\e[30m\n\n== == == == == == == == == == DON'T FORGET!!! == == == == == == == == == == ==\n"
        echo "Go to https://console.aws.amazon.com/route53 аnd add/remove next domains:"
        I=${DEV_NUM}
        while [ "${I}" -le "${DEV_NUM_STOP}" ]
        do
                echo "  dev${I}.pdffiller.com"

                I=$(( ${I} + 1 ))
        done
        echo -e "\n== == == == == == == == == == == == == == == == == == == == == == == == == ==\n\e[39m\e[49m\n"
}

function remove_resque_scheduler_settings {
        ## Params start ##
        DEV_NUM=$1
        ### Params end ###

        rm -rf /etc/supervisor/conf.d/php-resque-scheduler_${DEV_NUM}.conf
        rm -rf /var/log/supervisor/resque_scheduler${DEV_NUM}_*
}

function remove_resque_web_settings {
        ## Params start ##
        DEV_NUM=$1
        ### Params end ###

        rm -rf /etc/nginx/sites-enabled/dev${DEV_NUM}.pdffiller.conf
        rm -rf /etc/nginx/sites-available/dev${DEV_NUM}.pdffiller.conf
        rm -rf /opt/node-resque/resque-web-${DEV_NUM}
        rm -rf /etc/supervisor/conf.d/resque-web-${DEV_NUM}.conf
        rm -rf /var/log/supervisor/resque_web${DEV_NUM}.log*
}

function remove_resque_settings {
        ## Params start ##
        DEV_NUM=$1
        ### Params end ###

        rm -rf /etc/supervisor/conf.d/resque_${DEV_NUM}.conf
        rm -rf /var/log/supervisor/resque${DEV_NUM}_*
}

function remove_dev {
        ## Params start ##
        DEV_NUM=$1
        ### Params end ###

        rm -rf /mnt/www/dev${DEV_NUM}
}

function restart_supervisor_and_check_nginx {
        /etc/init.d/supervisor stop
        until /etc/init.d/supervisor status | grep -o "not running"; do
                sleep 1
        done
        /etc/init.d/supervisor start
        echo -e "\e[44m\n"
        nginx -t
        echo -e "IF ALL OK - run 'service nginx reload'\n\e[49m" 
}

DB_NUM=$1
DEV_NUM=$2
DEV_NUM_STOP=$3
SERVER_NAME=$4

if [ $(whoami) != root ]; then
        echo -e "\e[41m\n\nLogin as user 'root', and repeat again\n\e[49m"
        exit 1
fi

if [ "$4" == "" ]; then
        echo -e "\e[96m\e[40m\n"
        echo "Example usage:"
        echo "./dev_and_resque.sh DB_NUM DEV_NUM DEV_NUM_STOP SERVER_NAME"
        echo "./dev_and_resque.sh 200 200 210"
        echo -e "\nWhere:"
        echo "DB_NUM       - integer.  Redis DB number, which will be use for dev Resques"
        echo "DEV_NUM      - integer.  Create/Remove devs/resques from this number (inclusive)"
        echo "DEV_NUM_STOP - integer.  Create/Remove devs/resques  to  this number (inclusive)"
        echo "SERVER_NAME  - string.   Route53 3 level domain for this server. For example, in 'dev-pdf.pdffiller.com' - 'dev-pdf'"
        echo -e "\e[39m\e[49m"

        exit 1
fi

download_example_files
update_configs

I=${DEV_NUM}
while [ ${I} -le ${DEV_NUM_STOP} ]
do
        echo "dev${I} start at $(date)"
#        $(remove_resque_scheduler_settings ${I})
#        $(remove_resque_web_settings ${I})
#        $(remove_resque_settings ${I})
#        $(remove_dev ${I})

        $(create_dev ${I})
        $(create_resque_settings ${DB_NUM} ${I})
        $(create_resque_scheduler_settings ${DB_NUM} ${I})
        $(create_resque_web_settings ${DB_NUM} ${I})

        I=$(( ${I} + 1 ))
done

change_host_name ${SERVER_NAME}
generate_resque_hide_locations ${SERVER_NAME}
generate_resque_login_page ${SERVER_NAME}
create_server_oauth_settings ${SERVER_NAME}

remove_example_configs

route53_reminder ${DEV_NUM} ${DEV_NUM_STOP}
restart_supervisor_and_check_nginx
