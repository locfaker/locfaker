import datetime
import os
import re
import random

# Danh sách từ vựng Tiếng Anh (Bạn có thể thêm nhiều hơn ở đây)
ENGLISH_WORDS = [
    {"word": "Resilient", "type": "adj", "meaning": "Kiên cường, mau phục hồi", "example": "He'll get over it—young people are amazingly resilient."},
    {"word": "Ambiguous", "type": "adj", "meaning": "Mơ hồ, nhập nhằng", "example": "His reply to my question was somewhat ambiguous."},
    {"word": "Pragmatic", "type": "adj", "meaning": "Thực dụng, thực tế", "example": "In business, the pragmatic approach to problems is often best."},
    {"word": "Substantial", "type": "adj", "meaning": "Đáng kể, quan trọng", "example": "The findings show a substantial difference between the two groups."},
    {"word": "Innovative", "type": "adj", "meaning": "Sáng tạo, đổi mới", "example": "She was an imaginative and innovative manager."},
    {"word": "Elaborate", "type": "adj/v", "meaning": "Tỉ mỉ, trau chuốt", "example": "They’re making the most elaborate preparations for the wedding."},
    {"word": "Sovereign", "type": "n/adj", "meaning": "Tối cao, có chủ quyền", "example": "We must respect the rights of sovereign nations."},
    {"word": "Versatile", "type": "adj", "meaning": "Linh hoạt, đa năng", "example": "A versatile person is someone who is good at many different things."},
    {"word": "Benevolent", "type": "adj", "meaning": "Nhân từ, rộng lượng", "example": "A benevolent uncle paid for her graduate education."},
    {"word": "Profound", "type": "adj", "meaning": "Sâu sắc, uyên thâm", "example": "His mother's death when he was aged six had a profound effect on him."}
]

def get_progress_bar(percentage):
    filled = int(percentage / 5)
    bar = "█" * filled + "░" * (20 - filled)
    return f"| {bar} | {percentage:.2f}%"

def update_readme():
    # Vietnam Time (UTC+7)
    vn_time = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
    
    # Calculate Day Progress
    seconds_in_day = 24 * 60 * 60
    seconds_passed = (vn_time.hour * 3600) + (vn_time.minute * 60) + vn_time.second
    day_percentage = (seconds_passed / seconds_in_day) * 100
    
    # Calculate Year Progress
    year = vn_time.year
    year_start = datetime.datetime(year, 1, 1)
    year_end = datetime.datetime(year + 1, 1, 1)
    year_total_seconds = (year_end - year_start).total_seconds()
    year_passed_seconds = (vn_time - year_start).total_seconds()
    year_percentage = (year_passed_seconds / year_total_seconds) * 100

    # Chọn một từ vựng ngẫu nhiên
    word_of_the_moment = random.choice(ENGLISH_WORDS)

    stats_content = [
        "### 🕒 Live Status",
        f"- **Vietnam Time**: `{vn_time.strftime('%H:%M:%S')}` (Quy Nhơn/Gia Lai)",
        f"- **Day Progress**: \n  {get_progress_bar(day_percentage)}",
        f"- **Year Progress**: \n  {get_progress_bar(year_percentage)}",
        "\n### 📚 English Word of the Moment",
        f"> **{word_of_the_moment['word']}** ({word_of_the_moment['type']}): {word_of_the_moment['meaning']}",
        f"> *Example: {word_of_the_moment['example']}*",
        "\n*Last updated every 5 minutes.*"
    ]
    
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()
    
    start_tag = "<!-- START_SECTION:dynamic_stats -->"
    end_tag = "<!-- END_SECTION:dynamic_stats -->"
    
    # Tìm kiếm và thay thế nội dung giữa 2 thẻ Marker
    pattern = f"{re.escape(start_tag)}.*?{re.escape(end_tag)}"
    replacement = f"{start_tag}\n" + "\n".join(stats_content) + f"\n{end_tag}"
    
    new_readme = re.sub(pattern, replacement, readme, flags=re.DOTALL)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_readme)

if __name__ == "__main__":
    update_readme()
