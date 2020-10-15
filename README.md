# certbot_plugin_netim_unofficial

Netim.com offers domains for cheap but support of letsencrypt ssl certificates for subdomains is a pain. This repository contains a certbot plugin that can automate the ACME dns challenge for letsencrypt wildcard certificates that include all subdomains. However, the proper way of doing things via netim's web service API is only available to business customers. Therefore, this plugin uses a scripted webui client that performs all the steps using http get/post requests. Note, that this is a total hack and might be a bad idea for numerous reasons. There is no guarantee that the webui remains stable and any changes might break things and have undefined and potentially harmful effects. Also there is no such thing as an API key that only has the necessary permissions, instead you need to provide your full webui login and password in plain text that allow full access to everything. So be aware of all this and use at your own risk!

## install:

install letsencrypt certbot

` pip3 install letsencrypt --no-binary :all: `

install certbot netim plugin

```
git clone https://github.com/MalteOeljeklaus/certbot-plugin-netim.git
cd certbot-plugin-netim
pip3 install -e . --no-binary :all:
```

verify that the plugin is installed

` certbot plugins `

create credential file `netim.ini` with the following contents

```
certbot_plugin_netim_unofficial:dns_username=<your username>
certbot_plugin_netim_unofficial:dns_password=<your password>
```

make sure that \_acme-challenge subdomain is registered with netim to create DNS A record (not sure if necessary)

create certificates

` certbot certonly -a certbot-plugin-netim-unofficial:dns --certbot-plugin-netim-unofficial:dns-credentials netim.ini -d <yourdomain> --logs-dir=. --config-dir=. --work-dir=. `