import re

with open("/Users/mikehinford/Dropbox/Projects/CIC Website/CIC Air Quality Networks/LIVE UK AQ Networks/LIVE-uk-aq-webpage/hex_map.html", "r") as f:
    content = f.read()

shared_block = """
    <script>
      window.ukAqSharedAuth = (function() {
        const params = new URLSearchParams(window.location.search);
        const TURNSTILE_SITE_KEY_PLACEHOLDER = "0x4AAAAAADBX_LWQibZKSL8W";
        const turnstileSiteKeyParam = params.get("turnstile_site_key");
        const turnstileSiteKey = TURNSTILE_SITE_KEY_PLACEHOLDER.includes("__UK_AQ_TURNSTILE_SITE_KEY__")
          ? (turnstileSiteKeyParam || "")
          : (turnstileSiteKeyParam || TURNSTILE_SITE_KEY_PLACEHOLDER);

        const cacheBaseUrlParam = params.get("cache_base");
        function resolveCacheBaseUrl(rawValue) {
          const explicit = typeof rawValue === "string" ? rawValue.trim() : "";
          if (explicit) {
            return explicit.replace(/\\/+$/, "");
          }
          if (window.location.protocol === "http:" || window.location.protocol === "https:") {
            return `${window.location.origin.replace(/\\/$/, "")}/api/aq`;
          }
          return "https://cic-test.chronicillnesschannel.co.uk/api/aq";
        }
        const cacheBaseUrl = resolveCacheBaseUrl(cacheBaseUrlParam);
        const cacheOrigin = cacheBaseUrl ? new URL(cacheBaseUrl).origin : "";
        const defaultCacheSessionUrl = cacheOrigin ? `${cacheOrigin}/api/aq/session/start` : "";
        const cacheSessionParam = params.get("cache_session_url");
        const cacheSessionUrl = (cacheSessionParam || defaultCacheSessionUrl || "").trim();

        const CACHE_SESSION_SKEW_MS = 10000;
        const CACHE_SESSION_HINT_STORAGE_KEY = `uk_aq_cache_session_hint_v1:${cacheOrigin || "default"}:shared`;
        
        let cacheAuthToken = null;
        let cacheAuthTokenExpiresAt = 0;
        let cacheAuthInflight = null;
        let turnstileScriptInflight = null;
        let turnstileTokenInflight = null;
        let turnstileWidgetId = null;
        let turnstileTokenResolver = null;
        let turnstileTokenRejecter = null;
        let turnstileTokenTimeoutId = null;

        function readCacheSessionHintUntil() {
          try {
            const raw = window.localStorage.getItem(CACHE_SESSION_HINT_STORAGE_KEY);
            if (!raw) return 0;
            const parsed = Number(raw);
            return Number.isFinite(parsed) && parsed > 0 ? parsed : 0;
          } catch (_err) {
            return 0;
          }
        }

        function writeCacheSessionHintUntil(untilMs) {
          try {
            if (untilMs > 0) {
              window.localStorage.setItem(CACHE_SESSION_HINT_STORAGE_KEY, String(Math.floor(untilMs)));
            } else {
              window.localStorage.removeItem(CACHE_SESSION_HINT_STORAGE_KEY);
            }
          } catch (_err) {}
        }

        function syncCacheSessionHint() {
          const hintedUntil = readCacheSessionHintUntil();
          if (hintedUntil > cacheAuthTokenExpiresAt) {
            cacheAuthToken = "session";
            cacheAuthTokenExpiresAt = hintedUntil;
          }
        }

        function clearCacheAuthToken(clearSharedHint = true) {
          cacheAuthToken = null;
          cacheAuthTokenExpiresAt = 0;
          if (clearSharedHint) writeCacheSessionHintUntil(0);
        }

        function hasFreshCacheAuthToken() {
          syncCacheSessionHint();
          return Boolean(
            cacheAuthToken &&
            Date.now() < (cacheAuthTokenExpiresAt - CACHE_SESSION_SKEW_MS)
          );
        }

        syncCacheSessionHint();
        window.addEventListener("storage", (event) => {
          if (event.key === CACHE_SESSION_HINT_STORAGE_KEY) {
            syncCacheSessionHint();
          }
        });

        function ensureTurnstileContainer() {
          let container = document.getElementById("uk-aq-turnstile-widget-shared");
          if (!container) {
            container = document.createElement("div");
            container.id = "uk-aq-turnstile-widget-shared";
            container.style.display = "none";
            document.body.appendChild(container);
          }
          return container;
        }

        function clearTurnstilePendingState() {
          if (turnstileTokenTimeoutId) {
            clearTimeout(turnstileTokenTimeoutId);
            turnstileTokenTimeoutId = null;
          }
          turnstileTokenResolver = null;
          turnstileTokenRejecter = null;
        }

        async function ensureTurnstileScript() {
          if (window.turnstile && typeof window.turnstile.render === "function") return;
          if (!turnstileScriptInflight) {
            turnstileScriptInflight = new Promise((resolve, reject) => {
              const existing = document.getElementById("uk-aq-turnstile-script");
              if (existing) {
                existing.addEventListener("load", () => resolve(), { once: true });
                existing.addEventListener("error", () => reject(new Error("Failed to load Turnstile script.")), { once: true });
                return;
              }
              const script = document.createElement("script");
              script.id = "uk-aq-turnstile-script";
              script.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
              script.async = true;
              script.defer = true;
              script.onload = () => resolve();
              script.onerror = () => reject(new Error("Failed to load Turnstile script."));
              document.head.appendChild(script);
            });
          }
          await turnstileScriptInflight;
        }

        async function ensureTurnstileWidget() {
          if (!turnstileSiteKey) throw new Error("Missing Turnstile site key. Add ?turnstile_site_key=... to the URL.");
          await ensureTurnstileScript();
          if (turnstileWidgetId !== null) return;
          const turnstileApi = window.turnstile;
          if (!turnstileApi || typeof turnstileApi.render !== "function") throw new Error("Turnstile SDK unavailable.");
          const container = ensureTurnstileContainer();
          turnstileWidgetId = turnstileApi.render(container, {
            sitekey: turnstileSiteKey,
            appearance: "execute",
            execution: "execute",
            callback: (token) => {
              if (turnstileTokenResolver) {
                turnstileTokenResolver(token);
                clearTurnstilePendingState();
              }
            },
            "error-callback": () => {
              const _api = window.turnstile;
              if (_api && typeof _api.remove === "function" && turnstileWidgetId !== null) {
                _api.remove(turnstileWidgetId);
              }
              turnstileWidgetId = null;
              if (turnstileTokenRejecter) {
                turnstileTokenRejecter(new Error("Turnstile verification failed."));
                clearTurnstilePendingState();
              }
            },
            "expired-callback": () => {
              const _api = window.turnstile;
              if (_api && typeof _api.remove === "function" && turnstileWidgetId !== null) {
                _api.remove(turnstileWidgetId);
              }
              turnstileWidgetId = null;
              if (turnstileTokenRejecter) {
                turnstileTokenRejecter(new Error("Turnstile token expired."));
                clearTurnstilePendingState();
              }
            },
          });
        }

        async function getTurnstileToken() {
          await ensureTurnstileWidget();
          if (!turnstileTokenInflight) {
            turnstileTokenInflight = (async () => {
              const turnstileApi = window.turnstile;
              if (!turnstileApi || typeof turnstileApi.execute !== "function") throw new Error("Turnstile execute unavailable.");
              const token = await new Promise((resolve, reject) => {
                turnstileTokenResolver = resolve;
                turnstileTokenRejecter = reject;
                turnstileTokenTimeoutId = setTimeout(() => {
                  console.warn("Turnstile widget execution timed out. Could not obtain token.");
                  if (turnstileTokenRejecter) {
                    turnstileTokenRejecter(new Error("Turnstile token timed out."));
                  }
                  clearTurnstilePendingState();
                  if (turnstileWidgetId !== null && typeof turnstileApi.reset === "function") {
                    try { turnstileApi.reset(turnstileWidgetId); } catch(e) {}
                  }
                }, 30000);
                turnstileApi.execute(turnstileWidgetId);
              });
              return token;
            })().finally(() => {
              turnstileTokenInflight = null;
            });
          }
          return turnstileTokenInflight;
        }

        async function getCacheAuthToken(forceRefresh = false) {
          if (!forceRefresh && hasFreshCacheAuthToken()) return cacheAuthToken;
          if (!cacheSessionUrl) throw new Error("Missing cache session URL. Add ?cache_session_url=... to the URL.");
          if (!cacheAuthInflight) {
            cacheAuthInflight = (async () => {
              const turnstileToken = await getTurnstileToken();
              const response = await fetch(cacheSessionUrl, {
                method: "POST",
                headers: {
                  "Accept": "application/json",
                  "X-UK-AQ-Session-Init": "1",
                  "CF-Turnstile-Token": turnstileToken,
                },
                credentials: "include",
              });
              if (!response.ok) throw new Error(`Session start failed: ${response.status}`);
              const payload = await response.json().catch(() => ({}));
              const expiresIn = Number(payload?.session_expires_in);
              cacheAuthToken = "session";
              cacheAuthTokenExpiresAt = Date.now() + Math.max(
                30000,
                Math.floor((Number.isFinite(expiresIn) && expiresIn > 0 ? expiresIn : 300) * 1000)
              );
              writeCacheSessionHintUntil(cacheAuthTokenExpiresAt);
              return cacheAuthToken;
            })().finally(() => {
              cacheAuthInflight = null;
            });
          }
          return cacheAuthInflight;
        }

        async function fetchCacheApi(input, init = {}, retryOnAuthFailure = true, mapHooks = {}) {
          if (mapHooks && mapHooks.onStart) mapHooks.onStart();
          if (retryOnAuthFailure && !hasFreshCacheAuthToken()) {
            try { await getCacheAuthToken(false); } catch (_err) {}
          }
          try {
            const response = await fetch(input, { ...init, credentials: "include" });
            if (response.status === 401 && retryOnAuthFailure) {
              clearCacheAuthToken(false);
              await getCacheAuthToken(false);
              let retried = await fetch(input, { ...init, credentials: "include" });
              if (retried.status !== 401) return retried;
              clearCacheAuthToken();
              await getCacheAuthToken(true);
              retried = await fetch(input, { ...init, credentials: "include" });
              return retried;
            }
            return response;
          } finally {
            if (mapHooks && mapHooks.onEnd) mapHooks.onEnd();
          }
        }

        return {
          fetchCacheApi,
          getTurnstileToken,
          getCacheAuthToken
        };
      })();
    </script>
"""

# Replace block 1
block1_re = re.compile(r'      const CACHE_SESSION_SKEW_MS = 10000;\n      const CACHE_SESSION_HINT_STORAGE_KEY = `uk_aq_cache_session_hint_v1:\$\{cacheOrigin \|\| "default"\}:uk`;.*?window\.ukAqFetchCacheApi = fetchCacheApi;\n', re.DOTALL)

block1_sub = """      function setStatus(value) {
        if (!statusEl) {
          return;
        }
        statusEl.textContent = value;
        if (statusIndicator) {
          const isLive = value === "Live";
          statusIndicator.dataset.state = isLive ? "live" : "idle";
        }
      }

      if (endpointHint) {
        endpointHint.textContent = REST_URL
          ? `Endpoint: ${REST_URL} (${activeMap.label})`
          : "Missing cache endpoint base URL. Add ?cache_base=... to the URL.";
      }

      async function fetchCacheApi(input, init = {}, retryOnAuthFailure = true) {
        const timingId = nextHexMapTimingId();
        const requestLabel = getHexMapRequestLabel(input);
        return window.ukAqSharedAuth.fetchCacheApi(input, init, retryOnAuthFailure, {
          onStart: () => {
            markHexMapTiming(timingId, `fetch:${requestLabel}:start`);
          },
          onEnd: () => {
            markHexMapTiming(timingId, `fetch:${requestLabel}:end`);
            measureHexMapTiming(
              timingId,
              `fetch:${requestLabel}`,
              `fetch:${requestLabel}:start`,
              `fetch:${requestLabel}:end`
            );
          }
        });
      }
      window.ukAqFetchCacheApi = fetchCacheApi;
"""

new_content = block1_re.sub(block1_sub, content)

# Replace block 2
block2_re = re.compile(r'[\t ]*const CACHE_SESSION_SKEW_MS = 10000;\n[\t ]*const CACHE_SESSION_HINT_STORAGE_KEY = `uk_aq_cache_session_hint_v1:\$\{cacheOrigin \|\| "default"\}:cr`;.*?window\.ukAqFetchCacheApi = fetchCacheApi;\n', re.DOTALL)

block2_sub = """      function setStatus(value) {
        if (!statusEl) {
          return;
        }
        statusEl.textContent = value;
        if (statusIndicator) {
          const isLive = value === "Live";
          statusIndicator.dataset.state = isLive ? "live" : "idle";
        }
      }

      function updateEndpointHint() {
        if (!endpointHint) {
          return;
        }
        if (!REST_URL) {
          endpointHint.textContent = "Missing cache endpoint base URL. Add ?cache_base=... to the URL.";
          return;
        }
        const regionSuffix = activeRegion ? ` · ${activeRegion}` : "";
        endpointHint.textContent = `Endpoint: ${REST_URL} (${LA_CONFIG.label}${regionSuffix})`;
      }
      updateEndpointHint();

      async function fetchCacheApi(input, init = {}, retryOnAuthFailure = true) {
        const timingId = nextHexMapTimingId();
        const requestLabel = getHexMapRequestLabel(input);
        return window.ukAqSharedAuth.fetchCacheApi(input, init, retryOnAuthFailure, {
          onStart: () => {
            markHexMapTiming(timingId, `fetch:${requestLabel}:start`);
          },
          onEnd: () => {
            markHexMapTiming(timingId, `fetch:${requestLabel}:end`);
            measureHexMapTiming(
              timingId,
              `fetch:${requestLabel}`,
              `fetch:${requestLabel}:start`,
              `fetch:${requestLabel}:end`
            );
          }
        });
      }
      window.ukAqFetchCacheApi = fetchCacheApi;
"""

new_content = block2_re.sub(block2_sub, new_content)

# Insert shared block before line 6966: `    <script>\n      const PROJECT_REF_PLACEHOLDER`
insert_target = '    <script>\n      const PROJECT_REF_PLACEHOLDER'
new_content = new_content.replace(insert_target, shared_block + "\n" + insert_target)

with open("/Users/mikehinford/Dropbox/Projects/CIC Website/CIC Air Quality Networks/LIVE UK AQ Networks/LIVE-uk-aq-webpage/hex_map.html", "w") as f:
    f.write(new_content)

print("Done")
