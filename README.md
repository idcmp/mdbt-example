I have something like this tool that I use to manage the Mixxx database.

Always, always, make a backup of your Mixxx database before using this tool.
You would be sad if suddenly it corrupted something. Don't be sad.


# Installation

You can install the dependencies globally or locally. If you're not
much of a python person, then install them locally so they don't
interfere with the rest of your system.

You'll need virtualenv installed:

```
virtualenv local
source local/bin/activate
pip install -r ./requirements/requirements.txt
python mdbt/main.py --help
```

# Running

```
cp $HOME/.mixxx/mixxxdb.sqlite backup.sqlite
python mdbt/main.py --db=$HOME/.mixxx/mixxxdb.sqlite --scrub
```

HTH
