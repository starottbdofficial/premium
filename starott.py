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

    # প্রথমে নির্ধারিত সিকোয়েন্স অনুযায়ী প্রমোশন ও চ্যানেল রাইট করা
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
        print("Success! starott premium.m3u updated with FIFA sorting.")
    except Exception as e:
        print(f"Save Error: {e}")


if __name__ == "__main__":
    create_starott_playlist()
