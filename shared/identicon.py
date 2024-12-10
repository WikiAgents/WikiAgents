import hashlib

from PIL import Image, ImageDraw


def hex_to_rgb(hex_color):
    """
    Converts a 6-digit hex string to an RGB tuple.

    Args:
        hex_color (str): A 6-digit hex color code.

    Returns:
        tuple: A tuple containing three integers for RGB.
    """
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def draw_image(matrix, hex_color, symmetrical=True):
    """
    Creates an identicon image based on a boolean matrix.

    Args:
        matrix (list of list of bool): 2D grid indicating pixel activation.
        hex_color (str): Hexadecimal color string for active pixels.
        symmetrical (bool): If true, ensures the matrix is horizontally symmetrical.

    Returns:
        PIL.Image.Image: Generated identicon image.
    """
    SQUARE_SIZE = 50
    IMAGE_SIZE = (5 * SQUARE_SIZE, 5 * SQUARE_SIZE)
    BG_COLOR = (214, 214, 214)  # Light gray
    PIXEL_COLOR = hex_to_rgb(hex_color)

    if symmetrical:
        for row in matrix:
            row[3], row[4] = row[1], row[0]  # Mirror first two columns

    image = Image.new("RGB", IMAGE_SIZE, BG_COLOR)
    draw = ImageDraw.Draw(image)

    for x, row in enumerate(matrix):
        for y, cell in enumerate(row):
            if cell:  # Active pixel
                top_left = (y * SQUARE_SIZE, x * SQUARE_SIZE)
                bottom_right = (
                    y * SQUARE_SIZE + SQUARE_SIZE,
                    x * SQUARE_SIZE + SQUARE_SIZE,
                )
                draw.rectangle([top_left, bottom_right], fill=PIXEL_COLOR)

    return image


def generate_identicon(text):
    """
    Generates an identicon image from a given string.

    Args:
        text (str): Input text to hash for identicon generation.

    Returns:
        PIL.Image.Image: The generated identicon as an image object.
    """
    if not text:
        raise ValueError("Input text cannot be empty.")

    md5hash = hashlib.md5(text.encode("utf-8")).hexdigest()
    color = md5hash[:6]  # First 6 characters for the color
    grid_size = 5
    matrix = [
        [int(md5hash[i * grid_size + j + 6], 16) % 2 == 0 for j in range(grid_size)]
        for i in range(grid_size)
    ]

    return draw_image(matrix, color)


# Example usage:
if __name__ == "__main__":
    name = "example_name"
    image = generate_identicon(name)
    image.show()  # Display the image
    image.save(f"{name}.png", "PNG")  # Save as a PNG file
