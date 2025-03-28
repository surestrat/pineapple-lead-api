// Swagger UI Helper - Adds token management functionality

window.onload = function () {
	// Wait for Swagger UI to load
	setTimeout(function () {
		// Add a custom button to try authentication and store token
		const authSection = document.querySelector(
			'.opblock-tag-section[data-tag="Authentication"]'
		);

		if (authSection) {
			const buttonPanel = document.createElement("div");
			buttonPanel.className = "auth-helper-panel";
			buttonPanel.style.padding = "10px";
			buttonPanel.style.margin = "10px 0";
			buttonPanel.style.backgroundColor = "#f0f0f0";
			buttonPanel.style.borderRadius = "5px";

			const quickAuthButton = document.createElement("button");
			quickAuthButton.innerText = "Authenticate with Test Credentials";
			quickAuthButton.className = "btn try-out__btn";
			quickAuthButton.style.backgroundColor = "#49cc90";
			quickAuthButton.style.color = "white";
			quickAuthButton.onclick = tryAuthentication;

			const tokenDisplay = document.createElement("div");
			tokenDisplay.id = "token-display";
			tokenDisplay.style.marginTop = "10px";
			tokenDisplay.style.wordBreak = "break-all";

			buttonPanel.appendChild(quickAuthButton);
			buttonPanel.appendChild(tokenDisplay);

			// Insert before the first operation
			const firstOperation = authSection.querySelector(".opblock");
			if (firstOperation) {
				authSection.insertBefore(buttonPanel, firstOperation);
			}
		}

		// Check for stored token and update authorize button
		const storedToken = localStorage.getItem("bearerToken");
		if (storedToken) {
			updateAuthorizeButton(storedToken);
		}
	}, 1000);
};

function tryAuthentication() {
	const display = document.getElementById("token-display");
	display.innerHTML = "Authenticating...";

	fetch("/api/v1/auth/token", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({
			username: "test",
			password: "test",
		}),
	})
		.then((response) => response.json())
		.then((data) => {
			if (data.access_token) {
				const token = data.access_token;
				display.innerHTML = `<strong>Token received:</strong> ${token.substring(
					0,
					20
				)}...`;

				// Store token
				localStorage.setItem("bearerToken", token);

				// Update authorize button
				updateAuthorizeButton(token);
			} else {
				display.innerHTML = "Authentication failed!";
			}
		})
		.catch((error) => {
			display.innerHTML = `Error: ${error.message}`;
		});
}

function updateAuthorizeButton(token) {
	// Click on the authorize button
	const authorizeBtn = document.querySelector(".btn.authorize");
	if (authorizeBtn) {
		authorizeBtn.click();

		// Wait for modal to appear
		setTimeout(() => {
			// Fill in the token
			const tokenInput = document.querySelector(
				'.auth-container input[type="text"]'
			);
			if (tokenInput) {
				tokenInput.value = token;
			}

			// Click Authorize button in the modal
			const authBtnInModal = document.querySelector(
				".auth-btn-wrapper button.authorize"
			);
			if (authBtnInModal) {
				authBtnInModal.click();

				// Close the modal
				setTimeout(() => {
					const closeBtn = document.querySelector(".btn-done");
					if (closeBtn) {
						closeBtn.click();
					}
				}, 500);
			}
		}, 500);
	}
}
