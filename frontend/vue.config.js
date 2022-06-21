module.exports = {
    pages: {
        index: {
            entry: 'src/main.ts',
            template: 'public/index-template.html',
            filename: 'index.html',
            title: 'CAVstudio'
        },
    },
    pluginOptions: {
        webpackBundleAnalyzer: {
            openAnalyzer: false,
            reportFilename: '/tmp/webpack-bundle-report.html',
        }
    },
    chainWebpack: config => {
        config.module
            .rule("vue")
            .use("vue-svg-inline-loader")
                .loader("vue-svg-inline-loader")
                .options({ /* ... */ });
    }
}
