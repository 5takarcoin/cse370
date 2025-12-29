const canvas = document.getElementById("wheel");
const ctx = canvas.getContext("2d");

const options = ["Win", "Lose", "Try Again", "Bonus", "Jackpot", "Nothing"];
const colors = ["#f44336", "#2196f3", "#4caf50", "#ffeb3b", "#9c27b0", "#ff9800"];

const centerX = canvas.width / 2;
const centerY = canvas.height / 2;
const radius = 180;
const sliceAngle = (2 * Math.PI) / options.length;

let currentAngle = 0;
let spinning = false;

function drawWheel() {
    for (let i = 0; i < options.length; i++) {
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.arc(
            centerX,
            centerY,
            radius,
            currentAngle + i * sliceAngle,
            currentAngle + (i + 1) * sliceAngle
        );
        ctx.fillStyle = colors[i];
        ctx.fill();

        ctx.save();
        ctx.translate(centerX, centerY);
        ctx.rotate(currentAngle + (i + 0.5) * sliceAngle);
        ctx.textAlign = "right";
        ctx.fillStyle = "#000";
        ctx.font = "16px Arial";
        ctx.fillText(options[i], radius - 10, 5);
        ctx.restore();
    }
}

drawWheel();

document.getElementById("spinBtn").addEventListener("click", () => {
    if (spinning) return;
    spinning = true;

    let spinAngle = Math.random() * 2000 + 2000;
    let start = null;

    function animate(timestamp) {
        if (!start) start = timestamp;
        let progress = timestamp - start;
        currentAngle += spinAngle / 1000;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        drawWheel();

        if (progress < 2000) {
            requestAnimationFrame(animate);
        } else {
            spinning = false;
            showResult();
        }
    }

    requestAnimationFrame(animate);
});

function showResult() {
    const index = Math.floor(
        ((2 * Math.PI - (currentAngle % (2 * Math.PI))) / sliceAngle) % options.length
    );
    document.getElementById("result").innerText =
        "Result: " + options[index];
}
