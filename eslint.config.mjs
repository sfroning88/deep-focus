import { createRequire } from "node:module";
import eslint from "@eslint/js";
import { defineConfig, globalIgnores } from "eslint/config";
import tseslint from "typescript-eslint";

const require = createRequire(import.meta.url);
const { flatConfig } = require("@next/eslint-plugin-next");

const nextCoreWebVitalsBlocks = Array.isArray(flatConfig.coreWebVitals)
    ? flatConfig.coreWebVitals
    : [flatConfig.coreWebVitals];

export default defineConfig([
    globalIgnores([
        "**/node_modules/**",
        "**/dist/**",
        "**/.next/**",
        "**/out/**",
        "**/build/**",
        "**/coverage/**",
        "**/prisma/src/generated/**",
    ]),
    eslint.configs.recommended,
    ...tseslint.configs.recommended,
    ...nextCoreWebVitalsBlocks.map((block) => ({
        ...block,
        files: block.files ?? ["**/*.{js,jsx,mjs,cjs,ts,tsx}"],
    })),
]);
