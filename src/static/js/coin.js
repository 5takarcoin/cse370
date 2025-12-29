const coin = document.getElementById('coin');
const result = document.getElementById('result');
const scoreEl = document.getElementById('score');
const btnHeads = document.getElementById('pick-heads');
const btnTails = document.getElementById('pick-tails');

let wins = 0;
let losses = 0;

// Function to flip coin and update score
function flipCoin(playerPick) {
    const toss = Math.random() < 0.5 ? 'Heads' : 'Tails';
    const flips = 6;

    // Animate flip
    coin.style.transition = "none";
    coin.style.transform = "rotateY(0deg)";
    void coin.offsetWidth; // force reflow
    const finalRotation = flips * 360 + (toss === 'Tails' ? 180 : 0);
    coin.style.transition = "transform 1s ease-in-out";
    coin.style.transform = `rotateY(${finalRotation}deg)`;

    setTimeout(() => {
        if(playerPick === toss) {
            wins++;
            result.textContent = `You won!`;
        } else {
            losses++;
            result.textContent = `You lost!`;
        }

        // Calculate score
        const score = wins * 100 - losses * 50;
        scoreEl.textContent = `Score: ${score}`;
    }, 1000);
}

// Event listeners
btnHeads.addEventListener('click', () => flipCoin('Heads'));
btnTails.addEventListener('click', () => flipCoin('Tails'));
