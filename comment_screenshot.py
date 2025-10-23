from PIL import Image, ImageDraw, ImageFont
import os


def generate_reddit_comment_dark(username, time_ago, likes, comment, output_path="reddit_comment_dark.png"):
    # Visual configuration
    width = 756
    margin = 40
    avatar_size = 48
    bg_color = (26, 26, 27)          # dark background
    text_color = (215, 218, 220)     # main text
    gray = (129, 131, 132)           # medium gray
    light_gray = (52, 53, 54)        # lighter gray for details
    accent_gray = (68, 69, 70)       # for the left thread line

    # Load fonts
    try:
        font_user = ImageFont.truetype("arial.ttf", 20)
        font_meta = ImageFont.truetype("arial.ttf", 18)
        font_text = ImageFont.truetype("arial.ttf", 20)
        font_actions = ImageFont.truetype("arial.ttf", 18)
    except:
        # Linux fallback
        font_user = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_meta = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        font_actions = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

    # Temporary image (for text measurement)
    img = Image.new("RGB", (width, 1000), bg_color)
    draw = ImageDraw.Draw(img)

    # Avatar and left thread line positions
    line_x = margin - 25
    avatar_x = margin
    avatar_y = margin
    text_x = avatar_x + avatar_size + 12

    # Process comment text (handle newlines and paragraphs)
    paragraphs = comment.split("\n")
    max_text_width = width - (text_x + margin)
    lines = []

    for paragraph in paragraphs:
        if not paragraph.strip():
            lines.append("")  # blank line between paragraphs
            continue

        words = paragraph.split()
        current = ""
        for word in words:
            test = current + (" " if current else "") + word
            if draw.textlength(test, font=font_text) <= max_text_width:
                current = test
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)

    # Calculate total height
    line_height = font_text.getbbox("Ay")[3] + 6
    total_text_height = len(lines) * line_height
    total_height = margin + avatar_size + 20 + total_text_height + 80  # bottom spacing

    # Create final image with adjusted height
    img = Image.new("RGB", (width, total_height), bg_color)
    draw = ImageDraw.Draw(img)

    # Left vertical line (thread)
    draw.line((line_x, margin, line_x, total_height - 20), fill=accent_gray, width=2)

    # Circular avatar placeholder
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "reddit_icon.png")
        icon = Image.open(icon_path).convert("RGBA")
        icon = icon.resize((avatar_size, avatar_size))
        img.paste(icon, (avatar_x, avatar_y), icon)
    except:
        draw.ellipse(
            (avatar_x, avatar_y, avatar_x + avatar_size, avatar_y + avatar_size),
            fill=light_gray,
            outline=gray,
        )

    # Username and time
    draw.text((text_x, avatar_y), username, font=font_user, fill=text_color)
    user_width = draw.textlength(username, font=font_user)
    draw.text((text_x + user_width + 8, avatar_y), f"• {time_ago}", font=font_meta, fill=gray)

    # Comment text
    text_y = avatar_y + avatar_size + 10
    for line in lines:
        draw.text((text_x, text_y), line, font=font_text, fill=text_color)
        text_y += line_height

    # Actions (upvote, reply, etc.)
    actions_y = text_y + 10
    draw.text((text_x, actions_y), f"▲ {likes}", font=font_actions, fill=text_color)
    actions = ["Reply", "Give Award", "Share", "..."]
    x = text_x + 80
    for action in actions:
        draw.text((x, actions_y), action, font=font_actions, fill=gray)
        x += draw.textlength(action, font=font_actions) + 30

    img.save(output_path)
    print(f"✅ Image generated successfully: {output_path}")


# Example usage
if __name__ == "__main__":
    generate_reddit_comment_dark(
        username="0xnld",
        time_ago="3h ago",
        likes="955",
        comment=(
            "Ukrainian, born in late 80s, so I've got mostly 2nd hand experience, "
            "but many vestiges of that system remained well into the 00s and onwards.\n\n"
            "There was no equality in practice..."
        ),
    )

