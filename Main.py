import pygame
import sys
import random
import time

# Initialize Pygame and Pygame Mixer for audio
pygame.init()
pygame.mixer.init()

# Updated screen dimensions and colors
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 800
WHITE = (255, 255, 255)
RED = (255, 70, 70)
GREEN = (70, 255, 70)
BLACK = (30, 30, 30)
YELLOW = (255, 255, 0)
BLUE = (100, 100, 255)
BG_COLOR = (40, 40, 60)

# Set up display with new dimensions
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Link-Legacy Game")

# Font for displaying text
font = pygame.font.SysFont("arial", 48, bold=True)
small_font = pygame.font.SysFont("arial", 24)
title_font = pygame.font.Font(None, 80)  # Use a larger font for the title

# Stand positions (adjusted for larger window)
stand_positions = {
    "T1": (200, 150), "T2": (400, 150), "T3": (600, 150),  
    "M1": (400, 300), "M2": (600, 300),                    
    "C1": (200, 400), "C2": (400, 400),                    
    "B1": (200, 600), "B2": (400, 600), "B3": (600, 600)  
}

connections = [
    ("T1", "T2"), ("T2", "T3"), ("T2", "M1"), ("M1", "M2"),
    ("C1", "C2"), ("B1", "B2"), ("B2", "B3"), ("M1", "C2"), ("C2", "B2")
]

def display_selection_screen(screen):
    """Display the game selection screen with title and mode choices."""
    screen.fill(BG_COLOR)
    
    # Draw 8-bit nostalgic title
    title_text = "Link-Legacy Game"
    title_surface = title_font.render(title_text, True, YELLOW)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
    screen.blit(title_surface, title_rect)

    # Display menu options
    menu_font = pygame.font.SysFont("arial", 36)
    text1 = menu_font.render("1: Player vs AI", True, WHITE)
    text2 = menu_font.render("2: Player vs Player", True, WHITE)
    screen.blit(text1, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
    screen.blit(text2, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50))
    pygame.display.flip()

    # Wait for player to select a game mode
    waiting = True
    game_mode = None
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    game_mode = "AI"
                    waiting = False
                elif event.key == pygame.K_2:
                    game_mode = "Player"
                    waiting = False

    return game_mode

class GameState:
    def __init__(self):
        self.stand_colors = {key: None for key in stand_positions.keys()}
        self.current_color = RED
        self.selected_stand = None
        self.game_mode = None
        self.possible_moves = []
        self.ai_thinking = False
        self.ai_move_start_time = 0
        self.ai_move_duration = 1.0
        self.initialize_random_stands()
        self.last_ai_move = None
        self.ai_repeat_count = 0

    def initialize_random_stands(self):
        empty_positions = list(stand_positions.keys())
        red_positions = random.sample(empty_positions, 3)
        for pos in red_positions:
            self.stand_colors[pos] = RED
            empty_positions.remove(pos)
        green_positions = random.sample(empty_positions, 3)
        for pos in green_positions:
            self.stand_colors[pos] = GREEN

    def get_valid_moves(self, stand_key):
        valid_moves = []
        for start, end in connections:
            if start == stand_key and self.stand_colors[end] is None:
                valid_moves.append(end)
            elif end == stand_key and self.stand_colors[start] is None:
                valid_moves.append(start)
        return valid_moves

    def make_move(self, from_key, to_key):
        self.stand_colors[to_key] = self.stand_colors[from_key]
        self.stand_colors[from_key] = None
        self.current_color = GREEN if self.current_color == RED else RED
        self.selected_stand = None
        self.possible_moves = []

def display_rules_screen(screen):
    """Display the game rules screen."""
    screen.fill(BG_COLOR)
    rules = [
        "Link-Legacy Game: Quick Rules",
        "Goal:",
        "- Align three pucks in the top row (T1, T2, T3) or bottom row (B1, B2, B3) to win.",
        "- Alternatively, block all moves of your opponent to win by default.",
        "Game Setup:",
        "- Player 1: Red pucks, Player 2: Green pucks.",
        "- Each player starts with three pucks placed randomly.",
        "Turn Mechanics:",
        "- Click your puck to select it and move to an adjacent empty spot.",
        "Win Conditions:",
        "- Align three pucks in a row, or block your opponent's moves.",
        "",
        "Press any key to start the game!"
    ]

    font = pygame.font.SysFont("arial", 24)
    y_offset = 60
    line_height = 35
    for line in rules:
        text_surface = font.render(line, True, WHITE)
        screen.blit(text_surface, (50, y_offset))
        y_offset += line_height

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False

def draw_game(screen, game_state):
    screen.fill(BG_COLOR)
    
    # Draw turn indicator
    turn_text = f"{'Red' if game_state.current_color == RED else 'Green'}'s Turn"
    turn_surface = small_font.render(turn_text, True, game_state.current_color)
    screen.blit(turn_surface, (10, 10))

    # Draw connections with gradient effect
    for start, end in connections:
        start_pos, end_pos = stand_positions[start], stand_positions[end]
        pygame.draw.line(screen, (200, 200, 200), start_pos, end_pos, 5)

    # Draw possible moves with a faint overlay
    for move in game_state.possible_moves:
        pygame.draw.circle(screen, BLUE, stand_positions[move], 20, 2)

    # Draw stands with gradient effect and shadow
    for key, pos in stand_positions.items():
        color = game_state.stand_colors[key] if game_state.stand_colors[key] else WHITE
        shadow_offset = (5, 5)
        if key == game_state.selected_stand:
            pygame.draw.circle(screen, YELLOW, pos, 20, 2)  
        pygame.draw.circle(screen, BLACK, (pos[0] + shadow_offset[0], pos[1] + shadow_offset[1]), 15)
        pygame.draw.circle(screen, color, pos, 15)

def check_consecutive_sequence(sequence, stand_colors, color):
    count = 0
    for stand in sequence:
        if stand_colors[stand] == color:
            count += 1
        else:
            count = 0
    return count >= 3

def check_winner(stand_colors):
    winning_sequences = [
        ["T1", "T2", "T3"], ["B1", "B2", "B3"]
    ]
    for sequence in winning_sequences:
        if check_consecutive_sequence(sequence, stand_colors, RED):
            return RED
        if check_consecutive_sequence(sequence, stand_colors, GREEN):
            return GREEN
    return None

def check_for_blocked_player(game_state):
    for key in game_state.stand_colors:
        if game_state.stand_colors[key] == game_state.current_color:
            if game_state.get_valid_moves(key):
                return False
    return True

def ai_select_move(game_state):
    best_moves = []
    critical_block = None
    
    for key, color in game_state.stand_colors.items():
        if color == GREEN:
            valid_moves = game_state.get_valid_moves(key)
            for move in valid_moves:
                temp_colors = game_state.stand_colors.copy()
                temp_colors[move] = GREEN
                temp_colors[key] = None
                if check_winner(temp_colors) == GREEN:
                    return key, move

            for move in valid_moves:
                temp_colors = game_state.stand_colors.copy()
                temp_colors[move] = GREEN
                temp_colors[key] = None
                if check_consecutive_sequence(["T1", "T2", "T3"], temp_colors, GREEN) or \
                   check_consecutive_sequence(["B1", "B2", "B3"], temp_colors, GREEN):
                    best_moves.append((key, move))

        elif color == RED:
            valid_moves = game_state.get_valid_moves(key)
            for move in valid_moves:
                temp_colors = game_state.stand_colors.copy()
                temp_colors[move] = RED
                temp_colors[key] = None
                if check_winner(temp_colors) == RED:
                    critical_block = (key, move)

    if critical_block:
        return critical_block
    
    if best_moves:
        new_move = random.choice(best_moves)
        if new_move == game_state.last_ai_move:
            game_state.ai_repeat_count += 1
        else:
            game_state.ai_repeat_count = 0
        if game_state.ai_repeat_count > 6:
            best_moves.remove(new_move)
            if best_moves:
                new_move = random.choice(best_moves)
            game_state.ai_repeat_count = 0
        game_state.last_ai_move = new_move
        return new_move

    ai_pieces = [k for k, v in game_state.stand_colors.items() if v == GREEN]
    for piece in ai_pieces:
        moves = game_state.get_valid_moves(piece)
        if moves:
            new_move = (piece, random.choice(moves))
            if new_move == game_state.last_ai_move:
                game_state.ai_repeat_count += 1
            else:
                game_state.ai_repeat_count = 0
            if game_state.ai_repeat_count > 6:
                moves.remove(new_move[1])
                if moves:
                    new_move = (piece, random.choice(moves))
                game_state.ai_repeat_count = 0
            game_state.last_ai_move = new_move
            return new_move

    return None, None

def play_victory_sound():
    try:
        pygame.mixer.music.load(r"Paste the path of Victory_sound.wav")
        pygame.mixer.music.play()
    except Exception as e:
        print("Error loading sound:", e)

def display_end_message(screen, message, color):
    text_surface = font.render(message, True, color)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text_surface, text_rect)
    
    continue_text = small_font.render("Press any key to return to menu", True, WHITE)
    continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(continue_text, continue_rect)
    
    pygame.display.flip()
    play_victory_sound()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False
    return True

def main():
    clock = pygame.time.Clock()
    
    while True:
        game_state = GameState()
        game_state.game_mode = display_selection_screen(screen)
        display_rules_screen(screen)
        
        game_active = True
        while game_active:
            clock.tick(60)
            current_time = time.time()

            if game_state.game_mode == "AI" and game_state.current_color == GREEN:
                if not game_state.ai_thinking:
                    game_state.ai_thinking = True
                    game_state.ai_move_start_time = current_time
                    from_key, to_key = ai_select_move(game_state)
                    if from_key and to_key:
                        game_state.selected_stand = from_key
                        game_state.possible_moves = [to_key]

                elif current_time - game_state.ai_move_start_time > game_state.ai_move_duration:
                    if game_state.selected_stand and game_state.possible_moves:
                        game_state.make_move(game_state.selected_stand, game_state.possible_moves[0])
                    game_state.ai_thinking = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and not game_state.ai_thinking:
                    mouse_pos = pygame.mouse.get_pos()
                    for key, pos in stand_positions.items():
                        if (mouse_pos[0] - pos[0]) ** 2 + (mouse_pos[1] - pos[1]) ** 2 < 20 ** 2:
                            if game_state.selected_stand:
                                if key in game_state.possible_moves:
                                    game_state.make_move(game_state.selected_stand, key)
                                else:
                                    game_state.selected_stand = None
                                    game_state.possible_moves = []
                            if game_state.stand_colors[key] == game_state.current_color:
                                game_state.selected_stand = key
                                game_state.possible_moves = game_state.get_valid_moves(key)
            
            draw_game(screen, game_state)
            
            winner = check_winner(game_state.stand_colors)
            if winner:
                if display_end_message(screen, f"{'Red' if winner == RED else 'Green'} Wins!", winner):
                    game_active = False
            
            if check_for_blocked_player(game_state):
                if display_end_message(screen, f"{'Red' if game_state.current_color == RED else 'Green'} is blocked!", YELLOW):
                    game_active = False

            pygame.display.flip()

if __name__ == "__main__":
    main()