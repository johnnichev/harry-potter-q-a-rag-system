import eslint from "@eslint/js";
import tseslint from "@typescript-eslint/eslint-plugin";
import tsparser from "@typescript-eslint/parser";

export default [
  eslint.configs.recommended,
  {
    files: ["src/**/*.{ts,tsx}"],
    languageOptions: {
      parser: tsparser,
      parserOptions: { ecmaVersion: "latest", sourceType: "module" },
      globals: {
        window: "readonly",
        document: "readonly",
        fetch: "readonly",
        Response: "readonly",
        TextDecoder: "readonly",
      },
    },
    plugins: { "@typescript-eslint": tseslint },
    rules: {
      "no-unused-vars": ["warn", { argsIgnorePattern: "^_", varsIgnorePattern: "^_" }],
      "no-empty": "warn",
      "no-undef": "off",
    },
  },
  {
    files: ["src/__tests__/**/*.{ts,tsx}", "src/test/**/*.ts"],
    languageOptions: {
      parser: tsparser,
      parserOptions: { ecmaVersion: "latest", sourceType: "module" },
      globals: { vi: "readonly", test: "readonly", expect: "readonly" },
    },
  },
];
