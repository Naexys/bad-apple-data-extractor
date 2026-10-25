# Get the outputed frames file size
def getFramesDiskSpace(useChars, width, height, nbFrames):
    sizes = ['o', 'Ko', 'Mo', 'Go', 'To', 'Po']

    # Pixel disk space
    pixelSpace = 3 if useChars else 1
    # Line disk space (pixel * frames columns + ", " * frames columns -1 ( = spaces between pixels) + 2 ( = '[' and ']'))
    lineSpace = pixelSpace * width + 2 * (width-1) + 2
    # Frame disk space (same logic as line disk space)
    frameSpace = lineSpace * height + 2 * (height-1) + 2
    # File disk space (same logic as line disk space)
    fileSpace = frameSpace * nbFrames + 2 * (nbFrames-1) + 2

    # Find the correct extension
    extension = sizes[0]
    for i in range(1, len(sizes)):
        # If there is more than a thousand unit, got to next unit and round to 2 digits of precision
        if fileSpace > 1000:
            extension = sizes[i]
            fileSpace = round(fileSpace/1000, 2)

    # Return rounded size and size unit
    return str(fileSpace) + extension