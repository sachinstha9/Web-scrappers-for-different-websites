import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

def scrape_news_data(url):
    news_data = []
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all news cards
        news_cards = soup.find_all('div', class_='ok-news-post ltr-post')

        for card in news_cards:
            # Extract title and link
            title_element = card.find('div', class_='ok-post-contents').find('h2').find('a')
            title = title_element.text.strip()
            link = title_element['href']

            # Extract details from individual news page
            details = get_news_details(link)
            if details:
                news_item = {
                    'title': title,
                    'link': link,
                    'content': details['content'],
                    'date': details['date']
                }
                news_data.append(news_item)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
    except AttributeError as e:
        print(f"Error parsing data from {url}: {e}")
    return news_data


def get_news_details(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        content_wrap = soup.find('div', class_='post-content-wrap')
        if content_wrap:
            paragraphs = content_wrap.find_all('p')
            content = ' '.join(p.text.strip() for p in paragraphs)
        else:
            content = "Content not found"

        date_element = soup.find('span', class_='ok-post-date')
        date = date_element.text.strip() if date_element else "Date not found"

        return {'content': content, 'date': date}

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None
    except AttributeError as e:
        print(f"Error parsing data from {url}: {e}")
        return None



def main(sector, total_pages):
    base_url = f"https://english.onlinekhabar.com/category/{sector}/page/"
    all_news_data = []
    # Scrape up to page 238
    for page_num in range(1, total_pages + 1):
        page_url = base_url + str(page_num)
        news_data_from_page = scrape_news_data(page_url)
        all_news_data.extend(news_data_from_page)
        print(f"Scraped {len(news_data_from_page)} articles from {page_url}")

    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(all_news_data)
    df.to_csv(f"onlinekhabar_{sector}_news.csv", index=False, encoding="utf-8")
    print(f"Successfully saved {len(df)} articles to onlinekhabar_{sector}_news.csv")


if __name__ == "__main__":
    main("economy", 238)