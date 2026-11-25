(() => {
    const tokenKey = "newsuz-auth-token";
    const accountForms = document.querySelectorAll("[data-account-form]");
    const commentForms = document.querySelectorAll("[data-comment-form]");
    const logoutButtons = document.querySelectorAll("[data-logout]");
    let token = readToken();

    function readToken() {
        try {
            return sessionStorage.getItem(tokenKey);
        } catch {
            return null;
        }
    }

    function saveToken(value) {
        if (value) {
            sessionStorage.setItem(tokenKey, value);
        } else {
            try {
                sessionStorage.removeItem(tokenKey);
            } catch {
                // Local sign-out still clears this page's token below.
            }
        }
        token = value;
    }

    function localPath(value) {
        if (!value || !value.startsWith("/") || /^\/[/\\]/.test(value)) {
            return null;
        }

        const url = new URL(value, window.location.origin);
        if (url.origin !== window.location.origin || url.pathname.startsWith("//")) {
            return null;
        }
        return url.pathname + url.search + url.hash;
    }

    class APIError extends Error {
        constructor(status, payload) {
            super("So‘rov bajarilmadi.");
            this.status = status;
            this.payload = payload;
        }
    }

    async function api(path, { method = "GET", body, authenticated = false } = {}) {
        const endpoint = localPath(path);
        if (!endpoint) {
            throw new Error("So‘rov manzili topilmadi.");
        }

        const headers = { Accept: "application/json" };
        if (body !== undefined) {
            headers["Content-Type"] = "application/json";
        }
        if (authenticated && token) {
            headers.Authorization = "Token " + token;
        }

        const response = await fetch(endpoint, {
            method,
            headers,
            body: body === undefined ? undefined : JSON.stringify(body),
        });
        const payload = await response.json().catch(() => null);
        if (!response.ok) {
            throw new APIError(response.status, payload);
        }
        return payload;
    }

    function errorMessages(payload) {
        if (typeof payload === "string") {
            return [payload];
        }
        if (payload && typeof payload === "object") {
            return Object.values(payload).flatMap(errorMessages);
        }
        return [];
    }

    function describeError(error) {
        if (!(error instanceof APIError)) {
            return "Server bilan aloqa uzildi. Qayta urinib ko‘ring.";
        }
        if (error.status === 429) {
            return "Urinishlar limiti tugadi. Biroz kutib, qayta urinib ko‘ring.";
        }
        if (error.status === 401 || error.status === 403) {
            return "Davom etish uchun hisobingizga qayta kiring.";
        }
        if (error.status >= 500) {
            return "Serverda xato yuz berdi. Birozdan keyin qayta urinib ko‘ring.";
        }
        return errorMessages(error.payload).join(" ") ||
            "Ma’lumotlarni tekshirib, qayta urinib ko‘ring.";
    }

    function toggle(selector, visible) {
        document.querySelectorAll(selector).forEach((element) => {
            element.hidden = !visible;
        });
    }

    function showAccount(user) {
        const signedIn = Boolean(token);
        const name = user?.first_name || user?.username || "Hisobim";
        toggle("[data-guest]", !signedIn);
        toggle("[data-member]", signedIn);
        toggle("[data-comment-login]", !signedIn);
        toggle("[data-comment-form]", signedIn);
        document.querySelectorAll("[data-user-name]").forEach((element) => {
            element.textContent = name;
        });
    }

    function setStatus(form, message, state = "error") {
        const status = form.querySelector("[data-form-status]");
        if (status) {
            status.textContent = message;
            status.hidden = !message;
            status.dataset.state = state;
        }
    }

    function setBusy(form, busy) {
        form.setAttribute("aria-busy", String(busy));
        const button = form.querySelector('[type="submit"]');
        if (button) {
            button.disabled = busy;
        }
    }

    const query = new URLSearchParams(window.location.search);
    const next = localPath(query.get("next")) || "/";

    accountForms.forEach((form) => {
        const action = form.dataset.accountForm;
        if (action === "login" && query.get("registered") === "1") {
            setStatus(form, "Hisob yaratildi. Endi hisobingizga kiring.", "success");
        }

        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            if (form.getAttribute("aria-busy") === "true") {
                return;
            }
            setBusy(form, true);
            setStatus(form, "");
            const values = Object.fromEntries(new FormData(form));
            const credentials = {
                username: String(values.username || "").trim(),
                password: values.password,
            };

            try {
                if (action === "register") {
                    await api("/api/accounts/register/", {
                        method: "POST",
                        body: {
                            ...credentials,
                            email: String(values.email || "").trim(),
                            first_name: String(values.first_name || "").trim(),
                            last_name: String(values.last_name || "").trim(),
                            password_confirm: values.password_confirm,
                        },
                    });
                }

                try {
                    const result = await api("/api/accounts/login/", {
                        method: "POST",
                        body: credentials,
                    });
                    if (typeof result?.token !== "string" || !result.token) {
                        throw new Error("Login tokeni olinmadi.");
                    }
                    saveToken(result.token);
                } catch (error) {
                    if (action === "register") {
                        const params = new URLSearchParams({ registered: "1", next });
                        const loginPage = localPath(form.dataset.loginUrl) || "/login/";
                        window.location.assign(loginPage + "?" + params.toString());
                        return;
                    }
                    throw error;
                }
                window.location.assign(next);
            } catch (error) {
                setStatus(form, describeError(error));
            } finally {
                setBusy(form, false);
            }
        });
    });

    logoutButtons.forEach((button) => {
        button.addEventListener("click", async (event) => {
            event.preventDefault();
            if (button.disabled || !token) {
                return;
            }
            button.disabled = true;
            try {
                await api("/api/accounts/logout/", {
                    method: "POST",
                    authenticated: true,
                });
            } catch {
                // Clearing local credentials also signs out this browser tab.
            } finally {
                saveToken(null);
                showAccount();
                button.disabled = false;
            }
        });
    });

    commentForms.forEach((form) => {
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            if (!token || form.getAttribute("aria-busy") === "true") {
                return;
            }

            const text = String(new FormData(form).get("text") || "").trim();
            if (!text) {
                setStatus(form, "Izoh matnini yozing.");
                return;
            }

            setBusy(form, true);
            setStatus(form, "");
            try {
                await api(form.dataset.endpoint, {
                    method: "POST",
                    body: { text },
                    authenticated: true,
                });
                form.reset();
                setStatus(form, "Izoh yuborildi. Tasdiqlangach shu yerda chiqadi.", "success");
            } catch (error) {
                if (error.status === 401 || error.status === 403) {
                    saveToken(null);
                    showAccount();
                }
                setStatus(form, describeError(error));
            } finally {
                setBusy(form, false);
            }
        });
    });

    showAccount();
    if (token) {
        const initialToken = token;
        api("/api/accounts/me/", { authenticated: true })
            .then((user) => {
                if (token === initialToken) {
                    showAccount(user);
                }
            })
            .catch((error) => {
                if (token === initialToken && [401, 403].includes(error.status)) {
                    saveToken(null);
                    showAccount();
                }
            });
    }

    const progress = document.querySelector(".reading-progress");
    if (progress) {
        const updateProgress = () => {
            const maximum = document.documentElement.scrollHeight - window.innerHeight;
            const amount = maximum > 0 ? Math.min(1, Math.max(0, window.scrollY / maximum)) : 0;
            progress.style.transform = `scaleX(${amount})`;
        };
        updateProgress();
        window.addEventListener("scroll", updateProgress, { passive: true });
        window.addEventListener("resize", updateProgress);
        window.addEventListener("load", updateProgress, { once: true });
    }

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!reducedMotion && "IntersectionObserver" in window && Element.prototype.animate) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(({ target, isIntersecting }, index) => {
                if (!isIntersecting) {
                    return;
                }
                target.animate(
                    [
                        { opacity: 0.65, transform: "translateY(12px)" },
                        { opacity: 1, transform: "translateY(0)" },
                    ],
                    { duration: 360, delay: Math.min(index, 5) * 35, easing: "ease-out", fill: "none" },
                );
                observer.unobserve(target);
            });
        }, { threshold: 0.12 });
        document.querySelectorAll("[data-reveal]").forEach((element) => observer.observe(element));
    }
})();
