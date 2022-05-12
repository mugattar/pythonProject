from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


TEMPLATE_PATH = 'files/invitation.png'
FONT_PATH = 'files/try-clother-bold.ttf'
FONT_SIZE = 15
BLACK = (0, 0, 0, 225)
NAME_OFFSET = (180, 180)
REPORT_OFFSET = (180, 210)


def generate_invitation(name, report):
    with Image.open(TEMPLATE_PATH).convert("RGBA") as base:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        draw = ImageDraw.Draw(base)
        draw.text(NAME_OFFSET, name, font=font, fill=BLACK)
        draw.text(REPORT_OFFSET, report, font=font, fill=BLACK)

        temp_file = BytesIO()
        base.save(temp_file, 'png')
        temp_file.seek(0)

        return temp_file

