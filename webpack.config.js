const path = require("path");

module.exports = {
  entry: path.resolve(__dirname, "src", "app"),
  output: {
    path: path.resolve(__dirname, "public", "dist"),
    filename: "bundle.js",
    chunkFilename: "[name].bundle.js"
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader"]
      }
    ]
  },
  resolve: {
    extensions: [".json", ".js", ".css"]
  },
  devtool: "source-map"
};
