document.addEventListener("DOMContentLoaded", () => {

    const canvas =
        document.getElementById(
            "multiplayer-canvas"
        );

    if (!canvas) {
        return;
    }

    const roomCodeElement =
        document.getElementById(
            "room-code"
        );

    if (!roomCodeElement) {
        return;
    }

    const roomCode =
        roomCodeElement.textContent.trim();

    const gridSize =
        parseInt(
            canvas.getAttribute("width"),
            10
        );

    const editor =
        new PixelEditor(
            canvas,
            gridSize,
            gridSize
        );

    const colorInput =
        document.getElementById(
            "multiplayer-color"
        );

    const status =
        document.getElementById(
            "connection-status"
        );

    const statusDot =
        document.getElementById(
            "status-dot"
        );

    const onlineUsers =
        document.getElementById(
            "online-users"
        );

    const message =
        document.getElementById(
            "multiplayer-message"
        );

    let joined = false;

    let polling = null;

    let sendingPixel = false;


    // --------------------------------------------------
    // MESSAGE
    // --------------------------------------------------

    function showMessage(text) {

        if (!message) {
            return;
        }

        message.textContent = text;
    }


    // --------------------------------------------------
    // CONNECTION UI
    // --------------------------------------------------

    function setConnected() {

        if (status) {
            status.textContent =
                "Connected";
        }

        if (statusDot) {
            statusDot.classList.add(
                "connected"
            );
        }
    }


    function setDisconnected() {

        if (status) {
            status.textContent =
                "Disconnected";
        }

        if (statusDot) {
            statusDot.classList.remove(
                "connected"
            );
        }
    }


    // --------------------------------------------------
    // CANVAS CONVERSION
    // --------------------------------------------------

    function convertCanvasToEditorPixels(
        canvasData
    ) {

        const width =
            parseInt(
                canvasData.width,
                10
            );

        const height =
            parseInt(
                canvasData.height,
                10
            );

        const pixels = [];

        for (
            let y = 0;
            y < height;
            y++
        ) {

            const row = [];

            for (
                let x = 0;
                x < width;
                x++
            ) {

                row.push(
                    "#ffffff"
                );

            }

            pixels.push(row);
        }

        if (
            Array.isArray(
                canvasData.pixels
            )
        ) {

            canvasData.pixels.forEach(
                (pixel) => {

                    if (!pixel) {
                        return;
                    }

                    const x =
                        parseInt(
                            pixel.x,
                            10
                        );

                    const y =
                        parseInt(
                            pixel.y,
                            10
                        );

                    if (
                        x >= 0 &&
                        x < width &&
                        y >= 0 &&
                        y < height
                    ) {

                        pixels[y][x] =
                            pixel.color ||
                            "#ffffff";

                    }

                }
            );

        }

        return {
            width,
            height,
            pixels
        };
    }


    // --------------------------------------------------
    // DRAW SERVER CANVAS
    // --------------------------------------------------

    function applyCanvas(
        canvasData
    ) {

        if (!canvasData) {
            return;
        }

        const converted =
            convertCanvasToEditorPixels(
                canvasData
            );

        editor.width =
            converted.width;

        editor.height =
            converted.height;

        editor.pixels =
            converted.pixels;

        editor.draw();
    }


    // --------------------------------------------------
    // JOIN
    // --------------------------------------------------

    async function joinRoom() {

        try {

            const response =
                await fetch(
                    `/multiplayer/api/${roomCode}/join`,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type":
                                "application/json"
                        }
                    }
                );

            const data =
                await response.json();

            if (!response.ok) {

                if (
                    response.status === 409
                ) {

                    showMessage(
                        "Room is full. Maximum 3 players are allowed."
                    );

                    if (canvas) {
                        canvas.style.pointerEvents =
                            "none";

                        canvas.style.opacity =
                            "0.55";
                    }

                    if (status) {
                        status.textContent =
                            "Room Full";
                    }

                    return;
                }

                throw new Error(
                    data.message ||
                    "Unable to join room."
                );
            }

            joined = true;

            setConnected();

            updatePlayerCount(
                data.players
            );

            applyCanvas(
                data.canvas
            );

            showMessage(
                "You are painting together with everyone in this room."
            );

            startPolling();

        } catch (error) {

            console.error(
                "Multiplayer join error:",
                error
            );

            setDisconnected();

            showMessage(
                "Unable to connect to the multiplayer room."
            );
        }
    }


    // --------------------------------------------------
    // PLAYER COUNT
    // --------------------------------------------------

    function updatePlayerCount(
        count
    ) {

        if (!onlineUsers) {
            return;
        }

        onlineUsers.textContent =
            `${count}/3`;
    }


    // --------------------------------------------------
    // POLLING
    // --------------------------------------------------

    function startPolling() {

        if (polling) {
            return;
        }

        polling =
            setInterval(
                async () => {

                    if (!joined) {
                        return;
                    }

                    try {

                        const response =
                            await fetch(
                                `/multiplayer/api/${roomCode}/state`,
                                {
                                    cache:
                                        "no-store"
                                }
                            );

                        if (!response.ok) {

                            if (
                                response.status ===
                                403
                            ) {

                                joined = false;

                                showMessage(
                                    "Your room session expired."
                                );

                            }

                            return;
                        }

                        const data =
                            await response.json();

                        setConnected();

                        updatePlayerCount(
                            data.players
                        );

                        applyCanvas(
                            data.canvas
                        );

                    } catch (error) {

                        console.error(
                            "Multiplayer polling error:",
                            error
                        );

                        setDisconnected();
                    }

                },
                1000
            );
    }


    // --------------------------------------------------
    // COLOR
    // --------------------------------------------------

    if (colorInput) {

        colorInput.addEventListener(
            "input",
            () => {

                editor.setColor(
                    colorInput.value
                );

            }
        );
    }


    // --------------------------------------------------
    // PAINT
    // --------------------------------------------------

    canvas.addEventListener(
        "click",
        async (event) => {

            if (!joined) {
                return;
            }

            if (sendingPixel) {
                return;
            }

            const rect =
                canvas.getBoundingClientRect();

            if (
                rect.width === 0 ||
                rect.height === 0
            ) {
                return;
            }

            const x =
                Math.floor(
                    (
                        event.clientX -
                        rect.left
                    ) /
                    rect.width *
                    gridSize
                );

            const y =
                Math.floor(
                    (
                        event.clientY -
                        rect.top
                    ) /
                    rect.height *
                    gridSize
                );

            if (
                x < 0 ||
                x >= gridSize ||
                y < 0 ||
                y >= gridSize
            ) {
                return;
            }

            const color =
                colorInput
                    ? colorInput.value
                    : "#000000";

            sendingPixel = true;

            try {

                const response =
                    await fetch(
                        `/multiplayer/api/${roomCode}/paint`,
                        {
                            method: "POST",
                            headers: {
                                "Content-Type":
                                    "application/json"
                            },
                            body: JSON.stringify({
                                x: x,
                                y: y,
                                color: color
                            })
                        }
                    );

                const data =
                    await response.json();

                if (!response.ok) {

                    showMessage(
                        data.message ||
                        "Could not paint pixel."
                    );

                    return;
                }

                // Update our canvas immediately.
                if (
                    editor.pixels[y] &&
                    editor.pixels[y][x]
                ) {

                    editor.pixels[y][x] =
                        color;

                    editor.draw();
                }

            } catch (error) {

                console.error(
                    "Pixel paint error:",
                    error
                );

                showMessage(
                    "Could not send pixel to the room."
                );

            } finally {

                sendingPixel = false;
            }

        }
    );


    // --------------------------------------------------
    // LEAVE
    // --------------------------------------------------

    async function leaveRoom() {

        if (!joined) {
            return;
        }

        joined = false;

        try {

            await fetch(
                `/multiplayer/api/${roomCode}/leave`,
                {
                    method: "POST",
                    keepalive: true,
                    headers: {
                        "Content-Type":
                            "application/json"
                    }
                }
            );

        } catch (error) {

            console.error(
                "Leave room error:",
                error
            );
        }
    }


    window.addEventListener(
        "pagehide",
        leaveRoom
    );


    // --------------------------------------------------
    // START
    // --------------------------------------------------

    joinRoom();

});