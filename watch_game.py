"""
What Should I Watch? - Enhanced Pixel Art Game
A beautiful nature-themed pixel art application with sound effects!

Requirements:
pip install pygame

To run:
python watch_game.py
"""

import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen settings
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🎬 What Should I Watch?")
clock = pygame.time.Clock()

# Colors - Nature themed with enhanced palette
SKY_BLUE = (135, 206, 250)
DEEP_SKY = (70, 130, 180)
GRASS_GREEN = (124, 252, 0)
DARK_GREEN = (34, 139, 34)
TREE_GREEN = (46, 125, 50)
BROWN = (139, 69, 19)
YELLOW = (255, 215, 0)
ORANGE = (255, 165, 0)
PINK = (255, 105, 180)
PURPLE = (138, 43, 226)
WHITE = (255, 255, 255)
LIGHT_BLUE = (173, 216, 230)
RED = (220, 20, 60)
GOLD = (255, 215, 0)
MINT = (152, 251, 152)
CORAL = (255, 127, 80)
LAVENDER = (230, 230, 250)

# Generate simple sound effects procedurally
def create_sound(frequency, duration):
    """Create a simple beep sound"""
    sample_rate = 22050
    n_samples = int(round(duration * sample_rate))
    buf = []
    for i in range(n_samples):
        value = int(32767.0 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
        buf.append([value, value])
    sound = pygame.sndarray.make_sound(buf)
    return sound

# Create sound effects
try:
    click_sound = create_sound(800, 0.1)
    click_sound.set_volume(0.3)
    
    hover_sound = create_sound(600, 0.05)
    hover_sound.set_volume(0.15)
    
    success_sound = create_sound(1000, 0.2)
    success_sound.set_volume(0.25)
except:
    click_sound = None
    hover_sound = None
    success_sound = None

# Font
title_font = pygame.font.Font(None, 64)
option_font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 30)
result_font = pygame.font.Font(None, 36)
tiny_font = pygame.font.Font(None, 24)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-4, -2)
        self.color = color
        self.size = random.randint(4, 8)
        self.life = 40
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.life -= 1
    
    def draw(self, surface):
        if self.life > 0:
            alpha = int((self.life / 40) * 255)
            s = pygame.Surface((self.size, self.size))
            s.set_alpha(alpha)
            s.fill(self.color)
            surface.blit(s, (int(self.x), int(self.y)))

class Butterfly:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(HEIGHT // 2 - 100, HEIGHT // 2 + 50)
        self.speed = random.uniform(0.5, 1.5)
        self.flutter = 0
        self.color = random.choice([PINK, ORANGE, LAVENDER, CORAL])
    
    def update(self):
        self.x += self.speed
        self.flutter += 0.2
        self.y += math.sin(self.flutter) * 0.5
        if self.x > WIDTH + 50:
            self.x = -50
            self.y = random.randint(HEIGHT // 2 - 100, HEIGHT // 2 + 50)
    
    def draw(self, surface):
        wing_offset = int(abs(math.sin(self.flutter * 2)) * 4)
        # Left wing
        pygame.draw.circle(surface, self.color, (int(self.x - 5 - wing_offset), int(self.y)), 6)
        # Right wing
        pygame.draw.circle(surface, self.color, (int(self.x + 5 + wing_offset), int(self.y)), 6)
        # Body
        pygame.draw.circle(surface, BROWN, (int(self.x), int(self.y)), 3)

class Button:
    def __init__(self, x, y, width, height, text, color, emoji=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.emoji = emoji
        self.hover = False
        self.particles = []
        self.scale = 1.0
        self.hover_played = False
    
    def draw(self, surface):
        # Smooth scaling animation
        if self.hover:
            self.scale = min(1.08, self.scale + 0.02)
        else:
            self.scale = max(1.0, self.scale - 0.02)
        
        # Calculate scaled rect
        scaled_width = int(self.rect.width * self.scale)
        scaled_height = int(self.rect.height * self.scale)
        scaled_x = self.rect.centerx - scaled_width // 2
        scaled_y = self.rect.centery - scaled_height // 2
        scaled_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
        
        # Pixel art style with gradient
        border_color = tuple(min(c + 50, 255) for c in self.color) if self.hover else self.color
        
        # Shadow
        shadow_rect = scaled_rect.move(5, 5)
        pygame.draw.rect(surface, (0, 0, 0, 100), shadow_rect, border_radius=12)
        
        # Main button with gradient effect
        pygame.draw.rect(surface, border_color, scaled_rect, border_radius=12)
        inner_rect = scaled_rect.inflate(-10, -10)
        pygame.draw.rect(surface, tuple(max(c - 20, 0) for c in self.color), inner_rect, border_radius=10)
        
        # Highlight effect
        highlight_rect = pygame.Rect(scaled_rect.x + 10, scaled_rect.y + 10, 
                                     scaled_rect.width - 20, scaled_rect.height // 3)
        s = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (255, 255, 255, 40), s.get_rect(), border_radius=8)
        surface.blit(s, highlight_rect)
        
        # Emoji (larger and centered better)
        if self.emoji:
            emoji_surface = option_font.render(self.emoji, True, WHITE)
            emoji_rect = emoji_surface.get_rect(center=(scaled_rect.centerx, scaled_rect.centery - 20))
            surface.blit(emoji_surface, emoji_rect)
        
        # Text with shadow
        text_shadow = small_font.render(self.text, True, (0, 0, 0, 150))
        text_shadow_rect = text_shadow.get_rect(center=(scaled_rect.centerx + 2, 
                                                         scaled_rect.centery + (25 if self.emoji else 2)))
        surface.blit(text_shadow, text_shadow_rect)
        
        text_surface = small_font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=(scaled_rect.centerx, 
                                                   scaled_rect.centery + (25 if self.emoji else 0)))
        surface.blit(text_surface, text_rect)
        
        # Particles on hover
        if self.hover and random.random() < 0.4:
            self.particles.append(Particle(
                random.randint(scaled_rect.left, scaled_rect.right),
                scaled_rect.bottom,
                random.choice([YELLOW, ORANGE, PINK, LIGHT_BLUE, MINT])
            ))
        
        for particle in self.particles[:]:
            particle.update()
            particle.draw(surface)
            if particle.life <= 0:
                self.particles.remove(particle)
    
    def check_hover(self, pos):
        was_hover = self.hover
        self.hover = self.rect.collidepoint(pos)
        
        # Play sound on hover enter
        if self.hover and not was_hover and not self.hover_played and hover_sound:
            hover_sound.play()
            self.hover_played = True
        elif not self.hover:
            self.hover_played = False
        
        return self.hover

class Cloud:
    def __init__(self):
        self.x = random.randint(-100, WIDTH)
        self.y = random.randint(30, 180)
        self.speed = random.uniform(0.2, 0.6)
        self.size = random.randint(50, 90)
        self.puff_count = random.randint(3, 5)
    
    def update(self):
        self.x += self.speed
        if self.x > WIDTH + 150:
            self.x = -150
            self.y = random.randint(30, 180)
    
    def draw(self, surface):
        for i in range(self.puff_count):
            x_offset = i * (self.size // (self.puff_count - 1)) - self.size // 2
            y_offset = -abs(i - self.puff_count // 2) * (self.size // 8)
            radius = self.size // 3 + random.randint(-3, 3)
            pygame.draw.circle(surface, WHITE, 
                             (int(self.x + x_offset), int(self.y + y_offset)), radius)

class Flower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = random.choice([PINK, YELLOW, ORANGE, PURPLE, RED, CORAL])
        self.sway = 0
        self.sway_speed = random.uniform(0.03, 0.08)
        self.petal_count = random.choice([5, 6, 8])
    
    def update(self):
        self.sway += self.sway_speed
    
    def draw(self, surface):
        sway_angle = math.sin(self.sway) * 15
        
        # Stem with sway
        stem_end_x = self.x + math.sin(math.radians(sway_angle)) * 5
        pygame.draw.line(surface, DARK_GREEN, 
                        (self.x, self.y), 
                        (int(stem_end_x), self.y - 25), 4)
        
        # Leaf
        leaf_y = self.y - 12
        pygame.draw.circle(surface, TREE_GREEN, (int(self.x - 6), int(leaf_y)), 4)
        
        # Petals
        flower_x = stem_end_x
        flower_y = self.y - 25
        angle_step = 360 // self.petal_count
        for i in range(self.petal_count):
            angle = i * angle_step + sway_angle
            petal_x = flower_x + math.cos(math.radians(angle)) * 10
            petal_y = flower_y + math.sin(math.radians(angle)) * 10
            pygame.draw.circle(surface, self.color, (int(petal_x), int(petal_y)), 6)
        
        # Center
        pygame.draw.circle(surface, GOLD, (int(flower_x), int(flower_y)), 5)
        pygame.draw.circle(surface, ORANGE, (int(flower_x), int(flower_y)), 3)

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT // 2 - 50)
        self.twinkle = random.random() * 360
        self.speed = random.uniform(0.5, 2.0)
    
    def update(self):
        self.twinkle += self.speed
    
    def draw(self, surface):
        brightness = int(150 + 105 * abs(math.sin(math.radians(self.twinkle))))
        color = (brightness, brightness, 100)
        size = 2 if brightness > 200 else 1
        pygame.draw.circle(surface, color, (self.x, self.y), size)

class WatchApp:
    def __init__(self):
        self.state = "start"
        self.step = 0
        self.selections = {"type": "", "mood": "", "time": ""}
        self.recommendation = None
        self.clouds = [Cloud() for _ in range(6)]
        self.flowers = [Flower(random.randint(50, WIDTH - 50), HEIGHT - 40 - random.randint(0, 20)) 
                       for _ in range(20)]
        self.butterflies = [Butterfly() for _ in range(3)]
        self.stars = [Star() for _ in range(30)]
        
        # Animation
        self.bounce_offset = 0
        self.time = 0
        
        self.steps_data = [
            {
                "title": "What are you in the mood for?",
                "options": [
                    {"id": "movie", "text": "Movie", "color": PINK, "emoji": "🎬"},
                    {"id": "series", "text": "TV Series", "color": PURPLE, "emoji": "📺"},
                    {"id": "anime", "text": "Anime", "color": ORANGE, "emoji": "⭐"}
                ],
                "key": "type"
            },
            {
                "title": "How are you feeling?",
                "options": [
                    {"id": "happy", "text": "Happy & Upbeat", "color": YELLOW, "emoji": "😊"},
                    {"id": "sad", "text": "Sad & Reflective", "color": LIGHT_BLUE, "emoji": "😢"},
                    {"id": "excited", "text": "Excited & Energized", "color": CORAL, "emoji": "🤩"},
                    {"id": "chill", "text": "Relaxed & Chill", "color": MINT, "emoji": "😌"}
                ],
                "key": "mood"
            },
            {
                "title": "How much time do you have?",
                "options": [
                    {"id": "short", "text": "Quick Watch", "color": GRASS_GREEN, "emoji": "⚡"},
                    {"id": "medium", "text": "Moderate Time", "color": TREE_GREEN, "emoji": "⏰"},
                    {"id": "long", "text": "Long Session", "color": DARK_GREEN, "emoji": "🌙"}
                ],
                "key": "time"
            }
        ]
        
        # Enhanced recommendations database with more options
        self.recommendations_db = {
            "movie": {
                "happy": {
                    "short": [
                        ("Paddington 2", "Netflix", "Family Comedy", "103 min"),
                        ("Grand Budapest Hotel", "Disney+", "Comedy", "99 min"),
                        ("Sing Street", "Netflix", "Musical Comedy", "106 min"),
                        ("The Princess Bride", "Disney+", "Fantasy Comedy", "98 min"),
                        ("School of Rock", "Paramount+", "Comedy", "109 min")
                    ],
                    "medium": [
                        ("La La Land", "Netflix", "Musical Romance", "128 min"),
                        ("Crazy Rich Asians", "HBO Max", "Rom-Com", "120 min"),
                        ("The Intouchables", "Netflix", "Comedy Drama", "112 min"),
                        ("Little Miss Sunshine", "Hulu", "Comedy Drama", "101 min"),
                        ("Chef", "Netflix", "Comedy Drama", "114 min")
                    ],
                    "long": [
                        ("The Secret Life of Walter Mitty", "Disney+", "Adventure", "114 min"),
                        ("Amélie", "Netflix", "Romantic Comedy", "122 min"),
                        ("About Time", "Netflix", "Rom-Com Fantasy", "123 min"),
                        ("The Greatest Showman", "Disney+", "Musical", "105 min"),
                        ("Forrest Gump", "Paramount+", "Drama Comedy", "142 min")
                    ]
                },
                "sad": {
                    "short": [
                        ("Moonlight", "Netflix", "Drama", "111 min"),
                        ("Manchester by the Sea", "Prime", "Drama", "137 min"),
                        ("Room", "Hulu", "Drama", "118 min"),
                        ("Blue Valentine", "Netflix", "Romantic Drama", "112 min"),
                        ("The Fault in Our Stars", "Disney+", "Romance Drama", "126 min")
                    ],
                    "medium": [
                        ("Eternal Sunshine", "HBO Max", "Romantic Drama", "108 min"),
                        ("The Pursuit of Happyness", "Netflix", "Bio Drama", "117 min"),
                        ("A Beautiful Mind", "Paramount+", "Bio Drama", "135 min"),
                        ("Good Will Hunting", "Netflix", "Drama", "126 min"),
                        ("Dead Poets Society", "Disney+", "Drama", "128 min")
                    ],
                    "long": [
                        ("Schindler's List", "Netflix", "Historical", "195 min"),
                        ("The Green Mile", "HBO Max", "Drama", "189 min"),
                        ("The Shawshank Redemption", "Netflix", "Drama", "142 min"),
                        ("Requiem for a Dream", "HBO Max", "Drama", "102 min"),
                        ("Atonement", "Netflix", "Romance Drama", "123 min")
                    ]
                },
                "excited": {
                    "short": [
                        ("Mad Max: Fury Road", "HBO Max", "Action", "120 min"),
                        ("Baby Driver", "Netflix", "Action", "113 min"),
                        ("John Wick", "Peacock", "Action", "101 min"),
                        ("Edge of Tomorrow", "HBO Max", "Sci-Fi Action", "113 min"),
                        ("Kingsman", "Disney+", "Action Comedy", "129 min")
                    ],
                    "medium": [
                        ("Inception", "Netflix", "Sci-Fi Thriller", "148 min"),
                        ("The Dark Knight", "HBO Max", "Action", "152 min"),
                        ("The Matrix", "HBO Max", "Sci-Fi", "136 min"),
                        ("Casino Royale", "Prime", "Action", "144 min"),
                        ("Mission Impossible", "Paramount+", "Action", "147 min")
                    ],
                    "long": [
                        ("Interstellar", "Prime", "Sci-Fi", "169 min"),
                        ("Avengers: Endgame", "Disney+", "Action", "181 min"),
                        ("The Lord of the Rings", "HBO Max", "Fantasy", "178 min"),
                        ("Dune", "HBO Max", "Sci-Fi", "155 min"),
                        ("Blade Runner 2049", "Netflix", "Sci-Fi", "164 min")
                    ]
                },
                "chill": {
                    "short": [
                        ("Midnight in Paris", "Prime", "Romance", "94 min"),
                        ("Lost in Translation", "Netflix", "Drama", "102 min"),
                        ("Julie & Julia", "Netflix", "Comedy Drama", "123 min"),
                        ("The Secret Garden", "HBO Max", "Family Drama", "99 min"),
                        ("The Big Lebowski", "Peacock", "Comedy", "117 min")
                    ],
                    "medium": [
                        ("Moonrise Kingdom", "Peacock", "Comedy Drama", "94 min"),
                        ("Frances Ha", "Netflix", "Comedy Drama", "86 min"),
                        ("A Quiet Place", "Paramount+", "Thriller", "90 min"),
                        ("Call Me By Your Name", "Netflix", "Romance", "132 min"),
                        ("Lady Bird", "Netflix", "Comedy Drama", "94 min")
                    ],
                    "long": [
                        ("Pride and Prejudice", "Netflix", "Romance", "129 min"),
                        ("The Notebook", "Netflix", "Romance", "123 min"),
                        ("Begin Again", "Netflix", "Music Drama", "104 min"),
                        ("Her", "Netflix", "Sci-Fi Romance", "126 min"),
                        ("Brooklyn", "Netflix", "Romance Drama", "111 min")
                    ]
                }
            },
            "series": {
                "happy": {
                    "short": [
                        ("Brooklyn Nine-Nine", "Netflix", "Comedy", "22 min/ep"),
                        ("Parks & Recreation", "Peacock", "Comedy", "22 min/ep"),
                        ("The Good Place", "Netflix", "Comedy", "26 min/ep"),
                        ("Kim's Convenience", "Netflix", "Sitcom", "22 min/ep"),
                        ("New Girl", "Netflix", "Sitcom", "22 min/ep")
                    ],
                    "medium": [
                        ("Schitt's Creek", "Netflix", "Comedy", "22 min/ep"),
                        ("Ted Lasso", "Apple TV+", "Comedy", "30 min/ep"),
                        ("Abbott Elementary", "Hulu", "Comedy", "22 min/ep"),
                        ("Only Murders in the Building", "Hulu", "Comedy Mystery", "35 min/ep"),
                        ("Never Have I Ever", "Netflix", "Teen Comedy", "28 min/ep")
                    ],
                    "long": [
                        ("Modern Family", "Hulu", "Sitcom", "22 min/ep"),
                        ("Community", "Netflix", "Comedy", "25 min/ep"),
                        ("Jane the Virgin", "Netflix", "Comedy Drama", "42 min/ep"),
                        ("Emily in Paris", "Netflix", "Comedy", "30 min/ep"),
                        ("Gilmore Girls", "Netflix", "Comedy Drama", "44 min/ep")
                    ]
                },
                "sad": {
                    "short": [
                        ("Fleabag", "Prime", "Comedy Drama", "27 min/ep"),
                        ("After Life", "Netflix", "Dark Comedy", "25 min/ep"),
                        ("BoJack Horseman", "Netflix", "Animated Drama", "25 min/ep"),
                        ("Master of None", "Netflix", "Comedy Drama", "30 min/ep"),
                        ("Russian Doll", "Netflix", "Comedy Drama", "28 min/ep")
                    ],
                    "medium": [
                        ("This Is Us", "Hulu", "Drama", "42 min/ep"),
                        ("The Crown", "Netflix", "Historical", "58 min/ep"),
                        ("Normal People", "Hulu", "Romance Drama", "30 min/ep"),
                        ("13 Reasons Why", "Netflix", "Teen Drama", "60 min/ep"),
                        ("The Sinner", "Netflix", "Mystery Drama", "45 min/ep")
                    ],
                    "long": [
                        ("Breaking Bad", "Netflix", "Crime Drama", "47 min/ep"),
                        ("The Handmaid's Tale", "Hulu", "Dystopian", "52 min/ep"),
                        ("Dark", "Netflix", "Sci-Fi Mystery", "60 min/ep"),
                        ("Ozark", "Netflix", "Crime Drama", "60 min/ep"),
                        ("Better Call Saul", "Netflix", "Crime Drama", "46 min/ep")
                    ]
                },
                "excited": {
                    "short": [
                        ("The Boys", "Prime", "Action", "60 min/ep"),
                        ("Stranger Things", "Netflix", "Sci-Fi Horror", "51 min/ep"),
                        ("Squid Game", "Netflix", "Thriller", "50 min/ep"),
                        ("Peaky Blinders", "Netflix", "Crime Drama", "58 min/ep"),
                        ("Money Heist", "Netflix", "Heist Drama", "70 min/ep")
                    ],
                    "medium": [
                        ("Game of Thrones", "HBO Max", "Fantasy", "57 min/ep"),
                        ("The Mandalorian", "Disney+", "Sci-Fi", "40 min/ep"),
                        ("Vikings", "Netflix", "Historical Drama", "44 min/ep"),
                        ("The Witcher", "Netflix", "Fantasy", "60 min/ep"),
                        ("Arcane", "Netflix", "Animated Action", "41 min/ep")
                    ],
                    "long": [
                        ("Westworld", "HBO Max", "Sci-Fi", "62 min/ep"),
                        ("The Last of Us", "HBO Max", "Post-Apocalyptic", "60 min/ep"),
                        ("House of the Dragon", "HBO Max", "Fantasy", "68 min/ep"),
                        ("Succession", "HBO Max", "Drama", "60 min/ep"),
                        ("The Expanse", "Prime", "Sci-Fi", "43 min/ep")
                    ]
                },
                "chill": {
                    "short": [
                        ("British Bake Off", "Netflix", "Reality", "60 min/ep"),
                        ("Queer Eye", "Netflix", "Reality", "45 min/ep"),
                        ("Somebody Feed Phil", "Netflix", "Travel Food", "55 min/ep"),
                        ("Salt Fat Acid Heat", "Netflix", "Cooking", "60 min/ep"),
                        ("Nailed It!", "Netflix", "Reality Comedy", "33 min/ep")
                    ],
                    "medium": [
                        ("The Office", "Peacock", "Sitcom", "22 min/ep"),
                        ("Friends", "HBO Max", "Sitcom", "22 min/ep"),
                        ("How I Met Your Mother", "Hulu", "Sitcom", "22 min/ep"),
                        ("Arrested Development", "Netflix", "Sitcom", "22 min/ep"),
                        ("Grace and Frankie", "Netflix", "Comedy", "30 min/ep")
                    ],
                    "long": [
                        ("Bridgerton", "Netflix", "Period Drama", "60 min/ep"),
                        ("Downton Abbey", "Prime", "Period Drama", "66 min/ep"),
                        ("The Marvelous Mrs. Maisel", "Prime", "Comedy Drama", "55 min/ep"),
                        ("Virgin River", "Netflix", "Romance Drama", "44 min/ep"),
                        ("Sweet Magnolias", "Netflix", "Drama", "50 min/ep")
                    ]
                }
            },
            "anime": {
                "happy": {
                    "short": [
                        ("My Neighbor Totoro", "HBO Max", "Fantasy", "86 min"),
                        ("Kiki's Delivery Service", "HBO Max", "Fantasy", "103 min"),
                        ("Ponyo", "HBO Max", "Fantasy", "101 min"),
                        ("The Cat Returns", "HBO Max", "Fantasy", "75 min"),
                        ("Whisper of the Heart", "HBO Max", "Romance", "111 min")
                    ],
                    "medium": [
                        ("Haikyuu!!", "Crunchyroll", "Sports", "24 min/ep"),
                        ("Spy x Family", "Crunchyroll", "Comedy", "24 min/ep"),
                        ("Kaguya-sama: Love is War", "Crunchyroll", "Rom-Com", "24 min/ep"),
                        ("Fruits Basket", "Crunchyroll", "Romance Drama", "24 min/ep"),
                        ("K-On!", "Netflix", "Music Slice of Life", "24 min/ep")
                    ],
                    "long": [
                        ("One Piece", "Crunchyroll", "Adventure", "24 min/ep"),
                        ("Naruto", "Crunchyroll", "Action", "23 min/ep"),
                        ("My Hero Academia", "Crunchyroll", "Action", "24 min/ep"),
                        ("Fairy Tail", "Crunchyroll", "Fantasy Action", "24 min/ep"),
                        ("Dragon Ball Z", "Crunchyroll", "Action", "24 min/ep")
                    ]
                },
                "sad": {
                    "short": [
                        ("Your Name", "Crunchyroll", "Romance", "106 min"),
                        ("A Silent Voice", "Netflix", "Drama", "130 min"),
                        ("Weathering With You", "HBO Max", "Romance Fantasy", "112 min"),
                        ("Grave of the Fireflies", "HBO Max", "War Drama", "89 min"),
                        ("The Garden of Words", "Netflix", "Romance", "46 min")
                    ],
                    "medium": [
                        ("Violet Evergarden", "Netflix", "Drama", "24 min/ep"),
                        ("Anohana", "Crunchyroll", "Drama", "23 min/ep"),
                        ("Your Lie in April", "Netflix", "Music Drama", "23 min/ep"),
                        ("March Comes in Like a Lion", "Crunchyroll", "Drama", "25 min/ep"),
                        ("Angel Beats!", "Crunchyroll", "Drama Fantasy", "24 min/ep")
                    ],
                    "long": [
                        ("Clannad: After Story", "Crunchyroll", "Drama", "24 min/ep"),
                        ("Steins;Gate", "Crunchyroll", "Sci-Fi Thriller", "24 min/ep"),
                        ("Tokyo Magnitude 8.0", "Crunchyroll", "Drama", "23 min/ep"),
                        ("Nana", "Crunchyroll", "Music Drama", "23 min/ep"),
                        ("Plastic Memories", "Crunchyroll", "Sci-Fi Drama", "24 min/ep")
                    ]
                },
                "excited": {
                    "short": [
                        ("One Punch Man", "Netflix", "Action Comedy", "24 min/ep"),
                        ("Demon Slayer", "Crunchyroll", "Action", "24 min/ep"),
                        ("Mob Psycho 100", "Crunchyroll", "Action Comedy", "24 min/ep"),
                        ("Redline", "Crunchyroll", "Racing Action", "102 min"),
                        ("Akira", "Hulu", "Sci-Fi Action", "124 min")
                    ],
                    "medium": [
                        ("Attack on Titan", "Crunchyroll", "Dark Fantasy", "24 min/ep"),
                        ("Jujutsu Kaisen", "Crunchyroll", "Action", "24 min/ep"),
                        ("Chainsaw Man", "Crunchyroll", "Action Horror", "24 min/ep"),
                        ("Black Clover", "Crunchyroll", "Fantasy Action", "24 min/ep"),
                        ("Fire Force", "Crunchyroll", "Action", "24 min/ep")
                    ],
                    "long": [
                        ("Hunter x Hunter", "Crunchyroll", "Adventure", "24 min/ep"),
                        ("Fullmetal Alchemist: Brotherhood", "Crunchyroll", "Adventure", "24 min/ep"),
                        ("Code Geass", "Crunchyroll", "Mecha Thriller", "24 min/ep"),
                        ("Death Note", "Netflix", "Psychological Thriller", "23 min/ep"),
                        ("Sword Art Online", "Crunchyroll", "Action Fantasy", "24 min/ep")
                    ]
                },
                "chill": {
                    "short": [
                        ("Spirited Away", "HBO Max", "Fantasy", "125 min"),
                        ("Howl's Moving Castle", "HBO Max", "Fantasy", "119 min"),
                        ("Castle in the Sky", "HBO Max", "Adventure", "125 min"),
                        ("The Wind Rises", "HBO Max", "Drama", "126 min"),
                        ("From Up on Poppy Hill", "HBO Max", "Romance", "91 min")
                    ],
                    "medium": [
                        ("Laid-Back Camp", "Crunchyroll", "Slice of Life", "24 min/ep"),
                        ("Barakamon", "Crunchyroll", "Slice of Life", "24 min/ep"),
                        ("Silver Spoon", "Crunchyroll", "Slice of Life", "23 min/ep"),
                        ("A Place Further Than the Universe", "Crunchyroll", "Adventure", "24 min/ep"),
                        ("Sweetness and Lightning", "Crunchyroll", "Slice of Life", "24 min/ep")
                    ],
                    "long": [
                        ("Mushishi", "Crunchyroll", "Supernatural", "24 min/ep"),
                        ("Non Non Biyori", "Crunchyroll", "Slice of Life", "24 min/ep"),
                        ("Aria the Animation", "Crunchyroll", "Slice of Life", "24 min/ep"),
                        ("Flying Witch", "Crunchyroll", "Slice of Life", "24 min/ep"),
                        ("Natsume's Book of Friends", "Crunchyroll", "Supernatural", "24 min/ep")
                    ]
                }
            }
        }
        
        self.buttons = []
        self.create_buttons()
    
    def create_buttons(self):
        self.buttons = []
        if self.state == "steps":
            current_step = self.steps_data[self.step]
            options = current_step["options"]
            
            if len(options) == 3:
                button_width = 260
                button_height = 130
                spacing = 45
                total_width = len(options) * button_width + (len(options) - 1) * spacing
                start_x = (WIDTH - total_width) // 2
                y = 360
                
                for i, opt in enumerate(options):
                    x = start_x + i * (button_width + spacing)
                    btn = Button(x, y, button_width, button_height, 
                               opt["text"], opt["color"], opt["emoji"])
                    btn.data = opt
                    self.buttons.append(btn)
            else:
                button_width = 230
                button_height = 110
                spacing_x = 35
                spacing_y = 25
                cols = 2
                rows = (len(options) + cols - 1) // cols
                total_width = cols * button_width + (cols - 1) * spacing_x
                start_x = (WIDTH - total_width) // 2
                start_y = 330
                
                for i, opt in enumerate(options):
                    row = i // cols
                    col = i % cols
                    x = start_x + col * (button_width + spacing_x)
                    y = start_y + row * (button_height + spacing_y)
                    btn = Button(x, y, button_width, button_height, 
                               opt["text"], opt["color"], opt["emoji"])
                    btn.data = opt
                    self.buttons.append(btn)
            
            # Back button
            if self.step > 0:
                self.buttons.append(Button(50, HEIGHT - 80, 140, 55, "← Back", BROWN))
        
        elif self.state == "result":
            self.buttons.append(Button(WIDTH // 2 - 260, HEIGHT - 110, 220, 65, 
                                      "Start Over", TREE_GREEN, "🔄"))
            self.buttons.append(Button(WIDTH // 2 + 40, HEIGHT - 110, 220, 65, 
                                      "Another One", PINK, "✨"))
    
    def draw_background(self):
        # Enhanced sky gradient
        for y in range(HEIGHT // 2):
            ratio = y / (HEIGHT // 2)
            color = (
                int(DEEP_SKY[0] + (SKY_BLUE[0] - DEEP_SKY[0]) * ratio),
                int(DEEP_SKY[1] + (SKY_BLUE[1] - DEEP_SKY[1]) * ratio),
                int(DEEP_SKY[2] + (SKY_BLUE[2] - DEEP_SKY[2]) * ratio)
            )
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))
        
        # Stars (twinkle)
        for star in self.stars:
            star.update()
            star.draw(screen)
        
        # Clouds
        for cloud in self.clouds:
            cloud.update()
            cloud.draw(screen)
        
        # Sun with glow
        sun_y = 90 + int(8 * math.sin(self.time * 0.5))
        # Glow
        for i in range(5, 0, -1):
            alpha_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
            alpha = 30 - i * 5
            pygame.draw.circle(alpha_surface, (*YELLOW, alpha), (50, 50), 40 + i * 4)
            screen.blit(alpha_surface, (WIDTH - 150, sun_y - 50))
        # Sun
        pygame.draw.circle(screen, YELLOW, (WIDTH - 100, sun_y), 42)
        pygame.draw.circle(screen, GOLD, (WIDTH - 100, sun_y), 38)
        
        # Ground with grass gradient
        for y in range(HEIGHT // 2, HEIGHT):
            ratio = (y - HEIGHT // 2) / (HEIGHT // 2)
            color = (
                int(GRASS_GREEN[0] + (DARK_GREEN[0] - GRASS_GREEN[0]) * ratio),
                int(GRASS_GREEN[1] + (DARK_GREEN[1] - GRASS_GREEN[1]) * ratio),
                int(GRASS_GREEN[2] + (DARK_GREEN[2] - GRASS_GREEN[2]) * ratio)
            )
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))
        
        # Grass blades
        for i in range(0, WIDTH, 25):
            grass_sway = math.sin(self.time * 0.5 + i * 0.1) * 3
            grass_x = i + int(grass_sway)
            grass_height = random.randint(20, 30)
            pygame.draw.line(screen, DARK_GREEN, 
                           (grass_x, HEIGHT // 2 + 10), 
                           (grass_x, HEIGHT // 2 + grass_height), 3)
        
        # Flowers
        for flower in self.flowers:
            flower.update()
            flower.draw(screen)
        
        # Butterflies
        for butterfly in self.butterflies:
            butterfly.update()
            butterfly.draw(screen)
    
    def draw_title(self, text, y=80):
        # Shadow with multiple layers
        for offset in range(5, 0, -1):
            shadow = title_font.render(text, True, (0, 0, 0, 50 - offset * 5))
            shadow_rect = shadow.get_rect(center=(WIDTH // 2 + offset, y + offset))
            screen.blit(shadow, shadow_rect)
        
        # Main text with bounce
        bounce = int(6 * math.sin(self.bounce_offset * 0.05))
        
        # Outline for better readability
        for dx, dy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (-3, 0), (3, 0), (0, -3), (0, 3)]:
            outline = title_font.render(text, True, PURPLE)
            outline_rect = outline.get_rect(center=(WIDTH // 2 + dx, y + bounce + dy))
            screen.blit(outline, outline_rect)
        
        title = title_font.render(text, True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, y + bounce))
        screen.blit(title, title_rect)
    
    def draw_steps_screen(self):
        self.draw_background()
        
        # Enhanced progress bar
        progress = (self.step + 1) / len(self.steps_data)
        bar_width = 650
        bar_x = (WIDTH - bar_width) // 2
        bar_y = 170
        
        # Bar container with border
        pygame.draw.rect(screen, BROWN, (bar_x - 6, bar_y - 6, bar_width + 12, 42), border_radius=25)
        pygame.draw.rect(screen, WHITE, (bar_x - 3, bar_y - 3, bar_width + 6, 36), border_radius=22)
        pygame.draw.rect(screen, (230, 230, 230), (bar_x, bar_y, bar_width, 30), border_radius=20)
        
        # Animated progress fill with gradient
        fill_width = int(bar_width * progress)
        if fill_width > 0:
            gradient_surf = pygame.Surface((fill_width, 30), pygame.SRCALPHA)
            for x in range(fill_width):
                ratio = x / bar_width
                color = (
                    int(GRASS_GREEN[0] + (MINT[0] - GRASS_GREEN[0]) * ratio),
                    int(GRASS_GREEN[1] + (MINT[1] - GRASS_GREEN[1]) * ratio),
                    int(GRASS_GREEN[2] + (MINT[2] - GRASS_GREEN[2]) * ratio)
                )
                pygame.draw.line(gradient_surf, color, (x, 0), (x, 30))
            screen.blit(gradient_surf, (bar_x, bar_y))
            
            # Progress shine effect
            shine_surf = pygame.Surface((fill_width, 15), pygame.SRCALPHA)
            pygame.draw.rect(shine_surf, (255, 255, 255, 60), shine_surf.get_rect(), border_radius=15)
            screen.blit(shine_surf, (bar_x, bar_y + 3))
        
        # Step indicator with shadow
        step_text = f"Step {self.step + 1} of {len(self.steps_data)}"
        step_shadow = small_font.render(step_text, True, (0, 0, 0, 100))
        step_shadow_rect = step_shadow.get_rect(center=(WIDTH // 2 + 2, bar_y + 57))
        screen.blit(step_shadow, step_shadow_rect)
        
        step_surface = small_font.render(step_text, True, BROWN)
        step_rect = step_surface.get_rect(center=(WIDTH // 2, bar_y + 55))
        screen.blit(step_surface, step_rect)
        
        # Title
        self.draw_title(self.steps_data[self.step]["title"], 260)
        
        # Buttons
        for btn in self.buttons:
            btn.draw(screen)
    
    def draw_result_screen(self):
        self.draw_background()
        
        # Enhanced result panel with layered shadows
        panel_width = 700
        panel_height = 380
        panel_x = (WIDTH - panel_width) // 2
        panel_y = 140
        
        # Multi-layer shadow
        for i in range(8, 0, -1):
            shadow_surf = pygame.Surface((panel_width + i * 2, panel_height + i * 2), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, 15 - i), shadow_surf.get_rect(), border_radius=25)
            screen.blit(shadow_surf, (panel_x - i, panel_y - i))
        
        # Main panel
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, LAVENDER, panel_rect, border_radius=22)
        pygame.draw.rect(screen, PURPLE, panel_rect, 6, border_radius=22)
        
        # Inner glow
        inner_glow = panel_rect.inflate(-20, -20)
        pygame.draw.rect(screen, WHITE, inner_glow, border_radius=18)
        
        # Animated popcorn
        popcorn_y = panel_y + 50 + int(12 * abs(math.sin(self.time * 0.15)))
        popcorn = option_font.render("🍿", True, WHITE)
        popcorn_rect = popcorn.get_rect(center=(WIDTH // 2, popcorn_y))
        screen.blit(popcorn, popcorn_rect)
        
        # "You should watch..." text
        you_should_shadow = result_font.render("You should watch...", True, (0, 0, 0, 80))
        screen.blit(you_should_shadow, you_should_shadow.get_rect(center=(WIDTH // 2 + 2, panel_y + 112)))
        
        you_should = result_font.render("You should watch...", True, PURPLE)
        screen.blit(you_should, you_should.get_rect(center=(WIDTH // 2, panel_y + 110)))
        
        # Recommendation title
        title, platform, genre, duration = self.recommendation
        
        # Title shadow
        title_shadow = title_font.render(title, True, (0, 0, 0, 100))
        title_shadow_rect = title_shadow.get_rect(center=(WIDTH // 2 + 3, panel_y + 173))
        screen.blit(title_shadow, title_shadow_rect)
        
        title_text = title_font.render(title, True, PINK)
        title_rect = title_text.get_rect(center=(WIDTH // 2, panel_y + 170))
        screen.blit(title_text, title_rect)
        
        # Details with icons
        details_y = panel_y + 240
        details = [
            (f"📺  {platform}", PURPLE),
            (f"🎭  {genre}", DARK_GREEN),
            (f"⏱️  {duration}", ORANGE)
        ]
        
        for i, (text, color) in enumerate(details):
            # Shadow
            detail_shadow = small_font.render(text, True, (0, 0, 0, 70))
            detail_shadow_rect = detail_shadow.get_rect(center=(WIDTH // 2 + 2, details_y + i * 42 + 2))
            screen.blit(detail_shadow, detail_shadow_rect)
            
            # Main text
            detail_text = small_font.render(text, True, color)
            detail_rect = detail_text.get_rect(center=(WIDTH // 2, details_y + i * 42))
            screen.blit(detail_text, detail_rect)
        
        # Buttons
        for btn in self.buttons:
            btn.draw(screen)
    
    def handle_selection(self, btn_data):
        if click_sound:
            click_sound.play()
        
        if hasattr(btn_data, 'text'):
            if "Back" in btn_data.text:
                self.step -= 1
                self.create_buttons()
                return
            elif "Start Over" in btn_data.text:
                self.reset()
                return
            elif "Another One" in btn_data.text:
                self.get_recommendation()
                return
        
        current_step = self.steps_data[self.step]
        self.selections[current_step["key"]] = btn_data["id"]
        
        if self.step < len(self.steps_data) - 1:
            self.step += 1
            self.create_buttons()
        else:
            self.get_recommendation()
    
    def get_recommendation(self):
        if success_sound:
            success_sound.play()
        
        recs = self.recommendations_db[self.selections["type"]][self.selections["mood"]][self.selections["time"]]
        self.recommendation = random.choice(recs)
        self.state = "result"
        self.create_buttons()
    
    def reset(self):
        self.state = "steps"
        self.step = 0
        self.selections = {"type": "", "mood": "", "time": ""}
        self.recommendation = None
        self.create_buttons()
    
    def run(self):
        if self.state == "start":
            self.state = "steps"
            self.create_buttons()
        
        running = True
        while running:
            self.time += 0.05
            self.bounce_offset += 1
            
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in self.buttons:
                        if btn.check_hover(mouse_pos):
                            if hasattr(btn, 'data'):
                                self.handle_selection(btn.data)
                            else:
                                self.handle_selection(btn)
                
                if event.type == pygame.MOUSEMOTION:
                    for btn in self.buttons:
                        btn.check_hover(mouse_pos)
            
            screen.fill(SKY_BLUE)
            
            if self.state == "steps":
                self.draw_steps_screen()
            elif self.state == "result":
                self.draw_result_screen()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = WatchApp()
    app.run()