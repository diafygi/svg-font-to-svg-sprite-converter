import argparse, sys, re, textwrap

def convert_svg_font_to_svg_sprite(svg_font, css_file=None, offset_relative=False):
    result = ""
    # build a map of css names
    css_map = {}
    if css_file:
        for css_match in re.finditer(
            "\.([^:]+):{1,2}before\s*\{\s*content:\s*(?:\"|\')([^\"\']+)(?:\"|\')",
            css_file.read(),
            re.IGNORECASE|re.MULTILINE
        ):
            css_name, char = css_match.groups()
            # remove unicode escaping
            if char.startswith("\\"):
                char = char.lower().replace("\\", "")
            # populate the css map
            css_map[char] = css_name
    # find overall font size
    font_raw = svg_font.read()
    default_horiz_adv = int(re.search("<font[^>]+horiz-adv-x\s*=\s*(?:\"|\')([0-9\-\.]+)(?:\"|\')", font_raw).group(1))
    units_per_em = int(re.search("<font-face[^>]+units-per-em\s*=\s*(?:\"|\')([0-9\-\.]+)(?:\"|\')", font_raw).group(1))
    ascent = int(re.search("<font-face[^>]+ascent\s*=\s*(?:\"|\')([0-9\-\.]+)(?:\"|\')", font_raw).group(1))
    yoffset = units_per_em
    if offset_relative:
        yoffset = ascent
        sys.stderr.write("position:relative; top:{}em;\n".format(
            round(float(units_per_em - ascent)/float(units_per_em), 5)))
    # build map of glyph paths
    counter = -1
    for glyph_match in re.finditer(
        "<glyph[^>]+unicode\s*=\s*(?:\"|\')([^;\"\']+);*(?:\"|\')[^>]+d\s*=\s*(?:\"|\')([^\"]+)(?:\"|\')[^>]+>",
        font_raw,
        re.IGNORECASE|re.MULTILINE
    ):
        counter += 1
        glyph = glyph_match.group(0)
        char = glyph_match.group(1)
        name = char # default name is just the unicode character
        path_raw = glyph_match.group(2)
        # remove unicode binary prefix
        if char.startswith("&#x"):
            char = char.lower().replace("&#x", "", 1)
            name = char
        # override with glyph-name
        glyph_name_match = re.search("glyph-name\s*=\s*(?:\"|\')([^\"]+)(?:\"|\')", glyph)
        if glyph_name_match:
            name = glyph_name_match.group(1)
        # override with css name
        if char in css_map:
            name = css_map[char]
        # override horizontal advance
        width = default_horiz_adv
        horiz_adv_match = re.search("horiz-adv-x\s*=\s*(?:\"|\')([0-9]+)(?:\"|\')", glyph)
        if horiz_adv_match:
            width = int(horiz_adv_match.group(1))
        view_box = "0 0 {} {}".format(width, units_per_em)
        # convert path from bottom-y to top-y coordinate space
        path = ""
        for instruction_match in re.finditer("([MmHhVvLlQqCcTtSsAaZz])([0-9e\-\.\, ]*)", path_raw):
            instruction, val_raw = instruction_match.groups()
            # split the instruction value into an array of floats
            vals = re.findall("((?<!e)(?:^|\s|,|-)(?:[0-9\.]+(?:e-?[0-9\.]+|)))", val_raw)
            vals = [float(v.replace(" ", "").replace(",", "")) for v in vals]
            # translate y-coords (every 2nd value in many instructions)
            if instruction in "MLQCTS":
                vals = [(yoffset - v) if i % 2 == 1 else v for i, v in enumerate(vals)]
            elif instruction in "mlqcts":
                vals = [(-1 * v) if i % 2 == 1 else v for i, v in enumerate(vals)]
            # vertical line (a single y-coord)
            if instruction == "V":
                vals[0] = yoffset - vals[0]
            elif instruction == "v":
                vals[0] = -1 * vals[0]
            # arcto (rx,ry,xAxisRotate,LargeArcFlag,SweepFlag,x,y)
            if instruction in "A":
                vals[6] = yoffset - vals[6]
            elif instruction == "a":
                vals[6] = -1 * vals[6]
            # H, h, z don't have y-coordinates that need converting
            path += instruction + " ".join([str(int(v) if v == int(v) else v) for v in vals])
        # print the header
        if counter == 0:
            result += textwrap.dedent("""\
            <?xml version="1.0" encoding="UTF-8"?>
            <svg xmlns="http://www.w3.org/2000/svg">
            <defs>
            """)
        # print the symbol
        result += textwrap.dedent("""\
        <symbol id="{}" viewBox="{}" overflow="visible">
            <path d="{}"></path>
        </symbol>
        """.format(name, view_box, path))
        sys.stderr.write("""\
            <div>
                <svg class='icon'><use href='sprite-bootstrap-3.3.7-glyphicons.svg#{}'/></svg>
                <code>{}</code><br>
            </div>
""".format(name, name))
    # print the footer
    if counter >= 0:
        result += "</defs>\n</svg>\n"
    return result

def main(argv=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent("""\
            Convert an svg font to an svg sprite file.
            =============
            Example usage:
            python svg_font_to_svg_sprite_converter.py --css /tmp/bootstrap.css /tmp/fonts/glyphicons-halflings-regular.svg > /tmp/glyphicons-sprite.svg
            =============
            Using result in website:
            <style>.ico{position:relative;top:0;width:1em;height:1em;fill:currentColor;}</style>
            <body>
                ...
                <svg class='ico'><use href='glyphicons-sprite.svg#bookmark'/></svg>
                ...
            </body>
            =============
            """))
    parser.add_argument("svg_font", metavar='SVG_FONT', nargs=1, help="path to svg font file")
    parser.add_argument("--css", help="path to css file (if any)")
    parser.add_argument("--offset-relative", action='store_true', help="use if viewbox is cut off")
    args = parser.parse_args(argv)
    svg_font = open(args.svg_font[0])
    css_file = open(args.css) if args.css is not None else None
    offset_relative = args.offset_relative
    result = convert_svg_font_to_svg_sprite(svg_font, css_file=css_file, offset_relative=offset_relative)
    sys.stdout.write(result)
    sys.stdout.flush()

if __name__ == "__main__":
    main(sys.argv[1:])

