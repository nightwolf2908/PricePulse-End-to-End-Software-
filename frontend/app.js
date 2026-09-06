const loginTab = document.querySelector("#tab-login");
const registerTab = document.querySelector("#tab-register");

const loginForm = document.querySelector("#login-form");
const registerForm = document.querySelector("#register-form");
const formMessage = document.querySelector("#form-message");

const activeTabClasses = [
    "bg-white",
    "text-slate-900",
    "shadow-sm",
];

const inactiveTabClasses = [
    "text-slate-500",
];

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

function hideMessage() {
    formMessage.classList.add("hidden");
    formMessage.textContent = "";
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

    if (email) {
        userEmail.textContent = email;
    }
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

loginTab.addEventListener("click", showLogin);
registerTab.addEventListener("click", showRegister);

/*
 * Por ahora evitamos que los formularios recarguen la página.
 * En el siguiente incremento estas funciones llamarán a FastAPI.
 */
loginForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const formData = new FormData(loginForm);
    const email = formData.get("email");

    showDashboard(email);
});

registerForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const formData = new FormData(registerForm);
    const email = formData.get("email");

    showDashboard(email);
});

logoutButton.addEventListener("click", showAuthentication);

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
        "En el siguiente incremento enviaremos este producto a FastAPI.";

    productFormMessage.className =
        "mt-5 rounded-xl bg-blue-50 px-4 py-3 text-sm text-blue-700";
});