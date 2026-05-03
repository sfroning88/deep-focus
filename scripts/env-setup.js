#!/usr/bin/env node
/* eslint-disable */
const fs = require("fs");
const path = require("path");

// Determine environment
const env = process.argv[2] || "local";
const validEnvs = ["local", "prod"];

if (!validEnvs.includes(env)) {
  console.error(`Error: Environment must be one of: ${validEnvs.join(", ")}`);
  process.exit(1);
}

console.log(`Setting up environment: ${env}`);

// Source and destination paths
const sourcePath = path.join(process.cwd(), `.env.${env}`);
const destPath = path.join(process.cwd(), ".env");

// Check if source file exists
if (!fs.existsSync(sourcePath)) {
  console.error(`Error: Environment file ${sourcePath} does not exist`);
  process.exit(1);
}

// Copy the environment file
fs.copyFileSync(sourcePath, destPath);
console.log(`Copied ${sourcePath} to ${destPath}`);

// Check for local overrides
const localPath = path.join(process.cwd(), ".env.local");
if (fs.existsSync(localPath)) {
  console.log("Local overrides detected. These will take precedence.");
}

console.log("Environment setup complete!");
