import textwrap
from PIL import Image, ImageDraw, ImageFont

def make_lines(text, max_width, font):
    text = text.strip()
    #delete \n
    text = text.replace("\n", " ")
    words = text.split(" ")
    lines = []
    current_line = ""
    for word in words:
        if font.getlength(current_line + word)<= max_width:
            current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    #lines = '\n'.join(lines)
    return lines

def create_comment_screenshot(score, text, time_ago, output_path):
    # Configuración de la imagen
    img_width = 600
    img_height = 150
    background_color = (26, 26, 27)
    text_color = (255, 255, 255)
    score_color = (153, 170, 181)

    max_text_width = 500

    # Crear imagen en blanco
    img = Image.new('RGB', (img_width, img_height), color=background_color)
    draw = ImageDraw.Draw(img)

    # Cargar fuente
    font = ImageFont.truetype("static/Montserrat-Bold.ttf", 20)
    text_font = ImageFont.truetype("fonts/Roboto-Bold.ttf", 16)
    lines = make_lines(text, max_text_width, text_font)
    lines_number = len(lines)
    lines = '\n'.join(lines)

    profile_icon = Image.open("reddit_icon.png").resize((30, 30))
    img.paste(profile_icon, (10, 10))

    # Dibujar el puntaje
    draw.text((20, 50), f"{score}", fill=score_color, font=font)

    # Dibujar el nombre de usuario y el tiempo
    username_text = "User1234"
    draw.text((60, 10), username_text, fill=text_color, font=font)
    
    # Obtener las dimensiones del texto de nombre de usuario
    username_width = draw.textbbox((0, 0), username_text, font=font)[2]
    
    # Dibujar el tiempo transcurrido
    draw.text((60 + username_width + 10, 10), f"• {time_ago}", fill=score_color, font=font)

    # Dibujar el texto del comentario
    draw.text((60, 50), lines, fill=text_color, font=text_font)
    left, top, right, bottom = text_font.getbbox(text=lines)
    text_width = right - left
    text_height = bottom - top
    print(f"Text width: {text_width}, Text height: {text_height}")
    comment_icon = Image.open("low.png").resize((600, 40))
    comment_y_pos = 60 + (int(text_height)*lines_number) + 10
    img.paste(comment_icon, (0, comment_y_pos))
    #draw.text((85, comment_y_pos), "Reply", fill=text_color, font=text_font)
    """
    y_text = 50
    height = 20
    for line in lines:
        draw.text((60, y_text), line, fill=text_color, font=text_font)
        y_text += height

    """
    # Guardar la imagen
    img.save(output_path)

# Uso de la función
text = """
"if you tell the truth you won't be in trouble" yeah mom, I fell for that a few times and learned that lesson quickly.
"""
create_comment_screenshot(19, text, "3h ago", "output_comment.png")

