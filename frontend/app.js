const API_URL = window.PRICEPULSE_CONFIG.API_URL;
const TOKEN_KEY = "pricepulse_token";

const loginTab = document.querySelector("#tab-login");
const registerTab = document.querySelector("#tab-register");

const loginForm = document.querySelector("#login-form");
const registerForm = document.querySelector("#register-form");
const formMessage = document.querySelector("#form-message");

const authView = document.querySelector("#auth-view");
const dashboardView = document.querySelector("#dashboard-view");

const logoutButton = document.querySelector("#logout-button");
const userEmail = document.querySelector("#user-email");

const productModal = document.querySelector("#product-modal");
const openProductFormButton = document.querySelector(
    "#open-product-form"
);
const closeProductFormButton = document.querySelector(
    "#close-product-form"
);
const cancelProductFormButton = document.querySelector(
    "#cancel-product-form"
);
const productForm = document.querySelector("#product-form");
const productFormMessage = document.querySelector(
    "#product-form-message"
);

const activeTabClasses = [
    "bg-white",
    "text-slate-900",
    "shadow-sm",
];

const inactiveTabClasses = [
    "text-slate-500",
];


async function apiRequest(path, options = {}) {
    const response = await fetch(`${API_URL}${path}`, options);

    let data = null;

    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {
        let message = "Ocurrió un error inesperado.";

        if (typeof data?.detail === "string") {
            message = data.detail;
        }

        throw new Error(message);
    }

    return data;
}


function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}


function saveToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
}


function removeToken() {
    localStorage.removeItem(TOKEN_KEY);
}


function hideMessage() {
    formMessage.classList.add("hidden");
    formMessage.textContent = "";
}


function showFormMessage(message, type) {
    const colors = type === "error"
        ? "bg-red-50 text-red-700"
        : "bg-emerald-50 text-emerald-700";

    formMessage.textContent = message;
    formMessage.className =
        `mt-5 rounded-xl px-4 py-3 text-sm ${colors}`;
}


function showLogin() {
    loginForm.classList.remove("hidden");
    registerForm.classList.add("hidden");

    loginTab.classList.add(...activeTabClasses);
    loginTab.classList.remove(...inactiveTabClasses);

    registerTab.classList.remove(...activeTabClasses);
    registerTab.classList.add(...inactiveTabClasses);

    loginTab.setAttribute("aria-selected", "true");
    registerTab.setAttribute("aria-selected", "false");

    hideMessage();
}


function showRegister() {
    registerForm.classList.remove("hidden");
    loginForm.classList.add("hidden");

    registerTab.classList.add(...activeTabClasses);
    registerTab.classList.remove(...inactiveTabClasses);

    loginTab.classList.remove(...activeTabClasses);
    loginTab.classList.add(...inactiveTabClasses);

    registerTab.setAttribute("aria-selected", "true");
    loginTab.setAttribute("aria-selected", "false");

    hideMessage();
}


function showDashboard(email) {
    authView.classList.add("hidden");
    dashboardView.classList.remove("hidden");
    userEmail.textContent = email;
}


function showAuthentication() {
    dashboardView.classList.add("hidden");
    authView.classList.remove("hidden");
    showLogin();
}


function openProductModal() {
    productModal.classList.remove("hidden");
    productModal.classList.add("flex");

    document.querySelector("#product-url").focus();
}


function closeProductModal() {
    productModal.classList.add("hidden");
    productModal.classList.remove("flex");

    productForm.reset();
    productFormMessage.classList.add("hidden");
}


async function login(email, password) {
    const result = await apiRequest("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            email,
            password,
        }),
    });

    saveToken(result.access_token);

    const user = await apiRequest("/usuarios/me", {
        headers: {
            Authorization: `Bearer ${result.access_token}`,
        },
    });

    showDashboard(user.email);
}


async function restoreSession() {
    const token = getToken();

    if (!token) {
        showAuthentication();
        return;
    }

    try {
        const user = await apiRequest("/usuarios/me", {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });

        showDashboard(user.email);

    } catch {
        removeToken();
        showAuthentication();
    }
}


loginTab.addEventListener("click", showLogin);
registerTab.addEventListener("click", showRegister);


loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    hideMessage();

    const submitButton = loginForm.querySelector(
        'button[type="submit"]'
    );

    const formData = new FormData(loginForm);
    const email = formData.get("email");
    const password = formData.get("password");

    submitButton.disabled = true;
    submitButton.textContent = "Ingresando...";

    try {
        await login(email, password);
        loginForm.reset();

    } catch (error) {
        showFormMessage(error.message, "error");

    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Iniciar sesión";
    }
});


registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    hideMessage();

    const submitButton = registerForm.querySelector(
        'button[type="submit"]'
    );

    const formData = new FormData(registerForm);
    const email = formData.get("email");
    const password = formData.get("password");

    submitButton.disabled = true;
    submitButton.textContent = "Creando cuenta...";

    try {
        await apiRequest("/usuarios", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                email,
                password,
            }),
        });

        await login(email, password);
        registerForm.reset();

    } catch (error) {
        showFormMessage(error.message, "error");

    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Crear cuenta";
    }
});


logoutButton.addEventListener("click", () => {
    removeToken();
    showAuthentication();
});


openProductFormButton.addEventListener(
    "click",
    openProductModal
);

closeProductFormButton.addEventListener(
    "click",
    closeProductModal
);

cancelProductFormButton.addEventListener(
    "click",
    closeProductModal
);


productModal.addEventListener("click", (event) => {
    if (event.target === productModal) {
        closeProductModal();
    }
});


document.addEventListener("keydown", (event) => {
    if (
        event.key === "Escape"
        && !productModal.classList.contains("hidden")
    ) {
        closeProductModal();
    }
});


productForm.addEventListener("submit", (event) => {
    event.preventDefault();

    productFormMessage.textContent =
        "La creación del producto se conectará después.";

    productFormMessage.className =
        "mt-5 rounded-xl bg-blue-50 px-4 py-3 text-sm text-blue-700";
});


restoreSession();