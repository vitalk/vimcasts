What is it?
-----------

Vim is a **great** text editor. The [Drew Neil](http://drewneil.com/) thinks so
and creates an awesome screencast series about Vim. That script allow to
download all [video archive](http://vimcasts.org/episodes/archive) in one shoot.


## Usage

Run script with `--help` flag to get help of available arguments.

```bash
./vimcasts.py --help

# Fetch all episodes starts from 42th in quicktime video format and save them
# into separate directory
./vimcasts.py --starts-from=42 --video-format=quicktime --formatstr='Vimcasts/{number}-{title}.{ext}'
```

## Copyrights

Created by Vital Kudzelka <vital.kudzelka@gmail.com>. Licensed under the [MIT
License](http://mit-license.org/vitalk).
