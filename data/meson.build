gnome = import('gnome')

message('Compiling resources')

gnome.compile_resources(
  meson.project_name(),
  meson.project_name() + '.gresource.xml',
  gresource_bundle: true,
  source_dir: '.',
  install_dir: DATA_DIR,
  install: true,
  dependencies: configure_file(
    input: 'AboutDialog.ui.in',
    output: 'AboutDialog.ui',
    configuration: conf
  )
)

message('Compiling schemas')
gnome.compile_schemas()
install_data(
  project_id + '.gschema.xml',
  install_dir: 'share/glib-2.0/schemas'
)

message('Making a .desktop file')
i18n.merge_file(
  output: project_id + '.desktop',
  input: project_id + '.desktop.in',
  po_dir: '../subprojects/po',
  type: 'desktop',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications')
)

message('Preparing appdata')
i18n.merge_file(
  output: project_id + '.appdata.xml',
  input: project_id + '.appdata.xml.in',
  po_dir: '../subprojects/po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'appdata')
)

message('Making a list of icons')
subdir('icons')
