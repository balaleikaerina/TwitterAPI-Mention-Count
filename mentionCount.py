import requests
import os
import json

def create_headers(bearer_token:str) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {bearer_token}"}
    return headers


def create_url(tweet_id:int, next_token=None) -> str:
    base_url = "https://api.twitter.com/2/tweets/search/recent"
    query = f"query=conversation_id:{tweet_id}&tweet.fields=in_reply_to_user_id,author_id,created_at,conversation_id&max_results=100"
    if next_token:
        query += f"&next_token={next_token}"
    return f"{base_url}?{query}"

def connect_to_endpoint(url, headers):
    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Request returned an error: {response.status_code} {response.text}")
    return response.json()

def get_all_replies(tweet_id, headers):
    all_replies = []
    next_token = None

    while True:
        tweet_url = create_url(tweet_id, next_token)
        tweet_response = connect_to_endpoint(tweet_url, headers)

        if 'data' in tweet_response and tweet_response['data']:
            all_replies.extend(tweet_response['data'])
        
        if 'meta' in tweet_response and 'next_token' in tweet_response['meta']:
            next_token = tweet_response['meta']['next_token']
        else:
            break  # No more pages

    return all_replies

def count_mentions(replies, headers):
    mentions_count = {}
    if 'data' in replies:
        for reply in replies['data']:
            if 'text' in reply:
                user_mentions = get_user_mentions(reply['text'])
                for mention in user_mentions:
                    mentions_count[mention] = mentions_count.get(mention, 0) + 1
    return mentions_count

def get_user_mentions(tweet_text):
    # Extract @mentions from tweet text, excluding the first one
    mentions = [word[1:] for word in tweet_text.split() if word.startswith('@')]
    
    # Filter out the first mention if there are multiple mentions
    return mentions[1:] if len(mentions) > 1 else mentions


def main() -> None:
    try:
        tweet_id = input("Enter Tweet ID: ")
        bearer_token = 'YOUR BEARER TOKEN'

        # Fetch all replies
        all_replies = get_all_replies(tweet_id, create_headers(bearer_token))

        # Process replies
        mentions_count = count_mentions({'data': all_replies}, create_headers(bearer_token))

        # Print and save mentions count
        print("Mentions count:")
        for user_name, count in mentions_count.items():
            print(f"{user_name}: {count}")
            
        with open(f"mentions_{tweet_id}.txt", 'a') as outfile:
            outfile.write("Mentions count:\n")
            for user_name, count in mentions_count.items():
                outfile.write(f"{user_name}: {count}\n")

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()