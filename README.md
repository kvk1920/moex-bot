# moex-bot

## Установка

```shell
sudo apt install python3-rados
sudo pip3 install -R requirements.txt
```

Поднять ceph-кластер при помощи vagrant можно по этой инструкции:
https://github.com/carmstrong/multinode-ceph-vagrant

## Запуск
В корне репозитория:
```shell
export MOEXN_TG_TOKEN=<токен телеграм-бота>
export MOEXN_CEPH_CONF=<путь до ceph.conf>
export MOEXN_CEPH_KEYRING=<путь до ceph.client.admin.keyring>
export MOEXN_CEPH_POOL=<имя пула, использующееся для хранения чатов>
python3 -m bot
```
