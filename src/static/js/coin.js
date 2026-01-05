const coin = document.getElementById('coin');
const result = document.getElementById('result');
const scoreEl = document.getElementById('score');
const balanceEl = document.getElementById('balance');
const btnHeads = document.getElementById('pick-heads');
const btnTails = document.getElementById('pick-tails');
const multiplierSlider = document.getElementById('multiplier');
const multiplierText = document.getElementById('multiplier-text');
const formScore = document.getElementById('form-score');
const saveForm = document.getElementById('save-form');
const balanceToSend = document.getElementById('balance-to-send');
const endsession = document.getElementById("end-session");

let score = 0;
let balance = parseFloat(balanceEl.textContent.replace('Balance: $',''));
let multiplier = parseInt(multiplierSlider.value);

multiplierSlider.oninput = () => {
    multiplier = parseInt(multiplierSlider.value);
    multiplierText.textContent = multiplier;
};

function flipCoin(playerPick) {
    const toss = Math.random() < 0.5 ? 'Heads' : 'Tails';
    const flips = 6;

    coin.style.transition = "none";
    coin.style.transform = "rotateY(0deg)";
    void coin.offsetWidth; // force reflow

    const finalRotation = flips * 360 + (toss === 'Tails' ? 180 : 0);
    coin.style.transition = "transform 1s ease-in-out";
    coin.style.transform = `rotateY(${finalRotation}deg)`;

    setTimeout(() => {
        let change = 0;
        if(playerPick === toss) {
            change = multiplier;
            result.textContent = `You won! +$${change}`;
        } else {
            change = -multiplier;
            result.textContent = `You lost! -$${multiplier}`;
        }

        balance += change;
        score += change;

        balanceEl.textContent = `Balance: $${balance}`;
        scoreEl.textContent = `Score: ${score}`;
        formScore.value = score;
        balanceToSend.value = balance

        if(balance <= 0) {
            saveForm.submit();
        }
    }, 1000);
}

btnHeads.addEventListener('click', () => flipCoin('Heads'));
btnTails.addEventListener('click', () => flipCoin('Tails'));

endsession.addEventListener("click", () => {
    balanceToSend.value = balance;
    formScore.value = score;
    saveForm.submit();
});