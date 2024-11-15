import pygame
from tetris_game.tetris import Tetris

# Initialize the game window
pygame.init()
window_width, window_height = 600, 21 * 30  # 10 columns + room for hold and preview
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Tetris')

# Game clock to manage speed
clock = pygame.time.Clock()

# Initialize the game
game = Tetris()

def game_loop():
    running = True

    while running:
        screen.fill((0, 0, 0))  # Clear the screen

        # Get the current key state
        key_input = pygame.key.get_pressed()

        # Get all events from the event queue
        event_list = pygame.event.get()

        for event in event_list:
            if event.type == pygame.QUIT:
                running = False

        # Update the game state based on player input and events
        game.update(key_input, event_list)

        # Render the game
        game.draw(screen)

        # Update the display
        pygame.display.flip()

        # Control the game speed (e.g., 60 frames per second)
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    game_loop()
