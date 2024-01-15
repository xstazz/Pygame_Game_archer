import os
import sys
import pygame


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.walking_animation = load_animation('', 7)
        self.jump_animation = load_img_for_jump('', 7)
        self.image = self.walking_animation[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.creature_index = 0

    def update(self):
        # Update walking animation
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.image = self.walking_animation[self.creature_index]
            self.rect.x += creature_speed
            self.creature_index = (self.creature_index + 1) % len(self.walking_animation)
        elif keys[pygame.K_a]:
            self.image = pygame.transform.flip(self.walking_animation[self.creature_index], True, False)
            self.rect.x -= creature_speed
            self.creature_index = (self.creature_index + 1) % len(self.walking_animation)
        else:
            # Display 'pos.png' when nothing is pressed
            self.image = load_pos_image('pos.png')

        # Update jumping animation
        if is_jumping:
            if keys[pygame.K_a]:
                # Flip the image when jumping to the left
                self.image = pygame.transform.flip(self.jump_animation[self.creature_index], True, False)
            else:
                self.image = self.jump_animation[self.creature_index]


def load_image(name, folder='right', colorkey=None):
    fullname = os.path.join(folder, name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image.convert_alpha()


def load_animation(prefix, num_frames, folder='right'):
    images = [load_image(f'{prefix}{i}.png', folder) for i in range(num_frames)]
    return images


def load_pos_image(name):
    return load_image(name)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def load_img_for_jump(prefix, num_frames, folder='jump'):
    return load_animation(prefix, num_frames, folder)


def load_background(filename):
    return load_image(filename, folder='data')


def load_arrow():
    return load_image('arrow.png')


if __name__ == '__main__':
    pygame.init()
    size = width, height = 900, 900
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()

    walking_animation = load_animation('', 7)
    jump_animation = load_img_for_jump('', 7)
    arrow_image = load_arrow()

    creature_speed = 10
    is_jumping = False
    jump_count = 10
    in_air = False

    arrows = []

    player = Player(0, 0)
    camera = Camera()
    all_sprites = pygame.sprite.Group(player)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Spawn arrow when left mouse button is clicked
                arrow_x = player.rect.x + player.image.get_width() // 2
                arrow_y = player.rect.y + player.image.get_height() // 2
                arrow_direction = 1 if player.image in player.walking_animation else -1

                # Adjust arrow direction based on the cursor position
                if is_jumping:
                    cursor_x, cursor_y = pygame.mouse.get_pos()
                    angle = pygame.math.Vector2(cursor_x - arrow_x, cursor_y - arrow_y).angle_to((1, 0))
                    arrow_direction = 1 if -90 < angle < 90 else -1

                arrows.append({'x': arrow_x, 'y': arrow_y, 'direction': arrow_direction})

        keys = pygame.key.get_pressed()
        if keys[pygame.K_d] or keys[pygame.K_a]:
            player.update()

        if not is_jumping:
            if keys[pygame.K_SPACE]:
                is_jumping = True
                jump_count = 10
                in_air = True

        if is_jumping:
            player.update()
            if jump_count >= -10:
                neg = 1
                if jump_count < 0:
                    neg = -1
                player.rect.y -= (jump_count ** 2) * 0.5 * neg
                jump_count -= 1
            else:
                is_jumping = False
                in_air = False

        all_sprites.update()
        camera.update(player)

        for sprite in all_sprites:
            camera.apply(sprite)

        screen.fill((255, 255, 255))

        for sprite in all_sprites:
            screen.blit(sprite.image, (sprite.rect.x, sprite.rect.y))

        # Draw arrows
        for arrow in arrows:
            arrow['x'] += arrow['direction'] * 5  # Adjust arrow speed
            screen.blit(arrow_image, (arrow['x'], arrow['y']))

        pygame.display.flip()
        clock.tick(15)
