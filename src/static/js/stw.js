const canvas = document.getElementById("wheel");
const ctx = canvas.getContext("2d");

const scoreEl = document.getElementById('score');
const balanceEl = document.getElementById('balance');
const multiplierSlider = document.getElementById('multiplier');
const multiplierText = document.getElementById('multiplier-text');
const formScore = document.getElementById('form-score');
const saveForm = document.getElementById('save-form');
const balanceToSend = document.getElementById('balance-to-send');
const spinBtn = document.getElementById("spinBtn");
const endsession = document.getElementById("end-session");

let score = 0;
let balance = parseFloat(balanceEl.textContent.replace('Balance: $',''));
let multiplier = parseInt(multiplierSlider.value);

multiplierSlider.oninput = () => {
    multiplier = parseInt(multiplierSlider.value);
    multiplierText.textContent = multiplier;
};

const options = ["1X", "-1X", "0", "2X", "5X", "-1/2X"];
const colors = ["#4caf50","#f44336","#ffeb3b","#2196f3","#9c27b0","#ff9800"];
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
        ctx.arc(centerX, centerY, radius, currentAngle + i*sliceAngle, currentAngle + (i+1)*sliceAngle);
        ctx.fillStyle = colors[i];
        ctx.fill();

        ctx.save();
        ctx.translate(centerX, centerY);
        ctx.rotate(currentAngle + (i+0.5)*sliceAngle);
        ctx.textAlign = "right";
        ctx.fillStyle = "#000";
        ctx.font = "16px Arial";
        ctx.fillText(options[i], radius - 10, 5);
        ctx.restore();
    }
}

drawWheel();

spinBtn.addEventListener("click", () => {
    if(spinning) return;
    spinning = true;

    const spinAngle = Math.random()*2000 + 2000;
    let start = null;

    function animate(timestamp) {
        if(!start) start = timestamp;
        let progress = timestamp - start;
        currentAngle += spinAngle / 1000;
        ctx.clearRect(0,0,canvas.width,canvas.height);
        drawWheel();

        if(progress < 2000){
            requestAnimationFrame(animate);
        } else {
            spinning = false;
            showResult();
        }
    }

    requestAnimationFrame(animate);
});

function showResult() {
    const index = Math.floor(((2*Math.PI - (currentAngle % (2*Math.PI)))/sliceAngle)%options.length);
    let outcome = options[index];
    let change = 0;

    switch(outcome){
        case "1X": change = multiplier; break;
        case "2X": change = multiplier*2; break;
        case "5X": change = multiplier*5; break;
        case "-1X": change = -multiplier; break;
        case "0": change = 0; break;
        case "-1/2X": change = -Math.floor(multiplier/2); break;
    }

    balance += change;
    score += change;

    document.getElementById("result").innerText = `${outcome}! ${change >= 0 ? "+" : ""}$${change}`;
    balanceEl.textContent = `Balance: $${balance}`;
    scoreEl.textContent = `Score: ${score}`;
    formScore.value = score;
    balanceToSend.value = balance;
 
    multiplierSlider.max = balance
    multiplierSlider.value = Math.round(balance/2)
    multiplierText.textContent = multiplierSlider.value

    if(balance < 10) {
        saveForm.submit();
    }
}

endsession.addEventListener("click", () => {
    balanceToSend.value = balance;
    formScore.value = score;
    saveForm.submit();
});