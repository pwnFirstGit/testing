from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

extract = URLExtract()

# Version-compatible emoji extraction helper
def extract_emojis(text: str):
    """Return a list of emojis found in text, compatible with emoji v1.x and v2.x+."""
    # Preferred: emoji.emoji_list (v2.x)
    if hasattr(emoji, 'emoji_list'):
        try:
            return [e['emoji'] for e in emoji.emoji_list(text)]
        except Exception:
            pass

    # Fallback: regex extractor available in many versions
    if hasattr(emoji, 'get_emoji_regexp'):
        try:
            return emoji.get_emoji_regexp().findall(text)
        except Exception:
            pass

    # Final fallback: membership test against known emoji sets
    emoji_set = set()
    # Newer versions expose EMOJI_DATA
    if hasattr(emoji, 'EMOJI_DATA'):
        try:
            emoji_set = set(emoji.EMOJI_DATA.keys())
        except Exception:
            pass
    # Older versions expose UNICODE_EMOJI / UNICODE_EMOJI_ENGLISH
    if not emoji_set and hasattr(emoji, 'UNICODE_EMOJI'):
        try:
            # Sometimes UNICODE_EMOJI is a dict of language -> set/dict
            en = emoji.UNICODE_EMOJI.get('en') if isinstance(emoji.UNICODE_EMOJI, dict) else None
            if en:
                emoji_set = set(en.keys() if hasattr(en, 'keys') else en)
            else:
                emoji_set = set(emoji.UNICODE_EMOJI.keys())
        except Exception:
            pass
    return [ch for ch in text if ch in emoji_set]

def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # fetch the number of messages
    num_messages = df.shape[0]

    # fetch the total number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # fetch number of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)

def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return x, df

def create_wordcloud(selected_user, df):
    with open('stop_hinglish.txt', 'r') as f:
        stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user, df):
    with open('stop_hinglish.txt', 'r') as f:
        stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []

    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        # Use version-compatible extractor instead of deprecated UNICODE_EMOJI
        emojis.extend(extract_emojis(message))

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df

def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline

def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap