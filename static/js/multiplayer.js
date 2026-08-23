document.addEventListener("DOMContentLoaded", () => {

    const canvas = document.getElementById(
        "multiplayer-canvas"
    );

    if (!canvas) {
        return;
    }


    const roomCodeElement = document.getElementById(
        "room-code"
    );

    if (!roomCodeElement) {
        return;
    }


    const roomCode =
        roomCodeElement.textContent.trim();


    const socket = io();


    const gridSize = parseInt(
        canvas.getAttribute("width"),
        10
    );


    const editor = new PixelEditor(
        canvas,
        gridSize,
        gridSize
    );


    /*
     * Multiplayer does not need the normal
     * PixelEditor drawing handlers.
     *
     * We only use PixelEditor for rendering
     * and storing the canvas.
     */


    const colorInput =
        document.getElementById(
            "multiplayer-color"
        );


    /*
     * Convert the server's flat pixel array
     * into PixelEditor's 2D array.
     */

    function convertCanvasToEditorPixels(canvasData) {

        const width = parseInt(
            canvasData.width,
            10
        );

        const height = parseInt(
            canvasData.height,
            10
        );


        const pixels = [];


        for (let y = 0; y < height; y++) {

            const row = [];

            for (let x = 0; x < width; x++) {

                row.push("#ffffff");

            }

            pixels.push(row);
        }


        if (Array.isArray(canvasData.pixels)) {

            canvasData.pixels.forEach((pixel) => {

                if (!pixel) {
                    return;
                }


                const x = parseInt(
                    pixel.x,
                    10
                );

                const y = parseInt(
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
                        pixel.color || "#ffffff";

                }

            });

        }


        return {
            width,
            height,
            pixels
        };
    }


    /*
     * Load complete canvas state
     * received from the server.
     */

    socket.on(
        "canvas_state",
        (data) => {

            if (
                !data ||
                !data.canvas
            ) {
                return;
            }


            const converted =
                convertCanvasToEditorPixels(
                    data.canvas
                );


            editor.width =
                converted.width;

            editor.height =
                converted.height;

            editor.pixels =
                converted.pixels;


            editor.draw();

        }
    );


    /*
     * Color picker
     */

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


    /*
     * Connect to Socket.IO server.
     */

    socket.on(
        "connect",
        () => {

            const status =
                document.getElementById(
                    "connection-status"
                );

            if (status) {

                status.textContent =
                    "Connected";

            }


            const dot =
                document.getElementById(
                    "status-dot"
                );

            if (dot) {

                dot.classList.add(
                    "connected"
                );

            }


            socket.emit(
                "join_canvas",
                {
                    room_code: roomCode
                }
            );

        }
    );


    /*
     * Clicking a pixel sends it to the server.
     */

    canvas.addEventListener(
        "click",
        (event) => {

            const rect =
                canvas.getBoundingClientRect();


            if (
                rect.width === 0 ||
                rect.height === 0
            ) {
                return;
            }


            /*
             * Use the actual displayed canvas size.
             * This prevents incorrect coordinates when
             * CSS scales the canvas.
             */

            const x = Math.floor(
                (
                    event.clientX -
                    rect.left
                ) /
                rect.width *
                gridSize
            );


            const y = Math.floor(
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


            socket.emit(
                "paint_pixel",
                {
                    room_code: roomCode,
                    x: x,
                    y: y,
                    color: color
                }
            );

        }
    );


    /*
     * Receive a pixel painted by ANY player.
     */

    socket.on(
        "pixel_updated",
        (data) => {

            if (!data) {
                return;
            }


            const x = parseInt(
                data.x,
                10
            );

            const y = parseInt(
                data.y,
                10
            );


            if (
                Number.isNaN(x) ||
                Number.isNaN(y)
            ) {
                return;
            }


            if (
                x < 0 ||
                x >= editor.width ||
                y < 0 ||
                y >= editor.height
            ) {
                return;
            }


            editor.pixels[y][x] =
                data.color || "#000000";


            editor.draw();

        }
    );


    /*
     * Player count
     */

    socket.on(
        "player_count",
        (data) => {

            const element =
                document.getElementById(
                    "online-users"
                );


            if (
                element &&
                data
            ) {

                element.textContent =
                    data.count;

            }

        }
    );


    /*
     * Pixel cooldown
     */

    socket.on(
        "pixel_cooldown",
        (data) => {

            const timer =
                document.getElementById(
                    "pixel-timer"
                );


            if (!timer) {
                return;
            }


            let remaining =
                parseInt(
                    data.remaining,
                    10
                );


            if (
                Number.isNaN(remaining)
            ) {
                return;
            }


            timer.textContent =
                `${remaining}s`;


            const interval =
                setInterval(
                    () => {

                        remaining--;

                        if (
                            remaining <= 0
                        ) {

                            clearInterval(
                                interval
                            );

                            timer.textContent =
                                "Ready";

                            return;

                        }


                        timer.textContent =
                            `${remaining}s`;

                    },
                    1000
                );

        }
    );


    /*
     * Server-side errors
     */

    socket.on(
        "canvas_error",
        (data) => {

            const message =
                document.getElementById(
                    "multiplayer-message"
                );


            if (
                message &&
                data
            ) {

                message.textContent =
                    data.message || "Canvas error.";

            }

        }
    );


    /*
     * Disconnect
     */

    socket.on(
        "disconnect",
        () => {

            const status =
                document.getElementById(
                    "connection-status"
                );


            if (status) {

                status.textContent =
                    "Disconnected";

            }


            const dot =
                document.getElementById(
                    "status-dot"
                );


            if (dot) {

                dot.classList.remove(
                    "connected"
                );

            }

        }
    );


    /*
     * Tell the server when leaving.
     */

    window.addEventListener(
        "beforeunload",
        () => {

            socket.emit(
                "leave_canvas",
                {
                    room_code: roomCode
                }
            );

        }
    );

});