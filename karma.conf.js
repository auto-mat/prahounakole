// Karma configuration
// Generated on Wed Jul 27 2016 12:07:36 GMT+0200 (CEST)

module.exports = function(config) {
  config.set({

    // base path that will be used to resolve all patterns (eg. files, exclude)
    basePath: '',


    // frameworks to use
    // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    frameworks: ['jasmine'],


    // list of files / patterns to load in the browser
    files: [
      {pattern: 'apps/cyklomapa/static/css/img/*', watched: false, included: false, served: true, nocache: false},
      {pattern: 'apps/cyklomapa/static/js/tests/kml/*', watched: false, included: false, served: true, nocache: false},
      'apps/cyklomapa/static/bow/jquery/dist/jquery.js',
      'apps/cyklomapa/static/js/tests/fake_methods.js',
      'apps/cyklomapa/static/bow/jquery.tools/index.js',
      'apps/cyklomapa/static/bow/jquery-hashchange/jquery.ba-hashchange.js',
      'apps/cyklomapa/static/bow/openlayers/OpenLayers.PNK.js',
      'apps/cyklomapa/static/bow/jqueryui/jquery-ui.js',
      'apps/cyklomapa/static/js/*.js',
      'apps/cyklomapa/static/js/tests/test_mapa.js',
    ],

    proxies: {
      "/static/": "/base/apps/cyklomapa/static/",
      "/kml/": "/base/apps/cyklomapa/static/js/tests/kml/",
    },

    // list of files to exclude
    exclude: [
    ],


    // preprocess matching files before serving them to the browser
    // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
    preprocessors: {
      'apps/cyklomapa/static/js/*.js': ['coverage']
    },


    // test results reporter to use
    // possible values: 'dots', 'progress'
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ['progress', 'coverage', 'coveralls'],


    coverageReporter: {
      type : 'lcov',
      dir : 'coverage/'
    },


    coverallsReporter: {
      repoToken: "nyQ5MkiPqrO3zxy5PTR3WZRIV0TwEonLF",
      dir : 'coverage/'
    },


    // web server port
    port: 9876,


    // enable / disable colors in the output (reporters and logs)
    colors: true,


    // level of logging
    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_INFO,


    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,


    // start these browsers
    // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
    browsers: ['Firefox'],


    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: false,

    // Concurrency level
    // how many browser should be started simultaneous
    concurrency: Infinity
  })
}
