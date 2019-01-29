var path = require('path')

module.exports = {
  'applicationPath': './title_ui',
  'sourcePath': './title_ui/assets/src',
  'destinationPath': './title_ui/assets/dist',
  'sassPath': 'scss/*.scss',
  'sassIncludePaths': [
    process.env.NODE_PATH,
    'node_modules'
  ],
  'localhost': 'localhost:8080'
}
