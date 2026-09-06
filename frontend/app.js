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

const productsGrid = document.querySelector("#products-grid");
const productCardTemplate = document.querySelector(
    "#product-card-template"
);

const activeProductsCount = document.querySelector(
    "#active-products-count"
);
const reachedTargetsCount = document.querySelector(
    "#reached-targets-count"
);


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

        if (Array.isArray(data?.detail)) {
            message = data.detail
                .map((error) => error.msg)
                .join(" ");
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
    await loadProducts();
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
        await loadProducts();

    } catch {
        removeToken();
        showAuthentication();
    }
}

function formatPrice(value, currency) {
    if (value === null || value === undefined) {
        return "Sin precio";
    }

    return new Intl.NumberFormat("es-MX", {
        style: "currency",
        currency,
    }).format(Number(value));
}


function formatDate(value) {
    if (!value) {
        return "Sin revisiones";
    }

    return new Intl.DateTimeFormat("es-MX", {
        dateStyle: "medium",
        timeStyle: "short",
    }).format(new Date(value));
}


function renderProducts(products) {
    productsGrid.replaceChildren();

    const activeProducts = products.filter(
        (product) => product.activo
    );

    const reachedTargets = products.filter((product) => {
        if (product.precio_actual === null) {
            return false;
        }

        return (
            Number(product.precio_actual)
            <= Number(product.precio_objetivo)
        );
    });

    activeProductsCount.textContent = activeProducts.length;
    reachedTargetsCount.textContent = reachedTargets.length;

    if (products.length === 0) {
        const emptyState = document.createElement("div");

        emptyState.className =
            "col-span-full rounded-2xl border border-dashed " +
            "border-slate-300 bg-white px-6 py-14 text-center";

        const title = document.createElement("h2");
        title.className = "text-lg font-semibold";
        title.textContent = "Todavía no monitoreas productos";

        const description = document.createElement("p");
        description.className =
            "mx-auto mt-2 max-w-md text-sm text-slate-500";
        description.textContent =
            "Agrega un producto de Books to Scrape " +
            "y PricePulse comenzará a registrar su precio.";

        emptyState.append(title, description);
        productsGrid.append(emptyState);

        return;
    }

    products.forEach((product) => {
        const card = productCardTemplate.content.cloneNode(true);

        const image = card.querySelector('[data-field="image"]');
        const name = card.querySelector('[data-field="name"]');
        const status = card.querySelector('[data-field="status"]');

        const currentPrice = card.querySelector(
            '[data-field="current-price"]'
        );

        const targetPrice = card.querySelector(
            '[data-field="target-price"]'
        );

        const lastCheck = card.querySelector(
            '[data-field="last-check"]'
        );

        image.src = product.imagen_url;
        image.alt = `Portada de ${product.nombre}`;

        name.textContent = product.nombre;

        currentPrice.textContent = formatPrice(
            product.precio_actual,
            product.moneda
        );

        targetPrice.textContent = formatPrice(
            product.precio_objetivo,
            product.moneda
        );

        lastCheck.textContent = formatDate(
            product.fecha_ultima_revision
        );

        if (product.activo) {
            status.textContent = "Activo";

            status.classList.add(
                "bg-emerald-100",
                "text-emerald-700"
            );
        } else {
            status.textContent = "Inactivo";

            status.classList.add(
                "bg-slate-100",
                "text-slate-600"
            );
        }

        productsGrid.append(card);
    });
}


function renderProductsLoading() {
    productsGrid.innerHTML = `
        <div
            class="col-span-full rounded-2xl border
                   border-slate-200 bg-white px-6 py-14
                   text-center text-sm text-slate-500"
        >
            Cargando productos...
        </div>
    `;
}


function renderProductsError(message) {
    productsGrid.replaceChildren();

    const errorBox = document.createElement("div");

    errorBox.className =
        "col-span-full rounded-2xl border border-red-200 " +
        "bg-red-50 px-6 py-5 text-sm text-red-700";

    errorBox.textContent = message;

    productsGrid.append(errorBox);
}


async function loadProducts() {
    renderProductsLoading();

    try {
        const products = await apiRequest("/productos", {
            headers: {
                Authorization: `Bearer ${getToken()}`,
            },
        });

        renderProducts(products);

    } catch (error) {
        if (
            error.message.includes("token")
            || error.message.includes("sesión")
        ) {
            removeToken();
            showAuthentication();
            return;
        }

        renderProductsError(error.message);
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


productForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const submitButton = productForm.querySelector(
        'button[type="submit"]'
    );

    const formData = new FormData(productForm);

    const productData = {
        url: formData.get("url"),
        precio_objetivo: formData.get("precio_objetivo"),
    };

    productFormMessage.classList.add("hidden");
    submitButton.disabled = true;
    submitButton.textContent = "Consultando producto...";

    try {
        await apiRequest("/productos", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${getToken()}`,
            },
            body: JSON.stringify(productData),
        });

        closeProductModal();
        await loadProducts();

    } catch (error) {
        productFormMessage.textContent = error.message;

        productFormMessage.className =
            "mt-5 rounded-xl bg-red-50 px-4 py-3 " +
            "text-sm text-red-700";

    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Monitorear";
    }
});


restoreSession();