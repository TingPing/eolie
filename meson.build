project('eolie', 'c',
  version: '0.9.15',
  meson_version: '>= 0.40.0',
)
i18n = import('i18n')
python = import('python3')
project_id = 'org.gnome.Eolie'

message('Looking for dependencies')
python_bin = python.find_python()
if not python_bin.found()
    error('No valid python3 binary found')
else
    message('Found python3 binary')
endif
dependency('glib-2.0')
dependency('gobject-introspection-1.0', version: '>=1.35.9')
dependency('gtk+-3.0', version :'>=3.14')

env = environment()

python_dir = join_paths(get_option('prefix'), python.sysconfig_path('purelib'))
LIBEXEC_DIR = join_paths(get_option('prefix'), get_option('libexecdir'))
EXTENSION_DIR = join_paths(get_option('prefix'), get_option('libdir'), meson.project_name())
DATA_DIR = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
bindir = join_paths(get_option('prefix'), get_option('bindir'))

conf = configuration_data()
conf.set('PACKAGE_URL', 'https://github.com/gnumdk/eolie')
conf.set('DATA_DIR', DATA_DIR)
conf.set('EXTENSION_DIR', EXTENSION_DIR)
conf.set('LOCALE_DIR', join_paths(get_option('prefix'), get_option('datadir'), 'locale'))
conf.set('PYTHON_DIR', python_dir)
conf.set('PYTHON_EXEC_DIR', join_paths(get_option('prefix'), python.sysconfig_path('stdlib')))
conf.set('PYTHON', python_bin.path())
conf.set('libexecdir', LIBEXEC_DIR)
conf.set('VERSION', meson.project_version())

subdir('data')
subdir('python-webextension')
subproject('po')
subdir('search-provider')

install_subdir(
  'eolie',
  install_dir: python_dir
)

message('Preparing init file')
configure_file(
  input: 'eolie.in',
  output: 'eolie',
  configuration: conf,
  install_dir: bindir
)

meson.add_install_script('meson_post_install.py')
