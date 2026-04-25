export const PROVIDER_STALE_TIME = 60 * 1000;

export const COOKIE_MAX_AGE = 60 * 60 * 24 * 30;

export const USER_ID_COOKIE_NAME = "deep-focus-id";

export const COOKIE_BANNER_DISMISSED_KEY = "deep-focus-cookie-banner-dismissed";

export const COOKIE_BANNER_MESSAGE =
  "This site uses one first-party cookie for anonymous analytics. No third-party tracking.";

export const QUERY_STALE_TIME = 60 * 60 * 5;

export const QUERY_KEYS = {
  user: (userId: string) => ["user", userId] as const,
  properties: (userId: string) => ["properties", userId] as const,
  propertyCard: (userId: string, propertyId: string) =>
    ["propertyCard", userId, propertyId] as const,
};

export const CACHE_STALE_TIME = 60 * 60 * 60;

export const PRIVACY_DOC_PATH = "lib/docs/PRIVACY.md";

export const MOBILE_BREAKPOINT = 768;
