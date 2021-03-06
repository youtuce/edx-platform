"""
Internationalization tasks
"""
import sys
import subprocess
from path import Path as path
from paver.easy import task, cmdopts, needs, sh

try:
    from pygments.console import colorize
except ImportError:
    colorize = lambda color, text: text  # pylint: disable=invalid-name


@task
@needs(
    "pavelib.prereqs.install_prereqs",
    "pavelib.i18n.i18n_validate_gettext",
    "pavelib.assets.compile_coffeescript",
)
@cmdopts([
    ("verbose", "v", "Sets 'verbose' to True"),
])
def i18n_extract(options):
    """
    Extract localizable strings from sources
    """
    verbose = getattr(options, "verbose", None)
    cmd = "i18n_tool extract"

    if verbose:
        cmd += " -vv"

    sh(cmd)


@task
def i18n_fastgenerate():
    """
    Compile localizable strings from sources without re-extracting strings first.
    """
    cmd = "i18n_tool generate"
    sh(cmd)


@task
@needs("pavelib.i18n.i18n_extract")
def i18n_generate():
    """
    Compile localizable strings from sources, extracting strings first.
    """
    cmd = "i18n_tool generate"
    sh(cmd)


@task
@needs("pavelib.i18n.i18n_extract")
def i18n_generate_strict():
    """
    Compile localizable strings from sources, extracting strings first.
    Complains if files are missing.
    """
    cmd = "i18n_tool generate"
    sh(cmd + " --strict")


@task
@needs("pavelib.i18n.i18n_extract")
def i18n_dummy():
    """
    Simulate international translation by generating dummy strings
    corresponding to source strings.
    """
    cmd = "i18n_tool dummy"
    sh(cmd)
    # Need to then compile the new dummy strings
    cmd = "i18n_tool generate"
    sh(cmd)


@task
def i18n_validate_gettext():
    """
    Make sure GNU gettext utilities are available
    """

    returncode = subprocess.call(['which', 'xgettext'])

    if returncode != 0:
        msg = colorize(
            'red',
            "Cannot locate GNU gettext utilities, which are "
            "required by django for internationalization.\n (see "
            "https://docs.djangoproject.com/en/dev/topics/i18n/"
            "translation/#message-files)\nTry downloading them from "
            "http://www.gnu.org/software/gettext/ \n"
        )

        sys.stderr.write(msg)
        sys.exit(1)


@task
def i18n_validate_transifex_config():
    """
    Make sure config file with username/password exists
    """
    home = path('~').expanduser()
    config = home / '.transifexrc'

    if not config.isfile or config.getsize == 0:
        msg = colorize(
            'red',
            "Cannot connect to Transifex, config file is missing"
            " or empty: {config} \nSee "
            "http://help.transifex.com/features/client/#transifexrc \n".format(
                config=config,
            )
        )

        sys.stderr.write(msg)
        sys.exit(1)


@task
@needs("pavelib.i18n.i18n_validate_transifex_config")
def i18n_transifex_push():
    """
    Push source strings to Transifex for translation
    """
    cmd = "i18n_tool transifex"
    sh("{cmd} push".format(cmd=cmd))


@task
@needs("pavelib.i18n.i18n_validate_transifex_config")
def i18n_transifex_pull():
    """
    Pull translated strings from Transifex
    """
    cmd = "i18n_tool transifex"
    sh("{cmd} pull".format(cmd=cmd))


@task
def i18n_rtl():
    """
    Pull all RTL translations (reviewed AND unreviewed) from Transifex
    """
    cmd = "i18n_tool transifex"
    sh(cmd + " rtl")

    print "Now generating langugage files..."

    cmd = "i18n_tool generate"

    sh(cmd + " --rtl")

    print "Committing translations..."
    sh('git clean -fdX conf/locale')
    sh('git add conf/locale')
    sh('git commit --amend')


@task
def i18n_ltr():
    """
    Pull all LTR translations (reviewed AND unreviewed) from Transifex
    """
    cmd = "i18n_tool transifex"
    sh(cmd + " ltr")

    print "Now generating langugage files..."

    cmd = "i18n_tool generate"

    sh(cmd + " --ltr")

    print "Committing translations..."
    sh('git clean -fdX conf/locale')
    sh('git add conf/locale')
    sh('git commit --amend')


@task
@needs(
    "pavelib.i18n.i18n_clean",
    "pavelib.i18n.i18n_transifex_pull",
    "pavelib.i18n.i18n_extract",
    "pavelib.i18n.i18n_dummy",
    "pavelib.i18n.i18n_generate_strict",
)
def i18n_robot_pull():
    """
    Pull source strings, generate po and mo files, and validate
    """
    # sh('paver test_i18n')
    # Tests were removed from repo, but there should still be tests covering the translations
    # TODO: Validate the recently pulled translations, and give a bail option
    sh('git clean -fdX conf/locale/rtl')
    sh('git clean -fdX conf/locale/eo')
    cmd = "i18n_tool validate"
    print "\n\nValidating translations with `i18n_tool validate`..."
    sh("{cmd}".format(cmd=cmd))

    con = raw_input("Continue with committing these translations (y/n)? ")

    if con.lower() == 'y':
        sh('git add conf/locale')

        sh(
            'git commit --message='
            '"Update translations (autogenerated message)" --edit'
        )


@task
def i18n_clean():
    """
    Clean the i18n directory of artifacts
    """
    sh('git clean -fdX conf/locale')


@task
@needs(
    "pavelib.i18n.i18n_extract",
    "pavelib.i18n.i18n_transifex_push",
)
def i18n_robot_push():
    """
    Extract new strings, and push to transifex
    """
    pass
