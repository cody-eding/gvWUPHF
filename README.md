# gvWUPHF

A cross-platform alerting API, loosely inspired by [The Office](https://en.wikipedia.org/wiki/WUPHF.com).

## Overview

A simple FastAPI application receives alerts via HTTPS REST API calls. The application stores the alerts in a RabbitMQ message queue and the subsequently processes the alerts to various destinations.

Currently the application supports the following services:

* Email
* Microsoft Teams Chat (via [Incoming Webhook](https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook))
* Zoom Chat (via [Incoming Webhook](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0067640))

## Configuration 

A sample YAML file is provided.

```yaml
# fast api settings
title: FastAPI Alerting Gateway
description: A simple API for receiving alert hooks and sending to various services. Currently supports SMTP, Microsoft Teams chat and Zoom Chat as destinations.
debug_mode: true

# rabbitmq connection
rabbitmq_conn: amqp://guest:guest@localhost/

# smtp settings
smtp_from_address: test@test.com
smtp_server: smtp.test.com
smtp_port: 25

# authorized api key needed for all requests
api_keys: 
  - your_first_api_key
  - your_second_api_key

# zoom app authorization
# zoom_account_id: 
# zoom_client_id:
# zoom_client_secret:

# rabbitmq queues
# this determines what service queued messages are sent to
queues:
  - name: test
    id: 1
    service_ids:
      - 2

# service options
services:
  #- name: test-smtp
  #  id: 1
  #  type: smtp
  #  recipient: recipient@test.com
  #- name: test-zoom
  #  id: 2
  #  type: zoom
  #  recipient: https://integrations.zoom.us/chat/webhooks/incomingwebhook/...
  #  authorization:
  #- name: test-teams
  #  id: 3
  #  type: msteams
  #  recipient: https://tenant.webhook.office.com/webhookb2/...
```

## Running via Docker Compose

The project contains a `docker-compose.yml` definition. Create the `config.yaml` in the root of the project and run `docker compose up` from the docker directory to start the application.