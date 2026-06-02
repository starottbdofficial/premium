import requests
from datetime import datetime
import pytz
import re

# আপনার স্পোর্টস ও টিভি সোর্স ইউআরএলগুলো
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
    
    text = re.sub(r'\s+', ' ', text)
    return text.strip().strip(',')

def determine_group_by_name(channel_name):
    name_upper = channel_name.upper()
    
    # ১. FIFA World Cup
    if any(x in name_upper for x in ["FIFA", "WORLD CUP", "WC"]):
        return "FIFA World Cup"
        
    # ২. Live Event
    if "LIVE EVENT" in name_upper:
        return "Live Event"
        
    # ৩. Cricket
    if any(x in name_upper for x in ["CRICKET", "IPL", "T20", "ODI", "TEST", "BPL", "BIG BASH"]):
        return "Cricket"
        
    # ৪. Bangladesh 🇧🇩
    if any(x in name_upper for x in ["BANGLADESH", "BD ", "BANGLA", "BTV", "GTV", "TSPORTS", "SOMOY", "JAMUNA", "NTV", "RTV"]):
        return "Bangladesh 🇧🇩"
        
    # ৫. Kolkata Special
    if any(x in name_upper for x in ["STAR JALSHA", "ZEE BANGLA", "JALSHA", "RUPASHI", "AKASH AATH", "KOLKATA"]):
        return "Kolkata Special"
        
    # ৬. India
    if any(x in name_upper for x in ["INDIA", "SONY", "STAR ", "COLORS", "ZEE TV", "SAB TV", "ASIAD"]):
        return "India"
        
    # ৭. News
    if any(x in name_upper for x in ["NEWS", "24X7", "KHABAR"]):
        return "News"
        
    # ৮. Sports
    if any(x in name_upper for x in ["SPORTS", "TEN ", "FOX ", "ESPN", "CANAL"]):
        return "Sports"
        
    # ৯. Kids
    if any(x in name_upper for x in ["KIDS", "NICK", "CARTOON", "DISNEY", "POGO", "SONY YAY"]):
        return "Kids"
        
    # ১০. Documentary
    if any(x in name_upper for x in ["DOCUMENTARY", "DISCOVERY", "NAT GEO", "GEOGRAPHIC", "ANIMAL PLANET", "HISTORY"]):
        return "Documentary"
        
    # ১১. Music
    if any(x in name_upper for x in ["MUSIC", "MTV", "9XM", "ZOOM", "SONG"]):
        return "Music"
        
    # ১২. Movie
    if any(x in name_upper for x in ["MOVIE", "CINEMA", "HBO", "STAR MOVIES", "PIX", "ACTION"]):
        return "Movie"
        
    # ১৩. Islamic TV
    if any(x in name_upper for x in ["ISLAMIC", "ISLAM", "MAKKAH", "MADINAH", "PEACE TV", "AS-SUNNAH", "QURAN"]):
        return "Islamic TV"
        
    # ১৪. Default: International TV Channel
    return "International TV Channel"

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
                    
                    # কন্ডিশন: লিংকে drive.google.com থাকলে সেই চ্যানেল সম্পূর্ণ রিমুভ (স্কিপ) হবে
                    if "drive.google.com" in stream_url:
                        print(f"Skipping Google Drive link: {stream_url}")
                        continue
                    
                    if stream_url and stream_url not in seen_links:
                        # মূল চ্যানেলের নাম বের করা এবং পরিষ্কার করা
                        name_part = ext_block.split(",")[-1].split("\n")[0]
                        final_name = clean_channel_and_telegram(name_part)
                        
                        if not final_name:
                            continue

                        # চ্যানেলের নাম অনুযায়ী নতুন কাস্টম ক্যাটাগরি নির্ধারণ
                        final_group = determine_group_by_name(final_name)

                        # লোগো বের করা
                        logo_match = re.search(r'tvg-logo="([^"]+)"', ext_block)
                        final_logo = logo_match.group(1) if (logo_match and logo_match.group(1)) else DEFAULT_LOGO

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
                                     
