import pygame

def handle_input(key_input, event_list, tetris_game):
    """Handle player inputs."""
    if key_input[pygame.K_LEFT]:
        tetris_game.move_left()
    elif key_input[pygame.K_RIGHT]:
        tetris_game.move_right()

    if key_input[pygame.K_DOWN]:
        tetris_game.move_down()

    for event in event_list:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                tetris_game.hold()
            if event.key == pygame.K_z:
                tetris_game.rotate_ccw()
            if event.key == pygame.K_x:
                tetris_game.rotate_cw()
            if event.key == pygame.K_SPACE:
                tetris_game.hard_drop()
