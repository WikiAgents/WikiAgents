#!/bin/bash

python /custom_init/create_webhooks.py
python /custom_init/create_system_user.py
python /custom_init/update_settings.py
python /custom_init/create_system_pages.py