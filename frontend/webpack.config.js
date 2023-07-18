// Generated using webpack-cli https://github.com/webpack/webpack-cli

const path = require("path");
const isProduction = process.env.NODE_ENV === "production";
const autoprefixer = require("autoprefixer");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const WebpackAssetsManifest = require("webpack-assets-manifest");
const {CleanWebpackPlugin} = require("clean-webpack-plugin");


const config = {
    entry: {
        main: "./src/index.ts",
        icons: "./src/scss/icons.scss",
    },
    output: {
        path: path.resolve(__dirname, "../static"),
        filename: "[name]-[contenthash].js",
    },
    resolve: {
        extensions: [".tsx", ".ts", ".js"],
    },
    plugins: [
       // new CleanWebpackPlugin(),
        new WebpackAssetsManifest({
            // Options go here
        }),
        new MiniCssExtractPlugin({
            filename: "[name]-[contenthash].css",
        }),
    ],
    optimization: {
        splitChunks: {
            cacheGroups: {
                vendor: {
                    test: /[\\/]node_modules[\\/]/,
                    name: "vendors",
                    chunks: "all"
                }
            }
        }
    },
    module: {
        rules: [
            {
                test: /\.(scss)$/,
                use: [MiniCssExtractPlugin.loader,
                    "css-loader",
                    {
                        // Loader for webpack to process CSS with PostCSS
                        loader: "postcss-loader",
                        options: {
                            postcssOptions: {
                                plugins: () => [
                                    autoprefixer
                                ]
                            }
                        }
                    },
                    {
                        // Loads a SASS/SCSS file and compiles it to CSS
                        loader: "sass-loader",
                        options: {
                            additionalData: "$brand-color: #4377FF;", // TODO: set during build job
                        },
                    },
                ]
            },
            {
                test: /\.tsx?$/,
                use: "ts-loader",
                exclude: /node_modules/,
            },
            /* {
                 test: /\.(woff(2)?|ttf|eot|svg)(\?v=\d+\.\d+\.\d+)?$/,
                 use: [
                     {
                         loader: "file-loader",
                         options: {
                             name: "[name].[contentHash].[ext]",
                             outputPath: "file/"
                         }
                     }
                 ]
             },*/
            /* {
                 mimetype: "image/svg+xml",
                 scheme: "data",
                 type: "asset/resource",
                 generator: {
                     filename: "icons/[hash].svg"
                 }
             } */
        ]
    },

};

module.exports = () => {
    if (isProduction) {
        config.mode = "production";
    } else {
        config.mode = "development";
    }
    return config;
};