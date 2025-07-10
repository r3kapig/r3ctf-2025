The binaries here are provided as reference only. As an alternative, you can also test your SVGs as follows:

* Download Debian Stretch/Buster/Bullseye/Bookworm.
* If you are using Debian Stretch, replace the source in /etc/apt/sources.list with `deb http://archive.debian.org/debian stretch main`.
* Run `sudo apt update`
* Run `sudo apt install librsvg2-bin`
* Convert your SVG file via `rsvg-convert exp.svg -o exp.png`