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
    text = re.sub(r'https?://t\.me/[^\s\n,]+', '', text)
    text = re.sub(r'@[^\s\n,]+', '', text)
    junk = ["| High Quality", "| BDIX", "| VIP", "SD", "HD", "FHD", "(Backup)", "Premium", "1080p", "720p", "JOIN", "TELEGRAM", "👉", "⚡"]
    for word in junk:
        text = text.replace(word, "")
    text = re.sub(r'\s+', ' ', text)
    return text.strip().strip(',')

def determine_group_by_name(channel_name, stream_url):
    name_upper = channel_name.upper()
    url_upper = stream_url.upper()
    
    # ১. Movie (mkv, mp4, pixeldrain লিংক থাকলে)
    if any(x in url_upper for x in [".MKV", ".MP4", "PIXELDRAIN"]):
        return "Movie"

    # ২. FIFA World Cup (সবার ওপরে থাকবে এবং ESPN, TNT, FOX Sports সহ সব ফুটবল চ্যানেল এখানে আসবে)
    if any(x in name_upper for x in ["FIFA", "WORLD CUP", "WC", "FOOTBALL", "ESPN", "TNT", "FOX SPORTS", "FOXSPORTS"]):
        return "FIFA World Cup"
        
    # ৩. Live Event
    if "LIVE EVENT" in name_upper:
        return "Live Event"
        
    # ৪. Cricket
    if any(x in name_upper for x in ["CRICKET", "IPL", "T20", "ODI", "TEST", "BPL", "BIG BASH"]):
        return "Cricket"
        
    # ৫. Bangladesh 🇧🇩
    if any(x in name_upper for x in ["BANGLADESH", "BD ", "BANGLA", "BTV", "GTV", "TSPORTS", "SOMOY", "JAMUNA", "NTV", "RTV"]):
        return "Bangladesh 🇧🇩"
        
    # ৬. Kolkata Special
    if any(x in name_upper for x in ["STAR JALSHA", "ZEE BANGLA", "JALSHA", "RUPASHI", "AKASH AATH", "KOLKATA"]):
        return "Kolkata Special"
        
    # ৭. India
    if any(x in name_upper for x in ["INDIA", "SONY", "STAR ", "COLORS", "ZEE TV", "SAB TV", "ASIAD"]):
        return "India"
        
    # 👑 অন্যান্য ক্যাটাগরিগুলো...
    if any(x in name_upper for x in ["NEWS", "24X7", "KHABAR"]):
        return "News"
    if "SPORTS" in name_upper:
        return "Sports"
    if any(x in name_upper for x in ["KIDS", "NICK", "CARTOON", "DISNEY", "POGO", "SONY YAY"]):
        return "Kids"
    if any(x in name_upper for x in ["DOCUMENTARY", "DISCOVERY", "NAT GEO", "GEOGRAPHIC", "ANIMAL PLANET", "HISTORY"]):
        return "Documentary"
    if any(x in name_upper for x in ["MUSIC", "MTV", "9XM", "ZOOM", "SONG"]):
        return "Music"
    if any(x in name_upper for x in ["ISLAMIC", "ISLAM", "MAKKAH", "MADINAH", "PEACE TV", "AS-SUNNAH", "QURAN"]):
        return "Islamic TV"
        
    return "International TV Channel"

def create_starott_playlist():
    bd_tz = pytz.timezone('Asia/Dhaka')
    current_time = datetime.now(bd_tz).strftime('%I:%M %p %d-%m-%Y')

    DEFAULT_LOGO = "https://bdixiptvbd.com/logo.png"
    seen_links = set()
    
    # ক্যাটাগরি অনুযায়ী চ্যানেল জমা রাখার ডিকশনারি
    playlist_groups = {}

    for url in urls:
        try:
            print(f"Fetching from: {url}")
            response = requests.get(url, timeout=25)
            if response.status_code == 200:
                content = response.text
                blocks = re.findall(r'(#EXTINF:[^\n]+(?:\n#EXTVLCOPT:[^\n]+)*)\n(https?://[^\n]+)', content, re.M)
                
                for ext_block, stream_url in blocks:
                    stream_url = stream_url.strip()
                    
                    # 🚫 গুগল ড্রাইভ এবং প্লেজ (playz / playztv) লিংক ফিল্টার
                    if "drive.google.com" in stream_url or "playztv.pages.dev" in stream_url or "playz" in stream_url.lower() or "playz" in ext_block.lower():
                        continue
                    
                    if stream_url and stream_url not in seen_links:
                        name_part = ext_block.split(",")[-1].split("\n")[0]
                        final_name = clean_channel_and_telegram(name_part)
                        
                        if not final_name:
                            continue

                        # ক্যাটাগরি নির্ধারণ
                        final_group = determine_group_by_name(final_name, stream_url)

                        logo_match = re.search(r'tvg-logo="([^"]+)"', ext_block)
                        final_logo = logo_match.group(1) if (logo_match and logo_match.group(1)) else DEFAULT_LOGO

                        # ডিকশনারিতে গ্রুপ না থাকলে তৈরি করা
                        if final_group not in playlist_groups:
                            playlist_groups[final_group] = []

                        # চ্যানেলের ডাটা ব্লক তৈরি
                        channel_block = f'#EXTINF:-1 tvg-logo="{final_logo}" group-title="{final_group}",{final_name}\n'
                        extra_opts = re.findall(r'(#EXTVLCOPT:[^\n]+)', ext_block)
                        for opt in extra_opts:
                            channel_block += opt + "\n"
                        channel_block += stream_url + "\n"
                        
                        playlist_groups[final_group].append(channel_block)
                        seen_links.add(stream_url)

        except Exception as e:
            print(f"Error fetching from {url}: {e}")

    # 📄 মেইন ফাইল রাইটিং এবং ক্যাটাগরি সর্টিং (FIFA World Cup সবার ওপরে থাকবে)
    merged_content = f"""#EXTM3U
# Playlist Name: StarOTT Premium Sports
# Last Update: {current_time} (BD Time)
# Owner: Md. Sakib Hasan
# Telegram: https://t.me/bdixiptvbd\n"""

    # ক্যাটাগরির নির্দিষ্ট সিকোয়েন্স (FIFA World Cup থাকবে সবার ওপরে)
    custom_order = ["FIFA World Cup", "Live Event", "Cricket", "Bangladesh 🇧🇩", "Kolkata Special", "India", "News", "Sports", "Kids", "Documentary", "Music", "Movie", "Islamic TV", "International TV Channel"]

    # প্রথমে নির্ধারিত সিকোয়েন্স অনুযায়ী প্রমোশন ও চ্যানেল রাইট করা
    for group in custom_order:
        if group in playlist_groups and playlist_groups[group]:
            # প্রতি ক্যাটাগরির শুরুতে IBS TV প্রমোশন
            promo_line = f'#EXTINF:-1 tvg-logo="{DEFAULT_LOGO}" group-title="{group}",--- [ {group} PROMO ] ---'
            merged_content += promo_line + "\n" + IBS_PROMO_VIDEO + "\n"
            
            # চ্যানেলের কন্টেন্ট যোগ করা
            for channel in playlist_groups[group]:
                merged_content += channel

    # যদি নতুন কোনো ক্যাটাগরি লিস্টের বাইরে থাকে, সেগুলো শেষে যুক্ত হবে
    for group, channels in playlist_groups.items():
        if group not in custom_order and channels:
            promo_line = f'#EXTINF:-1 tvg-logo="{DEFAULT_LOGO}" group-title="{group}",--- [ {group} PROMO ] ---'
            merged_content += promo_line + "\n" + IBS_PROMO_VIDEO + "\n"
            for channel in channels:
                merged_content += channel

    try:
        with open("starott premium.m3u", "w", encoding="utf-8") as f:
            f.write(merged_content)
        print(f"Success! starott premium.m3u updated with FIFA sorting.")
    except Exception as e:
        print(f"Save Error: {e}")

if __name__ == "__main__":
    create_starott_playlist()
                                     
