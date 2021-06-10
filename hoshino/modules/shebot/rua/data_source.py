from os import path

from PIL import Image, ImageDraw


def get_circle_avatar(avatar, size):
    # avatar.thumbnail((size, size))
    avatar = avatar.resize((size, size))
    scale = 5
    mask = Image.new('L', (size * scale, size * scale), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size * scale, size * scale), fill=255)
    mask = mask.resize((size, size), Image.ANTIALIAS)
    ret_img = avatar.copy()
    ret_img.putalpha(mask)
    return ret_img


def generate_gif(frame_dir: str, avatar: Image.Image) -> Image.Image:
    avatar_size = [(350, 350), (372, 305), (395, 283), (380, 305), (350, 372)]
    avatar_pos = [(50, 150), (28, 195), (5, 217), (5, 195), (50, 128)]
    imgs = []
    for i in range(5):
        im = Image.new(mode='RGBA', size=(600, 600))
        hand = Image.open(path.join(frame_dir, f'hand-{i + 1}.png'))
        hand = hand.convert('RGBA')
        avatar = get_circle_avatar(avatar, 350)
        avatar = avatar.resize(avatar_size[i])
        im.paste(avatar, avatar_pos[i], mask=avatar.split()[3])
        im.paste(hand, mask=hand.split()[3])
        mask = im.split()[3]
        mask = Image.eval(mask, lambda a: 255 if a <= 50 else 0)
        im = im.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
        im.paste(255, mask)
        imgs.append(im)
    out_path = path.join(frame_dir, 'output.gif')
    imgs[0].save(fp=out_path, save_all=True, append_images=imgs,
                 duration=25, loop=0, quality=80, transparency=255, disposal=3)
    return out_path
