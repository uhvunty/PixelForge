document.addEventListener("DOMContentLoaded", () => {

    const canvas =
        document.getElementById("studio-canvas");

    if (!canvas) {

        console.error(
            "PixelForge: studio-canvas not found."
        );

        return;
    }


    const colorInput =
        document.getElementById("studio-color");


    const sizeSelect =
        document.getElementById("studio-grid-size");


    const sizeDisplay =
        document.getElementById("studio-size-display");


    const titleInput =
        document.getElementById("studio-title");


    const clearButton =
        document.getElementById("studio-clear");


    const downloadButton =
        document.getElementById("studio-download");


    const saveButton =
        document.getElementById("studio-save");


    const undoButton =
        document.getElementById("studio-undo");


    const redoButton =
        document.getElementById("studio-redo");


    const gridButton =
        document.getElementById("studio-grid");


    const message =
        document.getElementById("studio-message");



    /* =====================================
       EDITOR
    ===================================== */

    let size = 32;


    if (sizeSelect) {

        const selected =
            parseInt(sizeSelect.value, 10);


        if (
            selected === 16 ||
            selected === 32
        ) {

            size = selected;

        }

    }


    let editor =
        new PixelEditor(
            canvas,
            size,
            size
        );



    /* =====================================
       COLOR
    ===================================== */

    if (colorInput) {

        editor.setColor(
            colorInput.value
        );


        colorInput.addEventListener(
            "input",
            () => {

                editor.setColor(
                    colorInput.value
                );


                setActiveTool("brush");

            }
        );

    }



    /* =====================================
       ACTIVE TOOL
    ===================================== */

    function setActiveTool(tool) {

        editor.setTool(tool);


        const buttons =
            document.querySelectorAll(
                ".tool-button"
            );


        buttons.forEach(
            button => {

                button.classList.toggle(
                    "active",
                    button.dataset.tool === tool
                );

            }
        );

    }



    /* =====================================
       TOOL BUTTONS
    ===================================== */

    const toolButtons =
        document.querySelectorAll(
            ".tool-button"
        );


    toolButtons.forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    const tool =
                        button.dataset.tool;


                    if (!tool) {
                        return;
                    }


                    setActiveTool(tool);

                }
            );

        }
    );



    /* =====================================
       BRUSH SIZE
    ===================================== */

    const brushSizeButtons =
        document.querySelectorAll(
            ".brush-size"
        );


    brushSizeButtons.forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    const brushSize =
                        parseInt(
                            button.dataset.brushSize,
                            10
                        );


                    if (
                        Number.isNaN(brushSize)
                    ) {

                        return;

                    }


                    editor.setBrushSize(
                        brushSize
                    );


                    brushSizeButtons.forEach(
                        otherButton => {

                            otherButton.classList.toggle(
                                "active",
                                otherButton === button
                            );

                        }
                    );

                }
            );

        }
    );



    /* =====================================
       SIZE DISPLAY
    ===================================== */

    function updateSizeDisplay() {

        if (!sizeDisplay) {
            return;
        }


        sizeDisplay.textContent =
            `${size} × ${size}`;

    }


    updateSizeDisplay();



    /* =====================================
       CANVAS SIZE
    ===================================== */

    if (sizeSelect) {

        sizeSelect.addEventListener(
            "change",
            () => {

                const newSize =
                    parseInt(
                        sizeSelect.value,
                        10
                    );


                /*
                 * Only 16 and 32 are allowed.
                 */

                if (
                    newSize !== 16 &&
                    newSize !== 32
                ) {

                    sizeSelect.value =
                        size;

                    return;

                }


                if (
                    editor &&
                    typeof editor.destroy ===
                    "function"
                ) {

                    editor.destroy();

                }


                size =
                    newSize;


                editor =
                    new PixelEditor(
                        canvas,
                        size,
                        size
                    );


                if (colorInput) {

                    editor.setColor(
                        colorInput.value
                    );

                }


                editor.setBrushSize(1);


                setActiveTool("brush");


                brushSizeButtons.forEach(
                    (button, index) => {

                        button.classList.toggle(
                            "active",
                            index === 0
                        );

                    }
                );


                updateSizeDisplay();

            }
        );

    }



    /* =====================================
       CLEAR
    ===================================== */

    if (clearButton) {

        clearButton.addEventListener(
            "click",
            () => {

                editor.clear();


                showMessage(
                    "Canvas cleared.",
                    "success"
                );

            }
        );

    }



    /* =====================================
       DOWNLOAD
    ===================================== */

    if (downloadButton) {

        downloadButton.addEventListener(
            "click",
            () => {

                editor.download();

            }
        );

    }



    /* =====================================
       UNDO
    ===================================== */

    if (undoButton) {

        undoButton.addEventListener(
            "click",
            () => {

                editor.undo();

            }
        );

    }



    /* =====================================
       REDO
    ===================================== */

    if (redoButton) {

        redoButton.addEventListener(
            "click",
            () => {

                editor.redo();

            }
        );

    }



    /* =====================================
       GRID
    ===================================== */

    if (gridButton) {

        gridButton.addEventListener(
            "click",
            () => {

                const visible =
                    editor.toggleGrid();


                gridButton.classList.toggle(
                    "active",
                    visible
                );

            }
        );

    }



    /* =====================================
       SAVE ARTWORK
    ===================================== */

    if (saveButton) {

        saveButton.addEventListener(
            "click",
            async () => {

                const title =
                    titleInput
                        ? titleInput.value.trim()
                        : "";


                if (!title) {

                    showMessage(
                        "Please enter an artwork title.",
                        "error"
                    );


                    if (titleInput) {

                        titleInput.focus();

                    }


                    return;

                }


                saveButton.disabled = true;


                const originalText =
                    saveButton.textContent;


                saveButton.textContent =
                    "Saving...";


                try {

                    const editorData =
                        editor.getData();


                    const response =
                        await fetch(
                            "/studio/save",
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body:
                                    JSON.stringify({
                                        title: title,
                                        ...editorData
                                    })
                            }
                        );


                    let result;


                    try {

                        result =
                            await response.json();

                    } catch (error) {

                        result = {
                            success: false,
                            message:
                                "Invalid server response."
                        };

                    }


                    if (
                        !response.ok ||
                        !result.success
                    ) {

                        throw new Error(
                            result.message ||
                            "Unable to save artwork."
                        );

                    }


                    /*
                     * Save was successful.
                     *
                     * Instead of leaving the user
                     * inside the editor, return them
                     * directly to their dashboard.
                     */

                    saveButton.textContent =
                        "Saved!";


                    showMessage(
                        "Artwork saved. Returning to dashboard...",
                        "success"
                    );


                    setTimeout(
                        () => {

                            window.location.href =
                                "/dashboard";

                        },
                        700
                    );


                } catch (error) {

                    console.error(
                        "PixelForge save error:",
                        error
                    );


                    showMessage(
                        error.message ||
                        "Something went wrong while saving.",
                        "error"
                    );


                    saveButton.disabled =
                        false;


                    saveButton.textContent =
                        originalText;

                }

            }
        );

    }



    /* =====================================
       KEYBOARD SHORTCUTS
    ===================================== */

    document.addEventListener(
        "keydown",
        event => {

            const active =
                document.activeElement;


            if (
                active &&
                (
                    active.tagName === "INPUT" ||
                    active.tagName === "TEXTAREA" ||
                    active.tagName === "SELECT"
                )
            ) {

                return;

            }


            const key =
                event.key.toLowerCase();



            if (key === "b") {

                event.preventDefault();

                setActiveTool("brush");

            }


            else if (key === "e") {

                event.preventDefault();

                setActiveTool("eraser");

            }


            else if (key === "g") {

                event.preventDefault();

                setActiveTool("fill");

            }


            else if (key === "i") {

                event.preventDefault();

                setActiveTool("picker");

            }


            else if (
                event.ctrlKey &&
                key === "z"
            ) {

                event.preventDefault();

                editor.undo();

            }


            else if (
                event.ctrlKey &&
                key === "y"
            ) {

                event.preventDefault();

                editor.redo();

            }

        }
    );



    /* =====================================
       MESSAGE
    ===================================== */

    function showMessage(
        text,
        type = "success"
    ) {

        if (!message) {
            return;
        }


        message.textContent =
            text;


        message.className =
            `studio-message ${type}`;


        clearTimeout(
            message._timeout
        );


        message._timeout =
            setTimeout(
                () => {

                    message.textContent =
                        "";

                },
                4000
            );

    }



    /* =====================================
       INITIAL STATE
    ===================================== */

    setActiveTool("brush");


    console.log(
        "PixelForge Studio loaded successfully."
    );

});