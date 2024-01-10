document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("submit_logout").addEventListener("click", (e) => {
        e.preventDefault()
        document.getElementById("logout_form").submit()
    })
})