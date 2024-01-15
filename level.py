from settings import *
from tile import Tile
from player import Player
from debug import debug
from support import *
from random import choice, randint
from weapon import Weapon
from ui import UI
from enemy import Enemy
from particles import AnimationPlayer
from magic import MagicPLayer
from update import Upgrade


class Level:
    def __init__(self):

        # get the display surface
        self.player = None
        self.display_surface = pygame.display.get_surface()
        self.game_paused = False

        # sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        # attack sprites
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        # sprite setup
        self.create_map()

        #user interface
        self.ui = UI()
        self.upgrade = Upgrade(self.player)

        # particles
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPLayer(self.animation_player)

    def create_player(self, x, y):
        self.player = Player(
            (x, y),
            [self.visible_sprites],
            self.obstacle_sprites,
            self.create_attack,
            self.destroy_attack,
            self.create_magic
        )

    def play_again(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        self.bigfont = pygame.font.Font(None, 80)
        self.smallfont = pygame.font.Font(None, 45)

        text = self.bigfont.render('You Died', 13, (0, 0, 0))
        textx = WIDTH / 2 - text.get_width() / 2
        texty = HEIGTH / 2 - text.get_height() / 2
        textx_size = text.get_width()
        texty_size = text.get_height()
        pygame.draw.rect(
            self.screen,
            (255, 255, 255, 0),
            ((textx - 5, texty - 5),
             (textx_size + 10, texty_size + 10)
             )
        )

        self.screen.blit(text, (WIDTH / 2 - text.get_width() / 2,
                           HEIGTH / 2 - text.get_height() / 2))

        clock = pygame.time.Clock()
        pygame.display.flip()
        in_main_menu = True

        while in_main_menu:
            clock.tick(50)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    in_main_menu = False
                    pygame.display.quit()
                    pygame.quit()
                    quit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = event.pos
                    if x >= textx - 5 and x <= textx + textx_size + 5:
                        if y >= texty - 5 and y <= texty + texty_size + 5:
                            in_main_menu = False
                            break

    def create_map(self):
        layouts = {
            'boundary': import_csv_layout('./map/map_FloorBlocks.csv'),
            'grass': import_csv_layout('./map/map_Grass.csv'),
            'object': import_csv_layout('./map/map_LargeObjects.csv'),
            'entities': import_csv_layout('./map/map_Entities.csv')
        }
        graphics = {
            'grass': import_folder('./graphics/grass'),
            'objects': import_folder('./graphics/objects')
        }

        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        if style == 'boundary':
                            Tile((x, y), [self.obstacle_sprites], 'invisible')

                        if style == 'grass':
                            # create grass tile
                            random_grass_image = choice(graphics['grass'])
                            Tile(
                                (x,y),
                                [self.visible_sprites,self.attackable_sprites],
                                'grass',
                                random_grass_image
                            )

                        if style == 'object':
                            surf = graphics['objects'][int(col)]
                            Tile((x,y), [self.visible_sprites,self.obstacle_sprites],'object', surf)

                        if style == 'entities':
                            if col == '394':
                                self.create_player(x,y)
                            else:
                                if col == '390': monster_name = 'bamboo'
                                elif col == '391': monster_name = 'spirit'
                                elif col == '392': monster_name = 'raccoon'
                                else: monster_name = 'squid'
                                Enemy(
                                    monster_name,(x,y),
                                    [self.visible_sprites, self.attackable_sprites],
                                    self.obstacle_sprites,
                                    self.damage_player,
                                    self.trigger_death_particles,
                                    self.add_exp
                                )

    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visible_sprites,self.attack_sprites])

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def create_magic(self, style, strength, cost):
        if style == "heal":
            self.magic_player.heal(self.player, strength, cost, [self.visible_sprites])
        if style == "flame":
            self.magic_player.flame(self.player, cost, [self.visible_sprites, self.attack_sprites])

    def player_attack_logic(self):
        if self.attackable_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite,self.attackable_sprites,False)
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if target_sprite.sprite_type == 'grass':
                            pos = target_sprite.rect.center
                            offset = pygame.math.Vector2(0, 75)
                            for leaf in range(randint(3, 6)):
                                self.animation_player.create_grass_particles(pos - offset,[self.visible_sprites])
                            target_sprite.kill()
                        else:
                            target_sprite.get_damage(self.player,attack_sprite.sprite_type)

    def damage_player(self, amount, attack_type):
        if self.player.vulnerable:
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time= pygame.time.get_ticks()
            self.animation_player.create_particles(attack_type, self.player.rect.center, [self.visible_sprites])
    def trigger_death_particles(self, pos, particle_type):
        self.animation_player.create_particles(particle_type, pos, self.visible_sprites)

    def add_exp(self, amount):
        self.player.exp += amount

    def toggle_menu(self):

        self.game_paused = not self.game_paused

    def run(self):
        self.visible_sprites.custom_draw(self.player)
        self.ui.display(self.player)
        debug(f"x:{self.player.rect.x}, y:{self.player.rect.y}, WPN: {self.player.weapon}, MGC: {self.player.magic}, STATE: {self.player.status}, HP: {self.player.health}, Alpha 10.0.1, DREI ABMAB")
        if self.game_paused:
            self.upgrade.display()
        else:
            self.visible_sprites.update()
            self.visible_sprites.enemy_update(self.player)
            self.player_attack_logic()

        if self.player.health <= 0:
            self.play_again()

            pygame.display.quit()
            pygame.quit()


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        # general set up
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        # CREATING THE FLOOR
        self.floor_surf = pygame.image.load('./graphics/tilemap/ground.png').convert()
        self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))

    def custom_draw(self, player):
        # getting the offset
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # drawing the floor
        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf, floor_offset_pos)

        # for sprite in self.sprites():
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

    def enemy_update(self,player):
        enemy_sprites = [sprite for sprite in self.sprites()  if hasattr(sprite,'sprite_type') and sprite.sprite_type == 'enemy']

        for enemy in enemy_sprites:
            enemy.enemy_update(player)
