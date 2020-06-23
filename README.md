# Convert Icon Fonts to SVG Sprites

This is a simple script that reads svg font files and converts
them into an svg sprite file. I use this script to convert icon
fonts into svg sprite files.

## Demo Website

[https://diafygi.github.io/svg-font-to-svg-sprite-converter/examples/](https://diafygi.github.io/svg-font-to-svg-sprite-converter/examples/)

## Example icon fonts that have been converted

* Font Awesome v4.7.0 - [sprite-fontawesome-4.7.0.svg](examples/sprite-fontawesome-4.7.0.svg)
* Glyphicons (from Bootstrap 3.3.7) - [sprite-bootstrap-3.3.7-glyphicons.svg](examples/sprite-bootstrap-3.3.7-glyphicons.svg)
* Material Icons 2.2.0 [sprites-materialicons-regular-2.2.0.svg](examples/sprites-materialicons-regular-2.2.0.svg)

## Manual

```
$ python svg_font_to_svg_sprite_converter.py --help
usage: svg_font_to_svg_sprite_converter.py [-h] [--css CSS]
                                           [--offset-relative]
                                           SVG_FONT

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

positional arguments:
  SVG_FONT           path to svg font file

optional arguments:
  -h, --help         show this help message and exit
  --css CSS          path to css file (if any)
  --offset-relative  use if viewbox is cut off
```


## License

The script is released under the MIT license. The example files for [Bootstrap 3.3.7 Glyphicons](https://getbootstrap.com/docs/3.3/components/#glyphicons), [Font Awesome 4.7.0](https://fontawesome.com/v4.7.0/) and [Material Icons 2.2.0](https://github.com/google/material-design-icons/tree/master/iconfont) are also open source.

