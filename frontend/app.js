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

loginTab.addEventListener("click", showLogin);
registerTab.addEventListener("click", showRegister);

/*
 * Por ahora evitamos que los formularios recarguen la página.
 * En el siguiente incremento estas funciones llamarán a FastAPI.
 */
loginForm.addEventListener("submit", (event) => {
    event.preventDefault();

    formMessage.textContent =
        "La conexión con FastAPI se añadirá en el siguiente incremento.";

    formMessage.className =
        "mt-5 rounded-xl bg-blue-50 px-4 py-3 text-sm text-blue-700";
});

registerForm.addEventListener("submit", (event) => {
    event.preventDefault();

    formMessage.textContent =
        "La conexión con FastAPI se añadirá en el siguiente incremento.";

    formMessage.className =
        "mt-5 rounded-xl bg-blue-50 px-4 py-3 text-sm text-blue-700";
});