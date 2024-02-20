import sys

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb_color):
    return '#{:02x}{:02x}{:02x}'.format(*rgb_color)

def relative_luminance(rgb_color):
    def channel_luminance(channel):
        channel /= 255.0
        return channel / 12.92 if channel <= 0.03928 else ((channel + 0.055) / 1.055) ** 2.4
    r, g, b = rgb_color
    return 0.2126 * channel_luminance(r) + 0.7152 * channel_luminance(g) + 0.0722 * channel_luminance(b)

def contrast_ratio(lum1, lum2):
    light = max(lum1, lum2) + 0.05
    dark = min(lum1, lum2) + 0.05
    return light / dark

def adjust_foreground_color(bg_lum, fg_rgb, target_ratio):
    current_contrast = contrast_ratio(bg_lum, relative_luminance(fg_rgb))
    adjusted_rgb = fg_rgb

    if current_contrast == target_ratio:
        return fg_rgb  # Return the original color if it already meets the target

    # Determine the direction of adjustment needed
    lighten = current_contrast < target_ratio

    # Adjust the foreground color
    for adjustment in range(256):
        adjustment_value = adjustment if lighten else -adjustment
        adjusted_rgb = tuple(max(0, min(255, channel + adjustment_value)) for channel in fg_rgb)
        new_contrast = contrast_ratio(bg_lum, relative_luminance(adjusted_rgb))

        if lighten and new_contrast >= target_ratio:
            return adjusted_rgb  # Return the first color that meets/exceeds the target when lightening
        elif not lighten and new_contrast <= target_ratio:
            return last_valid_rgb if new_contrast < target_ratio else adjusted_rgb  # Return the last color before dropping below the target when darkening

        last_valid_rgb = adjusted_rgb  # Update the last valid RGB value

    return last_valid_rgb  # Return the last valid adjustment if no exact match found

def main(bg_hex, fg_hex, target_ratio):
    bg_rgb = hex_to_rgb(bg_hex)
    fg_rgb = hex_to_rgb(fg_hex)
    
    bg_lum = relative_luminance(bg_rgb)
    fg_lum = relative_luminance(fg_rgb)
    
    adjusted_rgb = adjust_foreground_color(bg_lum, fg_rgb, target_ratio)
    adjusted_fg_hex = rgb_to_hex(adjusted_rgb)

    print(f"{adjusted_fg_hex}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 meetWCGARatio.py <background_hex> <foreground_hex> <target_contrast_ratio>")
        sys.exit(1)

    bg_hex = sys.argv[1]
    fg_hex = sys.argv[2]
    try:
        target_ratio = float(sys.argv[3])
    except ValueError:
        print("Please enter a valid number for the target contrast ratio.")
        sys.exit(1)

    main(bg_hex, fg_hex, target_ratio)
