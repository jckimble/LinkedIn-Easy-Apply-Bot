LinkedIn Easy Apply Bot
=====

A bot for LinkedIn Easy Apply. Made for spite cause a recruter didn't think I had enough experience with python and selenium.

## Install

```sh
git clone https://github.com/jckimble/LinkedIn-Easy-Apply-Bot.git
cd LinkedIn-Easy-Apply-Bot
pip install -r requirements.txt
```

## Options

Options can be set by command arguments, environment variables, or a json config file

| Option            | Description 	        | Default       | JSON Field      	| Environment Variable 	  | Cli Option     	              |
|-----------------	|---------------------	|-------------- |-----------------	|-----------------------	|-----------------------------  |
| config            | JSON Config File      | ./config.json |                   |                      	  | --config CONFIG               |
| headless          | Run Headless          | False         | headless          | CI                   	  | --headless   	                |
| email             | LinkedIn Email        | None          | email             | LEAB_EMAIL              | --email EMAIL                 |
| password          | LinkedIn Password     | None          | password          | LEAB_PASSWORD           | --password PASSWORD           |
| code              | 2fa Code              | None          | code              | LEAB_CODE               | --code CODE                   |
| secret            | 2fa Secret            | None          | secret            | LEAB_SECRET             | --secret SECRET               |
| logging           | Logging Level         | WARN          | logging           | LEAB_LOGGING            | --logging LOGGING             |
| user_data         | Selenium User Data    | None          | user_data         | LEAB_USER_DATA          | --user-data USERDATA          |
| wait_time         | Wait Time for Element | 30 (Seconds)  | wait_time         | LEAB_WAIT_TIME          | --wait-time WAITTIME          |
| max_hours         | Max Time for Search   | 2 (Hours)     | max_hours         | LEAB_MAX_HOURS          | --max-hours MAXHOURS          |
| max_failed        | Failed Apps to Quit   | 20            | max_failed        | LEAB_MAX_FAILED         | --max-failed MAXFAILED        |
| timeout           | Apply Timeout         | 5 (Minutes)   | timeout           | LEAB_TIMEOUT            | --timeout TIMEOUT             |
| search_query      | Search Query          | None          | search_query      | LEAB_SEARCH_QUERY       | --search_query SEARCHQUERY    |
| blacklist.company | Company Blacklist     | None          | blacklist.company | LEAB_BLACKLIST_COMPANY  | --blacklist-company BLACKLIST |
| blacklist.title   | Title Blacklist       | None          | blacklist.title   | LEAB_BLACKLIST_TITLE    | --blacklist-title BLACKLIST   |

## Usage

Below is a simple example of how to use.

```sh
python ./main.py
```

## Contributions

Contributions are always welcome!

## Donations

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/jckimble)

## License
LinkedIn-Easy-Apply-Bot is available under the MIT license
Copyright (c) 2023 James C Kimble
