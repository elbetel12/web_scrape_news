
# Telegram Bot for Scarped News

This repository contains the source code for a Telegram bot that automates news and video updates on the Mereja channel. The bot is built using Python and utilizes the Telepot library to interact with the Telegram Bot API.

## Features

- Scrapes news articles from Mereja's website in both English and Amharic languages.
- Fetches videos from Mereja's video section and shares them on the Telegram channel.
- Retrieves the latest forum news from Mereja's forum section and sends them to the channel.
- Implements rate limiting to prevent spamming the channel.

## Requirements

- Python (version 3.6 or higher)
- Telepot library (install using `pip install telepot`)
- BeautifulSoup library (install using `pip install beautifulsoup4`)
- Requests library (install using `pip install requests`)

## How to Use

1. Clone the repository to your local machine.
2. Install the required libraries as mentioned in the Requirements section.
3. Obtain your Telegram Bot API token from [BotFather](https://core.telegram.org/bots#6-botfather) on Telegram.
4. Replace the 'YOUR_API_TOKEN' placeholder in the code with your actual Telegram bot token.
5. Replace the 'YOUR_CHANNEL_ID' placeholder with the ID of your Telegram channel.
6. Run the `main()` function in the code to start the bot.

## Contributions

Contributions to this project are welcome! If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.

## Disclaimer

Please note that web scraping may be subject to website policies and terms of service. Always ensure you have permission to scrape the content from the website you're targeting.

## License

This project is licensed under the [MIT License].

## Acknowledgments

- The code in this repository is inspired by various Telegram bot tutorials and examples available online.
- Special thanks to Mereja.com for providing a valuable news platform and API access.

---
