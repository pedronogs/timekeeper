module.exports = {
  root: true,
  env: {
    node: true
  },
  plugins: ["es-beautifier"],
  extends: [
    "plugin:vue/vue3-essential",
    "plugin:es-beautifier/standard",
    "@vue/typescript/recommended"
  ],
  parserOptions: {
    parser: "@typescript-eslint/parser"
  },
  rules: {
    "no-console": process.env.NODE_ENV === "production" ? "warn" : "off",
    "no-debugger": process.env.NODE_ENV === "production" ? "warn" : "off",
    "comma-dangle": ["error", "never"],
    "linebreak-style": "off",
    "indent": 0
  }
};
