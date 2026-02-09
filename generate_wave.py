import random

def generate_wave_svg():
    # Cấu hình màu sắc đẹp (Gradient tím - xanh của Tokyo Night)
    colors = ["#7aa2f7", "#bb9af7", "#b4f9f8", "#2ac3de", "#7dcfff"]
    
    # Số lượng thanh sóng
    num_bars = 40
    width = 400
    height = 60
    bar_width = 6
    gap = 4
    
    svg_header = f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">'
    svg_style = """
    <style>
        .bar {
            transform-box: fill-box;
            transform-origin: bottom;
            animation: wave 1.5s ease-in-out infinite;
        }
        @keyframes wave {
            0%, 100% { transform: scaleY(0.3); }
            50% { transform: scaleY(1); }
        }
    </style>
    """
    
    bars = []
    for i in range(num_bars):
        x = i * (bar_width + gap)
        # Tạo độ trễ ngẫu nhiên để sóng nhảy múa tự nhiên
        delay = random.uniform(0, 1.5)
        duration = random.uniform(0.8, 1.8)
        color = random.choice(colors)
        
        bar = f'<rect class="bar" x="{x}" y="0" width="{bar_width}" height="{height}" rx="3" fill="{color}" style="animation-delay: {delay:.2f}s; animation-duration: {duration:.2f}s" />'
        bars.append(bar)
        
    svg_footer = '</svg>'
    
    full_svg = svg_header + svg_style + "".join(bars) + svg_footer
    
    with open("assets/music-wave.svg", "w", encoding="utf-8") as f:
        f.write(full_svg)

if __name__ == "__main__":
    import os
    if not os.path.exists("assets"):
        os.makedirs("assets")
    generate_wave_svg()
