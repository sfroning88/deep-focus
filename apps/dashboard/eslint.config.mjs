import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";
import eslint from "@eslint/js";
import { defineConfig, globalIgnores } from "eslint/config";
import tseslint from "typescript-eslint";

/** Directory containing this config (`apps/dashboard`). Required in monorepos when multiple tsconfigs exist. */
const tsconfigRootDir = path.dirname(fileURLToPath(import.meta.url));

const require = createRequire(import.meta.url);
const { flatConfig } = require("@next/eslint-plugin-next");

const nextCoreWebVitalsBlocks = Array.isArray(flatConfig.coreWebVitals)
    ? flatConfig.coreWebVitals
    : [flatConfig.coreWebVitals];

/**
 * Load CJS plugin with `createRequire` so `flatConfig` is available in ESLint flat config.
 * @see https://nextjs.org/docs/app/api-reference/config/eslint
 */
const actionGuardNames =
    "createPublicAction|selfUserAction|platformAdminAction";
const routeAuthNames =
    "requireUser|requirePlatformAdmin";

/** Server actions: must be guard-wrapped const exports, not raw async exports. */
const actionFileRules = {
    "no-restricted-syntax": [
        "error",
        {
            selector:
                "ExportNamedDeclaration[declaration.type='FunctionDeclaration'][declaration.async=true]",
            message:
                "Exported async functions are not allowed in action files. Use `export const` values created via createPublicAction, selfUserAction, or platformAdminAction.",
        },
        {
            selector: "ExportNamedDeclaration > VariableDeclaration[kind!='const']",
            message:
                "Use `export const` in action files; do not export `let` or `var`.",
        },
        {
            selector: `ExportNamedDeclaration > VariableDeclaration > VariableDeclarator[id.name=/Action$/]:not(:has(CallExpression[callee.name=/^(${actionGuardNames})$/]))`,
            message: `Exported *Action values must be created via createPublicAction, selfUserAction, or platformAdminAction (from @focus/auth/server).`,
        },
    ],
};

/** app/api route handlers must call an auth helper inside the handler. */
const apiRouteRules = {
    "no-restricted-syntax": [
        "error",
        {
            selector: `ExportNamedDeclaration > FunctionDeclaration[id.name=/^(GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD)$/]:not(:has(CallExpression[callee.name=/^(${routeAuthNames})$/]))`,
            message: `Route handlers must call requireUser or requirePlatformAdmin (from @focus/auth/server).`,
        },
    ],
};

const eslintConfig = defineConfig([
    globalIgnores([
        ".next/**",
        "out/**",
        "build/**",
        "next-env.d.ts",
    ]),
    eslint.configs.recommended,
    ...tseslint.configs.recommended,
    ...nextCoreWebVitalsBlocks.map((block) => ({
        ...block,
        files: block.files ?? ["**/*.{js,jsx,mjs,cjs,ts,tsx}"],
    })),
    {
        files: [
            "app/**/actions.ts",
            "app/**/actions/*.ts",
            "app/**/(actions)/**/*.ts",
            "app/**/actions/**/*.ts",
            "lib/**/actions.ts",
            "lib/**/(actions)/**/*.ts",
            "lib/**/actions/*.ts",
            "lib/**/actions/**/*.ts",
        ],
        rules: actionFileRules,
    },
    {
        files: ["app/api/**/route.ts"],
        rules: apiRouteRules,
    },
    // After typescript-eslint configs so parserOptions win; pin monorepo tsconfig.
    {
        files: ["**/*.{ts,tsx}"],
        languageOptions: {
            parserOptions: {
                tsconfigRootDir,
                project: "./tsconfig.json",
            },
        },
    },
]);

export default eslintConfig;
