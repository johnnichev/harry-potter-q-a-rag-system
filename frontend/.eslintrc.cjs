module.exports = {
  root: true,
  env: { browser: true, es2022: true, node: true },
  parser: '@typescript-eslint/parser',
  parserOptions: { ecmaVersion: 'latest', sourceType: 'module' },
  plugins: ['@typescript-eslint', 'import'],
  extends: ['eslint:recommended', 'plugin:@typescript-eslint/recommended'],
  settings: { react: { version: 'detect' } },
  rules: {
    'import/order': ['error', { groups: [['builtin', 'external', 'internal'], ['parent', 'sibling', 'index']], 'newlines-between': 'always' }],
    'import/no-cycle': 'warn'
  }
}

