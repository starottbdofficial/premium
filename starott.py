import requests
from datetime import datetime
import pytz
import re

# আপনার নতুন স্পোর্টস সোর্স ইউআরএলগুলো
urls = [
    "https://raw.githubusercontent.com/srhady/CricketLive/refs/heads/main/playlist.m3u",
    "https://raw.githubusercontent.com/srhady/axsports/refs/heads/main/playlist.m3u",
    "https://raw.githubusercontent.com/etcvai/ExtenderMax/refs/heads/main/iptv.m3u8"
]

# IBS TV app promotion ভিডিও
IBS_PROMO_VIDEO = "https://raw.githubusercontent.com/ibstvofficial/IBS-TV-special-movies.m3u/refs/heads/main/promo%20dual.mp4"

def clean_channel_and_telegram(text):
    # টেলিগ্রাম লিংক (t.me/...) এবং @username রিমুভ করার জন্য রেগুলার এক্সপ্রেশন
    text = re.sub(r'https?://t\.me/[^\s\n,]+', '', text)
    text = re.sub(r'@[^\s\n,]+', '', text)
    
    # অন্যান্য অপ্রয়োজনীয় লেখা পরিষ্কার করা
    junk = ["| High Quality", "| BDIX", "| VIP", "SD", "HD", "FHD", "(Backup)", "Premium", "1080p", "720p", "JOIN", "TELEGRAM", "👉", "⚡"]
    for word in junk:
        text = text.replace(word, "")
    
    # ডাবল স্পেস বা বাড়তি কমা থাকলে তা ঠিক করা
    text = re.sub(r'\s+', ' ', text)
    return text.strip().strip(',')

def determine_group_by_name(channel_name):
    name_upper = channel_name.upper()
    
    # ফিফা ওয়ার্ল্ড কাপ এবং ফুটবল ম্যাচ ফিল্টার
    if any(x in name_upper for x in ["FIFA", "WORLD CUP", "FOOTBALL", "WC"]):
        return "FIFA WORLD CUP"
        
    # ক্রিকেট ও লাইভ স্পোর্টস ফিল্টার
    if any(x in name_upper for x in ["CRICKET", "IPL", "T20", "ODI", "TEST", "SPORTS", "LIVE"]):
        return "LIVE SPORTS"
        
    # বাংলা ও লোকাল চ্যানেল ফিল্টার
    if any(x in name_upper for x in ["BANGLA", "BD", "SONY", "STAR", "ZEE", "TSPORTS", "GTV"]):
        return "LIVE TV"
        
    return "SPORTS EVENTS"

def create_starott_playlist():
    bd_tz = pytz.timezone('Asia/Dhaka')
    current_time = datetime.now(bd_tz).strftime('%I:%M %p %d-%m-%Y')

    merged_content = f"""#EXTM3U
# Playlist Name: StarOTT Premium Sports
# Last Update: {current_time} (BD Time)
# Owner: Md. Sakib Hasan
# Telegram: https://t.me/bdixiptvbd\n"""

    DEFAULT_LOGO = "https://bdixiptvbd.com/logo.png"
    seen_links = set()
    added_groups = set()

    for url in urls:
        try:
            print(f"Fetching from: {url}")
            response = requests.get(url, timeout=25)
            if response.status_code == 200:
                content = response.text
                
                # এক্সট্রা অপশন ও স্ট্রিম লিংকসহ সম্পূর্ণ ব্লক ধরার রেগুলার এক্সপ্রেশন
                blocks = re.findall(r'(#EXTINF:[^\n]+(?:\n#EXTVLCOPT:[^\n]+)*)\n(https?://[^\n]+)', content, re.M)
                
                for ext_block, stream_url in blocks:
                    stream_url = stream_url.strip()
                    
                    if stream_url and stream_url not in seen_links:
                        # মূল চ্যানেলের নাম বের করা এবং পরিষ্কার করা
                        name_part = ext_block.split(",")[-1].split("\n")[0]
                        final_name = clean_channel_and_telegram(name_part)
                        
                        # নাম যদি একদম খালি হয়ে যায় (শুধু টেলিগ্রাম লিংক থাকার কারণে), তবে স্কিপ করবে
                        if not final_name:
                            continue

                        # চ্যানেলের নাম অনুযায়ী ক্যাটাগরি নির্ধারণ
                        final_group = determine_group_by_name(final_name)

                        # লোগো বের করা
                        logo_match = re.search(r'tvg-logo="([^"]+)"', ext_block)
                        final_logo = logo_match.group(1) if (logo_match and logo_match.group(1)) else DEFAULT_LOGO

                        # গ্রুপ টাইটেল থেকে টেলিগ্রাম রিমুভ করা
                        group_match = re.search(r'group-title="([^"]+)"', ext_block)
                        if group_match:
                            clean_group_title = clean_channel_and_telegram(group_match.group(1))
                            if any(x in clean_group_title.upper() for x in ["FIFA", "WORLD CUP", "FOOTBALL"]):
                                final_group = "FIFA WORLD CUP"

                        # ক্যাটাগরির শুরুতে IBS TV প্রমোশন যুক্ত করার লজিক
                        if final_group not in added_groups:
                            promo_line = f'#EXTINF:-1 tvg-logo="{DEFAULT_LOGO}" group-title="{final_group}",--- [ {final_group} PROMO ] ---'
                            merged_content += promo_line + "\n" + IBS_PROMO_VIDEO + "\n"
                            added_groups.add(final_group)

                        # নতুন ব্লকের হেডলাইন তৈরি
                        new_extinf = f'#EXTINF:-1 tvg-logo="{final_logo}" group-title="{final_group}",{final_name}'
                        merged_content += new_extinf + "\n"
                        
                        # এক্সট্রা অপশন (Referer / User-Agent) থাকলে তা যুক্ত করা
                        extra_opts = re.findall(r'(#EXTVLCOPT:[^\n]+)', ext_block)
                        for opt in extra_opts:
                            merged_content += opt + "\n"
                        
                        # স্ট্রিম লিংক যুক্ত করা
                        merged_content += stream_url + "\n"
                        seen_links.add(stream_url)

        except Exception as e:
            print(f"Error fetching from {url}: {e}")

    try:
        with open("starott premium.m3u", "w", encoding="utf-8") as f:
            f.write(merged_content)
        print(f"Success! starott premium.m3u updated at {current_time}")
    except Exception as e:
        print(f"Save Error: {e}")

if __name__ == "__main__":
    create_starott_playlist()
  
