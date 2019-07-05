# ses-forwarder

SESで受信したメールを転送する簡易サービス

### 前提

- SESで受信用のドメインの登録がされていること
- SESで転送用の送信元および受信先のメールアドレスの承認が済んでいること

### サービス構成

### デプロイ

- `<your domain>` 宛のメールを `<your forwarding address>` へ転送
  - 例の場合 `mail.example.com` ドメインのメールを受信・転送
  - 転送先は `ot-nemoto@mail.sample.com` になる
  - 転送先は事前に SESの Identity Management > Email Addresses で Verification Status を verified にしておく
  - またドメイン(`mail.example.com`)も SESの Identiry Management > Domains で Verification Status を verified にしておく

```sh
make deplwy domain=<your domain> \
            forwarding_address=<your forwarding address>

# e.g.
# make deplwy domain=mail.example.com \
#             forwarding_address=ot-nemoto@mail.sample.com
```

- 転送時のFromアドレス(`your forwarder`)を指定する場合
  - 例の場合 `ot-nemoto@mail.sample.com` が転送者となる
  - 指定しない場合は `ses@<your domain>` が転送者
  - 転送アドレスを指定する場合、SESの Identity Management > Email Addresses で Verification Status を verified にしておく
  - 転送アドレスのドメインが `<your domain>` であれば、Identity Management > Email Addresses への登録は不要

```sh
make deplwy domain=<your domain> \
            forwarding_address=<your forwarding address> \
            forwarder=<your forwarder>

# e.g.
# make deplwy domain=mail.example.com \
#             forwarding_address=ot-nemoto@mail.sample.com \
#             forwarder=forwarder@mail.forwarder.com
```

- 特定の宛先のみ受信・転送を許可する場合
  - 例の場合 `ot-nemoto@mail.example.com` のみ受信・転送を許可
  - 許可されないメールアドレスはバウンスされる

```sh
make deplwy domain=<your domain> \
            source_user=<your source name> \
            forwarding_address=<your forwarding address> \
            forwarder=<your forwarder>

# e.g.
# make deplwy domain=mail.example.com \
#             source_user=ot-nemoto \
#             forwarding_address=ot-nemoto@mail.sample.com \
#             forwarder=forwarder@mail.forwarder.com
```

### アンデプロイ

```sh
make delete
```
