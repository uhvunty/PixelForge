document.addEventListener("DOMContentLoaded", () => {

    const forms = document.querySelectorAll(
        "form[data-auth-form]"
    );

    forms.forEach((form) => {

        form.addEventListener("submit", (event) => {

            const password = form.querySelector(
                'input[name="password"]'
            );

            const confirmPassword = form.querySelector(
                'input[name="confirm_password"]'
            );

            if (!password) {
                return;
            }

            /*
             * Only validate password length when registering.
             * Login should always be allowed to submit the
             * entered password to Flask for verification.
             */
            const isRegisterForm =
                !!confirmPassword;

            if (
                isRegisterForm &&
                password.value.length < 8
            ) {

                event.preventDefault();

                showAuthMessage(
                    form,
                    "Password must contain at least 8 characters."
                );

                return;
            }

            if (
                isRegisterForm &&
                password.value !== confirmPassword.value
            ) {

                event.preventDefault();

                showAuthMessage(
                    form,
                    "Passwords do not match."
                );

            }

        });

    });


    /*
     * Password show/hide button
     */

    const passwordInputs =
        document.querySelectorAll(
            'input[type="password"][data-password-toggle]'
        );


    passwordInputs.forEach((input) => {

        const button =
            document.createElement("button");

        button.type = "button";

        button.className =
            "password-toggle";

        button.textContent =
            "Show";


        input.parentElement.appendChild(
            button
        );


        button.addEventListener(
            "click",
            () => {

                const hidden =
                    input.type === "password";


                input.type =
                    hidden
                        ? "text"
                        : "password";


                button.textContent =
                    hidden
                        ? "Hide"
                        : "Show";

            }
        );

    });

});


function showAuthMessage(
    form,
    message
) {

    let messageElement =
        form.querySelector(
            ".auth-client-message"
        );


    if (!messageElement) {

        messageElement =
            document.createElement("div");

        messageElement.className =
            "auth-client-message";

        form.prepend(
            messageElement
        );

    }


    messageElement.textContent =
        message;

}