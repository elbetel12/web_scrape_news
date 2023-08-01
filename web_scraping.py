import os
import time

import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup
import requests
from requests.exceptions import Timeout

# Replace 'YOUR_API_TOKEN' with your actual Telegram bot token
API_TOKEN = '6341741783:AAFrnJGeFji93D7FWpwdCTSLMNblQjN5lPk'

# Replace 'YOUR_CHANNEL_ID' with the ID of your Telegram channel (can be found in the channel's URL)
CHANNEL_ID = '-1001924184640'
# Set the maximum number of retries
max_retries = 3

for retry in range(max_retries):
    try:
        url1 = 'https://mereja.com/tv/'

        response = requests.get(url1, timeout=10)  # You can adjust the timeout value as needed
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        html_content = response.text
        break  # Exit the loop if the request is successful
    except (Timeout, requests.RequestException) as e:
        print(f"Request failed: {e}")
        if retry < max_retries - 1:
            print(f"Retrying... (Attempt {retry + 1})")
        else:
            print("Max retries exceeded. Exiting...")
            exit()


def rate_limited(max_per_second):
    min_interval = 1.0 / float(max_per_second)

    def decorate(func):
        last_time_called = [0.0]

        def rate_limited_function(*args, **kwargs):
            elapsed = time.perf_counter() - last_time_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_time_called[0] = time.perf_counter()
            return ret

        return rate_limited_function

    return decorate


# Apply rate limiting of 1 message per second to the send_message_to_channel function
rate_limited(1)

last_message_time = 0


# Add rate limiting to the send_message_to_channel function
def send_message_to_channel(bot, message, buttons=None):
    global last_message_time

    # Calculate the time elapsed since the last sent message
    elapsed_time = time.time() - last_message_time

    # If the elapsed time is less than 1 second, wait before sending the next message
    if elapsed_time < 1:
        time.sleep(1 - elapsed_time)

    # If buttons are provided, create an InlineKeyboardMarkup
    reply_markup = None
    if buttons:
        reply_markup = buttons

    try:
        # Split the message into smaller chunks
        message_chunks = [message[i:i + 4096] for i in range(0, len(message), 4096)]

        # Send each chunk as a separate message
        for chunk in message_chunks:
            bot.sendMessage(CHANNEL_ID, chunk, reply_markup=reply_markup)

            # Update the last message time
            last_message_time = time.time()
    except telepot.exception.TelegramError as e:
        print(f"Error sending message: {e}")


def handle_callback(msg, bot):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    # Respond differently based on the button selected
    if query_data == 'button_1':
        bot.answerCallbackQuery(query_id, text="You clicked Button 1!")
        # Call the function to scrape English news and send the results to the channel
        english_articles_data = english_scrape_news(bot)
        send_english_news_to_channel(bot, english_articles_data)
    elif query_data == 'button_2':
        bot.answerCallbackQuery(query_id, text="You clicked Button 2!")
        # Call the function to scrape Amharic news and send the results to the channel
        amharic_articles_data = amharic_scrape_news(bot)
        send_amharic_news_to_channel(bot, amharic_articles_data)
    elif query_data == 'button_3':
        bot.answerCallbackQuery(query_id, text="You clicked Button 3!")
        forum_news = scrape_forum_news(bot)
        send_forum_news_to_channel(bot, forum_news)

    elif query_data == 'button_4':
        bot.answerCallbackQuery(query_id, text="You clicked Button 4!")
        videos_data = scrape_mereja_videos(bot)
        send_videos_to_channel(bot, videos_data)


def send_photo_to_channel(bot, photo_url, caption=None, buttons=None):
    # If buttons are provided, create an InlineKeyboardMarkup
    reply_markup = None
    if buttons:
        reply_markup = buttons

    try:
        # Download the photo from the URL
        response = requests.get(photo_url)
        if response.status_code == 200:
            # Save the photo to a temporary file
            with open('temp_photo.jpg', 'wb') as f:
                f.write(response.content)

            # Send the photo as a photo message
            with open('temp_photo.jpg', 'rb') as f:
                bot.sendPhoto(CHANNEL_ID, f, caption=caption, reply_markup=reply_markup)

            # Delete the temporary file
            os.remove('temp_photo.jpg')

        else:
            print(f"Failed to download photo: {photo_url}")

    except telepot.exception.TelegramError as e:
        print(f"Error sending photo: {e}")


def send_english_news_to_channel(bot, articl_data):
    try:
        # Send each article's information along with its image to the channel
        for article_data in articl_data:
            images_url = article_data['image_url']
            title = article_data['title']
            published_date = article_data['published_date']
            link_element = article_data['link_element']

            # Prepare the caption for the photo message
            caption = f"Title: {title}\nPublished Date: {published_date}\nnews_detail: {link_element}\n"

            # Send the image URL along with the title and published date
            send_photo_to_channel(bot, images_url, caption=caption)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")


def send_videos_to_channel(bot, artcles_data):
    try:
        # Send each article's information to the channel
        for article_data in artcles_data:
            title = article_data['title']
            link = article_data['link']

            # Prepare the caption for the message
            caption = f"{link} \nTitle: {title}\n"

            # For videos scraped data, send the caption only
            send_message_to_channel(bot, caption)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")


def send_forum_news_to_channel(bot, articls_data):
    try:
        # Send each article's information to the channel
        for articlss_data in articls_data:
            title = articlss_data['title']
            authors = articlss_data['authors']
            published_date = articlss_data['published_date']
            link_element = articlss_data['link_element']

            # Prepare the caption for the message
            caption = f"Title: {title}\nAuthor: {authors}\n Published Date: {published_date}\nnews_detail: {link_element}\n"

            # For forum scraped data, send the caption only
            send_message_to_channel(bot, caption)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")


def send_amharic_news_to_channel(bot, artcles_data):
    try:
        # Send each article's information to the channel
        for articless_data in artcles_data:
            title = articless_data['title']
            published_date = articless_data['published_date']
            link_element = articless_data['link_element']

            # Prepare the caption for the message
            caption = f"Title: {title}\nPublished Date: {published_date}\nnews_detail: {link_element}\n"

            # For Amharic scraped data, send the caption only
            send_message_to_channel(bot, caption)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")


def amharic_scrape_news(bot):
    titles = []
    dates = []
    links = []

    url = 'https://mereja.com/amharic/v2/'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.3'}
    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            news = soup.find_all('div', class_='grid col-940')

            for topic in news:

                topics_title = topic.find_all('h1', class_='entry-title post-title')
                for title_tag in topics_title:
                    topic_title = title_tag.text.replace(' ', ' ')
                    titles.append(topic_title)

                published_dates = topic.find_all('div', class_='post-meta')
                for date_tag in published_dates:
                    published_date = date_tag.text.replace(' ', ' ').strip()
                    dates.append(published_date)

                links_found = topic.find_all('a')
                for link in links_found:
                    href = link.get('href')
                    links.append(href)

        # Prepare the message to send to the channel
        articles_datas = []
        for title, link, date in zip(titles, links, dates):
            article_data = {
                'title': title,
                'link_element': link,
                'published_date': date,
            }
            articles_datas.append(article_data)

        # Call the function to send news to the channel
        send_amharic_news_to_channel(bot, articles_datas)
        return articles_datas

    except requests.Timeout:
        print("Timeout occurred. Retrying in 60 seconds...")
        time.sleep(60)
        amharic_scrape_news(bot)
    except requests.RequestException as e:
        print(f"Error: {e}")
    except telepot.exception.TelegramError as e:
        print(f"Telegram API Error: {e}")


def english_scrape_news(bot):
    global articles_data
    url = 'https://mereja.com/index/'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.3'}
    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            news = soup.find_all('div', class_='content-area')

            # Lists to store image URLs and titles
            image_urls = []
            topic_titles = []
            time_published = []
            article_url = []

            for topic in news:
                img_tags = topic.find_all('img')
                for img_tag in img_tags:
                    image_url = img_tag['src']
                    image_urls.append(image_url)

                title_tags = topic.find_all('h1', class_='entry-title')
                for title_tag in title_tags:
                    topic_title = title_tag.text.replace(' ', ' ')
                    topic_titles.append(topic_title)

                time_tags = topic.find_all('div', class_='entry-meta')
                for time_tag in time_tags:
                    for span_tag in time_tag.find_all('span'):
                        span_tag.decompose()

                    anchor_texts = [anchor.text.strip() for anchor in time_tag.find_all('a') if
                                    not anchor.find('span')]
                    text_to_display = '\n'.join(anchor_texts)

                    time_published.append(text_to_display)

                url_tags = topic.find_all('a', class_='post-thumbnail')
                for url_tag in url_tags:
                    link = url_tag['href']
                    article_url.append(link)

                    # Prepare the message to send to the channel
                    articles_data = []
                for image_url, topic_title, text_to_display, link in zip(image_urls, topic_titles, time_published,
                                                                         article_url):
                    article_data = {
                        'image_url': image_url,
                        'title': topic_title,
                        'published_date': text_to_display,
                        'link_element': link
                    }
                    articles_data.append(article_data)

                # Call the function to send news to the channel
                send_english_news_to_channel(bot, articles_data)
        return articles_data

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")


def scrape_mereja_videos(bot):
    titles = []

    links = []

    url = 'https://mereja.com/tv/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.3'}

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            div_element = soup.find_all("li", class_="col-xs-6 col-sm-6 col-md-4")

            for videos in div_element:

                all_anchor_tags = videos.find_all("a")
                if len(all_anchor_tags) >= 2:
                    second_anchor_tag = all_anchor_tags[1]

                    href_value = second_anchor_tag.get("href")
                    links.append(href_value)
                else:
                    print("There are not enough <a> tags in the specified <div>.")

                video_tag = videos.find_all('h3')
                for videos_title in video_tag:
                    video_title = videos_title.text.replace(' ', ' ')
                    titles.append(video_title)
        articl_datas = []
        for title, link in zip(titles, links):
            article_data = {
                'title': title,
                'link': link,
            }
            articl_datas.append(article_data)

        # Call the function to send news to the channel
        send_videos_to_channel(bot, articl_datas)
        return articl_datas

    except requests.Timeout:
        print("Timeout occurred. Retrying in 60 seconds...")
        time.sleep(60)
        scrape_mereja_videos()
    except requests.RequestException as e:
        print(f"Error: {e}")
    except telepot.TelegramError as e:
        print(f"Telegram API Error: {e}")


def scrape_forum_news(bot):
    links = []
    titles = []
    Authors = []
    dates = []

    url = 'https://mereja.com/forum/viewforum.php?f=2'
    url2 = 'https://mereja.com/forum/'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.3'}
    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            topics = soup.find_all('li', class_=['row bg1', 'row bg2'])

            for topic in topics:
                topic_title = topic.find('a', class_='topictitle').text.replace(' ', ' ')
                titles.append(topic_title)

                authors = topic.find('a', class_='username').text.replace(' ', ' ')
                Authors.append(authors)

                published_date = topic.find('div', class_='responsive-show').text.split()
                last_three_terms = published_date[-3:]
                text_to_display = '\n'.join(last_three_terms)
                dates.append(text_to_display)

                detail_information = topic.find('div', class_='list-inner')
                link_element = detail_information.find('a', class_='topictitle')['href']
                link = url2 + link_element
                links.append(link)

        articlss_datas = []
        for title, authors, link, date in zip(titles, Authors, links, dates):
            article_data = {
                'title': title,
                'authors': authors,
                'link_element': link,
                'published_date': date
            }
            articlss_datas.append(article_data)
        send_forum_news_to_channel(bot, articlss_datas)
        return articlss_datas

    except requests.Timeout:
        print("Timeout occurred. Retrying in 60 seconds...")
    except requests.RequestException as e:
        print(f"Error: {e}")


def main():
    # Initialize the bot
    bot = telepot.Bot(API_TOKEN)

    # Send the welcome message and buttons to the channel when the bot starts
    welcome_message = "Welcome to our channel! Mereja:"

    # Create buttons
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ENGLISH", callback_data='button_1')],
        [InlineKeyboardButton(text="AMHARIC", callback_data='button_2')],
        [InlineKeyboardButton(text="FORUM", callback_data='button_3')],
        [InlineKeyboardButton(text="VIDEOS", callback_data='button_4')],
    ])

    # Send the welcome message with buttons
    send_message_to_channel(bot, welcome_message, buttons=keyboard)

    print("Bot is listening...")
    # Start the MessageLoop to handle incoming messages and button callbacks
    MessageLoop(bot, {'callback_query': lambda msg: handle_callback(msg, bot)}).run_as_thread()

    # Keep the program running
    while True:
        pass


if __name__ == '__main__':
    main()
