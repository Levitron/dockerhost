# dockerhost

```ansible-galaxy install -r requirements.yml```

```yaml
# Install a role from the Ansible Galaxy
- src: dfarrell07.opendaylight

# Install a role from GitHub
- name: opendaylight
  src: https://github.com/dfarrell07/ansible-opendaylight

# Install a role from a specific git branch
- name: opendaylight
  src: https://github.com/dfarrell07/ansible-opendaylight
  version: origin/master

# Install a role at a specific tag from GitHub
- name: opendaylight
  src: https://github.com/dfarrell07/ansible-opendaylight
  version: 1.0.0

# Install a role at a specific commit from GitHub
- name: opendaylight
  src: https://github.com/dfarrell07/ansible-opendaylight
  version: <commit hash>
```

# apply

```ansible-playbook dockerhost.yml -i inventory```


# SSL
```bash
# get cert via certbot
certbot-auto certonly --manual -d "*.4jp.de"  --agree-tos \
--no-bootstrap --manual-public-ip-logging-ok --preferred-challenges dns-01 \
-m  j.alten@gmx.de  \
--server https://acme-v02.api.letsencrypt.org/directory
```

```bash
# convert pem from letsencrypt to crt for jwilder nginx
openssl x509 -outform der -in 4jp.de.pem -out 4jp.de.crt
openssl rsa -outform der -in privkey.pem -out 4jp.de.key
```