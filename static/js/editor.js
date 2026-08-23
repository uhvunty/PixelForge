class PixelEditor {

    constructor(canvas, width, height) {

        this.canvas = canvas;
        this.ctx = canvas.getContext("2d");

        this.width = width;
        this.height = height;

        this.currentColor = "#7c3aed";
        this.backgroundColor = "#ffffff";

        this.tool = "brush";
        this.brushSize = 1;

        this.isDrawing = false;
        this.lastPixel = null;

        this.showGrid = true;

        this.undoStack = [];
        this.redoStack = [];

        this.pixels = [];

        this.pixelSize = 16;

        this.initialize();
    }


    initialize() {

        this.pixelSize = Math.max(
            1,
            Math.floor(512 / Math.max(this.width, this.height))
        );

        this.canvas.width = this.width * this.pixelSize;
        this.canvas.height = this.height * this.pixelSize;

        this.pixels = [];

        for (let y = 0; y < this.height; y++) {

            const row = [];

            for (let x = 0; x < this.width; x++) {

                row.push(this.backgroundColor);

            }

            this.pixels.push(row);
        }

        this.saveState();

        this.draw();

        this.attachEvents();
    }


    attachEvents() {

        this.canvas.addEventListener(
            "mousedown",
            (event) => {

                event.preventDefault();

                this.isDrawing = true;

                this.lastPixel = null;

                this.saveState();

                this.paintEvent(event);
            }
        );


        this.canvas.addEventListener(
            "mousemove",
            (event) => {

                if (!this.isDrawing) {
                    return;
                }

                this.paintEvent(event);
            }
        );


        window.addEventListener(
            "mouseup",
            () => {

                this.isDrawing = false;

                this.lastPixel = null;
            }
        );


        this.canvas.addEventListener(
            "mouseleave",
            () => {

                if (this.isDrawing) {
                    this.lastPixel = null;
                }
            }
        );


        this.canvas.addEventListener(
            "touchstart",
            (event) => {

                event.preventDefault();

                this.isDrawing = true;

                this.lastPixel = null;

                this.saveState();

                this.paintEvent(event.touches[0]);
            },
            { passive: false }
        );


        this.canvas.addEventListener(
            "touchmove",
            (event) => {

                event.preventDefault();

                if (!this.isDrawing) {
                    return;
                }

                this.paintEvent(event.touches[0]);
            },
            { passive: false }
        );


        window.addEventListener(
            "touchend",
            () => {

                this.isDrawing = false;

                this.lastPixel = null;
            }
        );
    }


    getPixelCoordinates(event) {

        const rect =
            this.canvas.getBoundingClientRect();

        /*
         * IMPORTANT:
         * The canvas may be displayed at a different
         * size than its internal resolution.
         *
         * Therefore we calculate the scale using
         * the actual displayed dimensions.
         */

        const scaleX =
            this.canvas.width / rect.width;

        const scaleY =
            this.canvas.height / rect.height;


        const canvasX =
            (event.clientX - rect.left) * scaleX;

        const canvasY =
            (event.clientY - rect.top) * scaleY;


        const x =
            Math.floor(
                canvasX / this.pixelSize
            );

        const y =
            Math.floor(
                canvasY / this.pixelSize
            );


        return { x, y };
    }


    paintEvent(event) {

        const { x, y } =
            this.getPixelCoordinates(event);


        if (
            x < 0 ||
            y < 0 ||
            x >= this.width ||
            y >= this.height
        ) {
            return;
        }


        /*
         * Prevent repeatedly painting the exact
         * same pixel while dragging.
         */

        if (
            this.lastPixel &&
            this.lastPixel.x === x &&
            this.lastPixel.y === y
        ) {
            return;
        }


        this.lastPixel = { x, y };


        if (this.tool === "brush") {

            this.paintBrush(x, y);

        }

        else if (this.tool === "eraser") {

            this.paintBrush(
                x,
                y,
                this.backgroundColor
            );

        }

        else if (this.tool === "fill") {

            this.fill(x, y);

            this.isDrawing = false;

        }

        else if (this.tool === "picker") {

            this.pickColor(x, y);

            this.isDrawing = false;
        }
    }


    paintBrush(x, y, color = this.currentColor) {

        const half =
            Math.floor(this.brushSize / 2);


        for (
            let offsetY = -half;
            offsetY <= half;
            offsetY++
        ) {

            for (
                let offsetX = -half;
                offsetX <= half;
                offsetX++
            ) {

                const pixelX = x + offsetX;
                const pixelY = y + offsetY;


                if (
                    pixelX >= 0 &&
                    pixelX < this.width &&
                    pixelY >= 0 &&
                    pixelY < this.height
                ) {

                    this.pixels[pixelY][pixelX] =
                        color;
                }
            }
        }


        this.draw();
    }


    setColor(color) {

        this.currentColor = color;

        this.tool = "brush";
    }


    setTool(tool) {

        this.tool = tool;
    }


    setBrushSize(size) {

        this.brushSize =
            Math.max(
                1,
                parseInt(size)
            );
    }


    fill(startX, startY) {

        const targetColor =
            this.pixels[startY][startX];

        const replacementColor =
            this.currentColor;


        if (
            targetColor === replacementColor
        ) {
            return;
        }


        const queue = [
            [startX, startY]
        ];

        const visited =
            new Set();


        while (queue.length > 0) {

            const [
                x,
                y
            ] = queue.shift();


            const key =
                `${x},${y}`;


            if (visited.has(key)) {
                continue;
            }


            visited.add(key);


            if (
                x < 0 ||
                x >= this.width ||
                y < 0 ||
                y >= this.height
            ) {
                continue;
            }


            if (
                this.pixels[y][x] !== targetColor
            ) {
                continue;
            }


            this.pixels[y][x] =
                replacementColor;


            queue.push([x + 1, y]);
            queue.push([x - 1, y]);
            queue.push([x, y + 1]);
            queue.push([x, y - 1]);
        }


        this.draw();
    }


    pickColor(x, y) {

        const color =
            this.pixels[y][x];


        this.currentColor = color;


        const colorInput =
            document.getElementById(
                "studio-color"
            );


        if (colorInput) {

            colorInput.value =
                color;
        }


        this.tool = "brush";
    }


    setPixel(x, y, color) {

        if (
            x < 0 ||
            y < 0 ||
            x >= this.width ||
            y >= this.height
        ) {
            return;
        }


        this.pixels[y][x] = color;

        this.draw();
    }


    saveState() {

        const state =
            this.pixels.map(
                row => [...row]
            );


        /*
         * Don't add duplicate states.
         */

        const last =
            this.undoStack[
                this.undoStack.length - 1
            ];


        if (
            last &&
            JSON.stringify(last) ===
            JSON.stringify(state)
        ) {
            return;
        }


        this.undoStack.push(state);


        if (this.undoStack.length > 50) {

            this.undoStack.shift();
        }


        this.redoStack = [];
    }


    undo() {

        if (this.undoStack.length <= 1) {
            return;
        }


        const current =
            this.undoStack.pop();


        this.redoStack.push(
            current
        );


        const previous =
            this.undoStack[
                this.undoStack.length - 1
            ];


        this.pixels =
            previous.map(
                row => [...row]
            );


        this.draw();
    }


    redo() {

        if (this.redoStack.length === 0) {
            return;
        }


        const next =
            this.redoStack.pop();


        this.undoStack.push(
            next.map(
                row => [...row]
            )
        );


        this.pixels =
            next.map(
                row => [...row]
            );


        this.draw();
    }


    toggleGrid() {

        this.showGrid =
            !this.showGrid;

        this.draw();

        return this.showGrid;
    }


    clear() {

        this.saveState();


        for (
            let y = 0;
            y < this.height;
            y++
        ) {

            for (
                let x = 0;
                x < this.width;
                x++
            ) {

                this.pixels[y][x] =
                    this.backgroundColor;
            }
        }


        this.draw();
    }


    draw() {

        this.ctx.clearRect(
            0,
            0,
            this.canvas.width,
            this.canvas.height
        );


        /*
         * Draw pixels.
         */

        for (
            let y = 0;
            y < this.height;
            y++
        ) {

            for (
                let x = 0;
                x < this.width;
                x++
            ) {

                this.ctx.fillStyle =
                    this.pixels[y][x];


                this.ctx.fillRect(
                    x * this.pixelSize,
                    y * this.pixelSize,
                    this.pixelSize,
                    this.pixelSize
                );
            }
        }


        /*
         * Draw grid on top.
         */

        if (this.showGrid) {

            this.ctx.beginPath();

            this.ctx.strokeStyle =
                "rgba(80, 60, 120, 0.18)";

            this.ctx.lineWidth = 1;


            for (
                let x = 0;
                x <= this.width;
                x++
            ) {

                const position =
                    x * this.pixelSize + 0.5;


                this.ctx.moveTo(
                    position,
                    0
                );

                this.ctx.lineTo(
                    position,
                    this.canvas.height
                );
            }


            for (
                let y = 0;
                y <= this.height;
                y++
            ) {

                const position =
                    y * this.pixelSize + 0.5;


                this.ctx.moveTo(
                    0,
                    position
                );

                this.ctx.lineTo(
                    this.canvas.width,
                    position
                );
            }


            this.ctx.stroke();
        }
    }


    getData() {

        const flatPixels = [];


        for (
            let y = 0;
            y < this.height;
            y++
        ) {

            for (
                let x = 0;
                x < this.width;
                x++
            ) {

                flatPixels.push({

                    x: x,

                    y: y,

                    color:
                        this.pixels[y][x]
                });
            }
        }


        return {

            width: this.width,

            height: this.height,

            pixels: flatPixels
        };
    }


    download() {

        /*
         * Create a clean version without
         * the editor grid.
         */

        const exportCanvas =
            document.createElement("canvas");


        exportCanvas.width =
            this.width;


        exportCanvas.height =
            this.height;


        const exportCtx =
            exportCanvas.getContext("2d");


        for (
            let y = 0;
            y < this.height;
            y++
        ) {

            for (
                let x = 0;
                x < this.width;
                x++
            ) {

                exportCtx.fillStyle =
                    this.pixels[y][x];


                exportCtx.fillRect(
                    x,
                    y,
                    1,
                    1
                );
            }
        }


        const link =
            document.createElement("a");


        link.download =
            "pixelforge-art.png";


        link.href =
            exportCanvas.toDataURL(
                "image/png"
            );


        link.click();
    }
}