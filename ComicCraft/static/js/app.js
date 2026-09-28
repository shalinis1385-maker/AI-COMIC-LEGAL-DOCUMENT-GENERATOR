function showLoading() {
    const button = document.getElementById("generateButton");
    const loading = document.getElementById("loading");
    if (button) {
        button.disabled = true;
        button.textContent = "Creating...";
    }
    if (loading) loading.classList.add("show");
}
