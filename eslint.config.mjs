import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";
import eslint from "@eslint/js";
import { defineConfig, globalIgnores } from "eslint/config";
import tseslint from "typescript-eslint";

const repoRoot = path.dirname(fileURLToPath(import.meta.url));

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
    {
        files: ["apps/dashboard/**/*.{ts,tsx}"],
        languageOptions: {
            parserOptions: {
                tsconfigRootDir: repoRoot,
                project: "./apps/dashboard/tsconfig.json",
            },
        },
    },
]);
