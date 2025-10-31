import qrcode
import os
from pathlib import Path
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFont

def generate_qr_codes():
    """Generate team-specific QR codes for each table in the workshop."""
    
    # Create QR codes directory
    qr_dir = Path("qr_codes")
    qr_dir.mkdir(exist_ok=True)
    
    # Base URL - replace with your deployed app URL
    base_url = "http://localhost:8501"
    
    print("Generiere QR-Codes für Workshop-Tische...\n")
    
    # Read team names
    with open('data/team_namen.txt', 'r', encoding='utf-8') as f:
        team_lines = [line.strip() for line in f.readlines() if line.strip()]
        teams = dict(item.split(":") for item in team_lines)
    
    print(f"Erstelle {len(teams)} Tisch-Bilder...\n")
    
    # Generate a QR code with team name and info for each team
    for team_name, indication in teams.items():
        # Create team-specific URL
        team_url = f"{base_url}?team={quote(team_name)}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(team_url)
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_size = qr_img.size[0]
        
        # Layout dimensions - ensure enough space for all text
        margin = 60
        title_section = 140
        team_section = 140
        
        total_width = qr_size + (2 * margin)
        total_height = margin + title_section + qr_size + team_section + margin
        
        # Create image
        full_img = Image.new('RGB', (total_width, total_height), 'white')
        draw = ImageDraw.Draw(full_img)
        
        # Load fonts
        try:
            title_font = ImageFont.truetype("arial.ttf", 40)
            subtitle_font = ImageFont.truetype("arial.ttf", 24)
            team_font = ImageFont.truetype("arialbd.ttf", 42)
            info_font = ImageFont.truetype("arial.ttf", 22)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            team_font = ImageFont.load_default()
            info_font = ImageFont.load_default()
        
        y_pos = margin
        
        # Title
        title_text = "ZUKUNFTSTAG 2025"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((total_width - title_width) // 2, y_pos), title_text, fill='black', font=title_font)
        y_pos += 63
        
        # Subtitle
        subtitle_text = "Mathe Macht Medikamente"
        subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        draw.text(((total_width - subtitle_width) // 2, y_pos), subtitle_text, fill='#0055AA', font=subtitle_font)
        y_pos += 77
        
        # QR code
        full_img.paste(qr_img, (margin, y_pos))
        y_pos += qr_size + 30
        
        # Team name
        team_text = f"TEAM: {team_name}"
        team_bbox = draw.textbbox((0, 0), team_text, font=team_font)
        team_width = team_bbox[2] - team_bbox[0]
        draw.text(((total_width - team_width) // 2, y_pos), team_text, fill='#007700', font=team_font)
        y_pos += 58
        
        # Indication (max 2 lines)
        max_chars = 50
        if len(indication) > max_chars:
            words = indication.split()
            lines = []
            current_line = []
            for word in words:
                test_line = ' '.join(current_line + [word])
                if len(test_line) <= max_chars:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
            
            for line in lines[:2]:
                line_bbox = draw.textbbox((0, 0), line, font=info_font)
                line_width = line_bbox[2] - line_bbox[0]
                draw.text(((total_width - line_width) // 2, y_pos), line, fill='#0055AA', font=info_font)
                y_pos += 28
        else:
            indication_bbox = draw.textbbox((0, 0), indication, font=info_font)
            indication_width = indication_bbox[2] - indication_bbox[0]
            draw.text(((total_width - indication_width) // 2, y_pos), indication, fill='#0055AA', font=info_font)
        
        # Save
        safe_team_name = team_name.replace(' ', '_').replace('/', '_')
        img_path = qr_dir / f"TISCH_{safe_team_name}.png"
        full_img.save(img_path, 'PNG', dpi=(300, 300))
        
        print(f"✅ TISCH_{safe_team_name}.png")
    
    print(f"\n{'='*60}")
    print(f"🎉 Fertig! {len(teams)} Tisch-Bilder in 'qr_codes/'")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    generate_qr_codes()
