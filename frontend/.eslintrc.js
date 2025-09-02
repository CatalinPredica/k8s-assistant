module.exports = {
  // Inherit the rules from ts-standard
  extends: 'standard-with-typescript',

  // This is the crucial part:
  // Tell the TypeScript parser where to find your project's configuration.
  parserOptions: {
    project: './tsconfig.json'
  },

  // You can add custom rules here if you ever need them
  rules: {
    // Example: '@typescript-eslint/strict-boolean-expressions': 'off'
  }
}
