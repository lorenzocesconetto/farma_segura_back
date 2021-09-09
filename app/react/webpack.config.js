const path = require("path");

const resolvePath = (relPath) => path.resolve(__dirname, relPath);

const cart = resolvePath("./src/Cart.js");
const orders = resolvePath("./src/Orders.js");
const outputDir = resolvePath("../static/");

const bundleName = "js/[name].js";
const imgName = "images/[name].[ext]";

module.exports = {
  entry: {
    cart,
    orders,
  },
  output: {
    path: outputDir,
    filename: bundleName,
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        use: {
          loader: "babel-loader",
          options: {
            presets: ["@babel/preset-react"],
          },
        },
      },
      {
        test: /\.(png|jpe?g|gif)$/,
        use: [
          {
            loader: "file-loader",
            options: {
              name: imgName,
              publicPath: "/static",
            },
          },
        ],
      },
    ],
  },
};
