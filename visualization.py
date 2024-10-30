import pygame
import sys
import time

# Constants
CELL_SIZE = 40
FPS = 5
BG_COLOR = (255, 255, 255)

# Colors for different tiles
COLORS = {
    '#': (0, 0, 0),        # Wall - Black
    '@': (0, 0, 255),      # Ares - Blue
    '$': (139, 69, 19),    # Stone - Brown
    '.': (0, 255, 0),      # Goal - Green
    '+': (0, 0, 255),      # Ares in Goal - Blue (same as Ares)
    '*': (139, 69, 19),    # Stone in Goal - Brown (same as Stone)
    ' ': BG_COLOR,         # Free space - White
}

# Moves for each direction
MOVES = {
    'U': (-1, 0),
    'D': (1, 0),
    'L': (0, -1),
    'R': (0, 1)
}

def draw_map(screen, game_map):
    """Draw the Sokoban map on the pygame screen."""
    screen.fill(BG_COLOR)
    for y, row in enumerate(game_map):
        for x, tile in enumerate(row):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, COLORS.get(tile, BG_COLOR), rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)  # Tile border for better visibility

def update_map(game_map, ares_pos, new_pos, new_tile):
    """Update the game map for Ares' movement."""
    ay, ax = ares_pos
    ny, nx = new_pos
    game_map[ay][ax] = ' ' if game_map[ay][ax] == '@' else '.'  # Restore old Ares position
    game_map[ny][nx] = new_tile  # Update new Ares position

def apply_move(game_map, move, ares_pos):
    """Apply a move to Ares' position and handle stone pushing."""
    dy, dx = MOVES[move]
    ay, ax = ares_pos
    ny, nx = ay + dy, ax + dx  # New Ares position

    if game_map[ny][nx] in (' ', '.'):  # Free or Goal
        update_map(game_map, (ay, ax), (ny, nx), '@' if game_map[ny][nx] == ' ' else '+')
        return ny, nx
    elif game_map[ny][nx] in ('$','*'):  # Stone or Stone in Goal
        nny, nnx = ny + dy, nx + dx  # New Stone position
        if game_map[nny][nnx] in (' ', '.'):  # Space for stone to move
            game_map[nny][nnx] = '*' if game_map[nny][nnx] == '.' else '$'
            update_map(game_map, (ay, ax), (ny, nx), '@' if game_map[ny][nx] == '$' else '+')
            return ny, nx
    return ares_pos


def read_input_file(filename):
    """the function to read the input file"""

    with open(filename, 'r') as file:
        weights = list(map(int, file.readline().strip().split()))
        grid = [list(line.strip()) for line in file]
    return weights, grid

def read_output_file(filename):
    """the function to read the output file"""

    with open(filename, 'r') as file:
        lines = file.readlines()
        if len(lines) >= 3:
            moves = lines[2].strip()
        else:
            moves = ""
    return moves

def main():
    # Initial game map and moves
    for i in range(1, 10):
        input_filename = f'input-0{i}.txt'
        output_filename = f'output-0{i}.txt'
        
        _, raw_map = read_input_file(input_filename) 
        moves = read_output_file(output_filename)
        moves = moves.upper()  # Ensure moves are in uppercase

        # Convert raw map to 2D list for easier manipulation
        game_map = [list(row) for row in raw_map]

        # Find initial position of Ares
        ares_pos = next((y, x) for y, row in enumerate(game_map) for x, tile in enumerate(row) if tile == '@')

        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((len(game_map[0]) * CELL_SIZE, len(game_map) * CELL_SIZE))
        pygame.display.set_caption("Sokoban Visualization")
        clock = pygame.time.Clock()

        # Main loop
        for move in moves:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            ares_pos = apply_move(game_map, move, ares_pos)
            draw_map(screen, game_map)
            pygame.display.flip()
            clock.tick(FPS)

        # Wait before closing
        time.sleep(2)
        pygame.quit()

if __name__ == "__main__":
    main()
