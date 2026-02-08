import datetime
import os
import re

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

    stats_content = [
        "### 🕒 Live Status",
        f"- **Vietnam Time**: `{vn_time.strftime('%H:%M:%S')}` (Quy Nhơn/Gia Lai)",
        f"- **Day Progress**: \n  {get_progress_bar(day_percentage)}",
        f"- **Year Progress**: \n  {get_progress_bar(year_percentage)}",
        "\n*Last updated every 5 minutes.*"
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
