from SublimeLinter.lint import util, Linter


class ERBLint(Linter):
    """A linter for Embedded Ruby files (.erb)

    This class extends SublimeLinter.lint.Linter. It defines the most basic set
    of configs for running the 'out of the box' version of `erblint`

    An example output of `erblint ~/path/to/file.erb is:

    ```
    .erb-lint.yml not found: using default config
    Linting 1 files with 12 linters...

    ...

    Tag `input` is self-closing, it must end with `/>`.
    In file: path/to/file.html.erb:123

    ...

    12 error(s) were found in ERB files
    ```

    The regex defined below matches the error output from `erblint`. In order to
    ignore the extra warning (when not passing a config file to `erblint`) we
    set `error_stream` to `util.STREAM_STDOUT`.
    """
    regex = (
        r'^(?P<message>.*)\n'
        r'In file: .*:(?P<line>[0-9]+)'
    )
    multiline = True
    tempfile_suffix = 'erb'
    error_stream = util.STREAM_STDOUT
    defaults = {
        'selector': 'text.html.ruby'
    }

    def cmd(self):
        """Build command, using STDIN if a file path can be determined."""

        command = ['erblint']

        path = self.filename
        if not path:
            # File is unsaved, and by default unsaved files use the default
            # `erblint` config because they do not technically belong to a folder
            # that might contain a custom `.erb-lint.yml`. This means the lint
            # results may not match the rules for the currently open project.
            #
            # If the current window has open folders then we can use the
            # first open folder as a best-guess for the current projects
            # root folder - we can then pretend that this unsaved file is
            # inside this root folder, and `erblint` will pick up on any
            # config file if it does exist:
            folders = self.view.window().folders()
            if folders:
                path = os.path.join(folders[0], 'untitled.erb')

        if path:
            # With this path we can instead pass the file contents in via STDIN
            # and then tell `erblint` to use this path (to search for config
            # files and to use for matching against configured paths - i.e. for
            # inheritance, inclusions and exclusions).
            #
            configFileLocation = self.findConfig(path)
            print ("Path was found: '% s'" % configFileLocation)
            command += ['--config', configFileLocation]
            command += ['--stdin', path]
            # Ensure the files contents are passed in via STDIN:
            self.tempfile_suffix = None
            # self.tempfile_suffix = 'erb'
            # command += ['${temp_file}']
        else:
            self.tempfile_suffix = 'erb'
            command += ['${temp_file}']

        return command


    def findConfig(self, currentPath):
        # walk PARENT directories looking for `filename`:

        print ("Mission: Find file within '%s' directory" % currentPath)

        f = '.erb-lint.yml'
        # d = os.getcwd()
        d = os.path.dirname(currentPath)

        print ("Looking for this file: '%s' in '%s'" % (f, d))

        while d != "/" and f not in os.listdir(d):
            d = os.path.abspath(d + "/../")
            print ("Not found in '%s'" % d)

        if os.path.isfile(os.path.join(d,f)):
            print(f)

        return os.path.join(d,f)
