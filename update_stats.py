import datetime
import os
import re
import random
import json
import urllib.request

# Danh sách từ vựng dự phòng (Backup list)
BACKUP_WORDS = [
    {"word": "Resilient", "type": "adj", "meaning": "Kiên cường, mau phục hồi", "example": "Young people are amazingly resilient."},
    {"word": "Ambiguous", "type": "adj", "meaning": "Mơ hồ, nhập nhằng", "example": "His reply was somewhat ambiguous."},
    {"word": "Pragmatic", "type": "adj", "meaning": "Thực dụng, thực tế", "example": "A pragmatic approach is often best."},
    {"word": "Substantial", "type": "adj", "meaning": "Đáng kể, quan trọng", "example": "There is a substantial difference."},
    {"word": "Innovative", "type": "adj", "meaning": "Sáng tạo, đổi mới", "example": "An innovative manager."},
    {"word": "Versatile", "type": "adj", "meaning": "Linh hoạt, đa năng", "example": "A versatile person."},
    {"word": "Benevolent", "type": "adj", "meaning": "Nhân từ, rộng lượng", "example": "A benevolent uncle."},
    {"word": "Profound", "type": "adj", "meaning": "Sâu sắc, uyên thâm", "example": "A profound effect."}
]

def get_unlimited_word():
    """Lấy từ vựng ngẫu nhiên từ API"""
    try:
        # 1. Lấy một từ ngẫu nhiên
        word_url = "https://random-word-api.herokuapp.com/word?number=1"
        with urllib.request.urlopen(word_url, timeout=5) as response:
            word = json.loads(response.read().decode())[0]
        
        # 2. Lấy định nghĩa
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
    word_info = get_unlimited_word()
    # Vietnam Time (UTC+7)
    vn_time = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

    # Chỉ để lại thông tin từ vựng Tiếng Anh theo yêu cầu
    stats_content = [
        f"**{word_info['word']}** ({word_info['type']})  ",
        f"**Định nghĩa**: {word_info['meaning']}  ",
        f"**Ví dụ**: {word_info['example']}"
    ]
    
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()
    
    start_tag = "<!-- START_SECTION:dynamic_stats -->"
    end_tag = "<!-- END_SECTION:dynamic_stats -->"
    
    pattern = f"{re.escape(start_tag)}.*?{re.escape(end_tag)}"
    # Thêm comment ẩn chứa timestamp cực chi tiết để đảm bảo file luôn thay đổi
    hidden_timestamp = f"<!-- Last refresh: {vn_time.strftime('%Y-%m-%d %H:%M:%S.%f')} -->"
    replacement = f"{start_tag}\n" + "\n".join(stats_content) + f"\n{hidden_timestamp}\n{end_tag}"
    
    new_readme = re.sub(pattern, replacement, readme, flags=re.DOTALL)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_readme)

if __name__ == "__main__":
    update_readme()
