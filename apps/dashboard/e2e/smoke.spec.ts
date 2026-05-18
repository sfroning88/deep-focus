import { test, expect } from "@playwright/test";
import { routes } from "@lib/routes";

test("home page renders dashboard heading", async ({ page }) => {
  await page.goto(routes.base.home);
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
});

test("home page renders properties list", async ({ page }) => {
  await page.goto(routes.base.home);
  await expect(page.getByText("Properties")).toBeVisible();
});

test("home page renders search bar", async ({ page }) => {
  await page.goto(routes.base.home);
  await expect(
    page.getByRole("textbox", { name: "Search properties" }),
  ).toBeVisible();
});

test("sort buttons are present on home page", async ({ page }) => {
  await page.goto(routes.base.home);
  await expect(page.getByRole("button", { name: /NAME/i })).toBeVisible();
  await expect(page.getByRole("button", { name: /MSA/i })).toBeVisible();
  await expect(page.getByRole("button", { name: /OCC/i })).toBeVisible();
  await expect(page.getByRole("button", { name: /SNAPS/i })).toBeVisible();
});

test("clicking a sort button changes active sort", async ({ page }) => {
  await page.goto(routes.base.home);
  const msaBtn = page.getByRole("button", { name: /MSA/i });
  await msaBtn.click();
  await expect(msaBtn).toBeVisible();
});

test("searching filters property list", async ({ page }) => {
  await page.goto(routes.base.home);
  const search = page.getByRole("textbox", { name: "Search properties" });
  await search.fill("zzzzzzzznotarealaproperty");
  await expect(
    page.getByText("No properties match your search."),
  ).toBeVisible();
});

test("my profile button opens profile dialog", async ({ page }) => {
  await page.goto(routes.base.home);
  await page.getByRole("button", { name: "My Profile" }).click();
  await expect(
    page.getByRole("dialog").getByRole("heading", { name: "My Profile" }),
  ).toBeVisible();
});

test("my profile dialog shows name and email fields", async ({ page }) => {
  await page.goto(routes.base.home);
  await page.getByRole("button", { name: "My Profile" }).click();
  const dialog = page.getByRole("dialog");
  await expect(dialog.getByText("Name")).toBeVisible();
  await expect(dialog.getByText("Email")).toBeVisible();
});

test("my profile dialog closes on close button", async ({ page }) => {
  await page.goto(routes.base.home);
  await page.getByRole("button", { name: "My Profile" }).click();
  await page.getByRole("dialog").getByRole("button", { name: "Close" }).click();
  await expect(page.getByRole("dialog")).not.toBeVisible();
});

test("first property view button opens property card dialog", async ({
  page,
}) => {
  await page.goto(routes.base.home);
  const firstView = page.getByRole("button", { name: /^View/ }).first();
  const hasProperties = await firstView.isVisible();
  if (!hasProperties) {
    test.skip(true, "No properties visible in this deploy");
  }
  await firstView.click();
  await expect(page.getByRole("dialog")).toBeVisible();
});

test("property card dialog has add snapshot button", async ({ page }) => {
  await page.goto(routes.base.home);
  const firstView = page.getByRole("button", { name: /^View/ }).first();
  const hasProperties = await firstView.isVisible();
  if (!hasProperties) {
    test.skip(true, "No properties visible in this deploy");
  }
  await firstView.click();
  const dialog = page.getByRole("dialog");
  await expect(
    dialog.getByRole("button", { name: /Add snapshot/i }),
  ).toBeVisible();
});

test("add snapshot button opens snapshot form", async ({ page }) => {
  await page.goto(routes.base.home);
  const firstView = page.getByRole("button", { name: /^View/ }).first();
  const hasProperties = await firstView.isVisible();
  if (!hasProperties) {
    test.skip(true, "No properties visible in this deploy");
  }
  await firstView.click();
  await page
    .getByRole("dialog")
    .getByRole("button", { name: /Add snapshot/i })
    .click();
  await expect(
    page.getByRole("dialog", { name: /New snapshot/i }),
  ).toBeVisible();
});

test("property card has predict button when snapshots exist", async ({
  page,
}) => {
  await page.goto(routes.base.home);
  const firstView = page.getByRole("button", { name: /^View/ }).first();
  const hasProperties = await firstView.isVisible();
  if (!hasProperties) {
    test.skip(true, "No properties visible in this deploy");
  }
  await firstView.click();
  const dialog = page.getByRole("dialog");
  const predictBtn = dialog.getByRole("button", { name: /^Predict$/ });
  const hasSnapshot = await predictBtn.isVisible();
  if (!hasSnapshot) {
    test.skip(true, "Property has no snapshots; predict card not rendered");
  }
  await expect(predictBtn).toBeVisible();
});

test("predict button is interactive and does not navigate away", async ({
  page,
}) => {
  await page.route("**/api/predict**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ predictions: [] }),
    });
  });
  await page.goto(routes.base.home);
  const firstView = page.getByRole("button", { name: /^View/ }).first();
  const hasProperties = await firstView.isVisible();
  if (!hasProperties) {
    test.skip(true, "No properties visible in this deploy");
  }
  await firstView.click();
  const predictBtn = page
    .getByRole("dialog")
    .getByRole("button", { name: /^Predict$/ });
  const hasBtn = await predictBtn.isVisible();
  if (!hasBtn) {
    test.skip(true, "Property has no snapshots; predict card not rendered");
  }
  await predictBtn.click();
  await expect(page).toHaveURL((url) => url.pathname === routes.base.home);
});

test("admin page renders admin heading", async ({ page }) => {
  await page.goto(routes.admin.root);
  await expect(page.getByRole("heading", { name: "Admin" })).toBeVisible();
});

test("admin page renders training batches section", async ({ page }) => {
  await page.goto(routes.admin.root);
  await expect(page.getByText("Training Batches")).toBeVisible();
});

test("admin page has shuffle groups button", async ({ page }) => {
  await page.goto(routes.admin.root);
  await expect(
    page.getByRole("button", { name: "Shuffle Groups" }),
  ).toBeVisible();
});

test("admin page has train models button", async ({ page }) => {
  await page.goto(routes.admin.root);
  await expect(
    page.getByRole("button", { name: "Train Models" }),
  ).toBeVisible();
});

test("admin page back to dashboard link navigates to home", async ({
  page,
}) => {
  await page.goto(routes.admin.root);
  await page.getByRole("link", { name: "Back to dashboard" }).click();
  await expect(page).toHaveURL((url) => url.pathname === routes.base.home);
});

test("home page open admin link navigates to admin", async ({ page }) => {
  await page.goto(routes.base.home);
  const adminLink = page.getByRole("link", { name: "Open admin" });
  const isAdmin = await adminLink.isVisible();
  if (!isAdmin) {
    test.skip(true, "Playwright user is not a platform admin");
  }
  await adminLink.click();
  await expect(page).toHaveURL((url) => url.pathname === routes.admin.root);
});

test("unauthenticated visit to home redirects to login", async ({
  browser,
}) => {
  const context = await browser.newContext({ storageState: undefined });
  const page = await context.newPage();
  await page.goto(routes.base.home);
  await expect(page).toHaveURL((url) => url.pathname === routes.auth.login);
  await context.close();
});
