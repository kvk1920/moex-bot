# moex-bot

## Описание
Телеграм-бот, который умеет сообщать пользователю об изменении цены какой-либо акции на МосБирже.
Пользователь может:
1. Начать следить за ростом/падением цены такой-то акции: бот будет сообщать каждый раз, когда цена выросла более чем на delta (задаётся пользавтелем).
2. Прекратить следить за ростом/падением.
3. Увидеть список того, за чем он следит.

Все данные персистентно хранятся в CEPH, между перезапусками бота пользовательские данные не теряются.

## Стек
python3, telegram api, moex api, ceph

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
