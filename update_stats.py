import datetime
import os
import re
import random
import json
import urllib.request

# Danh sách từ vựng dự phòng (Backup list)
BACKUP_WORDS = [
    {"word": "Resilient", "type": "adj", "meaning": "Kiên cường", "example": "Young people are amazingly resilient."},
    {"word": "Ambiguous", "type": "adj", "meaning": "Mơ hồ", "example": "His reply was somewhat ambiguous."},
    {"word": "Pragmatic", "type": "adj", "meaning": "Thực tế", "example": "A pragmatic approach is often best."},
    {"word": "Substantial", "type": "adj", "meaning": "Đáng kể", "example": "There is a substantial difference."},
    {"word": "Innovative", "type": "adj", "meaning": "Sáng tạo", "example": "An innovative manager."},
    {"word": "Versatile", "type": "adj", "meaning": "Linh hoạt", "example": "A versatile person."},
    {"word": "Benevolent", "type": "adj", "meaning": "Nhân từ", "example": "A benevolent uncle."},
    {"word": "Profound", "type": "adj", "meaning": "Sâu sắc", "example": "A profound effect."}
]

def get_progress_bar(percentage):
    filled = int(percentage / 5)
    bar = "█" * filled + "░" * (20 - filled)
    return f"| {bar} | {percentage:.2f}%"

def get_unlimited_word():
    """Lấy từ vựng ngẫu nhiên từ API để đảm bảo không giới hạn"""
    try:
        # 1. Lấy một từ ngẫu nhiên
        word_url = "https://random-word-api.herokuapp.com/word?number=1"
        with urllib.request.urlopen(word_url, timeout=5) as response:
            word = json.loads(response.read().decode())[0]
        
        # 2. Lấy định nghĩa của từ đó
        dict_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        with urllib.request.urlopen(dict_url, timeout=5) as response:
            data = json.loads(response.read().decode())[0]
            
            meanings = data.get('meanings', [])
            if not meanings: return random.choice(BACKUP_WORDS)
            
            part_of_speech = meanings[0].get('partOfSpeech', 'n/a')
            definition = meanings[0].get('definitions', [{}])[0].get('definition', 'No definition found.')
            example = meanings[0].get('definitions', [{}])[0].get('example', 'No example available.')
            
            return {
                "word": word.capitalize(),
                "type": part_of_speech,
                "meaning": definition,
                "example": example
            }
    except Exception as e:
        print(f"API Error: {e}")
        return random.choice(BACKUP_WORDS)

def update_readme():
    vn_time = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
    
    # Progress calculations
    seconds_in_day = 24 * 60 * 60
    seconds_passed = (vn_time.hour * 3600) + (vn_time.minute * 60) + vn_time.second
    day_percentage = (seconds_passed / seconds_in_day) * 100
    
    year = vn_time.year
    year_start = datetime.datetime(year, 1, 1)
    year_end = datetime.datetime(year + 1, 1, 1)
    year_total_seconds = (year_end - year_start).total_seconds()
    year_passed_seconds = (vn_time - year_start).total_seconds()
    year_percentage = (year_passed_seconds / year_total_seconds) * 100

    # Lấy từ vựng (Ưu tiên API để 'không giới hạn')
    word_info = get_unlimited_word()

    stats_content = [
        "### 🕒 Live Status",
        f"- **Vietnam Time**: `{vn_time.strftime('%H:%M:%S')}` (Quy Nhơn/Gia Lai)",
        f"- **Day Progress**: \n  {get_progress_bar(day_percentage)}",
        f"- **Year Progress**: \n  {get_progress_bar(year_percentage)}",
        "\n### 📚 English Word of the Moment (Unlimited Variety)",
        f"> **{word_info['word']}** ({word_info['type']})",
        f"> *Definition: {word_info['meaning']}*",
        f"> *Example: {word_info['example']}*",
        "\n*Last updated every 5 minutes using real-time dictionary data.*"
    ]
    
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()
    
    start_tag = "<!-- START_SECTION:dynamic_stats -->"
    end_tag = "<!-- END_SECTION:dynamic_stats -->"
    
    pattern = f"{re.escape(start_tag)}.*?{re.escape(end_tag)}"
    replacement = f"{start_tag}\n" + "\n".join(stats_content) + f"\n{end_tag}"
    
    new_readme = re.sub(pattern, replacement, readme, flags=re.DOTALL)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_readme)

if __name__ == "__main__":
    update_readme()
