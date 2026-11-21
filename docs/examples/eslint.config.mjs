export default [
  {
    files: ["src/**/*.{js,mjs,cjs,jsx}"],
    rules: {
      complexity: ["error", 3],
      "max-lines": ["error", 12],
      "no-restricted-syntax": [
        "error",
        {
          selector: "ImportExpression:not([source.type='Literal'][source.value=type(string)])",
          message: "Use a literal string module specifier so dependency analysis can resolve it.",
        },
      ],
    },
  },
];
