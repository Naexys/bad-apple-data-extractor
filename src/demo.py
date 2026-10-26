import pygame
import pygame.freetype
import json
import math

# Load all frames
def loadFrames(fileName):
    frames = None
    with open(f'output/{fileName}.json', 'r') as JSONFrames:
        frames = json.load(JSONFrames)
    return frames

# Display frame with chars
def blitChar(frame, screen, width, height, whiteSurface, blackSurface, charWhite, pixelSize):
    for line in range(height):
        for col in range(width):
            if frame[line][col] == charWhite:
                screen.blit(whiteSurface, (col * pixelSize, line * pixelSize))
            else:
                screen.blit(blackSurface, (col * pixelSize, line * pixelSize))

# Display frame with rectangles (binary frames)
def blitBin(frame, screen, width, height, blackSurface, pixelSize):
    for line in range(height):
        for col in range(width):
            if frame[line][col] == 0:
                screen.blit(blackSurface, (col * pixelSize, line * pixelSize))

# Start the demo
def startDemo(width, height, fileName, useChars, charWhite, charBlack, useMP3, useOGG, inputfps):
    # The pixel size, used for font and placing
    pixelSize = 10

    # Load the frames
    frames = loadFrames(fileName)

    # When audio synced, use higher frame rate to limit frameskips
    if useMP3 or useOGG:
        fps = inputfps * 2
    else:
        fps = inputfps

    # Start pygame
    pygame.init()

    # Load the music (if ther is music to be loaded); prioritize ogg format for its higher compression
    if useOGG:
        pygame.mixer.music.load(f'output/{fileName}.ogg')
    elif useMP3:
        pygame.mixer.music.load(f'output/{fileName}.mp3')

    # Check for sound and text
    if not pygame.font:
        print("Warning, fonts disabled")
    if not pygame.mixer:
        print("Warning, sound disabled")

    # Create a window
    screen = pygame.display.set_mode((width * pixelSize, height * pixelSize))
    clock = pygame.time.Clock()

    # Demo status
    running = True
    paused = False
    inverted = False

    # Colors
    bg = pygame.Color('white')
    fg = pygame.Color('black')

    # Text rendering
    font = pygame.freetype.Font(None, size=pixelSize)
    whiteChar = font.render(charWhite, fg)[0]
    blackChar = font.render(charBlack, fg)[0]

    # Rectangle rendering (for bin frame)
    blackRectangle = pygame.Surface((pixelSize, pixelSize))
    rectangle = pygame.Rect((0, 0), (pixelSize, pixelSize))
    pygame.draw.rect(blackRectangle, fg, rectangle)

    # Current frame index
    current = 0

    # Start the music (if there is)
    if useMP3 or useOGG:
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play()


    # Main loop
    while running:
        for event in pygame.event.get():
            # Handle quit event
            if event.type == pygame.QUIT:
                running = False
            # Handle key released events
            if event.type == pygame.KEYUP:
                # Pause / unpause the demo
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    paused = True if not paused else False
                    if paused and (useMP3 or useOGG):
                        pygame.mixer.music.pause()
                    elif useMP3 or useOGG:
                        pygame.mixer.music.unpause()
                # Switch every color for visibility
                if event.key == pygame.K_i and not paused:
                    inverted = True if not inverted else False
                    if inverted:
                        bg = pygame.Color('black')
                        fg = pygame.Color('white')
                    else:
                        bg = pygame.Color('white')
                        fg = pygame.Color('black')
                    whiteChar = font.render(charWhite, fg)[0]
                    blackChar = font.render(charBlack, fg)[0]
                    pygame.draw.rect(blackRectangle, fg, rectangle)
                # Increase the volume
                if event.key == pygame.K_UP and not paused:
                    if useMP3 or useOGG:
                        actualVolume = round(pygame.mixer.music.get_volume(), 1)
                        pygame.mixer.music.set_volume(actualVolume+0.1)
                # Decrease the volume
                if event.key == pygame.K_DOWN and not paused:
                    if useMP3 or useOGG:
                        actualVolume = round(pygame.mixer.music.get_volume(), 1)
                        pygame.mixer.music.set_volume(max(actualVolume-0.1, 0.0))
                # Restart animation and audio (if exists)
                if event.key == pygame.K_r and not paused:
                    current = 0
                    if useMP3 or useOGG:
                        pygame.mixer.music.stop()
                        pygame.mixer.music.play()

        # Handle keyboard inputs
        keys = pygame.key.get_pressed()
        # Quit the demo
        if keys[pygame.K_q] or keys[pygame.K_ESCAPE]:
            running = False            

        # When not paused
        if not paused:
            screen.fill(bg)
            if useChars:
                blitChar(frames[current], screen, width, height, whiteChar, blackChar, charWhite, pixelSize)
            else:
                blitBin(frames[current], screen, width, height, blackRectangle, pixelSize)

            if current < len(frames):
                if not useMP3 and not useOGG and current < len(frames) -1:
                    current += 1
                elif current < len(frames) -1:
                    musicProgress = pygame.mixer.music.get_pos()
                    musicProgressSec = musicProgress / 1000
                    current = min(math.floor(musicProgressSec * inputfps), len(frames)-1)


        # Refresh the screen
        pygame.display.flip()

        # Cap the framerate to the source framerate
        dt = clock.tick(fps) / 1000

    pygame.quit()